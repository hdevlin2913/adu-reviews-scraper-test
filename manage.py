import os

from scraper.main.cli.app import run_cli

if __name__ == "__main__":
    os.environ.setdefault("CONFIG_ENV", "dev")
    run_cli()
