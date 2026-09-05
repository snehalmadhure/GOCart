"""Evaluate the consumption estimator against hidden synthetic truth."""

from __future__ import annotations

from datetime import date

from pantry_restock_agent.forecasting import fit_consumption_model
from pantry_restock_agent.synthetic import generate_synthetic_history


def main() -> None:
    dataset = generate_synthetic_history(total_days=240, start_date=date(2026, 1, 1), seed=42)
    estimates = fit_consumption_model(dataset.events)

    print("item       truth(days)  estimate(days)  abs_error  confidence")
    print("---------- ------------ -------------- ---------- ----------")
    errors = []
    for item in sorted(dataset.truth_days_per_unit):
        truth = dataset.truth_days_per_unit[item]
        estimate = estimates[item]
        error = abs(estimate.days_per_unit - truth)
        errors.append(error)
        print(
            f"{item:<10} {truth:>12.2f} {estimate.days_per_unit:>14.2f}"
            f" {error:>10.2f} {estimate.confidence:>10.2f}"
        )

    print(f"\nMean absolute error: {sum(errors) / len(errors):.2f} days per unit")


if __name__ == "__main__":
    main()
