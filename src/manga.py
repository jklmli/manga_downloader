import argparse

from commands.list import List


def main():
    parser = argparse.ArgumentParser(description='Download manga.')

    subparsers = parser.add_subparsers()
    List.add_parser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
