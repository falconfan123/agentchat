# CLAUDE.md - AgentChat 项目指南

## 项目概述

AgentChat 是一个基于大语言模型的现代化智能对话系统，支持多 Agent 协作、知识库检索、工具调用等功能。

## 常用命令

```bash
# Docker 服务管理
cd docker
docker-compose up --build -d    # 启动所有服务
docker-compose restart          # 重启所有服务
docker-compose logs -f          # 查看日志

# 访问地址
# 前端: http://localhost:8090
# 后端: http://localhost:7860
# API文档: http://localhost:7860/docs
# MinIO控制台: http://localhost:9001
```

## 测试账号

- **用户名**: testuser
- **密码**: test123

首次登录后，系统会自动创建测试用户。

## 偏好设置

- **Docker 运行**: 使用 OrbStack 而非 Docker Desktop
- **端口冲突处理**: 当遇到端口冲突时，使用新增端口而非杀掉原有进程
- **网页修改测试**: 修改前端页面后，必须使用 chrome-mcp 自行测试验证，确保功能正常。如测试不通过，需分析原因并解决后再提交

## 自动提交规则

当完成任务时，需要：
1. 自动创建 git commit
2. 自动创建 Pull Request 推送到远程仓库

提交信息格式：
```
feat/fix/docs: 简短描述

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
