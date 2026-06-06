"""
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
"""

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
    BASE_SIZE = 120
    MIN_SCALE = 1.0
    MAX_SCALE = 3.0
    SCALE_STEP = 0.2
    
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
        self._scale_factor = 1.0
        
        self.init_ui()
        self.load_credentials()
        self.refresh_quota()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_quota)
        self.refresh_timer.start(5 * 60 * 1000)
        
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
        refresh_action.triggered.connect(self.refresh_quota)
        tray_menu.addAction(refresh_action)
        reset_scale_action = QAction("重置大小", self)
        reset_scale_action.triggered.connect(self.reset_scale)
        tray_menu.addAction(reset_scale_action)
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_click)
    
    def apply_scale(self):
        size = int(self.BASE_SIZE * self._scale_factor)
        self.setFixedSize(size, size)
    
    def reset_scale(self):
        self._scale_factor = 1.0
        self.apply_scale()
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            new_scale = min(self._scale_factor + self.SCALE_STEP, self.MAX_SCALE)
        else:
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
        radius = min(self.width(), self.height()) // 2 - int(12 * self._scale_factor)
        
        shadow_radius = radius + int(8 * self._scale_factor)
        shadow_color = QColor(0, 0, 0, 35)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - shadow_radius, center_y - shadow_radius, shadow_radius * 2, shadow_radius * 2)
        
        gradient = QLinearGradient(center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        gradient.setColorAt(0, QColor(40, 50, 45))
        gradient.setColorAt(0.5, QColor(25, 35, 32))
        gradient.setColorAt(1, QColor(18, 25, 24))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        self.draw_window_progress(painter, center_x, center_y, radius)
        
        border_color = QColor(79, 172, 142, int(190 + self._pulse_intensity * 35))
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        self.draw_text(painter, center_x, center_y)
    
    def draw_window_progress(self, painter, center_x, center_y, radius):
        if self.quota_data['weekly_used'] < 0:
            return
        window_percentage = min(int((self.quota_data['window_used'] / self.quota_data['window_limit']) * 100), 100)
        progress_offset = int(10 * self._scale_factor)
        segment_width = max(4, int(6 * self._scale_factor))
        progress_radius = radius - progress_offset
        if window_percentage > 80:
            active_color = QColor(239, 108, 108)
        elif window_percentage > 60:
            active_color = QColor(251, 191, 36)
        else:
            active_color = QColor(79, 172, 142)
        for i in range(10):
            start_angle = 90 - i * 36
            span_angle = -24
            if window_percentage >= (i + 1) * 10:
                segment_color = active_color
            else:
                segment_color = QColor(100, 110, 105, 150)
            painter.setPen(QPen(segment_color, segment_width))
            painter.drawArc(center_x - progress_radius, center_y - progress_radius, progress_radius * 2, progress_radius * 2, start_angle * 16, span_angle * 16)
    
    def draw_text(self, painter, center_x, center_y):
        title_font_size = max(6, int(8 * self._scale_factor))
        main_font_size = max(14, int(22 * self._scale_factor))
        title_opacity = int(170 + self._pulse_intensity * 20)
        painter.setPen(QColor(185, 205, 195, title_opacity))
        painter.setFont(QFont("Segoe UI", title_font_size, QFont.Weight.Light))
        title_width = int(50 * self._scale_factor)
        title_height = int(14 * self._scale_factor)
        title_y_offset = int(-30 * self._scale_factor)
        painter.drawText(center_x - title_width // 2, center_y + title_y_offset, title_width, title_height, Qt.AlignmentFlag.AlignCenter, "Kimi")
        
        if self.quota_data['weekly_used'] < 0:
            blink_intensity = (math.sin(self._error_blink * 6) + 1) / 2
            error_color = QColor(int(239 * blink_intensity + 140 * (1 - blink_intensity)), int(108 * blink_intensity + 100 * (1 - blink_intensity)), int(108 * blink_intensity + 100 * (1 - blink_intensity)))
            painter.setPen(error_color)
            painter.setFont(QFont("Segoe UI", int(16 * self._scale_factor), QFont.Weight.Bold))
            err_width = int(40 * self._scale_factor)
            err_height = int(24 * self._scale_factor)
            painter.drawText(center_x - err_width // 2, center_y - err_height // 2, err_width, err_height, Qt.AlignmentFlag.AlignCenter, "ERR")
            painter.setPen(QColor(150, 170, 160))
            painter.setFont(QFont("Segoe UI", max(5, int(6 * self._scale_factor)), QFont.Weight.Light))
            hint_width = int(40 * self._scale_factor)
            hint_height = int(12 * self._scale_factor)
            hint_y_offset = int(14 * self._scale_factor)
            painter.drawText(center_x - hint_width // 2, center_y + hint_y_offset, hint_width, hint_height, Qt.AlignmentFlag.AlignCenter, "检查凭证")
            return
        
        percentage = min(int((self.quota_data['weekly_used'] / self.quota_data['weekly_limit']) * 100), 100)
        text_color = QColor(255, 255, 255)
        scale_factor = 1.0 + self._pulse_intensity * 0.04
        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale_factor, scale_factor)
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", main_font_size, QFont.Weight.Bold))
        text_width = int(60 * self._scale_factor)
        text_height = int(30 * self._scale_factor)
        painter.drawText(-text_width // 2, -text_height // 2 + int(2 * self._scale_factor), text_width, text_height, Qt.AlignmentFlag.AlignCenter, f"{percentage}%")
        painter.restore()
    
    def create_icon(self):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y, radius = 12, 12, 10
        gradient = QLinearGradient(0, 0, 24, 24)
        gradient.setColorAt(0, QColor(35, 45, 42))
        gradient.setColorAt(1, QColor(22, 30, 28))
        painter.setBrush(gradient)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.setPen(QColor(79, 172, 142))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")
        painter.end()
        return pixmap

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    widget = KimiQuotaWidget()
    widget.show()
    sys.exit(app.exec())
