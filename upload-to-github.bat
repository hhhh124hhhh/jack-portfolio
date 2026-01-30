@echo off
REM GitHub Releases 一键上传脚本
REM 使用方法：双击运行此脚本

echo ==========================================
echo   GitHub Releases 上传助手
echo ==========================================
echo.

REM 检查当前目录
if not exist "dist-skills\clawdbot-skills-*.tar.gz" (
    echo ❌ 错误：未找到打包文件
    echo 请先运行: bash package-skills.sh
    pause
    exit /b 1
)

echo ✅ 找到打包文件
echo.
echo 📋 准备上传的文件:
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 完整包:
dir /b dist-skills\clawdbot-skills-*.tar.gz
echo.
echo 单独包 (11个):
dir /b dist-skills\single-skills\*.tar.gz
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo 🚀 上传方式选择:
echo.
echo 1. 打开浏览器上传 (推荐)
echo 2. 查看详细上传指南
echo 3. 取消
echo.
set /p choice="请选择 (1-3): "

if "%choice%"=="1" goto browser_upload
if "%choice%"=="2" goto show_guide
if "%choice%"=="3" goto end
goto end

:browser_upload
echo.
echo ✅ 正在打开浏览器...
echo.
echo 请按照以下步骤操作:
echo.
echo 1. 浏览器会自动打开 GitHub Releases 页面
echo 2. 填写信息:
echo    - Tag: v1.0.0
echo    - Title: Clawdbot Skills Collection v1.0.0
echo 3. 上传文件 (拖拽或选择):
echo    - dist-skills\clawdbot-skills-*.tar.gz (完整包)
echo    - dist-skills\single-skills\*.tar.gz (单独包)
echo 4. 从 "GitHub-Releases上传指南.md" 复制 Release Notes
echo 5. 点击 Publish release
echo.
pause

REM 打开浏览器
start https://github.com/hhhh124hhhh/Clawdbot-Skills-Converter/releases/new

echo.
echo 💡 提示: 上传时可以一次性选择多个文件
echo.
goto end

:show_guide
echo.
echo 📖 打开上传指南...
start GitHub-Releases上传指南.md
goto end

:end
echo.
echo ==========================================
echo   感谢使用！
echo ==========================================
echo.
timeout /t 3 >nul
