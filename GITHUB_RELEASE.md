# GitHub 发布指南

## 步骤 1: 创建 GitHub 仓库
1. 登录 GitHub，点击 + 按钮选择 New repository
2. 仓库名: kimi-quota-widget
3. 选择 Public，不要勾选任何初始化选项
4. 点击 Create repository

## 步骤 2: 推送代码
```bash
git init
git add .
git commit -m "Initial commit: Kimi Code 额度悬浮窗"
git remote add origin https://github.com/Handsome-Luo/kimi-quota-widget.git
git branch -M main
git push -u origin main
```

## 步骤 3: 创建 Release
1. 在 GitHub 仓库页面，点击 Releases
2. 点击 Draft a new release
3. 标签: v1.0.0，标题: Version 1.0.0
4. 添加说明并上传 dist/kimi-quota-widget.exe
5. 点击 Publish release

## 推荐 Topics
kimi, kimi-code, pyqt6, widget, quota, python, desktop-app