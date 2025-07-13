# -*- coding: utf-8 -*-
"""
通知器基类
定义所有通知器的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNotifier(ABC):
    """通知器基类"""
    
    @abstractmethod
    def send(self, title: str, content: str, recipient: Dict[str, Any], 
             priority: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            recipient: 接收者信息字典
            priority: 优先级 (1-4)
            metadata: 元数据
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    def is_enabled(self) -> bool:
        """
        检查通知器是否启用
        
        Returns:
            bool: 是否启用
        """
        return True
    
    def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """
        验证接收者信息是否有效
        
        Args:
            recipient: 接收者信息
            
        Returns:
            bool: 是否有效
        """
        return recipient and 'id' in recipient
