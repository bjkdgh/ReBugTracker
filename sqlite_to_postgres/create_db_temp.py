# create_db_temp.py: 数据库表结构更新脚本
# 主要功能：为users表添加新的字段，并根据现有字段值生成对应的英文标识

import psycopg2

def main():
    """主函数执行数据库表结构更新
    
    功能：
    - 为users表添加role_en、team_en和chinese_name新字段
    - 根据中文角色名称生成对应的角色英文标识
    - 根据中文团队名称生成对应的团队英文标识
    """
    try:
        # 获取数据库连接
        from db_factory import get_db_connection
        conn = get_db_connection()
        # 启用自动提交模式
        conn.autocommit = True
        # 创建游标对象
        c = conn.cursor()
        
        # 添加role_en和team_en列
        # 新增用户角色英文名字段
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS role_en TEXT')
        # 新增用户团队英文名字段
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS team_en TEXT')
        # 新增用户中文姓名字段
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS chinese_name TEXT')
        
        # 更新现有数据
        # 将中文角色转换为英文标识
        c.execute('''UPDATE users SET 
                   role_en = CASE 
                     WHEN role = '管理员' THEN 'gly' 
                     WHEN role = '负责人' THEN 'fzr' 
                     WHEN role = '组内成员' THEN 'zncy' 
                     WHEN role = '实施组' THEN 'ssz' 
                     ELSE role 
                   END,
                   # 将中文团队名称转换为英文标识
                   team_en = CASE
                     WHEN team = '网络分析' THEN 'wlfx'
                     WHEN team = '实施组' THEN 'ssz'
                     WHEN team = '第三道防线' THEN 'dsdfx'
                     WHEN team = '新能源' THEN 'xny'
                     ELSE team
                   END''')
        
        # 打印操作成功信息
        print("数据库表结构更新成功")
        # 关闭数据库连接
        conn.close()
        
    except Exception as e:
        # 捕获并打印异常信息
        print(f"数据库操作失败: {e}")

if __name__ == "__main__":
    # 当作为脚本运行时执行主函数
    main()
