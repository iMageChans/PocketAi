# PocketAI API 文档

## 基础信息

- 基础URL: `/api/`
- 认证方式: Token认证（在请求头中添加 `Authorization: <your_token>`）
- 响应格式: JSON
- 支持语言: 中文(zh-hans)、英文(en)、西班牙语(es)、葡萄牙语(pt)、法语(fr)、日语(ja)、韩语(ko)

## 3. 交易记录相关

### 3.1 获取交易记录列表

获取当前用户的所有交易记录。

- **URL**: `/api/transactions/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `ledger_id`: 按账本ID筛选
- `asset_id`: 按资产ID筛选
- `category_id`: 按交易分类ID筛选
- `is_expense`: 按交易类型筛选（true: 支出, false: 收入）
- `start_date`: 开始日期时间戳（秒）
- `end_date`: 结束日期时间戳（秒）
- `min_amount`: 最小金额
- `max_amount`: 最大金额
- `include_in_stats`: 是否纳入统计（true/false）
- `search`: 搜索关键词（搜索备注、分类名称、资产名称、账本名称）
- `page`: 页码
- `page_size`: 每页数量

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 42,
    "next": "http://example.com/api/transactions/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "user_id": "user123",
        "is_expense": true,
        "ledger": 1,
        "ledger_detail": {
          "id": 1,
          "name": "我的账本",
          "description": "日常开销记录"
        },
        "asset": 2,
        "asset_detail": {
          "id": 2,
          "name": "现金账户",
          "balance": 1500.00,
          "currency": "CNY"
        },
        "category": 3,
        "category_detail": {
          "id": 3,
          "name": "餐饮",
          "is_income": false
        },
        "amount": 42.50,
        "transaction_date": 1582790006000,
        "notes": "午餐费",
        "include_in_stats": true,
        "created_at": 1582790006000,
        "updated_at": 1582790006000
      }
    ]
  }
}
```

### 3.2 创建交易记录

创建新的交易记录。

- **URL**: `/api/transactions/`
- **方法**: `POST`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "is_expense": true,
  "ledger": 1,
  "asset": 2,
  "category": 3,
  "amount": 42.50,
  "transaction_date": 1582790006000,
  "notes": "午餐费",
  "include_in_stats": true
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "is_expense": true,
    "ledger": 1,
    "ledger_detail": {
      "id": 1,
      "name": "我的账本",
      "description": "日常开销记录"
    },
    "asset": 2,
    "asset_detail": {
      "id": 2,
      "name": "现金账户",
      "balance": 1500.00,
      "currency": "CNY"
    },
    "category": 3,
    "category_detail": {
      "id": 3,
      "name": "餐饮",
      "is_income": false
    },
    "amount": 42.50,
    "transaction_date": 1582790006000,
    "notes": "午餐费",
    "include_in_stats": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 3.3 获取单条交易记录

获取指定ID的交易记录详情。

- **URL**: `/api/transactions/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "is_expense": true,
    "ledger": 1,
    "ledger_detail": {
      "id": 1,
      "name": "我的账本",
      "description": "日常开销记录"
    },
    "asset": 2,
    "asset_detail": {
      "id": 2,
      "name": "现金账户",
      "balance": 1500.00,
      "currency": "CNY"
    },
    "category": 3,
    "category_detail": {
      "id": 3,
      "name": "餐饮",
      "is_income": false
    },
    "amount": 42.50,
    "transaction_date": 1582790006000,
    "notes": "午餐费",
    "include_in_stats": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 3.4 更新交易记录

更新指定ID的交易记录。

- **URL**: `/api/transactions/{id}/`
- **方法**: `PUT`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "is_expense": true,
  "ledger": 1,
  "asset": 2,
  "category": 3,
  "amount": 45.50,
  "transaction_date": 1582790006000,
  "notes": "午餐费（更新）",
  "include_in_stats": true
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "is_expense": true,
    "ledger": 1,
    "ledger_detail": {
      "id": 1,
      "name": "我的账本",
      "description": "日常开销记录"
    },
    "asset": 2,
    "asset_detail": {
      "id": 2,
      "name": "现金账户",
      "balance": 1500.00,
      "currency": "CNY"
    },
    "category": 3,
    "category_detail": {
      "id": 3,
      "name": "餐饮",
      "is_income": false
    },
    "amount": 45.50,
    "transaction_date": 1582790006000,
    "notes": "午餐费（更新）",
    "include_in_stats": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 3.5 部分更新交易记录

部分更新指定ID的交易记录。

- **URL**: `/api/transactions/{id}/`
- **方法**: `PATCH`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "amount": 45.50,
  "notes": "午餐费（更新）"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "is_expense": true,
    "ledger": 1,
    "ledger_detail": {
      "id": 1,
      "name": "我的账本",
      "description": "日常开销记录"
    },
    "asset": 2,
    "asset_detail": {
      "id": 2,
      "name": "现金账户",
      "balance": 1500.00,
      "currency": "CNY"
    },
    "category": 3,
    "category_detail": {
      "id": 3,
      "name": "餐饮",
      "is_income": false
    },
    "amount": 45.50,
    "transaction_date": 1582790006000,
    "notes": "午餐费（更新）",
    "include_in_stats": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 3.6 删除交易记录

删除指定ID的交易记录。

- **URL**: `/api/transactions/{id}/`
- **方法**: `DELETE`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 3.7 按账本获取交易统计

根据账本ID获取交易记录的统计数据，支持按不同时间周期查看和导航。

- **URL**: `/api/transactions/by_ledger/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `ledger_id`: 账本ID (必填)
- `period`: 时间周期 (`day`, `week`, `month`, `year`，默认为 `month`)
- `offset`: 时间偏移量，0表示当前周期，-1表示上一周期，1表示下一周期 (默认为0)

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "summary": {
      "total_expense": 1245.67,
      "total_income": 3000.00,
      "net_amount": 1754.33,
      "transaction_count": 24
    },
    "periods": [
      {
        "period": "2023-03-01",
        "total_expense": 425.67,
        "total_income": 1000.00,
        "net_amount": 574.33,
        "transaction_count": 8
      },
      {
        "period": "2023-03-15",
        "total_expense": 820.00,
        "total_income": 2000.00,
        "net_amount": 1180.00,
        "transaction_count": 16
      }
    ],
    "categories": [
      {
        "category_id": 3,
        "category_name": "餐饮",
        "is_income": false,
        "total_amount": 560.75,
        "transaction_count": 12
      },
      {
        "category_id": 5,
        "category_name": "工资",
        "is_income": true,
        "total_amount": 3000.00,
        "transaction_count": 1
      }
    ],
    "navigation": {
      "period": "month",
      "current_offset": 0,
      "previous_offset": -1,
      "next_offset": 1,
      "period_display": "March 2023",
      "start_date": 1677628800,
      "end_date": 1680307199
    }
  }
}
```

### 3.8 按资产获取交易统计

根据资产ID获取交易记录的统计数据，支持按不同时间周期查看和导航。

- **URL**: `/api/transactions/by_asset/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `asset_id`: 资产ID (必填)
- `period`: 时间周期 (`month`, `year`，默认为 `month`)
- `offset`: 时间偏移量，0表示当前周期，-1表示上一周期，1表示下一周期 (默认为0)

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "summary": {
      "total_expense": 845.67,
      "total_income": 2000.00,
      "net_amount": 1154.33,
      "transaction_count": 18
    },
    "periods": [
      {
        "period": "2023-03-01",
        "total_expense": 325.67,
        "total_income": 0.00,
        "net_amount": -325.67,
        "transaction_count": 6
      },
      {
        "period": "2023-03-15",
        "total_expense": 520.00,
        "total_income": 2000.00,
        "net_amount": 1480.00,
        "transaction_count": 12
      }
    ],
    "categories": [
      {
        "category_id": 3,
        "category_name": "餐饮",
        "is_income": false,
        "total_amount": 460.75,
        "transaction_count": 10
      },
      {
        "category_id": 5,
        "category_name": "工资",
        "is_income": true,
        "total_amount": 2000.00,
        "transaction_count": 1
      }
    ],
    "navigation": {
      "period": "month",
      "current_offset": 0,
      "previous_offset": -1,
      "next_offset": 1,
      "period_display": "March 2023",
      "start_date": 1677628800,
      "end_date": 1680307199
    }
  }
}
```

## 4. 资产相关

### 4.1 获取资产列表

获取当前用户的所有资产。

- **URL**: `/api/assets/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `category_id`: 按资产分类ID筛选
- `currency`: 按货币类型筛选
- `include_in_total`: 是否计入总资产（true/false）
- `search`: 搜索关键词（搜索资产名称、备注）
- `page`: 页码
- `page_size`: 每页数量

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user_id": "user123",
        "name": "现金账户",
        "category": 1,
        "category_detail": {
          "id": 1,
          "name": "现金资产",
          "is_positive_asset": true
        },
        "currency": "CNY",
        "balance": 5000.00,
        "notes": "日常使用的现金",
        "include_in_total": true,
        "created_at": 1582790006000,
        "updated_at": 1582790006000
      }
    ]
  }
}
```

### 4.2 创建资产

创建新的资产。

- **URL**: `/api/assets/`
- **方法**: `POST`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "新储蓄账户",
  "category": 1,
  "currency": "CNY",
  "balance": 10000.00,
  "notes": "新开的储蓄账户",
  "include_in_total": true
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 6,
    "user_id": "user123",
    "name": "新储蓄账户",
    "category": 1,
    "category_detail": {
      "id": 1,
      "name": "现金资产",
      "is_positive_asset": true
    },
    "currency": "CNY",
    "balance": 10000.00,
    "notes": "新开的储蓄账户",
    "include_in_total": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 4.3 获取单个资产

获取指定ID的资产详情。

- **URL**: `/api/assets/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "现金账户",
    "category": 1,
    "category_detail": {
      "id": 1,
      "name": "现金资产",
      "is_positive_asset": true
    },
    "currency": "CNY",
    "balance": 5000.00,
    "notes": "日常使用的现金",
    "include_in_total": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 4.4 更新资产

更新指定ID的资产。

- **URL**: `/api/assets/{id}/`
- **方法**: `PUT`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "现金账户（更新）",
  "category": 1,
  "currency": "CNY",
  "balance": 6000.00,
  "notes": "更新后的现金账户",
  "include_in_total": true
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "现金账户（更新）",
    "category": 1,
    "category_detail": {
      "id": 1,
      "name": "现金资产",
      "is_positive_asset": true
    },
    "currency": "CNY",
    "balance": 6000.00,
    "notes": "更新后的现金账户",
    "include_in_total": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 4.5 部分更新资产

部分更新指定ID的资产。

- **URL**: `/api/assets/{id}/`
- **方法**: `PATCH`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "balance": 5500.00,
  "notes": "余额已调整"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "现金账户",
    "category": 1,
    "category_detail": {
      "id": 1,
      "name": "现金资产",
      "is_positive_asset": true
    },
    "currency": "CNY",
    "balance": 5500.00,
    "notes": "余额已调整",
    "include_in_total": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 4.6 删除资产

删除指定ID的资产。

- **URL**: `/api/assets/{id}/`
- **方法**: `DELETE`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 4.7 按分类获取资产统计

获取用户资产按分类统计的总额。

- **URL**: `/api/assets/by_category/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "categories": [
      {
        "category_id": 1,
        "category_name": "现金资产",
        "category_type": "cash",
        "is_positive_asset": true,
        "total_balance_usd": "5000.00",
        "asset_count": 2
      },
      {
        "category_id": 2,
        "category_name": "信用卡",
        "category_type": "credit_card",
        "is_positive_asset": false,
        "total_balance_usd": "2500.00",
        "asset_count": 1
      }
    ],
    "summary": {
      "positive_total_usd": "15000.00", 
      "negative_total_usd": "5000.00",
      "net_asset_usd": "10000.00"
    }
  }
}
```

### 4.8 获取用户资产总览

获取用户所有资产的统计总览。

- **URL**: `/api/assets/overview/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_assets_usd": "15000.00",
    "total_liabilities_usd": "5000.00",
    "net_worth_usd": "10000.00",
    "asset_count": 5,
    "liability_count": 2,
    "currencies": [
      {
        "currency": "CNY",
        "assets_amount": "50000.00",
        "liabilities_amount": "20000.00",
        "net_amount": "30000.00",
        "exchange_rate": "6.5",
        "assets_usd": "7692.31",
        "liabilities_usd": "3076.92",
        "net_usd": "4615.39"
      },
      {
        "currency": "USD",
        "assets_amount": "12000.00",
        "liabilities_amount": "2000.00",
        "net_amount": "10000.00",
        "exchange_rate": "1.0",
        "assets_usd": "12000.00",
        "liabilities_usd": "2000.00",
        "net_usd": "10000.00"
      }
    ]
  }
}
```

## 5. 梦想基金相关

### 5.1 获取梦想基金列表

获取当前用户的所有梦想基金。

- **URL**: `/api/goals/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `is_completed`: 按完成状态筛选（true/false）
- `search`: 搜索关键词（搜索名称、描述）
- `page`: 页码
- `page_size`: 每页数量

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "买新手机",
        "user_id": "user123",
        "target_amount": 5000.00,
        "current_amount": 3000.00,
        "deadline": 1672531200000,
        "description": "存钱买新款手机",
        "is_completed": false,
        "progress_percentage": 60.00,
        "remaining_amount": 2000.00,
        "created_at": 1640995200000,
        "updated_at": 1641081600000
      },
      {
        "id": 2,
        "name": "旅行基金",
        "user_id": "user123",
        "target_amount": 10000.00,
        "current_amount": 10000.00,
        "deadline": 1688169600000,
        "description": "暑假旅行资金",
        "is_completed": true,
        "progress_percentage": 100.00,
        "remaining_amount": 0.00,
        "created_at": 1640995200000,
        "updated_at": 1641081600000
      }
    ]
  }
}
```

### 5.2 创建梦想基金

创建一个新的梦想基金。

- **URL**: `/api/goals/`
- **方法**: `POST`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "买新手机",
  "target_amount": 5000.00,
  "deadline": 1672531200000,
  "description": "存钱买新款手机"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 1,
    "name": "买新手机",
    "user_id": "user123",
    "target_amount": 5000.00,
    "current_amount": 0.00,
    "deadline": 1672531200000,
    "description": "存钱买新款手机",
    "is_completed": false,
    "progress_percentage": 0.00,
    "remaining_amount": 5000.00,
    "created_at": 1640995200000,
    "updated_at": 1640995200000
  }
}
```

### 5.3 获取梦想基金详情

获取指定梦想基金的详细信息。

- **URL**: `/api/goals/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "name": "买新手机",
    "user_id": "user123",
    "target_amount": 5000.00,
    "current_amount": 3000.00,
    "deadline": 1672531200000,
    "description": "存钱买新款手机",
    "is_completed": false,
    "progress_percentage": 60.00,
    "remaining_amount": 2000.00,
    "created_at": 1640995200000,
    "updated_at": 1641081600000
  }
}
```

### 5.4 更新梦想基金

更新指定梦想基金的信息。

- **URL**: `/api/goals/{id}/`
- **方法**: `PUT`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "买新手机",
  "target_amount": 6000.00,
  "deadline": 1675209600000,
  "description": "存钱买新款高端手机"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "name": "买新手机",
    "user_id": "user123",
    "target_amount": 6000.00,
    "current_amount": 3000.00,
    "deadline": 1675209600000,
    "description": "存钱买新款高端手机",
    "is_completed": false,
    "progress_percentage": 50.00,
    "remaining_amount": 3000.00,
    "created_at": 1640995200000,
    "updated_at": 1641168000000
  }
}
```

### 5.5 部分更新梦想基金

部分更新指定梦想基金的信息。

- **URL**: `/api/goals/{id}/`
- **方法**: `PATCH`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "买新手机",
  "description": "存钱买新款高端手机"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "name": "买新手机",
    "user_id": "user123",
    "target_amount": 5000.00,
    "current_amount": 3000.00,
    "deadline": 1672531200000,
    "description": "存钱买新款高端手机",
    "is_completed": false,
    "progress_percentage": 60.00,
    "remaining_amount": 2000.00,
    "created_at": 1640995200000,
    "updated_at": 1641168000000
  }
}
```

### 5.6 向梦想基金存款

向指定梦想基金存入资金。

- **URL**: `/api/goals/{id}/deposit/`
- **方法**: `POST`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "goal": 1,
  "amount": 1000.00,
  "notes": "本月工资存入"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "存款成功",
  "data": {
    "goal": {
      "id": 1,
      "name": "买新手机",
      "user_id": "user123",
      "target_amount": 5000.00,
      "current_amount": 4000.00,
      "deadline": 1672531200000,
      "description": "存钱买新款手机",
      "is_completed": false,
      "progress_percentage": 80.00,
      "remaining_amount": 1000.00,
      "created_at": 1640995200000,
      "updated_at": 1641168000000
    },
    "deposit": {
      "id": 3,
      "goal": 1,
      "amount": 1000.00,
      "notes": "本月工资存入",
      "deposit_date": 1641168000000
    }
  }
}
```

**错误响应**:

1. 当梦想基金已完成时:

```json
{
  "code": 400,
  "msg": "该梦想基金已达成目标，不能继续存款",
  "data": {}
}
```

2. 当存款目标不匹配时:

```json
{
  "code": 400,
  "msg": "存款目标不匹配",
  "data": {}
}
```

### 5.7 获取梦想基金的存款记录

获取指定梦想基金的所有存款记录。

- **URL**: `/api/goals/{id}/deposits/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 3,
        "goal": 1,
        "amount": 1000.00,
        "notes": "本月工资存入",
        "deposit_date": 1641168000000
      },
      {
        "id": 2,
        "goal": 1,
        "amount": 1500.00,
        "notes": "奖金存入",
        "deposit_date": 1641081600000
      },
      {
        "id": 1,
        "goal": 1,
        "amount": 1500.00,
        "notes": "初始存款",
        "deposit_date": 1640995200000
      }
    ]
  }
}
```

### 5.8 获取梦想基金总览

获取当前用户所有梦想基金的统计信息。

- **URL**: `/api/goals/summary/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_goals": 3,
    "completed_goals": 1,
    "in_progress_goals": 2,
    "total_target_amount": 20000.00,
    "total_current_amount": 15000.00,
    "overall_progress": 75.00
  }
}
```

## 6. 分类相关

### 6.1 账本分类

#### 6.1.1 获取账本分类列表

获取系统中所有的账本分类。

- **URL**: `/api/categories/ledger/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "日常账本",
      "description": "记录日常收支",
      "icon": "📅",
      "is_default": true,
      "sort_order": 1,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    },
    {
      "id": 2,
      "name": "商务账本",
      "description": "记录工作相关收支",
      "icon": "💼",
      "is_default": false,
      "sort_order": 2,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    }
  ]
}
```

#### 6.1.2 获取单个账本分类

获取指定ID的账本分类详情。

- **URL**: `/api/categories/ledger/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "name": "日常账本",
    "description": "记录日常收支",
    "icon": "📅",
    "is_default": true,
    "sort_order": 1,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 6.2 资产分类

#### 6.2.1 获取资产分类列表

获取系统中所有的资产分类。

- **URL**: `/api/categories/asset/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "现金",
      "icon": "💵",
      "category_type": "debit",
      "category_type_display": "借记卡/现金",
      "is_positive_asset": true,
      "sort_order": 1,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    },
    {
      "id": 5,
      "name": "信用卡",
      "icon": "💳",
      "category_type": "credit",
      "category_type_display": "信用卡",
      "is_positive_asset": false,
      "sort_order": 5,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    }
  ]
}
```

#### 6.2.2 获取单个资产分类

获取指定ID的资产分类详情。

- **URL**: `/api/categories/asset/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "name": "现金",
    "icon": "💵",
    "category_type": "debit",
    "category_type_display": "借记卡/现金",
    "is_positive_asset": true,
    "sort_order": 1,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 6.3 交易分类

#### 6.3.1 获取交易分类列表

获取系统中所有的交易分类。

- **URL**: `/api/categories/transaction/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `is_income`: 按交易类型筛选（true: 收入类别, false: 支出类别）

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "餐饮",
      "is_income": false,
      "type_display": "支出",
      "icon": "🍽️",
      "sort_order": 1,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    },
    {
      "id": 20,
      "name": "工资",
      "is_income": true,
      "type_display": "收入",
      "icon": "💰",
      "sort_order": 1,
      "created_at": 1582790006000,
      "updated_at": 1582790006000
    }
  ]
}
```

#### 6.3.2 获取单个交易分类

获取指定ID的交易分类详情。

- **URL**: `/api/categories/transaction/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "name": "餐饮",
    "is_income": false,
    "type_display": "支出",
    "icon": "🍽️",
    "sort_order": 1,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

## 7. 账本相关

### 7.1 获取账本列表

获取当前用户的所有账本。

- **URL**: `/api/ledgers/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `search`: 搜索关键词（搜索账本名称、描述）
- `page`: 页码
- `page_size`: 每页数量

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user_id": "user123",
        "name": "日常账本",
        "description": "记录日常生活支出",
        "icon": "daily",
        "color": "#FF5733",
        "is_default": true,
        "created_at": 1582790006000,
        "updated_at": 1582790006000
      }
    ]
  }
}
```

### 7.2 创建账本

创建新的账本。

- **URL**: `/api/ledgers/`
- **方法**: `POST`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "旅行账本",
  "description": "记录旅行支出",
  "icon": "travel",
  "color": "#3366FF",
  "is_default": false
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "id": 2,
    "user_id": "user123",
    "name": "旅行账本",
    "description": "记录旅行支出",
    "icon": "travel",
    "color": "#3366FF",
    "is_default": false,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 7.3 获取单个账本

获取指定ID的账本详情。

- **URL**: `/api/ledgers/{id}/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "日常账本",
    "description": "记录日常生活支出",
    "icon": "daily",
    "color": "#FF5733",
    "is_default": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 7.4 更新账本

更新指定ID的账本。

- **URL**: `/api/ledgers/{id}/`
- **方法**: `PUT`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "name": "日常账本",
  "description": "记录日常生活支出和收入",
  "icon": "daily",
  "color": "#FF5733",
  "is_default": true
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "日常账本",
    "description": "记录日常生活支出和收入",
    "icon": "daily",
    "color": "#FF5733",
    "is_default": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 7.5 部分更新账本

部分更新指定ID的账本。

- **URL**: `/api/ledgers/{id}/`
- **方法**: `PATCH`
- **认证**: 需要
- **权限**: 已认证用户

**请求参数**:

```json
{
  "description": "记录日常生活支出和收入",
  "color": "#FF5733"
}
```

**响应参数**:

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": {
    "id": 1,
    "user_id": "user123",
    "name": "日常账本",
    "description": "记录日常生活支出和收入",
    "icon": "daily",
    "color": "#FF5733",
    "is_default": true,
    "created_at": 1582790006000,
    "updated_at": 1582790006000
  }
}
```

### 7.6 删除账本

删除指定ID的账本。

- **URL**: `/api/ledgers/{id}/`
- **方法**: `DELETE`
- **认证**: 需要
- **权限**: 已认证用户

**响应参数**:

```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 7.7 账本统计

获取指定账本的统计数据。

- **URL**: `/api/ledgers/{id}/stats/`
- **方法**: `GET`
- **认证**: 需要
- **权限**: 已认证用户

**查询参数**:

- `period`: 统计周期（day, week, month, year，默认为month）
- `start_date`: 开始日期时间戳（秒）
- `end_date`: 结束日期时间戳（秒）

**响应参数**:

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_expense": 2456.78,
    "total_income": 5000.00,
    "net_amount": 2543.22,
    "transaction_count": 42,
    "top_expense_categories": [
      {
        "category_id": 3,
        "category_name": "餐饮",
        "total_amount": 756.23,
        "percentage": 30.78
      }
    ],
    "top_income_categories": [
      {
        "category_id": 8,
        "category_name": "工资",
        "total_amount": 5000.00,
        "percentage": 100.00
      }
    ]
  }
}
```

## 8. 数据和时间格式

### 8.1 时间戳

所有API中与时间相关的字段均使用Unix时间戳（毫秒级），如：

```
1582790006000  // 对应 2020-02-27 09:13:26 UTC
```

### 8.2 金额格式

所有金额均使用固定小数位（2位）的数值，如：

```
42.50, 100.00, 0.75
```

### 8.3 分页格式

分页接口返回的数据格式如下：

```json
{
  "count": 100,
  // 总记录数
  "next": "http://example.com/api/resource/?page=3",
  // 下一页URL，如果没有则为null
  "previous": "http://example.com/api/resource/?page=1",
  // 上一页URL，如果没有则为null
  "results": []
  // 当前页的数据列表
}
```

## 9. 错误处理

### 9.1 常见错误码

- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `429` - 请求过于频繁
- `500` - 服务器内部错误

### 9.2 错误响应格式

所有错误响应均遵循以下格式：

```json
{
  "code": 400,
  "msg": "参数错误",
  "errors": {
    "field_name": [
      "错误详情"
    ]
  }
}
```

## 10. 最佳实践

### 10.1 时间范围查询

对于需要按时间范围查询的接口，建议使用以下参数：

- `period`: 预定义的时间段（如 `day`, `week`, `month`, `year`）
- `offset`: 相对于当前时间的偏移（0表示当前，-1表示上一个周期，1表示下一个周期）

例如，查询上个月的交易记录：

```
GET /api/transactions/by_ledger/?ledger_id=1&period=month&offset=-1
```

### 10.2 批量操作

对于批量创建、更新、删除操作，API提供专门的批量端点。这些端点的命名通常为：

```
/api/resource/bulk_create/
/api/resource/bulk_update/
/api/resource/bulk_delete/
```

### 10.3 API版本控制

API 可能会随时间推移而演化。为确保兼容性，客户端可以在请求中指定希望使用的API版本：

```
Accept: application/json; version=1.0
```

或通过URL路径：

```
/api/v1/resource/
```

# API认证指南

## 认证方式

本API使用基于Token的认证机制，所有需要认证的API请求都必须在HTTP头部包含有效的认证信息。

### 获取Token

```
POST /api/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

#### 响应示例

```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
  }
}
```

### 使用Token

获取到Token后，后续所有API请求都需要在HTTP头部附加以下信息：

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 不需要认证的端点

以下API端点不需要认证即可访问：

- `/api/auth/token/` - 获取认证Token
- `/api/auth/register/` - 用户注册
- `/api/auth/social-login/` - 社交登录
- `/api/oauth-providers/` - 获取OAuth提供商信息
- `/api/languages/` - 获取支持的语言列表

## 时间戳处理

所有涉及日期时间的字段都以Unix时间戳（毫秒）的形式表示。

### 示例

```json
{
  "created_at": 1672531200000,
  // 2023-01-01 12:00:00
  "updated_at": 1672531200000
  // 2023-01-01 12:00:00
}
```

### 提交数据时的时间格式

提交包含时间的数据时，可以使用以下格式：

1. 毫秒时间戳（整数）：`1672531200000`
2. ISO 8601格式（字符串）：`"2023-01-01T12:00:00Z"`

## 国际化支持

API支持多语言响应，可通过以下两种方式指定语言：

1. 在URL参数中添加`lang`参数：
   ```
   GET /api/categories/transaction/?lang=en
   ```

2. 设置HTTP头部：
   ```
   Accept-Language: en
   ```

支持的语言代码：

- `zh-hans` - 简体中文（默认）
- `en` - 英语
- `es` - 西班牙语
- `fr` - 法语
- `ja` - 日语
- `ko` - 韩语
- `pt` - 葡萄牙语

