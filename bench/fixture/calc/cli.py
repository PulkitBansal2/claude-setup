import argparse

from calc import ops


def main(argv=None):
    p = argparse.ArgumentParser(prog="calc")
    sub = p.add_subparsers(dest="op", required=True)
    for name in ("add", "sub", "mul", "div"):
        sp = sub.add_parser(name)
        sp.add_argument("a", type=float)
        sp.add_argument("b", type=float)
    args = p.parse_args(argv)
    result = getattr(ops, args.op)(args.a, args.b)
    print(int(result) if float(result).is_integer() else result)


if __name__ == "__main__":
    main()
