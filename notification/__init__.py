# -*- coding: utf-8 -*-
"""
ReBugTracker 通知系统
简化版通知系统，专注于流转过程中的参与者通知
"""

__version__ = "1.0.0"
__author__ = "ReBugTracker Team"

from .simple_notifier import simple_notifier
from .notification_manager import NotificationManager

__all__ = ['simple_notifier', 'NotificationManager']
