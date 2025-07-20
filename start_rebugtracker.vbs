' ReBugTracker VBS 启动脚本
' 自动生成于部署过程

' 设置项目根目录路径
Dim projectPath
projectPath = "D:\app_data\repositories\ReBugTracker"

' 设置 Python 虚拟环境路径
Dim pythonPath
pythonPath = projectPath & "\.venv\Scripts\python.exe"

' 设置 Waitress 启动脚本路径
Dim waitressScript
waitressScript = projectPath & "\deployment_tools\run_waitress.py"

' 创建 Shell 对象
Dim shell
Set shell = CreateObject("WScript.Shell")

' 切换到项目目录
shell.CurrentDirectory = projectPath

' 构建启动命令(使用 Waitress 生产服务器)
Dim command
command = """" & pythonPath & """ """ & waitressScript & """"

' 在后台运行(窗口隐藏)
shell.Run command, 0, False

' 显示启动提示(可选)
MsgBox "ReBugTracker started in background" & vbCrLf & "Access URL: http://localhost:5000", vbInformation, "ReBugTracker"
