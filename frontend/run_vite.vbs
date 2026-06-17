Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Medical_Management_System\frontend"
WshShell.Run "cmd.exe /c npx vite --host", 0, False
