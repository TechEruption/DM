from pydantic import BaseModel


class CSVImportResponse(BaseModel):
    status: str
    dataset_type: str
    rows_received: int
    rows_inserted: int
    rows_skipped_existing: int
