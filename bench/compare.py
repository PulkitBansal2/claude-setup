"""Compare two benchmark runs and write a markdown table.

Usage: python3 bench/compare.py v1-original v2-lean   (writes bench/results.md)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(label):
    return {r["task"]: r for r in json.load(open(os.path.join(HERE, "results", f"{label}.json")))}


def routing(r):
    return ", ".join(r["agents"] + [f"/{s}" for s in r["skills"]]) or "main thread"


def main():
    a_label, b_label = sys.argv[1:3]
    a, b = load(a_label), load(b_label)
    lines = [
        f"# Benchmark: {a_label} vs {b_label}", "",
        f"| Task | {a_label} | {b_label} | Cost | Tokens | Time | Routing ({a_label} → {b_label}) |",
        "|---|---|---|---|---|---|---|",
    ]
    for task in a:
        x, y = a[task], b.get(task)
        if not y:
            continue
        mark = lambda r: "pass" if r["pass"] else "**FAIL**"
        lines.append(
            f"| {task} | {mark(x)} | {mark(y)} | ${x['cost_usd']} → ${y['cost_usd']} | {x['tokens']:,} → {y['tokens']:,} "
            f"| {x['seconds']}s → {y['seconds']}s | {routing(x)} → {routing(y)} |"
        )
    tot = lambda d, k: sum(r[k] for t, r in d.items() if t in a and t in b)
    lines += [
        "",
        f"**Passed:** {tot(a, 'pass')} → {tot(b, 'pass')}  ",
        f"**Total cost:** ${tot(a, 'cost_usd'):.2f} → ${tot(b, 'cost_usd'):.2f}  ",
        f"**Total tokens:** {tot(a, 'tokens'):,} → {tot(b, 'tokens'):,}",
    ]
    open(os.path.join(HERE, "..", "bench", "results.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
