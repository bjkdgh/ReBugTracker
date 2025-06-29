import sqlite3

# 查询roles表
conn = sqlite3.connect('bugtracker.db')
print("=== Roles表 ===")
cursor = conn.execute("SELECT * FROM roles")
for row in cursor:
    print(row)

# 查询users表
print("\n=== Users表 ===")
cursor = conn.execute("SELECT id, username, role FROM users")
for row in cursor:
    print(row)

conn.close()
