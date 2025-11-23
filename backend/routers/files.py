# -*- coding: UTF-8 -*-
from fastapi import APIRouter, Request, UploadFile, File, Form
from config.log import get_logger
from core.exceptions import ExternalServiceException
from core.response import success_response, APIResponse
from models import FileNameRequest
from utils import s3
from utils.config import get_storage_bucket
from io import BytesIO

router = APIRouter(prefix="/files", tags=["storage"])
logger = get_logger(__name__)


@router.post("/upload-urls", response_model=APIResponse)
async def create_upload_url(request: FileNameRequest, http_request: Request):
    """创建文件上传URL

    RESTful路径: POST /api/v1/files/upload-urls
    """
    logger.info(f"Creating upload URL for file: {request.filename}")

    try:
        url = s3.generate_upload_url(request.filename, http_request)

        logger.info(f"Upload URL created successfully for file: {request.filename}")

        return success_response(
            data={"upload_url": url}, message="Upload URL created successfully"
        )

    except Exception as e:
        logger.error(
            f"Failed to create upload URL for file {request.filename}: {str(e)}"
        )
        raise ExternalServiceException(
            "TOS", f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/upload", response_model=APIResponse)
async def upload_file_direct(
    http_request: Request,
    file: UploadFile = File(..., description="文件内容"),
    filename: str = Form(..., description="文件名")
) -> APIResponse:
    """直接上传文件（通过后端代理，避免 CORS 问题）

    RESTful路径: POST /api/v1/files/upload
    """
    logger.info(f"Uploading file directly: {filename}")

    try:
        s3_client = s3.get_s3_client(http_request)
        bucket = get_storage_bucket(http_request)
        
        # 读取文件内容
        file_content = await file.read()
        
        # 根据文件扩展名确定 Content-Type
        content_type = "application/octet-stream"
        if filename.lower().endswith('.mp3'):
            content_type = "audio/mpeg"
        elif filename.lower().endswith('.wav'):
            content_type = "audio/wav"
        elif filename.lower().endswith('.m4a'):
            content_type = "audio/mp4"
        
        # 上传到 COS
        s3_client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=BytesIO(file_content),
            ContentType=content_type
        )

        logger.info(f"File uploaded successfully: {filename}")

        return success_response(
            data={"filename": filename}, message="File uploaded successfully"
        )

    except Exception as e:
        logger.error(f"Failed to upload file {filename}: {str(e)}")
        raise ExternalServiceException("TOS", f"Failed to upload file: {str(e)}")
