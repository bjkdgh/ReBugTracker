import sqlite3

conn = sqlite3.connect('bugtracker.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, username, role, team FROM users WHERE username='admin'")
admin = c.fetchone()

if admin:
    print("Admin用户数据:")
    print(f"ID: {admin['id']}")
    print(f"用户名: {admin['username']}") 
    print(f"角色: {admin['role']}")
    print(f"团队: {admin['team']}")
else:
    print("未找到admin用户")

conn.close()
