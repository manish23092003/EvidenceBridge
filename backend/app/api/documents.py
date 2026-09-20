from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.document import PdfExtractionResult
from app.services.pdf_service import (
    InvalidPdfError,
    PdfEncryptedError,
    PdfNoTextError,
    PdfPageLimitError,
    PdfService,
    PdfTooLargeError,
)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.post(
    "/extract", response_model=PdfExtractionResult, status_code=status.HTTP_200_OK
)
async def extract_document(file: UploadFile = File(...)) -> PdfExtractionResult:
    # Let FastAPI require the file implicitly.

    # Read the bytes into memory (do not write to disk)
    pdf_bytes = await file.read()
    filename = file.filename

    # Pass directly to the PdfService, letting it handle validation natively.
    try:
        result = PdfService.extract(pdf_bytes, filename=filename)
        return result
    except InvalidPdfError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (PdfTooLargeError, PdfPageLimitError) as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e)
        )
    except (PdfEncryptedError, PdfNoTextError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
