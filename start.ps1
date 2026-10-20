<#
=============================================
校园点餐项目一键启动脚本
功能：
1. FastAPI 后端 : 8000 → 固定域名 https://campus-order.learnshare.uk（小程序 + H5 接口共用）
2. H5 静态页 : 8080 → cloudflared 临时域名暴露公网（快速隧道）
3. 复用已部署的固定域名隧道，不新建隧道、不改云端 Ingress 配置
=============================================
#>
$projectRoot = $PWD.Path
$serverDir = Join-Path $projectRoot "hutu-order-server"
$h5Dir = Join-Path $projectRoot "hutu-order-web\dist\build\h5"
$pythonAbsPath = "C:\Users\alfie\AppData\Local\Programs\Python\Python314\python.exe"
$publicDomain = "https://campus-order.learnshare.uk"
$cfToken = "eyJhIjoiMGM0NmVkNGI3YjA3OTAwN2VkZmQ3OGI5MDYxZGJhZmMiLCJ0IjoiZWU0MzdiZmYtMTAwNS00ZWMxLTg2NzgtZDI0YmYxZWFjZGE4IiwicyI6IllUZzVNR0l3TlRJdFltWmpZeTAwWTJVd0xXRTFOVEl0TWpZeE9HRXhOakJsWldObSJ9"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "     Campus Ordering - Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "公网接口域名(小程序/H5共用)：$publicDomain" -ForegroundColor Green
Write-Host "Swagger 文档：$publicDomain/docs" -ForegroundColor Green
Write-Host "本地 H5 页面：http://127.0.0.1:8080" -ForegroundColor Green
Write-Host "H5 公网地址：见 cloudflared 临时隧道窗口`n" -ForegroundColor Yellow

# 清理旧进程
Write-Host "[0/4] 清理残留 cloudflared / python 进程..."
taskkill /f /im cloudflared.exe 2>&1 | Out-Null
taskkill /f /im python.exe 2>&1 | Out-Null
Start-Sleep -Seconds 1

# 1. 启动 FastAPI 后端
Write-Host "[1/4] 启动 FastAPI 后端 : 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$serverDir`"; & `"$pythonAbsPath`" -m uvicorn main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 3
Write-Host "    后端已拉起`n"

# 2. 启动 H5 静态服务
Write-Host "[2/4] 启动 H5 静态服务 : 8080"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$h5Dir`"; & `"$pythonAbsPath`" -m http.server 8080"
Start-Sleep -Seconds 2
Write-Host "    H5 静态服务已拉起`n"

# 3. 启动固定域名隧道（小程序 + H5 接口 → 8000）
Write-Host "[3/4] 启动 Cloudflare 固定域名隧道 -> 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$projectRoot`"; .\cloudflared.exe tunnel run --token $cfToken --protocol http2"
Start-Sleep -Seconds 2
Write-Host "    固定域名隧道已启动`n"

# 4. 启动临时域名隧道（H5 页面暴露公网 → 8080）
Write-Host "[4/4] 启动 Cloudflare 临时域名隧道 -> 8080 (H5 页面)"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$projectRoot`"; .\cloudflared.exe tunnel --url http://127.0.0.1:8080 --protocol http2"
Start-Sleep -Seconds 2
Write-Host "    临时域名隧道已启动，H5 公网地址见该窗口`n"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  全部服务启动完成！" -ForegroundColor Green
Write-Host "  公网接口：$publicDomain" -ForegroundColor Green
Write-Host "  四个窗口都别关，关闭则服务中断" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
