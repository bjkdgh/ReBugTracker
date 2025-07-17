' =============================================================================
' ReBugTracker 生产环境启动脚本
' =============================================================================
' 
' 使用说明：
' 1. 修改下面的 projectPath 为你的ReBugTracker项目实际路径
' 2. 保存此文件为 start_rebugtracker.vbs
' 3. 双击运行即可启动ReBugTracker服务器
' 
' 路径配置示例：
' projectPath = "C:\Users\用户名\Desktop\ReBugTracker"
' projectPath = "D:\Projects\ReBugTracker" 
' projectPath = "E:\WebApps\ReBugTracker"
' 
' 生成的文件位置：
' 所有运行时文件都会在项目根目录下生成：
' - uploads\          (用户上传的图片文件)
' - logs\             (应用日志文件)
' - rebugtracker.db   (SQLite数据库文件，如果使用SQLite)
' - __pycache__\      (Python缓存文件)
' 
' 访问地址：
' 启动成功后访问：http://localhost:5000
' 
' 故障排除：
' 1. 如果启动失败，检查 项目目录\logs\startup.log 文件
' 2. 确认Python已安装且在PATH环境变量中
' 3. 确认项目目录路径正确
' 4. 如果使用虚拟环境，确认虚拟环境路径正确
' 
' 停止服务：
' 在任务管理器中结束 python.exe 进程
' 
' =============================================================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' =============================================================================
' 重要：请修改下面的路径为你的实际项目路径
' =============================================================================
Dim projectPath
projectPath = "D:\app_data\repositories\ReBugTracker"

' =============================================================================
' Python配置
' =============================================================================
Dim useVirtualEnv
useVirtualEnv = True

Dim venvPythonPath
venvPythonPath = projectPath & "\.venv\Scripts\python.exe"

Dim systemPython
systemPython = "python"

' =============================================================================
' 启动脚本主体
' =============================================================================

' 检查项目目录
If Not fso.FolderExists(projectPath) Then
    MsgBox "错误：项目目录不存在！" & vbCrLf & vbCrLf & "配置的路径：" & projectPath & vbCrLf & vbCrLf & "请检查VBS脚本中的 projectPath 配置是否正确", vbCritical, "ReBugTracker启动失败"
    WScript.Quit
End If

' 检查启动脚本
Dim waitressScript
waitressScript = projectPath & "\deployment_tools\run_waitress.py"
If Not fso.FileExists(waitressScript) Then
    MsgBox "错误：启动脚本不存在！" & vbCrLf & vbCrLf & "缺失文件：deployment_tools\run_waitress.py" & vbCrLf & vbCrLf & "请确认项目文件完整", vbCritical, "ReBugTracker启动失败"
    WScript.Quit
End If

' 设置工作目录
WshShell.CurrentDirectory = projectPath

' 创建必要目录
If Not fso.FolderExists(projectPath & "\logs") Then
    fso.CreateFolder(projectPath & "\logs")
End If

If Not fso.FolderExists(projectPath & "\uploads") Then
    fso.CreateFolder(projectPath & "\uploads")
End If

' 确定Python路径
Dim pythonCommand
If useVirtualEnv And fso.FileExists(venvPythonPath) Then
    pythonCommand = """" & venvPythonPath & """"
Else
    pythonCommand = systemPython
    If useVirtualEnv Then
        MsgBox "警告：虚拟环境Python不存在，将使用系统Python" & vbCrLf & vbCrLf & "虚拟环境路径：" & venvPythonPath & vbCrLf & "系统Python：" & systemPython, vbExclamation, "ReBugTracker启动提示"
    End If
End If

' 构建启动命令
Dim startCommand
startCommand = pythonCommand & " deployment_tools\run_waitress.py > logs\startup.log 2>&1"

' 显示启动信息
Dim startMsg
startMsg = "正在启动ReBugTracker..." & vbCrLf & vbCrLf
startMsg = startMsg & "项目目录：" & projectPath & vbCrLf
startMsg = startMsg & "Python：" & pythonCommand & vbCrLf
startMsg = startMsg & "日志文件：logs\startup.log" & vbCrLf & vbCrLf
startMsg = startMsg & "请稍等片刻..."
MsgBox startMsg, vbInformation, "ReBugTracker启动中"

' 启动服务器
WshShell.Run startCommand, 0, False

' 等待启动
WScript.Sleep 3000

' 检查启动状态
Dim logFile
logFile = projectPath & "\logs\startup.log"
Dim startupSuccess
startupSuccess = False

If fso.FileExists(logFile) Then
    Dim logContent
    Dim logFileObj
    Set logFileObj = fso.OpenTextFile(logFile, 1)
    If Not logFileObj.AtEndOfStream Then
        logContent = logFileObj.ReadAll()
        If InStr(LCase(logContent), "error") = 0 And InStr(LCase(logContent), "failed") = 0 Then
            startupSuccess = True
        End If
    End If
    logFileObj.Close
End If

' 显示结果
If startupSuccess Then
    Dim successMsg
    successMsg = "ReBugTracker启动成功！" & vbCrLf & vbCrLf
    successMsg = successMsg & "访问地址：http://localhost:5000" & vbCrLf
    successMsg = successMsg & "项目目录：" & projectPath & vbCrLf
    successMsg = successMsg & "日志文件：" & logFile & vbCrLf & vbCrLf
    successMsg = successMsg & "提示：要停止服务，请在任务管理器中结束python.exe进程"
    MsgBox successMsg, vbInformation, "启动成功"
Else
    Dim errorMsg
    errorMsg = "启动可能失败或遇到问题" & vbCrLf & vbCrLf
    errorMsg = errorMsg & "请检查以下内容：" & vbCrLf
    errorMsg = errorMsg & "1. 查看日志文件：" & logFile & vbCrLf
    errorMsg = errorMsg & "2. 确认Python环境正确" & vbCrLf
    errorMsg = errorMsg & "3. 确认端口5000未被占用" & vbCrLf
    errorMsg = errorMsg & "4. 确认数据库配置正确"
    MsgBox errorMsg, vbExclamation, "启动检查"
End If

' 清理对象
Set WshShell = Nothing
Set fso = Nothing