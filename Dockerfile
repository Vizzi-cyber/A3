# 后端构建阶段
FROM python:3.11-slim as backend

WORKDIR /app/backend

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 前端构建阶段
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# 安装依赖
COPY frontend/package.json .
RUN npm install

# 复制前端代码并构建
COPY frontend/ .
RUN npm run build

# Nginx 服务阶段（可选，用于生产环境托管前端）
FROM nginx:alpine as frontend

# 复制前端构建产物
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
