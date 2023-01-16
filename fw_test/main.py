import argparse

from .context import Context

parser = argparse.ArgumentParser(description="a toolkit to test embedded firmware releases")
parser.add_argument("--firmware", "-f", help="firmware binary to test", required=True)
parser.add_argument("--config", "-c", help="configuration file to use", default="config.toml")


def main():
    args = parser.parse_args()
    context = Context(args.config)

    print("hello, world!", context.config)
