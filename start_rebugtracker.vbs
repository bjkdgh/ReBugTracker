' ReBugTracker VBS �����ű�
' �Զ������ڲ������

' ������Ŀ��Ŀ¼·��
Dim projectPath
projectPath = "D:\app_data\repositories\ReBugTracker"

' ���� Python ���⻷��·��
Dim pythonPath
pythonPath = projectPath & "\.venv\Scripts\python.exe"

' ���� Waitress �����ű�·��
Dim waitressScript
waitressScript = projectPath & "\deployment_tools\run_waitress.py"

' ���� Shell ����
Dim shell
Set shell = CreateObject("WScript.Shell")

' �л�����ĿĿ¼
shell.CurrentDirectory = projectPath

' ������������(ʹ�� Waitress ����������)
Dim command
command = """" & pythonPath & """ """ & waitressScript & """"

' �ں�̨����(��������)
shell.Run command, 0, False

' ��ʾ������ʾ(��ѡ)
MsgBox "ReBugTracker started in background" & vbCrLf & "Access URL: http://localhost:5000", vbInformation, "ReBugTracker"
