#!/usr/bin/env python3
"""🚀 J++ 24B launcher — runs on the CONSORTIUM. Rents ONE 80 GB GPU, ships the bundle, starts the pod
script, then hands the pod to supervise_24b.py (nohup setsid) and exits.

GPU preference (cheapest work per dollar is roughly a wash, so prefer the fastest wall clock = least idle risk):
H100 SXM community -> H100 PCIe community -> A100 SXM community -> A100 PCIe community. Never secure H100
($3.99/h would project past the cap). If nothing deploys, nothing is spent: it says so and exits.
The key is read from ~/.config/jpp_runpod_key (chmod 600) and never printed.
"""
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rp import KEY, gql  # noqa: E402

CHOICES = [("COMMUNITY", "NVIDIA H100 80GB HBM3"), ("COMMUNITY", "NVIDIA H100 PCIe"),
           ("COMMUNITY", "NVIDIA A100-SXM4-80GB"), ("COMMUNITY", "NVIDIA A100 80GB PCIe"),
           ("COMMUNITY", "NVIDIA RTX PRO 6000 Blackwell Server Edition"),
           ("SECURE", "NVIDIA A100-SXM4-80GB"), ("SECURE", "NVIDIA A100 80GB PCIe")]
# (07:38 first try: all four community 80 GB types SUPPLY_CONSTRAINT under tighter filters; nothing rented)
MAX_RATE = 2.75          # $/h; anything pricier is not what Ren's estimate assumed
BUDGET_FOR_DEADLINE = 18.0
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
JPP = Path("/home/Ace/jpp_lens")
PROMPTS = Path("/home/Ace/vspace-jlens/jpp_runs/cha743/wikitext_prompts_1000.json")  # the SAME file P-3B used (A1 item 3)
DRIVER = HERE / "run_cha743_24b.py"
POD_SH = HERE / "pod_jpp24b.sh"
SSHO = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=20", "-o", "LogLevel=ERROR"]


def say(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def deploy(cloud, gpu):
    pub = Path("~/.ssh/id_ed25519.pub").expanduser().read_text().strip()
    inp = {"cloudType": cloud, "gpuCount": 1, "volumeInGb": 0, "containerDiskInGb": 200,
           "minVcpuCount": 4, "minMemoryInGb": 32, "gpuTypeId": gpu, "name": "ace-jpp-24b-cha743",
           "imageName": IMAGE, "dockerArgs": "", "ports": "22/tcp", "volumeMountPath": "/workspace",
           "startSsh": True, "supportPublicIp": True,
           "env": [{"key": "PUBLIC_KEY", "value": pub}]}
    d = gql("mutation($input: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $input) "
            "{ id costPerHr machine { gpuDisplayName } } }", {"input": inp})
    return (d or {}).get("podFindAndDeployOnDemand")


def main():
    start_bal = gql("query { myself { clientBalance pods { id } } }")["myself"]
    if start_bal["pods"]:
        sys.exit(f"pods already exist {start_bal['pods']}: refusing to add another")
    start_bal = start_bal["clientBalance"]
    say(f"balance ${start_bal:.2f}")
    pod = None
    for cloud, gpu in CHOICES:
        say("trying", cloud, gpu)
        pod = deploy(cloud, gpu)
        if pod:
            break
    if not pod:
        sys.exit("no 80 GB GPU deployable on community cloud right now: nothing rented, nothing spent")
    pid, rate = pod["id"], pod["costPerHr"]
    say(f"POD {pid} on {pod['machine']['gpuDisplayName']} at ${rate}/h")
    (HERE / "pod.json").write_text(json.dumps({"id": pid, "rate": rate, "gpu": pod["machine"]["gpuDisplayName"],
                                               "start_balance": start_bal, "launched": time.time()}))
    if rate > MAX_RATE:
        gql('mutation { podTerminate(input:{podId:"%s"}) }' % pid)
        sys.exit(f"rate ${rate}/h > ${MAX_RATE}: terminated immediately")

    # wait for ssh
    ip = port = None
    for _ in range(60):
        r = gql('query { pod(input:{podId:"%s"}) { runtime { uptimeInSeconds ports { ip isIpPublic publicPort privatePort type } } } }' % pid)
        rt = ((r or {}).get("pod") or {}).get("runtime")
        for p in (rt or {}).get("ports") or []:
            if p["privatePort"] == 22 and p["isIpPublic"]:
                ip, port = p["ip"], str(p["publicPort"])
        if ip:
            break
        time.sleep(15)
    if not ip:
        gql('mutation { podTerminate(input:{podId:"%s"}) }' % pid)
        sys.exit("no public ssh within 15 min: terminated")
    say("ssh", ip, port)
    ssh = ["ssh", *SSHO, "-p", port, f"root@{ip}"]
    for _ in range(20):
        if subprocess.run(ssh + ["true"], capture_output=True).returncode == 0:
            break
        time.sleep(15)
    else:
        gql('mutation { podTerminate(input:{podId:"%s"}) }' % pid)
        sys.exit("sshd never answered: terminated")

    # bundle
    deadline_h = round(min(10.0, BUDGET_FOR_DEADLINE / rate - 0.75), 2)
    b = Path("/tmp/jpp24b_bundle")
    subprocess.run(["rm", "-rf", str(b)], check=True)
    (b / "bundle").mkdir(parents=True)
    for f in (DRIVER, POD_SH, PROMPTS):
        subprocess.run(["cp", str(f), str(b / "bundle")], check=True)
    (b / "bundle" / "deadline_h").write_text(str(deadline_h))
    subprocess.run(["rsync", "-a", "--exclude", "__pycache__", "--exclude", ".pytest_cache", "--exclude", ".venv",
                    f"{JPP}/", str(b / "jpp_lens")], check=True)
    subprocess.run(["sed", "-i", "s/\\r$//", str(b / "bundle" / "pod_jpp24b.sh")], check=True)
    subprocess.run(["tar", "-C", str(b), "-czf", "/tmp/jpp24b_bundle.tgz", "bundle", "jpp_lens"], check=True)
    subprocess.run(["scp", "-q", *SSHO, "-P", port, "/tmp/jpp24b_bundle.tgz", f"root@{ip}:/root/"], check=True)
    # pod env: id + key for self-termination, piped on stdin into a 600 file (never on a command line)
    env = f"export RUNPOD_POD_ID={shlex.quote(pid)}\nexport RUNPOD_API_KEY={shlex.quote(KEY)}\n"
    subprocess.run(ssh + ["umask 077; cat > /root/pod_env"], input=env, text=True, check=True)
    out = subprocess.run(ssh + ["cd /root && tar -xzf jpp24b_bundle.tgz && ls bundle jpp_lens | wc -l && "
                                "nohup setsid bash -c 'source /root/pod_env; bash /root/bundle/pod_jpp24b.sh' "
                                "> /dev/null 2>&1 < /dev/null & sleep 5; echo started; head -3 /root/run/pod.log"],
                         capture_output=True, text=True)
    say(out.stdout.strip(), out.stderr.strip()[-300:])

    sup = HERE / "supervise_24b.py"
    subprocess.Popen(f"nohup setsid python3 {sup} {pid} {ip} {port} {start_bal} >> {HERE}/supervise.log 2>&1 < /dev/null &",
                     shell=True)
    say(f"supervisor started; deadline {deadline_h} h on the pod; status in {HERE}/status.json")


if __name__ == "__main__":
    main()
