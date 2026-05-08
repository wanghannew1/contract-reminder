# 合同到期钉钉提醒系统

基于 Flask 的合同到期提醒系统，支持 CSV 合同数据导入和钉钉日历提醒。

## 功能特性

- 用户认证（手机号+密码登录）
- CSV 合同数据导入（支持 GBK/UTF-8 编码）
- 合同列表管理（搜索、筛选、分页）
- 钉钉日历日程创建（支持每周/每日提醒）
- 批量创建/删除日程
- 系统配置（钉钉应用参数）
- 用户管理（超级管理员）

## 系统要求

- Python 3.10+
- SQLite 3
- Chrome/Edge 最新版浏览器

## 安装步骤

### 1. 克隆/复制项目

```bash
cd /home/ubuntu/coding/contract_manager/contract-reminder
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# Flask
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development  # 或 production

# Database
DATABASE_URL=sqlite:///contract_reminder.db

# DingTalk（也可通过后台页面配置）
DINGTALK_APPKEY=your_dingtalk_appkey
DINGTALK_APPSECRET=your_dingtalk_appsecret

# Upload
MAX_CONTENT_LENGTH=52428800  # 50MB

# Session
SESSION_LIFETIME_DAYS=7
```

### 5. 初始化数据库

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. 创建超级管理员账号

```bash
python -c "
from app import create_app, db
from app.models.user import User

app = create_app()
app.app_context().push()

admin = User(
    name='系统管理员',
    phone='13800000000',
    is_active=True,
    is_superadmin=True,
    unionid='your_dingtalk_unionid'  # 可选
)
admin.set_password('Admin@123456')
db.session.add(admin)
db.session.commit()
print('超级管理员创建成功！')
"
```

### 7. 启动应用

**开发环境：**
```bash
python run.py
```

**生产环境（使用 gunicorn）：**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 8. 访问系统

打开浏览器访问：http://localhost:5000

默认账号：
- 手机号：`13800000000`
- 密码：`Admin@123456`

## 使用说明

### 首次使用配置

1. 以超级管理员登录
2. 进入「系统设置」页面
3. 配置钉钉应用参数（AppKey、AppSecret）
4. 点击「测试连接」确认配置正确

### 导入合同数据

1. 进入「合同管理」→「导入」页面
2. 上传从薪福通导出的 CSV 文件
3. 系统自动解析并显示导入结果
4. 支持查看失败明细

### 创建日程提醒

1. 进入「合同列表」
2. 勾选需要提醒的合同
3. 点击「批量创建提醒」
4. 配置提醒参数：
   - 提前提醒天数（默认60天）
   - 重复频率（每周/每日）
   - 提醒星期（仅每周时）
   - 提醒时间
5. 点击确认创建

### 管理日程

- 进入「日程管理」查看已创建日程
- 支持单个/批量删除
- 删除可选择仅本地删除或同步删除钉钉端

## 目录结构

```
contract-reminder/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── config.py             # 配置
│   ├── models/               # 数据模型
│   │   ├── user.py           # 用户模型
│   │   ├── contract.py       # 合同模型
│   │   ├── calendar_event.py # 日程事件模型
│   │   ├── system_config.py  # 系统配置
│   │   └── import_log.py     # 导入日志
│   ├── routes/               # 路由
│   │   ├── auth.py           # 认证
│   │   ├── contract.py       # 合同管理
│   │   ├── calendar.py       # 日程管理
│   │   └── admin.py          # 系统管理
│   ├── services/             # 业务服务
│   │   ├── dingtalk.py       # 钉钉API
│   │   └── csv_importer.py   # CSV导入
│   └── utils/                # 工具
│       ├── helpers.py        # 辅助函数
│       └── decorators.py     # 装饰器
├── templates/                # HTML模板
├── static/                   # 静态文件
├── tests/                    # 测试
├── scripts/                  # 脚本
├── uploads/                 # 上传文件目录
├── requirements.txt         # 依赖
├── .env.example              # 环境变量示例
└── run.py                    # 入口文件
```

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_auth.py -v

# 查看测试覆盖率
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html
```

## 常见问题

### 1. 钉钉连接失败

- 确认 AppKey 和 AppSecret 正确
- 确认钉钉应用已开通日历权限
- 检查服务器网络能否访问钉钉 API

### 2. CSV 导入失败

- 确认文件编码（支持 GBK/UTF-8/UTF-8-BOM）
- 确认文件格式为 CSV（逗号分隔）
- 检查必填列是否存在

### 3. 日程创建失败

- 确认用户已授权应用访问日历
- 检查 unionId 是否正确

## 生产部署

### 使用 Docker（可选）

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Nginx + Gunicorn

```nginx
upstream app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/contract-reminder/static;
        expires 30d;
    }
}
```

## 许可证

MIT License
