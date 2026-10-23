from app.analysis.column_detector import detect_columns
from app.analysis.data_validator import validate_dataframe
from app.analysis.cascade_analyzer import analyze_cascades
from app.analysis.influence_analyzer import analyze_influence
from app.analysis.risk_scorer import score_risks
from app.analysis.trend_analyzer import analyze_trends
from app.analysis.content_classifier import classify_content


def run_analysis(df):
    validation = validate_dataframe(df)

    if not validation["valid"]:
        return {
            "success": False,
            "validation": validation,
            "error": "Dataset validation failed.",
        }

    column_info = detect_columns(df.columns)
    columns = column_info["detected_columns"]

    results = {
        "success": True,
        "validation": validation,
        "columns": columns,
        "missing_fields": column_info["missing_fields"],
        "classification": classify_content(df, columns),
        "cascades": analyze_cascades(df, columns),
        "influence": analyze_influence(df, columns),
        "trends": analyze_trends(df, columns),
    }

    results["risk"] = score_risks(results)

    return results
