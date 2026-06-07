<div align="center">

# 🎨 Kimi Code 额度悬浮窗

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.7.0-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![GitHub stars](https://img.shields.io/github/stars/Handsome-Luo/kimi-quota-widget?style=social)](https://github.com/Handsome-Luo/kimi-quota-widget/stargazers)

一个美观的桌面悬浮小部件，实时显示 Kimi Code 会员额度使用情况。

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用说明](#-使用说明) • [贡献指南](#-贡献)

</div>

---

## ✨ 功能特性

| 特性 | 描述 |
|------|------|
| 🎯 **实时显示** | 周用量百分比和窗口限制进度条 |
| 🎨 **精美UI** | 深色护眼配色，10段等分圆弧设计 |
| 🔄 **自动刷新** | 每5分钟自动更新额度数据 |
| 🖱️ **交互功能** | 拖拽移动、滚轮缩放、托盘菜单 |
| 💫 **动态效果** | 三层叠加呼吸动画、脉冲效果、字体平滑过渡 |
| 📱 **跨平台** | 基于PyQt6开发，支持Windows |

## 📸 预览

![Widget Preview](https://via.placeholder.com/400x300/1e2824/ffffff?text=Kimi+Quota+Widget+Preview)

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- 已安装并登录 [Kimi Code CLI](https://kimi.com/)

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/Handsome-Luo/kimi-quota-widget/releases) 页面下载最新的 `kimi-quota-widget.exe`，直接运行即可！

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/Handsome-Luo/kimi-quota-widget.git
cd kimi-quota-widget

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 📖 使用说明

### 基础操作

| 操作 | 说明 |
|------|------|
| **拖拽移动** | 鼠标左键按住悬浮窗，拖动到任意位置 |
| **滚轮缩放** | 鼠标滚轮可调整窗口大小（1-3倍） |
| **托盘图标** | 右键点击系统托盘图标查看菜单 |
| **隐藏/显示** | 左键单击托盘图标可切换窗口可见性 |

### 托盘菜单功能

- **刷新额度** - 立即获取最新额度数据
- **重置大小** - 恢复到默认尺寸
- **退出** - 关闭程序

### UI 说明

| 元素 | 说明 |
|------|------|
| 中心白色数字 | 周用量百分比 |
| 内圈彩色圆弧 | 窗口限制使用进度（10段等分） |
| 外圈青色圆弧 | 窗口重置倒计时进度 |
| 🟢 绿色 | 正常（<60%） |
| 🟡 黄色 | 警告（60%-80%） |
| 🔴 红色 | 危险（>80%） |

## 🛠️ 技术栈

- **GUI 框架** - [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- **网络请求** - [requests](https://requests.readthedocs.io/)
- **打包工具** - [PyInstaller](https://www.pyinstaller.org/)

## 📦 项目结构

```
kimi-quota-widget/
├── main.py              # 主程序文件
├── requirements.txt     # Python 依赖列表
├── README.md           # 项目说明文档（本文件）
├── DEVELOPMENT.md      # 开发说明文档
├── LICENSE             # MIT 许可证
├── .gitignore         # Git 忽略规则
└── CONTRIBUTING.md    # 贡献指南
```

## 🔧 开发指南

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/Handsome-Luo/kimi-quota-widget.git
cd kimi-quota-widget

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python main.py
```

### 打包发布

```bash
# 使用 PyInstaller 打包
pyinstaller --onefile --windowed --name=kimi-quota-widget main.py --distpath=dist
```

打包后的可执行文件位于 `dist/` 目录。

## 📄 API 说明

程序通过以下 API 获取 Kimi Code 额度数据：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/coding/v1/usages` | GET | 获取用量信息 |

## 🔒 安全说明

- ✅ 凭证文件位于用户主目录 `~/.kimi/credentials/kimi-code.json`
- ✅ 凭证不会被提交到 Git 仓库
- ✅ 使用 HTTPS 加密通信
- ✅ Token 仅在内存中存储，程序退出后清除
- ✅ 错误信息脱敏处理，不泄露敏感内容

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献指南。

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

- 提交 [Issue](https://github.com/Handsome-Luo/kimi-quota-widget/issues) 反馈问题或建议
- 项目主页：[https://github.com/Handsome-Luo/kimi-quota-widget](https://github.com/Handsome-Luo/kimi-quota-widget)

## 🙏 致谢

- 感谢 [Kimi Code](https://kimi.com/) 提供的 API 服务
- 感谢 [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) 提供的 GUI 框架
- 感谢所有为本项目做出贡献的开发者！

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

Made with ❤️ by Kimi Quota Widget Contributors

</div>
