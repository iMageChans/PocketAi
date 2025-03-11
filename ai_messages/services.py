import json

import requests


def fire(url, params, token, method="post"):
    base_url = 'https://users.pulseheath.com/agent/'
    # base_url = 'http://127.0.0.1:8000/'
    if method == "post":
        return requests.post(base_url + url,
                             params=params,
                             headers={
                                 'Content-Type': 'application/json',
                                 'Authorization': token,
                             },
                             data=json.dumps(params))
    elif method == "get":
        return requests.get(base_url + url,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': token,
                            })


def create_ai_analyst(users_input, token, assistant_name="financial_analyst", model_name="gpt-3.5-turbo", language="en"):
    params = {
        "assistant_name": assistant_name,
        "model_name": model_name,
        "users_input": users_input,
        "language": language
    }
    rsp = fire(url="api/agent/chat/", token=token, method="post", params=params)

    if rsp.status_code == 200:
        raw_content = rsp.json()['data']['content']
        if isinstance(raw_content, str):
            cleaned_content = raw_content.strip()
            # 处理可能的 ```json 标记
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 移除 ```json
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 移除 ```
            cleaned_content = cleaned_content.strip()

            parsed_content = json.loads(cleaned_content)
            return parsed_content
        elif isinstance(raw_content, dict):
            parsed_content = raw_content
            return parsed_content


def creat_ai_chat(users_input, token, assistant_name="Alice", model_name="gpt-3.5-turbo", language="en"):
    params = {
        "assistant_name": assistant_name,
        "model_name": model_name,
        "users_input": users_input,
        "language": language
    }
    rsp = fire(url="api/agent/chat/", token=token, method="post", params=params)

    if rsp.status_code == 200:
        raw_content = rsp.json()['data']['content']
        if isinstance(raw_content, str):
            cleaned_content = raw_content.strip()
            # 处理可能的 ```json 标记
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 移除 ```json
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 移除 ```
            cleaned_content = cleaned_content.strip()

            parsed_content = cleaned_content
            return parsed_content
        elif isinstance(raw_content, dict):
            parsed_content = raw_content
            return parsed_content
        else:
            return raw_content


def get_assistant_list(token):
    rsp = fire(url="api/assistant/", token=token, method="get", params={})
    if rsp.status_code == 200:
        return rsp.json()
    else:
        return []

