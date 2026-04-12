"""Entry point for Q1 text classification."""

from __future__ import annotations

import argparse

from src.common.config import load_config
from src.common.export import create_run_dir, save_config_copy, save_environment_info
from src.common.seed import set_global_seed
from src.q1_classification.train import run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Q1 text classification baselines.")
    parser.add_argument("--config", required=True, help="Path to the question config YAML file.")
    parser.add_argument("--override", nargs="*", default=[], help="Optional dotted config overrides.")
    parser.add_argument(
        "--final-eval",
        action="store_true",
        help="Also evaluate on the held-out test split and export test predictions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config, args.override)

    set_global_seed(config.seed)

    run_dir = create_run_dir(config.output_dir, config.question)
    save_config_copy(config, run_dir)
    save_environment_info(run_dir)

    run_training(config, run_dir=run_dir, final_eval=args.final_eval)
    print(f"Saved outputs to {run_dir}")


if __name__ == "__main__":
    main()
