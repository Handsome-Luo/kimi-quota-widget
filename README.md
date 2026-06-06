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
| 💫 **动态效果** | 呼吸动画、脉冲效果 |
| 📱 **跨平台** | 基于PyQt6开发，支持Windows |

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- 已安装并登录 [Kimi Code CLI](https://kimi.com/)

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/Handsome-Luo/kimi-quota-widget/releases) 页面下载最新的 `kimi-quota-widget.exe`，直接运行即可！

### 方式二：从源码运行

```bash
git clone https://github.com/Handsome-Luo/kimi-quota-widget.git
cd kimi-quota-widget
pip install -r requirements.txt
python main.py
```

## 📖 使用说明

| 操作 | 说明 |
|------|------|
| **拖拽移动** | 鼠标左键按住悬浮窗，拖动到任意位置 |
| **滚轮缩放** | 鼠标滚轮可调整窗口大小（1-3倍） |
| **托盘图标** | 右键点击系统托盘图标查看菜单 |
| **隐藏/显示** | 左键单击托盘图标可切换窗口可见性 |

### UI 说明

| 元素 | 说明 |
|------|------|
| 中心白色数字 | 周用量百分比 |
| 外圈彩色圆弧 | 窗口限制使用进度（10段等分） |
| 🟢 绿色 | 正常（<60%） |
| 🟡 黄色 | 警告（60%-80%） |
| 🔴 红色 | 危险（>80%） |

## 🔒 安全说明

- ✅ 凭证文件位于用户主目录，不会被提交到 Git 仓库
- ✅ 使用 HTTPS 加密通信
- ✅ Token 仅在内存中存储
- ✅ 错误信息脱敏处理

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">Made with ❤️</div>