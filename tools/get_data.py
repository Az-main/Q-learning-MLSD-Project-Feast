"""Create the raw sales dataset from Kaggle data or a synthetic series."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "sales.csv"


def from_kaggle(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[(df["store"] == 1) & (df["item"] == 1)]
    return df[["date", "store", "item", "sales"]]


def synthetic(seed: int = 7) -> pd.DataFrame:
    """Generate daily sales with trend, seasonality and noise."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2013-01-01", "2017-12-31", freq="D")
    t = np.arange(len(dates))
    trend = 14 + 0.004 * t
    weekly = np.array([0.8, 0.9, 0.9, 1.0, 1.1, 1.25, 1.3])[dates.dayofweek]
    annual = 1 + 0.25 * np.sin(2 * np.pi * (dates.dayofyear - 80) / 365)
    sales = rng.poisson(trend * weekly * annual)
    return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "store": 1, "item": 1, "sales": sales})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kaggle", help="path to the Kaggle train.csv")
    args = parser.parse_args()

    df = from_kaggle(args.kaggle) if args.kaggle else synthetic()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} rows to {OUT.relative_to(ROOT)}")
    print(df.head())


if __name__ == "__main__":
    main()
