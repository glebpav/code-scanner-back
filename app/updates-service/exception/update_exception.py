from fastapi import HTTPException


class UpdateVersionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Update version not found")


class UpdateFileNotFoundException(HTTPException):
    def __init__(self, s3_key: str):
        super().__init__(status_code=404, detail=f"File '{s3_key}' not found in S3")


class UpdateArchiveBuildException(HTTPException):
    def __init__(self, detail: str = "Failed to build update archive"):
        super().__init__(status_code=502, detail=detail)