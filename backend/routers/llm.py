# -*- coding: UTF-8 -*-

from fastapi import APIRouter, Request
from openai import OpenAI

from core.response import success_response, APIResponse
from models import ChatRequest
from utils.config import get_llm_base_url, get_llm_model_id, get_llm_api_key

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/completions", response_model=APIResponse)
async def default_chat(request: ChatRequest, http_request: Request):
    """默认聊天接口"""
    base_url = get_llm_base_url(http_request)
    api_key = get_llm_api_key(http_request)
    model_id = get_llm_model_id(http_request)
    
    if not api_key or not model_id:
        raise ValueError("LLM API Key 或 Model ID 未配置")
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    messages = [
        {"role": message.role, "content": message.content}
        for message in request.messages
    ]

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        timeout=120,
    )
    return success_response(
        data={"choices": [choices.model_dump() for choices in response.choices]},
        message="Chat completed successfully",
    )


@router.post("/markdown-generation", response_model=APIResponse)
async def generate_markdown_text(request: ChatRequest, http_request: Request):
    """生成 Markdown 文本"""
    base_url = get_llm_base_url(http_request)
    api_key = get_llm_api_key(http_request)
    model_id = get_llm_model_id(http_request)
    
    if not api_key or not model_id:
        raise ValueError("LLM API Key 或 Model ID 未配置")
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    messages = [
        {"role": message.role, "content": message.content}
        for message in request.messages
    ]

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        timeout=request.timeout,
        max_tokens=request.max_tokens,
    )

    return success_response(
        data={"choices": [choices.model_dump() for choices in response.choices]},
        message="Chat completed successfully",
    )
