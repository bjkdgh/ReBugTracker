# -*- coding: utf-8 -*-
"""
流转通知规则
定义在不同业务流转过程中，哪些用户应该收到通知
"""

from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class FlowNotificationRules:
    """流转通知规则"""
    
    @staticmethod
    def get_notification_targets(event_type: str, event_data: Dict) -> Set[str]:
        """
        获取通知目标用户ID
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
            
        Returns:
            Set[str]: 目标用户ID集合
        """
        targets = set()
        
        try:
            if event_type == "bug_created":
                # 问题创建：实施组提交问题，只通知指定的负责人
                assigned_manager_id = event_data.get('assigned_manager_id')
                if assigned_manager_id:
                    targets.add(str(assigned_manager_id))
                    logger.debug(f"Bug created notification target: assigned manager {assigned_manager_id}")
                else:
                    # 如果没有指定负责人，则通知所有负责人（兼容旧逻辑）
                    targets.update(FlowNotificationRules._get_users_by_roles(['fzr']))
                    logger.debug(f"Bug created notification targets (fallback): {len(targets)} managers")
                
            elif event_type == "bug_assigned":
                # 问题分配：负责人分配给组内成员，通知被分配者
                assignee_id = event_data.get('assignee_id')
                if assignee_id:
                    targets.add(str(assignee_id))
                    logger.debug(f"Bug assigned notification target: {assignee_id}")
                    
            elif event_type == "bug_status_changed":
                # 状态变更：通知创建者、分配者、当前处理人
                creator_id = event_data.get('creator_id')
                assignee_id = event_data.get('assignee_id')
                
                if creator_id:
                    targets.add(str(creator_id))
                if assignee_id:
                    targets.add(str(assignee_id))
                    
                logger.debug(f"Bug status changed notification targets: {len(targets)} users")
                    
            elif event_type == "bug_resolved":
                # 问题解决：组内成员解决问题，通知实施组（创建者）和负责人
                creator_id = event_data.get('creator_id')
                if creator_id:
                    targets.add(str(creator_id))
                targets.update(FlowNotificationRules._get_users_by_roles(['fzr']))
                logger.debug(f"Bug resolved notification targets: {len(targets)} users")
                
            elif event_type == "bug_closed":
                # 问题关闭：通知所有相关人员
                creator_id = event_data.get('creator_id')
                assignee_id = event_data.get('assignee_id')
                
                if creator_id:
                    targets.add(str(creator_id))
                if assignee_id:
                    targets.add(str(assignee_id))
                    
                logger.debug(f"Bug closed notification targets: {len(targets)} users")
            
            else:
                logger.warning(f"Unknown event type: {event_type}")
        
        except Exception as e:
            logger.error(f"Error getting notification targets for {event_type}: {e}")
        
        return targets
    
    @staticmethod
    def _get_users_by_roles(roles: List[str]) -> List[str]:
        """
        根据角色获取用户ID列表
        
        Args:
            roles: 角色列表 ['ssz', 'fzr', 'gly', 'zncy']
            
        Returns:
            List[str]: 用户ID列表
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 构建IN查询
            placeholders = ','.join(['%s'] * len(roles))
            query = f"""
                SELECT id FROM users 
                WHERE role_en IN ({placeholders})
                AND id IS NOT NULL
            """
            
            query, params = adapt_sql(query, roles)
            cursor.execute(query, params)
            
            users = cursor.fetchall()
            conn.close()
            
            user_ids = [str(user[0]) for user in users]
            logger.debug(f"Found {len(user_ids)} users for roles {roles}")
            
            return user_ids
            
        except Exception as e:
            logger.error(f"Error getting users by roles {roles}: {e}")
            return []
    
    @staticmethod
    def get_role_description(role_en: str) -> str:
        """获取角色中文描述"""
        role_map = {
            'gly': '管理员',
            'fzr': '负责人', 
            'ssz': '实施组',
            'zncy': '组内成员'
        }
        return role_map.get(role_en, role_en)
    
    @staticmethod
    def is_workflow_participant(user_role: str, event_type: str) -> bool:
        """
        判断用户角色是否是某个事件的工作流参与者
        
        Args:
            user_role: 用户角色
            event_type: 事件类型
            
        Returns:
            bool: 是否为参与者
        """
        # 定义每个事件类型的参与者角色
        event_participants = {
            "bug_created": ['fzr'],  # 指定的负责人（接收实施组提交的问题）
            "bug_assigned": ['zncy'],  # 组内成员（接收负责人分配的问题）
            "bug_status_changed": ['ssz', 'zncy', 'fzr'],  # 实施组、组内成员、负责人
            "bug_resolved": ['ssz', 'fzr'],  # 实施组和负责人（接收组内成员解决的问题）
            "bug_closed": ['fzr', 'gly']  # 负责人和管理员
        }
        
        participants = event_participants.get(event_type, [])
        return user_role in participants
