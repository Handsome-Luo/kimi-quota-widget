# 贡献指南

感谢你有兴趣为 Kimi Code 额度悬浮窗项目做出贡献！

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [Pull Request 指南](#pull-request-指南)
- [代码规范](#代码规范)
- [问题反馈](#问题反馈)

## 行为准则

- 尊重其他贡献者
- 保持友善和专业
- 接受建设性批评
- 关注项目的最佳利益

## 如何贡献

### 🐛 报告 Bug

1. 先搜索 [Issues](https://github.com/Handsome-Luo/kimi-quota-widget/issues)，确认是否已有人报告过
2. 如未找到，创建新的 Issue，包含：
   - 清晰的标题
   - 复现步骤
   - 预期行为
   - 实际行为
   - 截图（如适用）
   - 环境信息（操作系统、Python 版本等）

### ✨ 请求新功能

1. 先搜索 [Issues](https://github.com/Handsome-Luo/kimi-quota-widget/issues)，确认是否已有人提出过
2. 创建新的 Issue，描述：
   - 功能描述
   - 使用场景
   - 实现建议（可选）

### 💻 贡献代码

请按照下方的 [开发流程](#开发流程) 进行。

## 开发流程

### 1. Fork 仓库

点击项目主页右上角的 "Fork" 按钮，将仓库 fork 到你的 GitHub 账号下。

### 2. 克隆仓库

```bash
# 克隆你的 fork
git clone https://github.com/Handsome-Luo/kimi-quota-widget.git
cd kimi-quota-widget

# 添加上游仓库
git remote add upstream https://github.com/original-username/kimi-quota-widget.git
```

### 3. 创建分支

```bash
# 从 main 分支创建新分支
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/your-feature-name
# 或创建修复分支
git checkout -b fix/your-fix-name
```

### 4. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 进行开发

- 遵循项目的代码规范
- 确保代码可以正常运行
- 测试你的修改

### 6. 提交更改

```bash
# 添加修改的文件
git add .

# 提交，使用清晰的提交信息
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复问题描述"
```

### 7. 推送并创建 PR

```bash
# 推送到你的 fork
git push origin feature/your-feature-name

# 然后在 GitHub 上创建 Pull Request
```

## Pull Request 指南

### PR 标题格式

使用清晰的标题，包含类型：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 建筑/工具相关

示例：
- `feat: 添加深色主题支持`
- `fix: 修复刷新时崩溃的问题`

### PR 内容

请在 PR 中包含：

1. 描述变更的内容
2. 相关的 Issue 编号（如 `Closes #123`）
3. 测试说明
4. 截图（如 UI 有变更）

### 代码审查

- PR 创建后，等待维护者审查
- 根据反馈进行修改
- 合并后可以删除你的分支

## 代码规范

### Python 代码

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 风格
- 使用有意义的变量和函数名
- 添加必要的注释
- 保持函数简洁，单一职责

### Git 提交信息

- 使用现在时态（"Add feature" 而不是 "Added feature"）
- 第一行不超过 72 字符
- 详细说明可在第二行开始

## 问题反馈

如有任何问题，请通过以下方式联系：

- 提交 [Issue](https://github.com/Handsome-Luo/kimi-quota-widget/issues)

---

再次感谢你的贡献！🎉
