# 公益账号分享平台

这是一个用于分享公益账号的网站平台，包含前端和后端实现。

## 项目结构

```
gongyizhh/
├── backend/           # Flask后端
│   └── app.py        # 后端主程序
├── frontend/         # React前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/      # 页面
│   │   └── App.js      # 主应用
│   └── package.json
└── requirements.txt  # Python依赖
```

## 安装说明

### 后端设置

1. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行后端：
```bash
cd backend
python app.py
```

### 前端设置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 运行前端：
```bash
npm start
```

## 功能特性

- 浏览公益账号信息
- 发布新的公益账号
- 管理员后台管理
- 响应式设计

## 技术栈

- 后端：Flask + SQLAlchemy
- 前端：React + Ant Design
- 数据库：SQLite
