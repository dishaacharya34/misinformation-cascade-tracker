import pandas as pd


def analyze_trends(df: pd.DataFrame, columns: dict) -> dict:
    timestamp_col = columns.get("timestamp")

    if not timestamp_col:
        return {
            "available": False,
            "reason": "No timestamp or date column was detected.",
        }

    timestamps = pd.to_datetime(
        df[timestamp_col],
        errors="coerce",
        utc=True,
    )

    valid = timestamps.dropna()

    if valid.empty:
        return {
            "available": False,
            "reason": "The timestamp column contains no valid dates.",
        }

    daily_counts = (
        valid.dt.floor("D")
        .value_counts()
        .sort_index()
    )

    hourly_counts = (
        valid.dt.floor("h")
        .value_counts()
        .sort_index()
    )

    return {
        "available": True,
        "valid_timestamp_count": int(len(valid)),
        "invalid_timestamp_count": int(timestamps.isna().sum()),
        "daily_posts": [
            {
                "date": date.isoformat(),
                "count": int(count),
            }
            for date, count in daily_counts.items()
        ],
        "hourly_posts": [
            {
                "hour": hour.isoformat(),
                "count": int(count),
            }
            for hour, count in hourly_counts.items()
        ],
        "note": (
            "These are observed posting volumes, not proof that "
            "misinformation is trending."
        ),
    }
