# 开发说明文档

## 技术架构

### 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.11** | 开发语言 |
| **PyQt6** | GUI 框架，提供窗口管理和绘图能力 |
| **requests** | HTTP 客户端，用于调用 Kimi Code API |
| **PyInstaller** | 打包工具，将 Python 程序打包为独立可执行文件 |

### 整体架构

```
┌──────────────────────────────────────────────────────┐
│                    KimiQuotaWidget                        │
│  ┌────────────────────────────────────────────────┐  │
│  │                    UI 层                            │  │
│  │  ┌─────────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │  paintEvent │  │ 托盘菜单  │  │  动画系统     │  │  │
│  │  │  (自绘UI)   │  │ QSystem  │  │  QTimer驱动   │  │  │
│  │  │             │  │ TrayIcon │  │  呼吸/脉冲    │  │  │
│  │  └─────────────┨  └──────────┨  └──────────────┨  │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │                  数据层                             │  │
│  │  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │ load_creds   │  │ refresh_quota│               │  │
│  │  │ (凭证加载)   │  │ (API请求)    │               │  │
│  │  └──────────────┨  └──────────────┨               │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │                 交互层                              │  │
│  │  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  mousePress  │  │  wheelEvent  │               │  │
│  │  │  (拖拽移动)  │  │  (滚轮缩放)  │               │  │
│  │  └──────────────┨  └──────────────┨               │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## 代码结构详解

### 核心类：`KimiQuotaWidget`

继承自 `QWidget`，是整个程序的核心类，负责 UI 绘制、数据管理和交互响应。

#### 常量定义

| 常量 | 值 | 说明 |
|------|-----|------|
| `BASE_SIZE` | 120 | 窗口基础尺寸（像素） |
| `MIN_SCALE` | 1.0 | 最小缩放比例 |
| `MAX_SCALE` | 3.0 | 最大缩放比例 |
| `SCALE_STEP` | 0.2 | 滚轮缩放步进（20%） |

#### 初始化流程

```
__init__()
├── setWindowFlags() → 无边框、置顶、工具窗口
├── setAttribute() → 透明背景
├── 设置凭证路径 → ~/.kimi/credentials/kimi-code.json
├── 初始化 quota_data 字典
├── 初始化动画变量 (_pulse_intensity, _error_blink)
├── init_ui() → 创建托盘图标和菜单
├── load_credentials() → 读取本地凭证
├── refresh_quota() → 首次获取额度数据
├── refresh_timer → 每5分钟自动刷新
└── animation_timer → 每16ms更新动画（60fps）
     └── font_pulse_timer → 每2ms数值插值（500fps）
```

### UI 绘制系统

所有 UI 元素通过 `paintEvent()` 使用 `QPainter` 自绘实现。

#### 绘制层级（从底到顶）

```
第1层: 阴影圆（半透明黑色，扩大外圈）
第2层: 背景渐变圆（深色护眼渐变）
第3层: 窗口限制进度条（10段等分圆弧，内圈）
第4层: 窗口倒计时弧（外圈单弧，青色）
第5层: 边框（带脉冲动画效果）
第6层: 文字（周用量百分比 + 标题，带呼吸效果）
```

#### 核心方法

**`paintEvent(self, event)`**

主绘制方法，按顺序调用各子绘制方法：

```python
def paintEvent(self, event):
    # 1. 设置抗锯齿渲染
    # 2. 计算中心点和半径
    # 3. 绘制阴影
    # 4. 绘制背景渐变圆
    # 5. 绘制窗口限制进度条（10段圆弧，内圈）
    # 6. 绘制窗口倒计时弧（外圈单弧）
    # 7. 绘制边框（含脉冲效果）
    # 8. 绘制文字（含呼吸效果）
```

**`draw_window_progress(self, painter, center_x, center_y, radius)`**

窗口限制进度条绘制，10段等分圆弧：

- 每段 36 度，绘制 24 度，留 12 度间隔
- 已使用段变色（绿/黄/红，取决于使用率）
- 未使用段为灰色半透明

**`draw_window_countdown(self, painter, center_x, center_y, radius)`**

窗口重置倒计时弧绘制，外圈单弧：

- 灰色底环始终显示
- 青色弧随时间推移顺时针填满
- 颜色从亮青 → 青绿 → 橙黄过渡

**`draw_text(self, painter, center_x, center_y)`**

文字绘制，支持呼吸缩放效果：

- 标题 "Kimi" 在上方（半透明白色）
- 中央百分比数字（白色，粗体，带呼吸缩放）
- 错误状态显示 "ERR" 和提示文字（带闪烁效果）

### 动画系统

使用双 `QTimer` 驱动，主渲染 60fps，字体插值 500fps。

| 动画 | 实现方式 | 效果 |
|------|----------|------|
| **呼吸效果** | 三层正弦波叠加 + smoothstep 缓动 | 字体大小和透明度有机变化 |
| **脉冲边框** | 亮度随 `_pulse_intensity` 变化 | 边框颜色在 180-230 之间变化 |
| **文字缩放** | 缩放因子 `1.0 + smooth * 0.12` | 百分比数字平滑呼吸 |
| **错误闪烁** | `_error_blink` 累加驱动 | 错误文字颜色闪烁 |

#### 三层叠加呼吸算法

```
主波（6秒周期）60% + 微动波（3.5秒周期）25% + 漂移波（10秒周期）15%
→ 混合后过一次 smoothstep 缓动 → 最终平滑值
```

字体呼吸使用独立的 500fps 数值插值定时器，仅当变化超过阈值（0.002）时才触发重绘，避免无效 paint 调用导致的视觉卡顿。

### 数据流

#### 凭证管理

```
凭证文件路径: ~/.kimi/credentials/kimi-code.json
格式:
{
    "access_token": "...",     // API 访问令牌
    "refresh_token": "...",    // 刷新令牌
    "expires_at": 1234567890,  // 过期时间戳
    "scope": "kimi-code",
    "token_type": "Bearer",
    "expires_in": 900
}
```

**安全性**：凭证仅保存在用户主目录，不会随项目文件被提交到 Git。

#### 数据获取

| API 端点 | 方法 | 用途 |
|----------|------|------|
| `/coding/v1/usages` | GET | 获取额度使用数据 |
| `/coding/v1/auth/refresh` | POST | 刷新访问令牌 |

**认证方式**：`Authorization: Bearer {access_token}`

**返回数据结构**：

```json
{
    "usage": {
        "used": "45",
        "limit": "100",
        "remaining": "55",
        "resetTime": "2025-01-01T00:00:00Z"
    },
    "limits": [
        {
            "detail": {
                "used": "2",
                "limit": "100",
                "remaining": "98"
            }
        }
    ],
    "parallel": {
        "limit": "10"
    }
}
```

#### 刷新机制

```
refresh_quota()
├── 检查 access_token 是否存在
│   └── 不存在 → 设置 weekly_used = -1
├── refresh_token_if_needed()
│   └── 检查 expires_at 是否即将过期
│       └── 是 → 调用刷新 API 更新令牌
├── GET /coding/v1/usages (带 Bearer 认证)
├── 解析响应数据 → parse_quota_data()
└── update() → 触发重绘
```

### 交互系统

#### 拖拽移动

通过重写 `mousePressEvent` 和 `mouseMoveEvent` 实现：

```python
def mousePressEvent(self, event):
    # 记录拖拽起始位置
    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

def mouseMoveEvent(self, event):
    # 根据鼠标偏移移动窗口
    self.move(event.globalPosition().toPoint() - self.drag_position)
```

#### 滚轮缩放

通过重写 `wheelEvent` 实现，步进 20%，范围 1.0x ~ 3.0x：

```python
def wheelEvent(self, event):
    delta = event.angleDelta().y()
    if delta > 0:  # 向上滚动 → 放大
        new_scale = min(self._scale_factor + 0.2, 3.0)
    else:           # 向下滚动 → 缩小
        new_scale = max(self._scale_factor - 0.2, 1.0)
    # 应用新缩放
    self._scale_factor = new_scale
    self.apply_scale()  # setFixedSize(size, size)
```

#### 托盘菜单

| 菜单项 | 功能 |
|--------|------|
| 刷新额度 | 立即调用 API 获取最新数据 |
| 重置大小 | 将缩放比例重置为 1.0x |
| 退出 | 关闭程序 |

左键单击托盘图标：切换窗口显示/隐藏。

## 关键设计决策

### 1. 使用 QPainter 自绘而非 QSS

**原因**：需要绘制圆弧进度条、渐变圆、呼吸动画等复杂 UI 效果，QSS 无法满足。

### 2. 10 段等分圆弧设计

**原因**：将窗口限制进度直观地分为 10 段，每段代表 10% 使用率，用户一目了然。

### 3. 缩放因子独立于绘制参数

所有绘制尺寸都乘以 `_scale_factor`，确保缩放时 UI 比例不变形。

### 4. 动画使用双 Timer 驱动

主渲染使用 16ms（60fps）`QTimer` 驱动边框和圆弧动画，字体呼吸使用独立的 2ms（500fps）数值插值定时器，仅当变化超过阈值时才触发重绘，兼顾流畅度和性能。

### 5. 凭证安全保护

- 凭证文件位于用户主目录，不在项目目录内
- `.gitignore` 已配置忽略凭证文件
- Token 仅在内存中存储

## 开发环境搭建

### 前置要求

- Python 3.8+
- pip（Python 包管理器）
- Git

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Handsome-Luo/kimi-quota-widget.git
cd kimi-quota-widget

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python main.py
```

### 依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| PyQt6 | ≥6.5 | GUI 框架 |
| requests | ≥2.28 | HTTP 请求 |

### 打包为可执行文件

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name=kimi-quota-widget main.py
```

输出文件位于 `dist/kimi-quota-widget.exe`。

## 项目文件结构

```
kimi-quota-widget/
├── main.py              # 主程序（全部业务逻辑）
├── requirements.txt     # Python 依赖列表
├── README.md           # 项目说明文档（面向用户）
├── DEVELOPMENT.md      # 开发说明文档（面向开发者）
├── CONTRIBUTING.md     # 贡献指南
├── LICENSE             # MIT 许可证
└── .gitignore         # Git 忽略规则
```

## 常见问题

### Q: 程序启动后看不到窗口？
A: 窗口默认显示在屏幕左上角，请检查是否有托盘图标（系统托盘区），左键单击可切换显示。

### Q: 显示 "ERR" / "检查凭证"？
A: 表示未找到 Kimi Code 凭证或 Token 无效。请确保已安装并登录 Kimi Code CLI。

### Q: 如何更新凭证？
A: 重新登录 Kimi Code CLI 即可更新凭证文件。

### Q: 缩放后 UI 元素错位？
A: 尝试点击托盘菜单中的 "重置大小" 恢复默认缩放。

### Q: API 返回 401 错误？
A: Token 已过期，程序会自动尝试刷新 Token。如果刷新失败，需要重新登录 Kimi Code CLI。
