# AI消息API接口文档

## 目录

- [会话管理](#会话管理)
  - [获取会话列表](#获取会话列表)
  - [创建会话](#创建会话)
  - [获取会话详情](#获取会话详情)
  - [更新会话](#更新会话)
  - [删除会话](#删除会话)
  - [获取会话消息](#获取会话消息)
- [消息管理](#消息管理)
  - [获取消息列表](#获取消息列表)
  - [发送文本消息](#发送文本消息)
  - [发送语音消息](#发送语音消息)
  - [获取消息详情](#获取消息详情)
  - [更新消息](#更新消息)
  - [删除消息](#删除消息)
  - [获取消息使用情况](#获取消息使用情况)

## 会话管理

### 获取会话列表

获取当前用户的所有消息会话。

**请求URL**

```
GET /api/ai_messages/sessions/
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- |----| --- |
| model | string | 是  | 按模型名称筛选 |
| assistant_name | string | 否  | 按助手名称搜索 |

model：
- ChatGPT
- DeepSeek
- Qwen

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 123,
      "model": "ChatGPT",
      "assistant_name": "Alice",
      "created_at": "2025-03-11T12:00:00Z",
      "updated_at": "2025-03-11T12:30:00Z"
    }
  ]
}
```

### 创建会话

创建新的消息会话。

**请求URL**

```
POST /api/ai_messages/sessions/
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| model | string | 是 | 模型名称 |
| assistant_name | string | 否 | 助手名称 |

**请求示例**

```json
{
  "model": "ChatGPT",
  "assistant_name": "Alice"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "user_id": 123,
    "model": "ChatGPT",
    "assistant_name": "Alice",
    "created_at": "2025-03-11T12:00:00Z",
    "updated_at": "2025-03-11T12:00:00Z"
  }
}
```

### 获取会话详情

获取指定会话的详细信息。

**请求URL**

```
GET /api/ai_messages/sessions/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 会话ID |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "user_id": 123,
    "model": "ChatGPT",
    "assistant_name": "Alice",
    "created_at": "2025-03-11T12:00:00Z",
    "updated_at": "2025-03-11T12:30:00Z",
    "messages": [
      {
        "id": 1,
        "content": "你好",
        "message_type": "user",
        "is_user": true,
        "is_voice": false,
        "created_at": "2025-03-11T12:00:00Z"
      },
      {
        "id": 2,
        "content": "你好！有什么我可以帮助你的吗？",
        "message_type": "assistant",
        "is_user": false,
        "is_voice": false,
        "created_at": "2025-03-11T12:00:05Z"
      }
    ]
  }
}
```

### 更新会话

更新指定会话的信息。

**请求URL**

```
PUT /api/ai_messages/sessions/{id}/
PATCH /api/ai_messages/sessions/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 会话ID |

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| model | string | 否 | 模型名称 |
| assistant_name | string | 否 | 助手名称 |

**请求示例**

```json
{
  "assistant_name": "Financial Advisor"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": 123,
    "model": "ChatGPT",
    "assistant_name": "Financial Advisor",
    "created_at": "2025-03-11T12:00:00Z",
    "updated_at": "2025-03-11T13:00:00Z"
  }
}
```

### 删除会话

删除指定的会话。

**请求URL**

```
DELETE /api/ai_messages/sessions/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 会话ID |

**响应**

```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 获取会话消息

获取指定会话的所有消息。

**请求URL**

```
GET /api/ai_messages/sessions/{id}/messages/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 会话ID |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "session_id": 1,
      "content": "你好",
      "message_type": "user",
      "is_user": true,
      "is_voice": false,
      "transaction_ids": "0",
      "created_at": "2025-03-11T12:00:00Z"
    },
    {
      "id": 2,
      "session_id": 1,
      "content": "你好！有什么我可以帮助你的吗？",
      "message_type": "assistant",
      "is_user": false,
      "is_voice": false,
      "transaction_ids": "0",
      "created_at": "2025-03-11T12:00:05Z"
    }
  ]
}
```

### 同步历史消息

获取指定消息之前的所有历史消息。

**请求URL**

```
GET /api/ai_messages/sessions/{id}/sync_history/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 会话ID |

**查询参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| message_id | integer | 是 | 参考消息ID，将返回该消息之前的所有消息 |
| page | integer | 否 | 页码，默认为1 |
| page_size | integer | 否 | 每页记录数，默认为20，最大为100 |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 50,
    "next": "http://example.com/api/ai_messages/sessions/1/sync_history/?message_id=100&page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "session_id": 1,
        "content": "你好",
        "message_type": "user",
        "is_user": true,
        "is_voice": false,
        "transaction_ids": "0",
        "created_at": "2025-03-11T12:00:00Z"
      }
    ]
  }
}
```

## 消息管理

### 获取消息列表

获取当前用户的所有消息。

**请求URL**

```
GET /api/ai_messages/messages/
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| session_id | integer | 否 | 按会话ID筛选 |
| is_user | boolean | 否 | 是否用户消息 |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "session_id": 1,
      "content": "你好",
      "message_type": "user",
      "is_user": true,
      "is_voice": false,
      "transaction_ids": "0",
      "created_at": "2025-03-11T12:00:00Z"
    }
  ]
}
```

### 发送文本消息

发送文本消息并获取AI回复。

**请求URL**

```
POST /api/ai_messages/text_message/
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| session_id | integer | 是 | 会话ID |
| content | string | 是 | 消息内容 |
| ledger_id | integer | 是 | 账本ID |
| asset_id | integer | 否 | 资产ID |
| language | string | 否 | 语言代码，默认为"en" |
| assistant_name | string | 否 | 助手名称，默认为"Alice" |

**请求示例**

```json
{
  "session_id": 1,
  "content": "早餐20，午餐30",
  "ledger_id": 1,
  "language": "zh",
  "assistant_name": "financial_analyst"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "发送成功",
  "data": {
    "results": [
      {
        "id": 3,
        "session_id": 1,
        "content": "早餐20，午餐30",
        "message_type": "user",
        "is_user": true,
        "is_voice": false,
        "transaction_ids": "0",
        "created_at": "2025-03-11T14:00:00Z"
      },
      {
        "id": 4,
        "session_id": 1,
        "content": "已为您记录两笔支出：早餐20元和午餐30元。",
        "message_type": "assistant",
        "is_user": false,
        "is_voice": false,
        "transaction_ids": "1,2",
        "created_at": "2025-03-11T14:00:05Z"
      }
    ]
  }
}
```

### 发送语音消息

发送语音消息（已转为文字）并获取AI回复。

**请求URL**

```
POST /api/ai_messages/voice_message/
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| session_id | integer | 是 | 会话ID |
| content | string | 是 | 语音转文字的内容 |
| ledger_id | integer | 是 | 账本ID |
| asset_id | integer | 否 | 资产ID |
| language | string | 否 | 语言代码，默认为"en" |
| assistant_name | string | 否 | 助手名称，默认为"Alice" |

**请求示例**

```json
{
  "session_id": 1,
  "content": "早餐20，午餐30",
  "ledger_id": 1,
  "language": "zh",
  "assistant_name": "financial_analyst"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "发送成功",
  "data": {
    "results": [
      {
        "id": 5,
        "session_id": 1,
        "content": "早餐20，午餐30",
        "message_type": "user",
        "is_user": true,
        "is_voice": true,
        "transaction_ids": "0",
        "created_at": "2025-03-11T15:00:00Z"
      },
      {
        "id": 6,
        "session_id": 1,
        "content": "已为您记录两笔支出：早餐20元和午餐30元。",
        "message_type": "assistant",
        "is_user": false,
        "is_voice": false,
        "transaction_ids": "3,4",
        "created_at": "2025-03-11T15:00:05Z"
      }
    ]
  }
}
```

### 获取消息详情

获取指定消息的详细信息。

**请求URL**

```
GET /api/ai_messages/messages/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 消息ID |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "session_id": 1,
    "content": "你好",
    "message_type": "user",
    "is_user": true,
    "is_voice": false,
    "transaction_ids": "0",
    "created_at": "2025-03-11T12:00:00Z",
    "updated_at": "2025-03-11T12:00:00Z"
  }
}
```

### 更新消息

更新指定消息的内容。

**请求URL**

```
PUT /api/ai_messages/messages/{id}/
PATCH /api/ai_messages/messages/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 消息ID |

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| content | string | 否 | 消息内容 |

**请求示例**

```json
{
  "content": "你好啊"
}
```

**响应**

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "session_id": 1,
    "content": "你好啊",
    "message_type": "user",
    "is_user": true,
    "is_voice": false,
    "transaction_ids": "0",
    "created_at": "2025-03-11T12:00:00Z",
    "updated_at": "2025-03-11T16:00:00Z"
  }
}
```

### 删除消息

删除指定的消息。

**请求URL**

```
DELETE /api/ai_messages/messages/{id}/
```

**路径参数**

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | integer | 消息ID |

**响应**

```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### Get Message Usage

Get user's message usage information, including sent message count and limits.

**Request URL**

```
GET /api/ai_messages/messages/message_usage/
```

**Response**

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "message_count": 35,
    "message_limit": 50,
    "is_premium": false
  }
}
```

**Response Fields**

| Field | Type | Description |
| --- | --- | --- |
| message_count | integer | Number of messages sent by the user |
| message_limit | integer/null | Message count limit, null for premium users (unlimited) |
| is_premium | boolean | Whether the user is a premium user |

## 错误码说明

| 错误码 | 描述 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 所有请求需要在Header中包含有效的认证信息
2. 发送消息时，如果内容包含财务信息，系统会自动识别并创建交易记录
3. 创建的交易记录ID会保存在AI回复消息的`transaction_ids`字段中
4. 语音消息和文本消息的处理流程相同，只是`is_voice`字段的值不同
