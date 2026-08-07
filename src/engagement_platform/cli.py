"""Command-line interface for synthetic generation and local execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engagement_platform.config import load_config
from engagement_platform.monitoring import configure_logging
from engagement_platform.orchestration import EngagementPipeline
from engagement_platform.synthetic import generate_customers, generate_transactions, write_csv


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the synthetic engagement data platform")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--customers", type=int, default=100)
        command.add_argument("--config", default="configs/development.yml")
        if name == "generate":
            command.add_argument("--output", type=Path, default=Path("data/generated"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = load_config(args.config)
    customers = generate_customers(args.customers, config.seed, config.as_of_date)
    transactions = generate_transactions(customers, config.seed, config.as_of_date)
    if args.command == "generate":
        write_csv(customers, args.output / "customers.csv")
        write_csv(transactions, args.output / "transactions.csv")
        print(json.dumps({"customers": len(customers), "transactions": len(transactions)}))
        return 0

    logger = configure_logging()
    result = EngagementPipeline(config, logger=logger).run(customers, transactions)
    print(json.dumps(result.metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
