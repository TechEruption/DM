from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.data import CSVImportResponse
from app.utils.csv_loader import CSVImportError, import_csv_data

router = APIRouter(prefix="/api/data", tags=["data"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/upload", summary="Validate and import one supported CSV dataset", response_model=CSVImportResponse)
async def upload_data(
    dataset_type: str = Form(..., description="One of channels, campaigns, customers, or touchpoints."),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a file with a .csv extension.")
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CSV uploads must be 10 MB or smaller.")
    try:
        result = import_csv_data(db, dataset_type, contents)
    except CSVImportError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"status": "imported", **result}
