"""🐙 Ace (CHA-743, 2026-10-13): LRP surgery on Llama + Mistral, the classes WE registered.

Why this file exists: we added LlamaRMSNorm / MistralRMSNorm / LlamaMLP / MistralMLP to lrp.py,
mapped onto the Qwen2 rules, because their forwards are byte-identical in transformers 5.14.1.
"Byte-identical source" is a claim about TEXT; these tests are the claim about BEHAVIOUR, and each
one can fail:
  1. forward values unchanged (bit-exact for detach-only rules, close for the full preset)
  2. context exit restores stock bit-exactly
  3. every residual RMSNorm + every MLP got patched (none silently skipped)
  4. LN-rule gradient == the Llama formula  cot * w * rsqrt(mean(x^2)+eps)   (NOTE: plain w,
     not Qwen3.5's (1+w); derived here independently, not copied)
  5. POSITIVE CONTROL: the patched gradient differs from stock (a no-op surgery can't pass)
"""
from __future__ import annotations

import pytest
import torch as t
from transformers import LlamaConfig, LlamaForCausalLM, MistralConfig, MistralForCausalLM

from workspace_lens.lrp.lrp import LrpRuleConfig, apply_lrp_rules, lrp_rule_config_for_mode

TINY = dict(vocab_size=128, hidden_size=32, intermediate_size=64, num_hidden_layers=2,
            num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=64)


def _build(kind: str):
    t.manual_seed(0)
    if kind == "llama":
        model = LlamaForCausalLM(LlamaConfig(**TINY, mlp_bias=False))
    else:
        model = MistralForCausalLM(MistralConfig(**TINY))
    # random init leaves RMSNorm weights at 1.0; perturb so "w" vs "1+w" is actually distinguishable
    with t.no_grad():
        for m in model.modules():
            if type(m).__name__.endswith("RMSNorm"):
                m.weight.add_(0.3 * t.randn_like(m.weight))
    return model.eval()


@pytest.fixture(scope="module", params=["llama", "mistral"])
def tiny(request):
    return _build(request.param)


def _last_hidden(model, ids):
    with t.no_grad():
        return model.model(input_ids=ids, use_cache=False).last_hidden_state


IDS = t.randint(0, 128, (1, 12), generator=t.Generator().manual_seed(1))


def test_detach_only_rules_bit_exact(tiny):
    stock = _last_hidden(tiny, IDS)
    with apply_lrp_rules(tiny, LrpRuleConfig(ln_rule=True, identity_rule=False, half_rule=True)):
        patched = _last_hidden(tiny, IDS)
    assert t.equal(stock, patched)


def test_full_preset_close(tiny):
    stock = _last_hidden(tiny, IDS)
    with apply_lrp_rules(tiny, lrp_rule_config_for_mode("rlens")):
        patched = _last_hidden(tiny, IDS)
    assert t.allclose(stock, patched, rtol=1e-5, atol=1e-6)


def test_exit_restores_stock(tiny):
    stock = _last_hidden(tiny, IDS)
    with apply_lrp_rules(tiny, lrp_rule_config_for_mode("rlens")):
        pass
    assert t.equal(stock, _last_hidden(tiny, IDS))


def test_every_residual_norm_and_mlp_patched(tiny):
    norms = [n for n, m in tiny.named_modules()
             if type(m).__name__.endswith("RMSNorm") and ".self_attn" not in n]
    with apply_lrp_rules(tiny, lrp_rule_config_for_mode("rlens")) as report:
        pass
    assert sorted(report.ln_rule) == sorted(norms), (report.ln_rule, norms)
    assert len(report.mlp_rule) == tiny.config.num_hidden_layers


def test_ln_rule_gradient_matches_llama_formula_and_differs_from_stock(tiny):
    norm = tiny.model.layers[0].input_layernorm
    g = t.Generator().manual_seed(2)
    x = t.randn(5, 32, generator=g, requires_grad=True)
    cot = t.randn(5, 32, generator=g)
    with apply_lrp_rules(tiny, LrpRuleConfig(ln_rule=True, identity_rule=False, half_rule=False)):
        (patched,) = t.autograd.grad(norm(x), x, cot)
    scale = t.rsqrt(x.detach().pow(2).mean(-1, keepdim=True) + norm.variance_epsilon)
    expected = cot * norm.weight.detach() * scale          # Llama/Mistral: plain w
    assert t.allclose(patched, expected, rtol=1e-5, atol=1e-7)
    (stock,) = t.autograd.grad(norm(x), x, cot)
    assert not t.allclose(patched, stock, rtol=1e-3, atol=1e-5)   # 🧪 positive control


def test_half_rule_halves_mlp_product_gradient(tiny):
    mlp = tiny.model.layers[0].mlp
    g = t.Generator().manual_seed(3)
    x = t.randn(4, 32, generator=g, requires_grad=True)
    cot = t.randn(4, 32, generator=g)
    (stock,) = t.autograd.grad(mlp(x), x, cot)
    with apply_lrp_rules(tiny, LrpRuleConfig(ln_rule=False, identity_rule=False, half_rule=True)):
        (patched,) = t.autograd.grad(mlp(x), x, cot)
    # half-rule: every path into x goes through the gate*up product, so the whole input gradient halves
    assert t.allclose(patched, 0.5 * stock, rtol=1e-4, atol=1e-6)
