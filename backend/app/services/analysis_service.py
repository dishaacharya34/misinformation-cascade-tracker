from io import BytesIO

import pandas as pd

from app.analysis.pipeline import run_analysis


def analyze_csv(file_bytes: bytes) -> dict:
    try:
        df = pd.read_csv(BytesIO(file_bytes))
    except UnicodeDecodeError:
        df = pd.read_csv(BytesIO(file_bytes), encoding="latin-1")

    results = run_analysis(df)

    return results
