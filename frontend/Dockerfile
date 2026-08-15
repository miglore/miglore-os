# Miglore OS Frontend — 开发环境容器镜像 (multi-stage)
# Stage 1: Node 构建 → Stage 2: Nginx 托管静态产物
# 不使用 npm dev server 作为生产容器

# ---- Stage 1: build ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

# ---- Stage 2: serve ----
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
