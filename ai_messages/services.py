import json
import logging
from typing import Dict, Any, Optional, Union

import requests
from requests.exceptions import RequestException

# 配置日志
logger = logging.getLogger(__name__)

# 基础URL配置
BASE_URL = 'https://pocket.nicebudgeting.com/agent/'
# BASE_URL = 'http://127.0.0.1:8000/'


def fire(url: str, params: Dict[str, Any], token: str, method: str = "post") -> requests.Response:
    """
    发送HTTP请求到AI服务

    Args:
        url: API端点
        params: 请求参数
        token: 认证令牌
        method: HTTP方法，默认为"post"

    Returns:
        requests.Response: HTTP响应对象
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
    }

    full_url = f"{BASE_URL}{url}"

    try:
        if method.lower() == "post":
            return requests.post(
                full_url,
                params=params,
                headers=headers,
                data=json.dumps(params),
                timeout=30  # 添加超时设置
            )
        elif method.lower() == "get":
            return requests.get(
                full_url,
                headers=headers,
                timeout=30  # 添加超时设置
            )
        else:
            logger.error(f"不支持的HTTP方法: {method}")
            raise ValueError(f"不支持的HTTP方法: {method}")
    except RequestException as e:
        logger.error(f"请求失败: {str(e)}")
        # 重新抛出异常，让调用者处理
        raise


def create_ai_chat(
        users_input: str,
        token: str,
        assistant_name: str = "Alice",
        model_name: str = "	qwen-max",
        language: str = "zh-cn",
        user_template_id: str = None,
) -> Optional[dict[str, Any]]:
    """
    调用AI聊天服务，获取对用户输入的回复

    Args:
        users_input: 用户输入的文本
        token: 认证令牌
        assistant_name: 助手名称，默认为"Alice"
        model_name: 模型名称，默认为"gpt-3.5-turbo"
        language: 语言代码，默认为"en"

    Returns:
        str: AI的回复文本，如果失败则返回None
    """
    params = {
        "assistant_name": assistant_name,
        "model_name": model_name,
        "users_input": users_input,
        "language": language,
        "user_template_id": user_template_id
    }

    try:
        response = fire(url="api/agent/chat/", token=token, method="post", params=params)
        logger.info(f"AI聊天服务响应状态码: {response.status_code}")
        print(response.json())
        return response.json()['data']['content']
    except Exception as e:
        logger.error(f"调用AI聊天服务失败: {str(e)}")
        return None


def get_assistant_list(token: str) -> dict[str, Any]:
    """
    获取助手列表

    Args:
        token: 认证令牌

    Returns:
        list: 助手列表，如果失败则返回空列表
    """
    try:
        response = fire(url="api/assistant/", token=token, method="get", params={})
        logger.info(f"获取助手列表响应状态码: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"获取助手列表失败: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        logger.error(f"获取助手列表失败: {str(e)}")
        return []

creat_ai_chat = create_ai_chat
