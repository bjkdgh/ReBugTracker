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

            elif event_type == "bug_rejected":
                # 问题驳回：负责人驳回问题，通知提出人
                creator_id = event_data.get('creator_id')
                if creator_id:
                    targets.add(str(creator_id))
                    logger.debug(f"Bug rejected notification target: creator {creator_id}")

                # 如果问题之前已分配给某人，也通知被分配者
                old_assignee_id = event_data.get('old_assignee_id')
                if old_assignee_id:
                    targets.add(str(old_assignee_id))
                    logger.debug(f"Bug rejected notification target: old assignee {old_assignee_id}")
                    
            elif event_type == "bug_status_changed":
                # 状态变更：通知创建者、分配者、当前处理人、相关产品经理
                creator_id = event_data.get('creator_id')
                assignee_id = event_data.get('assignee_id')
                product_line_id = event_data.get('product_line_id')

                if creator_id:
                    targets.add(str(creator_id))
                if assignee_id:
                    targets.add(str(assignee_id))

                # 通知相关产品经理
                if product_line_id:
                    product_managers = FlowNotificationRules._get_product_managers_by_product_line(product_line_id)
                    targets.update(product_managers)
                    logger.debug(f"Added {len(product_managers)} product managers for product line {product_line_id}")

                logger.debug(f"Bug status changed notification targets: {len(targets)} users")
                    
            elif event_type == "bug_resolved":
                # 问题解决：组内成员解决问题，通知实施组（创建者）和负责人
                creator_id = event_data.get('creator_id')
                if creator_id:
                    targets.add(str(creator_id))
                targets.update(FlowNotificationRules._get_users_by_roles(['fzr']))
                logger.debug(f"Bug resolved notification targets: {len(targets)} users")
                
            elif event_type == "bug_closed":
                # 问题关闭：通知相关负责人和组内成员
                creator_id = event_data.get('creator_id')
                assignee_id = event_data.get('assignee_id')

                # 通知创建者（实施组）
                if creator_id:
                    targets.add(str(creator_id))

                # 通知被分配者（组内成员）
                if assignee_id:
                    targets.add(str(assignee_id))

                    # 通过组内成员找到对应的负责人
                    manager_id = FlowNotificationRules._get_manager_by_assignee(assignee_id)
                    if manager_id:
                        targets.add(str(manager_id))
                        logger.debug(f"Found manager {manager_id} for assignee {assignee_id}")

                logger.debug(f"Bug closed notification targets: {len(targets)} users (creator: {creator_id}, assignee: {assignee_id})")
            
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
    def _get_manager_by_assignee(assignee_id: str) -> str:
        """
        根据被分配者ID找到对应的负责人ID

        Args:
            assignee_id: 被分配者（组内成员）ID

        Returns:
            str: 负责人ID，如果未找到则返回None
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            # 先获取被分配者的团队信息
            query, params = adapt_sql("""
                SELECT team FROM users WHERE id = %s
            """, (assignee_id,))
            cursor.execute(query, params)

            assignee_result = cursor.fetchone()
            if not assignee_result:
                logger.warning(f"Assignee {assignee_id} not found")
                conn.close()
                return None

            assignee_team = assignee_result[0]

            # 根据团队找到对应的负责人
            query, params = adapt_sql("""
                SELECT id FROM users
                WHERE team = %s AND role_en = 'fzr'
                LIMIT 1
            """, (assignee_team,))
            cursor.execute(query, params)

            manager_result = cursor.fetchone()
            conn.close()

            if manager_result:
                manager_id = str(manager_result[0])
                logger.debug(f"Found manager {manager_id} for assignee {assignee_id} in team {assignee_team}")
                return manager_id
            else:
                logger.warning(f"No manager found for team {assignee_team}")
                return None

        except Exception as e:
            logger.error(f"Error getting manager for assignee {assignee_id}: {e}")
            return None
    
    @staticmethod
    def get_role_description(role_en: str) -> str:
        """获取角色中文描述"""
        role_map = {
            'gly': '管理员',
            'fzr': '负责人',
            'ssz': '实施组',
            'zncy': '组内成员',
            'pm': '产品经理'
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
            "bug_rejected": ['ssz', 'zncy'],  # 实施组和组内成员（接收负责人驳回的问题）
            "bug_status_changed": ['ssz', 'zncy', 'fzr'],  # 实施组、组内成员、负责人
            "bug_resolved": ['ssz', 'fzr'],  # 实施组和负责人（接收组内成员解决的问题）
            "bug_closed": ['fzr', 'gly']  # 负责人和管理员
        }
        
        participants = event_participants.get(event_type, [])
        return user_role in participants

    @staticmethod
    def _get_product_managers_by_product_line(product_line_id: int) -> set:
        """根据产品线ID获取相关产品经理的ID列表"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            # 先获取产品线名称
            query, params = adapt_sql("""
                SELECT name FROM product_lines WHERE id = %s
            """, (product_line_id,))

            cursor.execute(query, params)
            result = cursor.fetchone()

            if not result:
                conn.close()
                return set()

            product_line_name = result[0]

            # 查询团队包含该产品线的产品经理
            query, params = adapt_sql("""
                SELECT id
                FROM users
                WHERE role_en = 'pm' AND (team LIKE %s OR team LIKE %s OR team LIKE %s OR team = %s)
            """, (f"%{product_line_name},%", f"%,{product_line_name},%", f"%,{product_line_name}", product_line_name))

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            product_managers = {str(row[0]) for row in results}
            logger.debug(f"Found {len(product_managers)} product managers for product line {product_line_name}")

            return product_managers

        except Exception as e:
            logger.error(f"Error getting product managers for product line {product_line_id}: {e}")
            return set()
