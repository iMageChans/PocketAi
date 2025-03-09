import requests

base_url = "http://localhost:8000/api/categories/ledger/"

# 测试不同语言的API响应
languages = ['zh-hans', 'en', 'es', 'fr', 'ja', 'ko', 'pt']

for lang in languages:
    print(f"\n测试语言: {lang}")
    response = requests.get(f"{base_url}?lang={lang}")
    if response.status_code == 200:
        print("状态码:", response.status_code)
        print("消息:", response.json().get('msg'))
    else:
        print(f"请求失败: {response.status_code}") 