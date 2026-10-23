import pandas as pd


def classify_content(df: pd.DataFrame, columns: dict) -> dict:
    label_col = columns.get("label")
    text_col = columns.get("text")

    if not label_col:
        return {
            "available": False,
            "reason": (
                "No verified label column was detected. "
                "Automated misinformation classification is not enabled."
            ),
            "predictions": [],
        }

    labels = (
        df[label_col]
        .dropna()
        .astype(str)
        .str.strip()
    )

    if labels.empty:
        return {
            "available": False,
            "reason": "The detected label column contains no usable labels.",
            "predictions": [],
        }

    counts = labels.value_counts()

    result = {
        "available": True,
        "mode": "dataset_labels",
        "label_column": label_col,
        "label_counts": {
            str(label): int(count)
            for label, count in counts.items()
        },
        "labeled_rows": int(len(labels)),
        "note": (
            "These are labels already present in the uploaded dataset. "
            "They are not predictions made by this system."
        ),
    }

    if text_col:
        result["text_column"] = text_col
    else:
        result["text_column"] = None
        result["note"] += " No text column was detected."

    return result
