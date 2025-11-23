# -*- coding: UTF-8 -*-
import boto3
from botocore.client import Config
from typing import Optional
from fastapi import Request
from config.log import get_logger

from utils.config import (
    get_storage_access_key,
    get_storage_secret_key,
    get_storage_endpoint,
    get_storage_region,
    get_storage_bucket,
)

logger = get_logger(__name__)


def get_s3_client(request: Optional[Request] = None):
    """获取 S3 客户端实例"""
    access_key = get_storage_access_key(request)
    secret_key = get_storage_secret_key(request)
    endpoint = get_storage_endpoint(request)
    region = get_storage_region(request)
    bucket = get_storage_bucket(request)
    
    # 检查必需的配置
    if not endpoint:
        raise ValueError("STORAGE_ENDPOINT 未配置")
    if not access_key:
        raise ValueError("STORAGE_ACCESS_KEY 未配置")
    if not secret_key:
        raise ValueError("STORAGE_SECRET_KEY 未配置")
    if not region:
        raise ValueError("STORAGE_REGION 未配置")
    if not bucket:
        raise ValueError("STORAGE_BUCKET 未配置")
    
    # 确保 endpoint 包含协议前缀
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    
    # 检测是否为腾讯云 COS（通过 endpoint 判断）
    is_tencent_cos = "myqcloud.com" in endpoint.lower() or "qcloud.com" in endpoint.lower()
    
    # 腾讯云 COS 必须使用虚拟主机风格
    # 重要：使用虚拟主机风格时，endpoint 应该是路径风格（cos.region.myqcloud.com）
    # boto3 会根据 addressing_style="virtual" 自动构建虚拟主机风格的 URL
    # 如果 endpoint 包含 bucket，会导致重复
    if is_tencent_cos and bucket:
        if "://" in endpoint:
            protocol, rest = endpoint.split("://", 1)
            domain = rest.split("/")[0]
            logger.info(f"Original endpoint domain: {domain}, bucket: {bucket}")
            
            # 如果 endpoint 包含 bucket 名称，移除它
            # 例如：med-1370746848.cos.ap-beijing.myqcloud.com -> cos.ap-beijing.myqcloud.com
            # 或者：med-1370746848.med-1370746848.cos.ap-beijing.myqcloud.com -> cos.ap-beijing.myqcloud.com
            if bucket and domain.startswith(bucket + "."):
                # 移除开头的 bucket.
                while domain.startswith(bucket + "."):
                    domain = domain[len(bucket) + 1:]  # 移除 "bucket."
                endpoint = f"{protocol}://{domain}"
                logger.info(f"Removed bucket from endpoint: {endpoint}")
            
            # 确保是标准的路径风格格式：cos.region.myqcloud.com
            if not domain.startswith("cos."):
                # 如果不是标准格式，尝试提取并重建
                # 如果包含 .cos.，提取 region
                if ".cos." in domain:
                    parts = domain.split(".cos.")
                    if len(parts) >= 2:
                        region_part = parts[1].split(".")[0]  # 提取 region
                        domain = f"cos.{region_part}.myqcloud.com"
                        endpoint = f"{protocol}://{domain}"
                        logger.info(f"Normalized endpoint to path style: {endpoint}")
    
    # 腾讯云 COS 强制使用虚拟主机风格
    # boto3 会自动将 bucket 添加到域名前面，构建为 bucket.cos.region.myqcloud.com
    addressing_style = "virtual"

    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint,
        region_name=region,
        use_ssl=True,
        verify=True,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": addressing_style},
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def generate_download_url(file_name: str, request: Optional[Request] = None):
    """生成文件下载 URL (使用 S3 兼容协议)"""
    s3_client = get_s3_client(request)
    bucket = get_storage_bucket(request)

    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": file_name},
        ExpiresIn=3600,
    )


def generate_upload_url(file_name: str, request: Optional[Request] = None):
    """生成文件上传 URL (使用 S3 兼容协议)"""
    s3_client = get_s3_client(request)
    bucket = get_storage_bucket(request)
    endpoint = get_storage_endpoint(request)
    
    # 确保 endpoint 包含协议前缀
    if endpoint and not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    
    # 检查是否是虚拟主机风格（endpoint 包含 bucket 名称）
    is_virtual_style = False
    if endpoint and "myqcloud.com" in endpoint.lower():
        if "://" in endpoint:
            domain = endpoint.split("://")[1].split("/")[0]
            # 虚拟主机风格：bucket.cos.region.myqcloud.com（4个点以上）
            if domain.count(".") >= 4 and ".cos." in domain:
                is_virtual_style = True

    # 生成预签名 URL
    # 根据文件扩展名推断 Content-Type
    content_type = "application/octet-stream"
    if file_name.lower().endswith('.mp3'):
        content_type = "audio/mpeg"
    elif file_name.lower().endswith('.wav'):
        content_type = "audio/wav"
    elif file_name.lower().endswith('.m4a'):
        content_type = "audio/mp4"
    
    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": file_name,
            "ContentType": content_type,
        },
        ExpiresIn=3600,
    )
