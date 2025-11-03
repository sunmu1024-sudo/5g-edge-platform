@echo off
chcp 65001
echo 🚀 启动5G边缘计算平台...
echo.

echo 1. 检查ngrok...
if not exist "ngrok.exe" (
    echo ❌ 未找到ngrok，正在下载...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"
    del ngrok.zip
    echo ✅ ngrok下载完成！
)

echo 2. 启动后端服务...
start cmd /k "cd backend && python app.py"
timeout 5

echo 3. 启动前端服务...
start cmd /k "cd frontend && python -m http.server 8000"
timeout 5

echo 4. 启动公网访问...
echo 📢 请把生成的网址发给老师和同学！
echo.
ngrok.exe http 8000

pause