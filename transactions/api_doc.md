### 获取资产按月分类统计数据

根据资产ID查询每个月按分类统计的数据，支持分页。

**请求URL**

```
GET /api/transactions/asset_monthly_categories/
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| asset_id | integer | 是 | 资产ID |
| start_date | integer | 否 | 开始日期时间戳 |
| end_date | integer | 否 | 结束日期时间戳 |
| page | integer | 否 | 页码，默认为1 |
| page_size | integer | 否 | 每页数量，默认为项目设置 |

**响应**

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "count": 24,
    "next": "http://example.com/api/transactions/asset_monthly_categories/?asset_id=1&page=2",
    "previous": null,
    "results": [
      {
        "month": "2023-12",
        "month_timestamp": 1701388800,
        "categories": [
          {
            "category_id": 1,
            "category_name": "餐饮",
            "is_income": false,
            "total_amount": "1250.00",
            "transaction_count": 15
          },
          {
            "category_id": 2,
            "category_name": "交通",
            "is_income": false,
            "total_amount": "350.00",
            "transaction_count": 8
          }
        ],
        "total_expense": "1600.00",
        "total_income": "5000.00",
        "net_amount": "3400.00"
      },
      {
        "month": "2023-11",
        "month_timestamp": 1698796800,
        "categories": [
          {
            "category_id": 1,
            "category_name": "餐饮",
            "is_income": false,
            "total_amount": "1100.00",
            "transaction_count": 12
          }
        ],
        "total_expense": "1100.00",
        "total_income": "5000.00",
        "net_amount": "3900.00"
      }
    ]
  }
}
``` 