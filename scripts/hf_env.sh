# Shared cache/storage policy for this box. Source this before any HF work.
#
#   HOT (active runs)      -> /mnt/arcana   916G, ~91% full: lenses/, checkpoints
#   COLD (model cache)     -> /mnt/nursery  7.3T, 7% full:   the HF cache
#   NOTHING                -> /             439G, 97% full:  keep it that way
#
# The Consortium is our box. Every model in the cache is ours (Three Babies,
# Below the Floor, earlier runs). There is no third party to defer to -- only
# the sensible caution of not moving a cache while something is reading it.
export HF_HOME=/mnt/nursery/hf-cache
export HF_HUB_CACHE=/mnt/nursery/hf-cache/hub
export TRANSFORMERS_CACHE=/mnt/nursery/hf-cache/hub
export HF_DATASETS_CACHE=/mnt/nursery/hf-cache/datasets
