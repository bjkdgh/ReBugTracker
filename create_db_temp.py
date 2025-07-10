import psycopg2

def main():
    try:
        # 连接到postgres数据库
        conn = psycopg2.connect(
            host="192.168.1.5",
            dbname="postgres",
            user="postgres",
            password="$RFV5tgb"
        )
        conn.autocommit = True
        c = conn.cursor()
        
        # 添加role_en和team_en列
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS role_en TEXT')
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS team_en TEXT')
        c.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS chinese_name TEXT')
        
        # 更新现有数据
        c.execute('''UPDATE users SET 
                   role_en = CASE 
                     WHEN role = '管理员' THEN 'gly' 
                     WHEN role = '负责人' THEN 'fzr' 
                     WHEN role = '组内成员' THEN 'zncy' 
                     WHEN role = '实施组' THEN 'ssz' 
                     ELSE role 
                   END,
                   team_en = CASE
                     WHEN team = '网络分析' THEN 'wlfx'
                     WHEN team = '实施组' THEN 'ssz'
                     WHEN team = '第三道防线' THEN 'dsdfx'
                     WHEN team = '新能源' THEN 'xny'
                     ELSE team
                   END''')
        
        print("数据库表结构更新成功")
        conn.close()
        
    except Exception as e:
        print(f"数据库操作失败: {e}")

if __name__ == "__main__":
    main()
