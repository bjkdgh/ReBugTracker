Set WshShell = CreateObject("WScript.Shell")

' �޸������·��
WshShell.CurrentDirectory = "C:\Users\23703\Desktop\ReBugTracker"

' ����
WshShell.Run "python deployment_tools\run_waitress.py", 0, False

MsgBox "ReBugTracker������������ http://localhost:5000", vbInformation