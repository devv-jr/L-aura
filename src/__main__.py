# src/__main__.py
from src.cli_interface import HuggyCLI

if __name__ == "__main__":
    cli = HuggyCLI()
    cli.run()