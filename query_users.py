import sqlite3

conn = sqlite3.connect('bugtracker.db')
cursor = conn.cursor()

print("Users Table:")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

print("\nRoles Table Structure:")
cursor.execute("PRAGMA table_info(roles)")
print([column[1] for column in cursor.fetchall()])

print("\nRoles Table Data:")
cursor.execute("SELECT * FROM roles")
for row in cursor.fetchall():
    print(row)

conn.close()
