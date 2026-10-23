
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.csv_service import process_csv
from app.services.analysis_service import analyze_csv
from app.database.firebase_service import get_firestore_client

router = APIRouter()


@router.get("/status")
def api_status():
    return {
        "message": "Misinformation Cascade Tracker API routes are working",
        "status": "healthy",
    }


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds the 10 MB limit.")

    result = process_csv(contents)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "CSV processing failed."),
        )

    return result


@router.post("/analyze")
async def analyze_uploaded_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds the 10 MB limit.")

    try:
        result = analyze_csv(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {exc}",
        ) from exc

    # Save successful analysis results when Firestore is configured.
    try:
        db = get_firestore_client()
        if db is not None and result.get("success", True):
            db.collection("analysis_history").add({
                "filename": file.filename,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "results": result,
            })
    except Exception as exc:
        # Keep the analysis result available even if history saving fails.
        print(f"Could not save analysis history: {exc}")

    return result


@router.get("/history")
def get_analysis_history():
    try:
        db = get_firestore_client()
        if db is None:
            return {"success": True, "history": [], "message": "Firestore is not configured."}

        documents = (
            db.collection("analysis_history")
            .order_by("created_at", direction="DESCENDING")
            .limit(50)
            .stream()
        )

        history = []
        for document in documents:
            record = document.to_dict()
            record["id"] = document.id
            history.append(record)

        return {"success": True, "history": history}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve analysis history: {exc}",
        ) from exc
