from io import BytesIO

import pandas as pd

from app.analysis.column_detector import detect_columns
from app.analysis.data_validator import validate_dataframe


def process_csv(file_bytes: bytes) -> dict:
    try:
        df = pd.read_csv(BytesIO(file_bytes))
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(BytesIO(file_bytes), encoding="latin-1")
        except Exception as exc:
            return {
                "success": False,
                "error": f"Could not read CSV encoding: {exc}",
            }
    except pd.errors.EmptyDataError:
        return {
            "success": False,
            "error": "The uploaded CSV file is empty.",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Could not read CSV: {exc}",
        }

    validation = validate_dataframe(df)

    if not validation["valid"]:
        return {
            "success": False,
            "error": "CSV validation failed.",
            "validation": validation,
        }

    column_info = detect_columns(df.columns)

    return {
        "success": True,
        "validation": validation,
        "columns": column_info["detected_columns"],
        "missing_fields": column_info["missing_fields"],
        "preview": df.head(10).where(pd.notna(df), None).to_dict(
            orient="records"
        ),
    }
