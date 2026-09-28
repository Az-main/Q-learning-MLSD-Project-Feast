"""Prepare features and chronological train, stream and test splits."""

import pandas as pd

from utils import ROOT, load_params, save_json

RAW = ROOT / "data" / "raw" / "sales.csv"
OUT = ROOT / "data" / "processed"


def main() -> None:
    p = load_params()["prepare"]

    df = pd.read_csv(RAW, parse_dates=["date"])
    df = df[(df["store"] == p["store_id"]) & (df["item"] == p["item_id"])]
    df = df.rename(columns={"sales": "demand"})
    df = df.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    df["demand"] = df["demand"].clip(lower=0).astype(float)

    df["day_of_week"] = df["date"].dt.dayofweek
    w = p["rolling_window"]
    # Use only demand known before the current day.
    original_rolling = df["demand"].shift(1).rolling(w).mean()

    in_drift = (df["date"] >= p["drift_start"]) & (df["date"] <= p["stream_end"])
    df.loc[in_drift, "demand"] = (df.loc[in_drift, "demand"] * p["drift_factor"]).round()
    drifted_rolling = df["demand"].shift(1).rolling(w).mean()
    # Keep simulated drift out of the final test year.
    is_test = df["date"] > p["stream_end"]
    df["rolling_demand"] = drifted_rolling.where(~is_test, original_rolling)
    df = df.dropna().reset_index(drop=True)

    train = df[df["date"] <= p["train_end"]].copy()
    stream = df[(df["date"] > p["train_end"]) & (df["date"] <= p["stream_end"])].copy()
    test = df[df["date"] > p["stream_end"]].copy()

    low = float(train["rolling_demand"].quantile(0.33))
    high = float(train["rolling_demand"].quantile(0.67))
    for part in (train, stream, test):
        part["demand_trend"] = 1
        part.loc[part["rolling_demand"] < low, "demand_trend"] = 0
        part.loc[part["rolling_demand"] > high, "demand_trend"] = 2

    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["date", "store", "item", "demand", "day_of_week", "rolling_demand", "demand_trend"]
    train[cols].to_parquet(OUT / "train.parquet", index=False)
    stream[cols].to_parquet(OUT / "stream.parquet", index=False)
    test[cols].to_parquet(OUT / "test.parquet", index=False)

    meta = {
        "trend_low_threshold": round(low, 3),
        "trend_high_threshold": round(high, 3),
        "rows": {"train": len(train), "stream": len(stream), "test": len(test)},
    }
    save_json(meta, OUT / "meta.json")
    print("prepare done:", meta)


if __name__ == "__main__":
    main()
