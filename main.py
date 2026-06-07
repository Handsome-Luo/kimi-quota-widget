'''
Kimi Code 额度悬浮窗
A beautiful desktop widget that displays Kimi Code quota usage in real-time.

MIT License
Copyright (c) 2025 Kimi Quota Widget Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys
import json
import time
import os
import math
from datetime import datetime, timezone

import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QSystemTrayIcon,
    QMessageBox, QProgressBar, QFrame
)
from PyQt6.QtGui import QIcon, QFont, QAction, QColor, QPainter, QPixmap, QLinearGradient, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF


class KimiQuotaWidget(QWidget):
    # 基础尺寸常量
    BASE_SIZE = 120  # 基础尺寸放大1.5倍 (80 * 1.5)
    MIN_SCALE = 1.0   # 最小缩放比例
    MAX_SCALE = 3.0   # 最大缩放比例
    SCALE_STEP = 0.2  # 缩放步进 20%
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint |
                          Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.credential_path = os.path.join(
            os.path.expanduser("~"), ".kimi", "credentials", "kimi-code.json"
        )
        
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0
        self._last_credential_mtime = 0  # 记录凭证文件最后修改时间
        
        self.quota_data = {
            'weekly_used': 0,
            'weekly_limit': 100,
            'weekly_remaining': 100,
            'weekly_reset_time': None,
            'window_used': 0,
            'window_limit': 100,
            'window_remaining': 100,
            'window_reset_time': None,
            'parallel_limit': 10
        }
        
        self._pulse_intensity = 0
        self._error_blink = 0
        self._scale_factor = 1.0  # 当前缩放比例
        self._is_error_state = False  # 是否处于错误状态
        
        self.init_ui()
        self.load_credentials()
        # 记录初始凭证文件修改时间
        if os.path.exists(self.credential_path):
            self._last_credential_mtime = os.path.getmtime(self.credential_path)
        self.refresh_quota()
        
        # 正常刷新定时器（5分钟一次）
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_quota)
        self.refresh_timer.start(5 * 60 * 1000)
        
        # 错误状态下的快速检测定时器（30秒一次）
        self.error_check_timer = QTimer(self)
        self.error_check_timer.timeout.connect(self.check_credential_update)
        
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(8)
        
        self.drag_position = QPoint()
    
    def update_animations(self):
        self._pulse_intensity = (math.sin(time.time() * 1.5) + 1) / 2
        self._error_blink += 0.15
        if self._error_blink > math.pi * 2:
            self._error_blink = 0
        self.update()
    
    def init_ui(self):
        self.apply_scale()
        
        self.tray_icon = QSystemTrayIcon(QIcon())
        self.tray_icon.setIcon(QIcon(self.create_icon()))
        
        tray_menu = QMenu()
        refresh_action = QAction("刷新额度", self)
        refresh_action.setFont(QFont("Segoe UI", 9))
        refresh_action.triggered.connect(self.refresh_quota)
        tray_menu.addAction(refresh_action)
        
        reset_scale_action = QAction("重置大小", self)
        reset_scale_action.setFont(QFont("Segoe UI", 9))
        reset_scale_action.triggered.connect(self.reset_scale)
        tray_menu.addAction(reset_scale_action)
        
        quit_action = QAction("退出", self)
        quit_action.setFont(QFont("Segoe UI", 9))
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_click)
    
    def apply_scale(self):
        """应用缩放比例"""
        size = int(self.BASE_SIZE * self._scale_factor)
        self.setFixedSize(size, size)
    
    def reset_scale(self):
        """重置缩放比例"""
        self._scale_factor = 1.0
        self.apply_scale()
    
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 缩放窗口"""
        delta = event.angleDelta().y()
        if delta > 0:
            # 向上滚动 - 放大
            new_scale = min(self._scale_factor + self.SCALE_STEP, self.MAX_SCALE)
        else:
            # 向下滚动 - 缩小
            new_scale = max(self._scale_factor - self.SCALE_STEP, self.MIN_SCALE)
        
        if new_scale != self._scale_factor:
            self._scale_factor = new_scale
            self.apply_scale()
            self.update()
        
        event.accept()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        # 给外圆留出足够空间，避免被截断
        radius = min(self.width(), self.height()) // 2 - int(12 * self._scale_factor)
        
        # 绘制阴影
        shadow_radius = radius + int(8 * self._scale_factor)
        shadow_color = QColor(0, 0, 0, 35)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - shadow_radius, center_y - shadow_radius, 
                            shadow_radius * 2, shadow_radius * 2)
        
        # 绘制背景渐变
        gradient = QLinearGradient(center_x - radius, center_y - radius, 
                                   center_x + radius, center_y + radius)
        gradient.setColorAt(0, QColor(40, 50, 45))
        gradient.setColorAt(0.5, QColor(25, 35, 32))
        gradient.setColorAt(1, QColor(18, 25, 24))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, 
                            radius * 2, radius * 2)
        
        # 绘制窗口限制进度条（10段）
        self.draw_window_progress(painter, center_x, center_y, radius)
        
        # 绘制边框
        border_color = QColor(79, 172, 142, int(190 + self._pulse_intensity * 35))
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, 
                            radius * 2, radius * 2)
        
        # 绘制文字
        self.draw_text(painter, center_x, center_y)
    
    def draw_window_progress(self, painter, center_x, center_y, radius):
        """绘制窗口限制进度条（10等分圆弧）"""
        if self.quota_data['weekly_used'] < 0:
            return
        
        window_percentage = min(int((self.quota_data['window_used'] / self.quota_data['window_limit']) * 100), 100)
        
        # 进度条参数
        progress_offset = int(10 * self._scale_factor)
        segment_width = max(4, int(6 * self._scale_factor))  # 统一宽度
        progress_radius = radius - progress_offset
        
        # 判断颜色
        if window_percentage > 80:
            active_color = QColor(239, 108, 108)
        elif window_percentage > 60:
            active_color = QColor(251, 191, 36)
        else:
            active_color = QColor(79, 172, 142)
        
        # 绘制所有10个圆弧段 - 确保每个段都有明显间隔
        for i in range(10):
            # 每段36度，留12度超大间隔，确保非常清晰
            start_angle = 90 - i * 36
            span_angle = -24  # 段更短，间隔超大，视觉超清晰
            
            # 判断该段是否被使用
            if window_percentage >= (i + 1) * 10:
                # 已使用段
                segment_color = active_color
            else:
                # 未使用段
                segment_color = QColor(100, 110, 105, 150)
            
            painter.setPen(QPen(segment_color, segment_width))
            painter.drawArc(center_x - progress_radius, 
                           center_y - progress_radius, 
                           progress_radius * 2, 
                           progress_radius * 2, 
                           start_angle * 16, span_angle * 16)
    
    def draw_text(self, painter, center_x, center_y):
        """绘制文字 - 周用量用白色字体，窗口限制用进度条"""
        # 根据缩放比例调整字体大小
        title_font_size = max(6, int(8 * self._scale_factor))
        main_font_size = max(14, int(22 * self._scale_factor))
        
        # 绘制标题
        title_opacity = int(170 + self._pulse_intensity * 20)
        painter.setPen(QColor(185, 205, 195, title_opacity))
        painter.setFont(QFont("Segoe UI", title_font_size, QFont.Weight.Light))
        
        title_width = int(50 * self._scale_factor)
        title_height = int(14 * self._scale_factor)
        title_y_offset = int(-30 * self._scale_factor)
        
        painter.drawText(center_x - title_width // 2, center_y + title_y_offset, 
                         title_width, title_height, 
                         Qt.AlignmentFlag.AlignCenter, "Kimi")
        
        if self.quota_data['weekly_used'] < 0:
            # 错误状态 - 根据错误码显示不同提示
            blink_intensity = (math.sin(self._error_blink * 6) + 1) / 2
            error_color = QColor(int(239 * blink_intensity + 140 * (1 - blink_intensity)), 
                                int(108 * blink_intensity + 100 * (1 - blink_intensity)), 
                                int(108 * blink_intensity + 100 * (1 - blink_intensity)))
            
            painter.setPen(error_color)
            painter.setFont(QFont("Segoe UI", int(16 * self._scale_factor), QFont.Weight.Bold))
            
            err_width = int(40 * self._scale_factor)
            err_height = int(24 * self._scale_factor)
            painter.drawText(center_x - err_width // 2, center_y - err_height // 2, 
                             err_width, err_height, 
                             Qt.AlignmentFlag.AlignCenter, "ERR")
            
            painter.setPen(QColor(150, 170, 160))
            painter.setFont(QFont("Segoe UI", max(5, int(6 * self._scale_factor)), QFont.Weight.Light))
            
            hint_width = int(50 * self._scale_factor)
            hint_height = int(12 * self._scale_factor)
            hint_y_offset = int(14 * self._scale_factor)
            
            # 区分错误类型显示不同提示
            if self.quota_data['weekly_used'] == -1:
                hint_text = "未登录"
            elif self.quota_data['weekly_used'] == -2:
                hint_text = "凭证无效"
            elif self.quota_data['weekly_used'] == -3:
                hint_text = "重新登录"
            elif self.quota_data['weekly_used'] == -4:
                hint_text = "网络错误"
            else:
                hint_text = "检查凭证"
            
            painter.drawText(center_x - hint_width // 2, center_y + hint_y_offset, 
                             hint_width, hint_height, 
                             Qt.AlignmentFlag.AlignCenter, hint_text)
            return
        
        # 计算周用量百分比
        percentage = min(int((self.quota_data['weekly_used'] / self.quota_data['weekly_limit']) * 100), 100)
        
        # 周用量 - 使用白色字体
        text_color = QColor(255, 255, 255)
        
        # 呼吸缩放效果
        scale_factor = 1.0 + self._pulse_intensity * 0.04
        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale_factor, scale_factor)
        
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", main_font_size, QFont.Weight.Bold))
        
        # 使用更大的绘制区域确保文字不被截断
        text_width = int(60 * self._scale_factor)
        text_height = int(30 * self._scale_factor)
        painter.drawText(-text_width // 2, -text_height // 2 + int(2 * self._scale_factor), 
                         text_width, text_height, 
                         Qt.AlignmentFlag.AlignCenter, f"{percentage}%")
        
        painter.restore()
    
    def create_icon(self):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = 12
        center_y = 12
        radius = 10
        
        gradient = QLinearGradient(0, 0, 24, 24)
        gradient.setColorAt(0, QColor(35, 45, 42))
        gradient.setColorAt(1, QColor(22, 30, 28))
        painter.setBrush(gradient)
        painter.drawEllipse(center_x - radius, center_y - radius, 
                            radius * 2, radius * 2)
        
        painter.setPen(QColor(79, 172, 142))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, 
                            radius * 2, radius * 2)
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")
        
        painter.end()
        return pixmap
    
    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def load_credentials(self):
        try:
            if os.path.exists(self.credential_path):
                with open(self.credential_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.expires_at = data.get('expires_at', 0)
                # 同步更新文件修改时间记录
                self._last_credential_mtime = os.path.getmtime(self.credential_path)
        except Exception as e:
            print(f"Failed to load credentials: {e}")
    
    def refresh_token_if_needed(self):
        if self.expires_at > 0 and time.time() > self.expires_at - 60:
            if self.refresh_token:
                try:
                    response = requests.post(
                        "https://api.kimi.com/coding/v1/auth/refresh",
                        json={"refresh_token": self.refresh_token},
                        timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        self.access_token = data.get('access_token')
                        self.expires_at = time.time() + data.get('expires_in', 900)
                        
                        with open(self.credential_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                'access_token': self.access_token,
                                'refresh_token': self.refresh_token,
                                'expires_at': self.expires_at,
                                'scope': 'kimi-code',
                                'token_type': 'Bearer',
                                'expires_in': 900
                            }, f)
                        return True
                    else:
                        print(f"Refresh API returned {response.status_code}, refresh endpoint may be deprecated")
                except requests.RequestException as e:
                    print(f"Network error during token refresh: {e}")
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
        return False
    
    def check_credential_update(self):
        """检查凭证文件是否有更新（外部登录更新），如有则重新加载并刷新额度"""
        try:
            if os.path.exists(self.credential_path):
                current_mtime = os.path.getmtime(self.credential_path)
                if current_mtime != self._last_credential_mtime:
                    print("检测到凭证文件已更新，重新加载...")
                    self.load_credentials()  # 内部会更新 _last_credential_mtime
                    self.refresh_quota()
        except Exception as e:
            print(f"检查凭证更新失败: {e}")
    
    def refresh_quota(self):
        # 每次刷新前重新加载凭证（确保外部登录更新能被捕获）
        self.load_credentials()
        
        if not self.access_token:
            self.quota_data['weekly_used'] = -1  # 无凭证
            self._enter_error_state()
            return
        
        refresh_success = self.refresh_token_if_needed()
        
        try:
            response = requests.get(
                "https://api.kimi.com/coding/v1/usages",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.parse_quota_data(data)
                self._exit_error_state()
                self.update()
            elif response.status_code == 401:
                if refresh_success:
                    self.quota_data['weekly_used'] = -2  # Token无效
                else:
                    self.quota_data['weekly_used'] = -3  # Token过期且无法刷新
                self._enter_error_state()
                self.update()
        except requests.RequestException as e:
            print(f"Network error fetching quota: {e}")
            self.quota_data['weekly_used'] = -4  # 网络错误
            self._enter_error_state()
            self.update()
        except Exception as e:
            print(f"Failed to fetch quota: {e}")
    
    def _enter_error_state(self):
        """进入错误状态：启动快速检测定时器"""
        if not self._is_error_state:
            self._is_error_state = True
            self.error_check_timer.start(30 * 1000)  # 每30秒检查一次凭证更新
            print("进入错误状态，启动快速凭证检测（每30秒）")
    
    def _exit_error_state(self):
        """退出错误状态：停止快速检测定时器"""
        if self._is_error_state:
            self._is_error_state = False
            self.error_check_timer.stop()
            print("恢复正常状态，停止快速凭证检测")
    
    def parse_quota_data(self, data):
        usage = data.get('usage', {})
        self.quota_data['weekly_used'] = int(usage.get('used', '0'))
        self.quota_data['weekly_limit'] = int(usage.get('limit', '100'))
        self.quota_data['weekly_remaining'] = int(usage.get('remaining', '100'))
        
        reset_time_str = usage.get('resetTime')
        if reset_time_str:
            self.quota_data['weekly_reset_time'] = datetime.fromisoformat(reset_time_str.replace('Z', '+00:00'))
        
        limits = data.get('limits', [])
        if limits:
            window_detail = limits[0].get('detail', {})
            self.quota_data['window_used'] = int(window_detail.get('used', '0'))
            self.quota_data['window_limit'] = int(window_detail.get('limit', '100'))
            self.quota_data['window_remaining'] = int(window_detail.get('remaining', '100'))
        
        self.quota_data['parallel_limit'] = int(data.get('parallel', {}).get('limit', '10'))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    widget = KimiQuotaWidget()
    widget.show()
    
    sys.exit(app.exec())
