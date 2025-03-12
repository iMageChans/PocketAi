import json
import logging
from typing import Dict, Any, Optional, Union

import requests
from requests.exceptions import RequestException

# 配置日志
logger = logging.getLogger(__name__)

# 基础URL配置
BASE_URL = 'https://users.pulseheath.com/agent/'
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


def _process_ai_response(response: requests.Response) -> Optional[Union[Dict, str]]:
    """
    处理AI服务的响应
    
    Args:
        response: HTTP响应对象
        
    Returns:
        处理后的响应内容，可能是字典或字符串
    """
    if response.status_code != 200:
        logger.error(f"AI服务返回错误: {response.status_code} - {response.text}")
        return None
    
    try:
        raw_content = response.json().get('data', {}).get('content')
        
        # 如果内容为空，返回None
        if raw_content is None:
            return None
            
        # 如果是字符串，处理可能的JSON格式
        if isinstance(raw_content, str):
            cleaned_content = raw_content.strip()
            
            # 处理可能的 ```json 标记
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 移除 ```json
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 移除 ```
                
            cleaned_content = cleaned_content.strip()
            
            # 尝试解析JSON字符串
            try:
                if cleaned_content.startswith('{') or cleaned_content.startswith('['):
                    return json.loads(cleaned_content)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，返回原始字符串
                pass
                
            return cleaned_content
            
        # 如果是字典，直接返回
        elif isinstance(raw_content, dict):
            return raw_content
            
        # 其他类型，直接返回
        return raw_content
        
    except Exception as e:
        logger.error(f"处理AI响应时出错: {str(e)}")
        return None


def create_ai_analyst(
    users_input: str, 
    token: str, 
    assistant_name: str = "financial_analyst", 
    model_name: str = "gpt-3.5-turbo", 
    language: str = "en",
) -> Dict[str, Any]:
    """
    调用AI分析服务，分析用户输入中的财务信息
    
    Args:
        users_input: 用户输入的文本
        token: 认证令牌
        assistant_name: 助手名称，默认为"financial_analyst"
        model_name: 模型名称，默认为"gpt-3.5-turbo"
        language: 语言代码，默认为"en"
        
    Returns:
        Dict: 包含分析结果的字典，如果失败则返回空字典
    """
    params = {
        "assistant_name": assistant_name,
        "model_name": model_name,
        "users_input": users_input,
        "language": language
    }
    
    try:
        response = fire(url="api/agent/chat/", token=token, method="post", params=params)
        logger.info(f"AI分析服务响应状态码: {response.status_code}")
        
        result = _process_ai_response(response)
        
        # 确保返回字典类型
        if isinstance(result, dict):
            return result
        elif result is None:
            # 如果处理失败，返回空的交易列表
            return {"transactions": []}
        else:
            # 如果返回的不是字典，尝试解析或返回空字典
            try:
                if isinstance(result, str):
                    parsed = json.loads(result)
                    if isinstance(parsed, dict):
                        return parsed
            except:
                pass
            
            # 默认返回空的交易列表
            return {"transactions": []}
            
    except Exception as e:
        logger.error(f"调用AI分析服务失败: {str(e)}")
        return {"transactions": []}


def create_ai_chat(
    users_input: str, 
    token: str, 
    assistant_name: str = "Alice", 
    model_name: str = "gpt-3.5-turbo", 
    language: str = "en",
    user_template_id: str = None,
) -> Optional[str]:
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
        
        result = _process_ai_response(response)
        
        # 确保返回字符串类型
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # 如果返回的是字典，尝试转换为字符串
            return json.dumps(result)
        else:
            # 其他情况，转换为字符串或返回None
            return str(result) if result is not None else None
            
    except Exception as e:
        logger.error(f"调用AI聊天服务失败: {str(e)}")
        return None


def create_ai_emotion(
    users_input: str, 
    token: str, 
    assistant_name: str = "emotion", 
    model_name: str = "gpt-3.5-turbo", 
    language: str = "en"
) -> Optional[str]:
    """
    调用AI情感分析服务，分析用户输入的情感
    
    Args:
        users_input: 用户输入的文本
        token: 认证令牌
        assistant_name: 助手名称，默认为"emotion"
        model_name: 模型名称，默认为"gpt-3.5-turbo"
        language: 语言代码，默认为"en"
        
    Returns:
        str: 情感分析结果，如果失败则返回None
    """
    params = {
        "assistant_name": assistant_name,
        "model_name": model_name,
        "users_input": users_input,
        "language": language
    }
    
    try:
        response = fire(url="api/agent/chat/emotion/", token=token, method="post", params=params)
        logger.info(f"AI情感分析服务响应状态码: {response.status_code}")
        
        result = _process_ai_response(response)
        
        # 确保返回字符串类型
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # 如果返回的是字典，尝试转换为字符串
            return json.dumps(result)
        else:
            # 其他情况，转换为字符串或返回None
            return str(result) if result is not None else None
            
    except Exception as e:
        logger.error(f"调用AI情感分析服务失败: {str(e)}")
        return None


def get_assistant_list(token: str) -> list:
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


# 修正函数名称，保持向后兼容
creat_ai_chat = create_ai_chat
creat_ai_emotion = create_ai_emotion

# 测试代码（已注释）
# chat = creat_ai_emotion("今天购物花了20，有点兴奋", "33c0e80df373d8d2b0154ce97210950522ff9f31", language="zh-cn")
# print(isinstance(chat, str))
print(creat_ai_chat("你好", "33c0e80df373d8d2b0154ce97210950522ff9f31", language="zh-cn"))
