Set WshShell = CreateObject("WScript.Shell")

' 修改这里的路径
WshShell.CurrentDirectory = "C:\Users\23703\Desktop\ReBugTracker"

' 启动
WshShell.Run "python deployment_tools\run_waitress.py", 0, False

MsgBox "ReBugTracker已启动！访问 http://localhost:5000", vbInformation