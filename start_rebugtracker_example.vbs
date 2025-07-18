'一定注意编码GBK！！！！！！！！！！！！！
' ReBugTracker VBS 启动脚本示例
' 此脚本用于在后台无窗口启动 ReBugTracker
' 请根据实际情况修改路径

' 设置项目根目录路径（请修改为实际路径）
Dim projectPath
projectPath = "C:\path\to\your\ReBugTracker"

' 设置 Python 虚拟环境路径
Dim pythonPath
pythonPath = projectPath & "\.venv\Scripts\python.exe"

' 设置 Waitress 启动脚本路径（生产级服务器）
Dim scriptPath
scriptPath = projectPath & "\deployment_tools\run_waitress.py"

' 创建 Shell 对象
Dim shell
Set shell = CreateObject("WScript.Shell")

' 切换到项目目录
shell.CurrentDirectory = projectPath

' 构建启动命令
Dim command
command = """" & pythonPath & """ """ & scriptPath & """"

' 在后台运行（窗口隐藏）
' 参数说明：
' - command: 要执行的命令
' - 0: 隐藏窗口
' - False: 不等待程序结束
shell.Run command, 0, False

' 显示启动提示（可选，注释掉则完全静默）
' MsgBox "ReBugTracker 已在后台启动" & vbCrLf & "访问地址: http://localhost:5000", vbInformation, "ReBugTracker"

' 脚本结束
