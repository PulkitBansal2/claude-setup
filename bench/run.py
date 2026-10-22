"""Benchmark the installed Claude Code setup on fixed tasks.

Each task runs headless (`claude -p`) in a fresh copy of bench/fixture, then a check decides pass/fail.
Records which subagents and skills fired, cost, tokens, turns and time.

Usage: python3 bench/run.py <label> [task ...]   e.g. python3 bench/run.py v1-original
Writes bench/results/<label>.json; compare two runs with bench/compare.py.
"""
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "fixture")
PARALLEL = 5
BUDGET_USD = "3"
TIMEOUT_S = 1200

BUGGY_MUL = "def mul(a, b):\n    return a + b\n"


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)


def tests_pass(cwd, target="tests"):
    return sh(f"python3 -m unittest discover -s {target} -t .", cwd).returncode == 0


def setup_review(cwd):
    path = os.path.join(cwd, "calc/ops.py")
    src = open(path).read().replace("def mul(a, b):\n    return a * b\n", BUGGY_MUL)
    open(path, "w").write(src)


def setup_dirty(cwd):
    with open(os.path.join(cwd, "calc/ops.py"), "a") as f:
        f.write("\n\ndef neg(a):\n    return -a\n")


def check_commit(cwd, out):
    log = sh("git log --format=%B%n---", cwd).stdout
    count = sh("git rev-list --count HEAD", cwd).stdout.strip()
    banned = ("claude", "anthropic", "co-authored-by", "generated with")
    return count == "2" and not any(b in log.lower() for b in banned) and sh("git status --porcelain", cwd).stdout == ""


# name: (prompt, setup or None, check(cwd, output) -> bool)
TASKS = {
    "find": (
        "Where is the median function defined, and which functions or files call it? Answer only; do not change any files.",
        None,
        lambda cwd, out: "stats.py" in out and sh("git status --porcelain", cwd).stdout == "",
    ),
    "one-line-fix": (
        "Fix the division bug in calc/ops.py so that div(7, 2) returns 3.5.",
        None,
        lambda cwd, out: sh("python3 -c 'from calc.ops import div; assert div(7,2)==3.5'", cwd).returncode == 0,
    ),
    "multi-file-feature": (
        "Add a power(a, b) operation: implement it in calc/ops.py, expose it as a `power` subcommand in calc/cli.py, "
        "add a unit test for it, and document it in README.md.",
        None,
        lambda cwd, out: sh("python3 -m calc.cli power 2 3", cwd).stdout.strip() == "8"
        and "power" in open(os.path.join(cwd, "README.md")).read()
        and "power" in sh("cat tests/*.py", cwd).stdout,
    ),
    "unclear-bug": (
        "One of the tests is failing. Find the root cause and fix it.",
        None,
        lambda cwd, out: tests_pass(cwd) and "assertEqual(stats.median([4, 1, 3, 2]), 2.5)" in open(os.path.join(cwd, "tests/test_stats.py")).read(),
    ),
    "docs": (
        "Add a section to README.md explaining how to use the CLI and how to run the tests.",
        None,
        lambda cwd, out: all(s in open(os.path.join(cwd, "README.md")).read() for s in ("calc.cli", "unittest")),
    ),
    "review": (
        "Review the uncommitted changes for bugs. Do not modify any files; just report what you find.",
        setup_review,
        lambda cwd, out: "mul" in out and BUGGY_MUL in open(os.path.join(cwd, "calc/ops.py")).read(),
    ),
    "cli-flag": (
        "Add a --version flag to the calc CLI that prints 0.1.0 and exits.",
        None,
        lambda cwd, out: "0.1.0" in sh("python3 -m calc.cli --version", cwd).stdout + sh("python3 -m calc.cli --version", cwd).stderr,
    ),
    "run-tests": (
        "Run the test suite and tell me which tests fail. Do not fix anything.",
        None,
        lambda cwd, out: "median_even" in out and not tests_pass(cwd),
    ),
    "git-commit": (
        "Commit the current uncommitted changes with a good commit message.",
        setup_dirty,
        check_commit,
    ),
    "new-project": (
        "Create a new minimal Python project in ./newproj with a hello() function that returns 'hello' and a unit test for it.",
        None,
        lambda cwd, out: sh("python3 -m unittest discover -t .", os.path.join(cwd, "newproj")).returncode == 0
        and os.path.exists(os.path.join(cwd, "newproj")),
    ),
}


def run(name):
    prompt, setup, check = TASKS[name]
    cwd = tempfile.mkdtemp(prefix=f"bench-{name}-")
    shutil.copytree(FIXTURE, cwd, dirs_exist_ok=True)
    sh("git init -q && git add -A && git -c user.name=bench -c user.email=bench@example.com commit -q -m init", cwd)
    sh("git config user.name bench && git config user.email bench@example.com", cwd)
    if setup:
        setup(cwd)
    start = time.time()
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
             "--permission-mode", "auto", "--max-budget-usd", BUDGET_USD],
            cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S,
        )
        lines = proc.stdout.splitlines()
    except subprocess.TimeoutExpired as e:
        lines = (e.stdout or b"").decode(errors="replace").splitlines() if isinstance(e.stdout, bytes) else (e.stdout or "").splitlines()
    agents, skills, result, text = [], [], {}, ""
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    inp = block.get("input", {})
                    if block.get("name") in ("Agent", "Task"):
                        agents.append(inp.get("subagent_type", "general-purpose"))
                    elif block.get("name") == "Skill":
                        skills.append(inp.get("skill", "?"))
                elif block.get("type") == "text":
                    text += block.get("text", "") + "\n"
        elif ev.get("type") == "result":
            result = ev
    out = (result.get("result") or "") + "\n" + text
    try:
        passed = bool(check(cwd, out))
    except Exception:
        passed = False
    usage = result.get("usage", {})
    row = {
        "task": name,
        "pass": passed,
        "agents": agents,
        "skills": skills,
        "cost_usd": round(result.get("total_cost_usd", 0.0), 4),
        "tokens": sum(usage.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "turns": result.get("num_turns"),
        "seconds": round(time.time() - start),
        "error": result.get("subtype") if result.get("is_error") else None,
    }
    shutil.rmtree(cwd, ignore_errors=True)
    print(f"{name:20} {'PASS' if passed else 'FAIL'}  ${row['cost_usd']:<7} {row['seconds']}s  agents={agents} skills={skills}", flush=True)
    return row


def main():
    label, names = sys.argv[1], sys.argv[2:] or list(TASKS)
    with cf.ThreadPoolExecutor(PARALLEL) as pool:
        rows = list(pool.map(run, names))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", f"{label}.json")
    json.dump(rows, open(path, "w"), indent=2)
    print(f"{sum(r['pass'] for r in rows)}/{len(rows)} passed, ${sum(r['cost_usd'] for r in rows):.2f} -> {path}")


if __name__ == "__main__":
    main()
