from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_inputs(
    output_dir: str | Path = "data/sample",
    n_customers: int = 1_200,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    customer_ids = np.arange(100_000, 100_000 + n_customers)
    customer_value = rng.gamma(shape=2.1, scale=0.9, size=n_customers)
    thresholds = np.quantile(customer_value, [0.25, 0.55, 0.82])
    segments = np.select(
        [
            customer_value >= thresholds[2],
            customer_value >= thresholds[1],
            customer_value >= thresholds[0],
        ],
        ["Champion", "Loyal", "Potential Loyalist"],
        default="At Risk",
    )

    subscription_rows: list[dict[str, object]] = []
    plan_windows: dict[int, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}
    subscription_number = 1
    for index, customer_id in enumerate(customer_ids):
        adoption_probability = min(
            0.82,
            0.12 + 0.16 * np.log1p(customer_value[index]),
        )
        if rng.random() >= adoption_probability:
            plan_windows[int(customer_id)] = []
            continue

        start_index = int(rng.integers(20, 240))
        customer_windows: list[tuple[pd.Timestamp, pd.Timestamp]] = []
        for _ in range(3):
            if start_index >= len(dates):
                break
            duration_days = int(rng.choice([30, 90], p=[0.58, 0.42]))
            start_date = dates[start_index]
            plan_end = start_date + pd.Timedelta(days=duration_days)
            paid_price = (180.0 if duration_days == 30 else 450.0) * float(
                rng.uniform(0.86, 1.0)
            )
            subscription_rows.append(
                {
                    "subscription_id": f"S{subscription_number:06d}",
                    "customer_id": int(customer_id),
                    "start_date": start_date,
                    "duration_days": duration_days,
                    "paid_price": round(paid_price, 2),
                    "plan_name": ("Monthly" if duration_days == 30 else "Quarterly"),
                }
            )
            subscription_number += 1
            customer_windows.append((start_date, plan_end))

            renewal_probability = min(
                0.78,
                0.28 + 0.12 * np.log1p(customer_value[index]),
            )
            if rng.random() >= renewal_probability:
                break
            renewal_gap = int(rng.integers(-3, 11))
            start_index = int((plan_end - dates[0]).days + renewal_gap)
        plan_windows[int(customer_id)] = customer_windows

    activity_rows: list[dict[str, object]] = []
    for index, customer_id in enumerate(customer_ids):
        windows = plan_windows[int(customer_id)]
        for day in dates:
            membership_active = int(any(start <= day < end for start, end in windows))
            annual_seasonality = 1 + 0.10 * np.sin(2 * np.pi * day.dayofyear / 365)
            order_rate = annual_seasonality * (
                0.014 + 0.021 * customer_value[index] + 0.006 * membership_active
            )
            orders = int(rng.poisson(order_rate))
            items = int(sum(max(1, rng.poisson(1.35)) for _ in range(orders)))
            nmv = float(sum(rng.lognormal(mean=4.7, sigma=0.38) for _ in range(orders)))
            pc1 = nmv * float(np.clip(rng.normal(0.14, 0.018), 0.08, 0.20))
            shipping_contribution = float(
                orders
                * rng.normal(
                    -2.2 if membership_active else 0.6,
                    1.1,
                )
            )
            benefit_cost = float(membership_active * orders * rng.uniform(2.0, 6.0))
            service_cost = float(membership_active * rng.uniform(0.08, 0.18))
            activity_rows.append(
                {
                    "customer_id": int(customer_id),
                    "day": day,
                    "rfm_segment": str(segments[index]),
                    "membership_active": membership_active,
                    "orders": orders,
                    "items": items,
                    "nmv": round(nmv, 2),
                    "pc1": round(pc1, 2),
                    "shipping_contribution": round(shipping_contribution, 2),
                    "benefit_cost": round(benefit_cost, 2),
                    "service_cost": round(service_cost, 2),
                }
            )

    activity = pd.DataFrame(activity_rows)
    subscriptions = pd.DataFrame(
        subscription_rows,
        columns=[
            "subscription_id",
            "customer_id",
            "start_date",
            "duration_days",
            "paid_price",
            "plan_name",
        ],
    )
    activity.to_csv(output / "activity_daily.csv", index=False)
    subscriptions.to_csv(output / "subscriptions.csv", index=False)
    return activity, subscriptions
