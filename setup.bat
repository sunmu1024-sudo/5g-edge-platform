@echo off
chcp 65001
echo 🚀 正在设置5G边缘计算平台...
echo.

echo 1. 下载ngrok...
powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
if %errorlevel% neq 0 (
    echo ❌ 下载失败，请检查网络连接
    pause
    exit /b 1
)

echo 2. 解压ngrok...
powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"
if %errorlevel% neq 0 (
    echo ❌ 解压失败
    pause
    exit /b 1
)

echo 3. 清理文件...
del ngrok.zip

echo 4. 请注册ngrok并配置token...
echo 📝 访问: https://dashboard.ngrok.com/signup
echo 🔑 注册后，在这个窗口运行: ngrok.exe authtoken 您的token
echo.

echo ✅ 设置完成！
pause