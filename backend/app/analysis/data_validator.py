import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> dict:
    errors = []
    warnings = []

    if df is None or df.empty:
        return {
            "valid": False,
            "errors": ["The uploaded CSV contains no data rows."],
            "warnings": [],
            "row_count": 0,
            "duplicate_rows": 0,
            "missing_values": {},
        }

    if len(df.columns) == 0:
        errors.append("The CSV contains no columns.")

    if df.columns.duplicated().any():
        errors.append("The CSV contains duplicate column names.")

    blank_columns = [
        str(column)
        for column in df.columns
        if str(column).strip() == ""
    ]
    if blank_columns:
        errors.append("The CSV contains blank column names.")

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        warnings.append(
            f"{duplicate_rows} duplicate rows were detected."
        )

    missing_values = {
        str(column): int(count)
        for column, count in df.isna().sum().items()
        if count > 0
    }

    if missing_values:
        warnings.append(
            "Some columns contain missing values; review them before analysis."
        )

    if len(df) < 5:
        warnings.append(
            "The dataset is very small; analysis may be unreliable."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
    }
