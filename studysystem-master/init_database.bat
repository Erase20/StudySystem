@echo off

echo 开始初始化数据库...

REM 检查MySQL是否安装
where mysql >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: MySQL未安装或未添加到环境变量
    pause
    exit /b 1
)

echo 正在创建数据库...
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS manager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"

if %errorlevel% neq 0 (
    echo 错误: 创建数据库失败，请检查MySQL用户名密码
    pause
    exit /b 1
)

echo 正在导入数据库结构...
mysql -u root -p manager < "%~dp0springboot\src\main\resources\manager.sql"

if %errorlevel% neq 0 (
    echo 错误: 导入数据库结构失败
    pause
    exit /b 1
)

echo 正在导入演示数据...
mysql -u root -p manager < "%~dp0springboot\src\main\resources\demo_data.sql"

if %errorlevel% neq 0 (
    echo 错误: 导入演示数据失败
    pause
    exit /b 1
)

echo 数据库初始化完成！
echo 测试账号：
echo - 用户：test / 123
echo - 管理员：admin / 123

pause