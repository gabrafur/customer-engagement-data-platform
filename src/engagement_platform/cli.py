"""Command-line interface for synthetic generation and local execution."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from engagement_platform.benchmark import benchmark_operation
from engagement_platform.change_impact import load_module_registry, resolve_change_impact
from engagement_platform.config import load_config
from engagement_platform.monitoring import configure_logging
from engagement_platform.orchestration import EngagementPipeline
from engagement_platform.replay import rebuild_historical_snapshot
from engagement_platform.synthetic import generate_customers, generate_transactions, write_csv


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the synthetic engagement data platform")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "run", "rebuild", "benchmark"):
        command = subparsers.add_parser(name)
        command.add_argument("--customers", type=int, default=100)
        command.add_argument("--config", default="configs/development.yml")
        if name == "generate":
            command.add_argument("--output", type=Path, default=Path("data/generated"))
        if name == "rebuild":
            command.add_argument("--as-of-date", type=date.fromisoformat, required=True)
    impact = subparsers.add_parser("impact")
    impact.add_argument("--registry", default="configs/modules.toml")
    impact.add_argument("--changed", nargs="+", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "impact":
        resolution = resolve_change_impact(
            args.changed, load_module_registry(args.registry)
        )
        print(
            json.dumps(
                {
                    "modules": [module.module_id for module in resolution.modules],
                    "checks": resolution.checks,
                    "unmatched_paths": resolution.unmatched_paths,
                    "matrix": resolution.matrix(),
                },
                sort_keys=True,
            )
        )
        return 0

    config = load_config(args.config)
    customers = generate_customers(args.customers, config.seed, config.as_of_date)
    transactions = generate_transactions(customers, config.seed, config.as_of_date)
    if args.command == "generate":
        write_csv(customers, args.output / "customers.csv")
        write_csv(transactions, args.output / "transactions.csv")
        print(json.dumps({"customers": len(customers), "transactions": len(transactions)}))
        return 0

    if args.command == "rebuild":
        snapshot = rebuild_historical_snapshot(
            customers, transactions, config, args.as_of_date
        )
        print(
            json.dumps(
                {
                    "as_of_date": snapshot.as_of_date.isoformat(),
                    "recommendations": len(snapshot.recommendations),
                    "external_deliveries": 0,
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "benchmark":
        result, benchmark = benchmark_operation(
            "synthetic-pipeline",
            len(customers) + len(transactions),
            lambda: EngagementPipeline(config).run(customers, transactions),
            lambda value: len(value.recommendations),
        )
        print(
            json.dumps(
                {
                    "name": benchmark.name,
                    "input_records": benchmark.input_records,
                    "output_records": len(result.recommendations),
                    "elapsed_seconds": round(benchmark.elapsed_seconds, 6),
                    "records_per_second": round(benchmark.records_per_second, 2),
                },
                sort_keys=True,
            )
        )
        return 0

    logger = configure_logging()
    result = EngagementPipeline(config, logger=logger).run(customers, transactions)
    print(json.dumps(result.metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
