# 钉钉日历API接口文档

## 一、认证相关

### 1.1 获取 Access Token

**接口地址**: `https://api.dingtalk.com/v1.0/oauth2/accessToken`

**请求方式**: POST

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "appKey": "dingvteraijpiknlwdls",
  "appSecret": "fNa3xcZod3g3RNivBIWhXz2I4tUJxcA10f6NLbd402JJFthvSwZzel7QfHky0D9S"
}
```

**响应体**:
```json
{
  "accessToken": "46efeb9af0523104a317...",
  "expireIn": 7200
}
```

**返回字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| accessToken | string | 访问令牌，有效期2小时 |
| expireIn | number | 有效期秒数 |

---

## 二、用户信息相关

### 2.1 通过手机号获取用户ID

**接口地址**: `https://oapi.dingtalk.com/topapi/v2/user/getbymobile`

**请求方式**: POST

**认证方式**: access_token 参数

**请求参数**:
| 参数名 | 类型 | 必须 | 说明 |
|--------|------|------|------|
| access_token | string | 是 | 访问令牌 |

**请求体**:
```json
{
  "mobile": "18843112066"
}
```

**响应体**:
```json
{
  "errcode": 0,
  "errmsg": "ok",
  "result": {
    "userid": "1855404625945034",
    "name": "王涵",
    "unionid": "JblB9ViiEHFuDuJva79ii60QiEiE"
  }
}
```

**返回字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | number | 0表示成功 |
| errmsg | string | 错误信息 |
| result.userid | string | 用户ID |
| result.name | string | 用户姓名 |
| result.unionid | string | 用户的unionId |

---

### 2.2 通过用户ID获取UnionId

**接口地址**: `https://oapi.dingtalk.com/topapi/v2/user/get`

**请求方式**: POST

**认证方式**: access_token 参数

**请求参数**:
| 参数名 | 类型 | 必须 | 说明 |
|--------|------|------|------|
| access_token | string | 是 | 访问令牌 |

**请求体**:
```json
{
  "userid": "1855404625945034",
  "language": "zh_CN"
}
```

**响应体**:
```json
{
  "errcode": 0,
  "errmsg": "ok",
  "result": {
    "unionid": "JblB9ViiEHFuDuJva79ii60QiEiE",
    "name": "王涵"
  }
}
```

---

## 三、日历事件相关

> **说明**: 以下接口使用阿里云SDK调用
> SDK包: `alibabacloud-dingtalk >= 2.0.0`
> Client类: `alibabacloud_dingtalk.calendar_1_0.client.Client`

**通用请求头**:
```python
headers = dingtalkcalendar__1_0_models.CreateEventHeaders()
headers.x_acs_dingtalk_access_token = access_token  # 访问令牌
```

**通用参数**:
| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 日程所有者的unionId |
| calendar_id | string | 是 | 日历ID，使用'primary'表示默认日历 |

**API Base URL**: `https://api.dingtalk.com`

---

### 3.1 创建日历事件

**HTTP URL**: `POST https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events`

**SDK方法**: `client.create_event_with_options(user_id, calendar_id, request, headers, runtime)`

**请求体 (CreateEventRequest)**:
```python
from alibabacloud_dingtalk.calendar_1_0 import models as dingtalkcalendar__1__0_models

start = dingtalkcalendar__1__0_models.CreateEventRequestStart(
    date_time='2026-04-30T10:00:00+08:00',  # 开始时间，ISO8601格式
    time_zone='Asia/Shanghai'                 # 时区
)
end = dingtalkcalendar__1__0_models.CreateEventRequestEnd(
    date_time='2026-04-30T11:00:00+08:00',  # 结束时间
    time_zone='Asia/Shanghai'
)
reminders = dingtalkcalendar__1__0_models.CreateEventRequestReminders(
    method='dingtalk',  # 提醒方式
    minutes=30          # 提前多少分钟提醒
)

request = dingtalkcalendar__1__0_models.CreateEventRequest(
    summary='日程标题',           # 日程标题
    description='日程描述',       # 日程描述
    start=start,                 # 开始时间
    end=end,                     # 结束时间
    is_all_day=False,            # 是否全天事件
    reminders=[reminders]        # 提醒设置
)

# 可选：添加重复规则
# recurrence 格式为 RRULE 字符串数组
# 例如：每周四重复，到期前5天结束
request.recurrence = [
    "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20260522"
]
```

**重复规则 (RRULE) 格式说明**:
| 参数 | 说明 | 示例 |
|------|------|------|
| FREQ | 频率 | WEEKLY(每周), DAILY(每天) |
| INTERVAL | 间隔 | 1表示每周，2表示每隔一周 |
| BYDAY | 周几 | MO(周一), TU(周二), WE(周三), TH(周四), FR(周五), SA(周六), SU(周日) |
| UNTIL | 结束日期 | 格式YYYYMMDD，如20260522表示2026年5月22日 |

**响应体 (CreateEventResponseBody)**:
```python
{
    'id': 'UXYzWDlDMWdVcVh1bkhQcXlHcCtNdz09',     # 日程ID
    'summary': '日程标题',                          # 日程标题
    'description': '日程描述',                      # 日程描述
    'start': {'dateTime': '2026-04-30T10:00:00+08:00', 'timeZone': 'Asia/Shanghai'},
    'end': {'dateTime': '2026-04-30T11:00:00+08:00', 'timeZone': 'Asia/Shanghai'},
    'isAllDay': False,
    'organizer': {'displayName': '组织者', 'id': 'unionid', 'self': True},
    'attendees': [...],
    'reminders': [{'method': 'dingtalk', 'minutes': '30'}],
    'createTime': '2026-04-27T09:02:22Z',
    'updateTime': '2026-04-27T09:02:22Z'
}
```

**返回字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 日程唯一标识ID |
| summary | string | 日程标题 |
| description | string | 日程描述 |
| start.dateTime | string | 开始时间 |
| end.dateTime | string | 结束时间 |
| isAllDay | boolean | 是否全天事件 |
| organizer | object | 组织者信息 |
| attendees | array | 参与者列表 |
| reminders | array | 提醒设置列表 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |

---

### 3.2 删除日历事件

**HTTP URL**: `DELETE https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events/{event_id}`

**请求头**:
```
x-acs-dingtalk-access-token: {access_token}
Content-Type: application/json
```

**认证方式**: access_token 在请求头中

**请求体**: 无

**响应**: HTTP 200 或 204 表示成功，无响应体

---

### 3.3 查询单个事件

**HTTP URL**: `GET https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events/{event_id}`

**SDK方法**: `client.get_event_with_options(user_id, calendar_id, event_id, headers, runtime)`

**响应体 (GetEventResponseBody)**:
```python
{
    'id': '日程ID',
    'summary': '日程标题',
    'description': '日程描述',
    'start': {'dateTime': '...', 'timeZone': '...'},
    'end': {'dateTime': '...', 'timeZone': '...'},
    # ... 其他字段同上
}
```

**说明**: 如果事件不存在，抛出异常

---

### 3.4 列出日历事件

**HTTP URL**: `GET https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events`

**SDK方法**: `client.list_events_with_options(unionid, calendar_id, request, headers, runtime)`

**请求体 (ListEventsRequest)**:
```python
request = dingtalkcalendar__1__0_models.ListEventsRequest(
    time_min='2026-04-01T00:00:00+08:00',  # 开始时间 (ISO8601格式)
    time_max='2026-10-01T23:59:59+08:00'   # 结束时间 (ISO8601格式)
)
```

**请求参数说明**:
| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| time_min | string | 是 | 开始时间，ISO8601格式如 `2026-04-01T00:00:00+08:00` |
| time_max | string | 是 | 结束时间，ISO8601格式如 `2026-10-01T23:59:59+08:00` |
| max_results | number | 否 | 最大返回条数 |
| next_token | string | 否 | 分页令牌 |

**响应体 (ListEventsResponseBody)**:
```python
{
    'events': [
        {
            'id': '日程ID',                              # 日程ID
            'summary': '日程标题',                        # 日程标题
            'description': '描述',                        # 日程描述
            'start': {'date_time': '2026-04-30T10:00:00+08:00', 'time_zone': 'Asia/Shanghai'},
            'end': {'date_time': '2026-04-30T11:00:00+08:00', 'time_zone': 'Asia/Shanghai'},
            'is_all_day': False,                         # 是否全天事件
            'status': 'confirmed',                       # 状态
            'organizer': {'displayName': '组织者', 'id': 'unionid', 'self': True},
            'attendees': [...],                          # 参与者列表
            'reminders': [...],                          # 提醒设置
            'recurrence': None,                         # 重复规则（主日程才有）
            'series_master_id': None,                    # 重复主日程ID（非重复实例此字段为空）
            'create_time': '2025-12-04T05:41:46Z',      # 创建时间
            'update_time': '2025-12-04T05:41:46Z',     # 更新时间
            'location': None,                           # 地点
            'extended_properties': {'sharedProperties': {'belongCorpId': 'dingxxx'}},  # 扩展属性
        },
        # ...
    ],
    'next_token': None,  # 分页令牌
    'sync_token': None   # 同步令牌
}
```

**返回字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 日程唯一标识ID |
| summary | string | 日程标题 |
| description | string | 日程描述 |
| start.date_time | string | 开始时间 |
| end.date_time | string | 结束时间 |
| is_all_day | boolean | 是否全天事件 |
| status | string | 状态 (confirmed/tentative/cancelled) |
| organizer | object | 组织者信息 {displayName, id, self} |
| attendees | array | 参与者列表 |
| reminders | array | 提醒设置列表 |
| recurrence | string/null | 重复规则（RRULE格式） |
| series_master_id | string/null | 重复主日程ID，实例此字段有值 |
| create_time | string | 创建时间 (UTC) |
| update_time | string | 更新时间 (UTC) |
| location | object/null | 地点信息 |
| extended_properties | object | 扩展属性，包含所属企业ID |

**注意**:
- 重复日程会返回主日程和多个实例
- 实例的 `series_master_id` 指向主日程ID
- 可通过过滤 `series_master_id` 是否为 None 来区分主日程和实例
| 字段 | 类型 | 说明 |
|------|------|------|
| events | array | 日程列表 |
| events[].id | string | 日程ID |
| events[].summary | string | 日程标题 |
| events[].start.date_time | string | 开始时间 |
| events[].end.date_time | string | 结束时间 |
| events[].is_all_day | boolean | 是否全天事件 |
| events[].organizer | object | 组织者信息 |
| events[].attendees | array | 参与者列表 |

**注意**: 重复日程会返回多个实例（ID格式为 `主ID_数字`），需过滤

---

## 四、错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 300000 | 开发者消息，具体看message |
| InvalidParameter.ParsedValueError | 用户ID格式错误 |

---

## 五、使用示例

### 5.1 完整创建流程

```python
from alibabacloud_dingtalk.calendar_1_0.client import Client as dingtalkcalendar_1_0Client
from alibabacloud_dingtalk.calendar_1_0 import models as dingtalkcalendar__1__0_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

# 1. 获取access_token
# (见1.1节)

# 2. 通过手机号获取unionid
# (见2.1节和2.2节)

# 3. 创建日历事件
config = open_api_models.Config()
config.protocol = 'https'
config.region_id = 'central'
client = dingtalkcalendar_1_0Client(config)

headers = dingtalkcalendar__1__0_models.CreateEventHeaders()
headers.x_acs_dingtalk_access_token = access_token

start = dingtalkcalendar__1__0_models.CreateEventRequestStart(
    date_time='2026-04-30T10:00:00+08:00',
    time_zone='Asia/Shanghai'
)
end = dingtalkcalendar__1__0_models.CreateEventRequestEnd(
    date_time='2026-04-30T11:00:00+08:00',
    time_zone='Asia/Shanghai'
)
reminders = dingtalkcalendar__1__0_models.CreateEventRequestReminders(
    method='dingtalk',
    minutes=30
)

request = dingtalkcalendar__1__0_models.CreateEventRequest(
    summary='合同到期提醒：张三',
    description='派遣员工张三合同将于2026-05-30到期',
    start=start,
    end=end,
    is_all_day=False,
    reminders=[reminders]
)

resp = client.create_event_with_options(unionid, 'primary', request, headers, util_models.RuntimeOptions())
event_id = resp.body.id  # 获取日程ID
```

### 5.2 重复日程示例

创建每周四提醒，直到合同到期前5天：

```python
# 合同到期日: 2026-05-30
# 提前5天: 2026-05-25
recurrence = [
    "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20260525"
]
request.recurrence = recurrence
```
