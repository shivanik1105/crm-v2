from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

class ErrorEnvelope:
    @staticmethod
    def create(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> JSONResponse:
        content = {
            "error_code": error_code,
            "message": message,
            "details": details or {}
        }
        return JSONResponse(status_code=status_code, content=content)

class CRMException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

async def crm_exception_handler(request, exc: CRMException):
    return ErrorEnvelope.create(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code
    )
