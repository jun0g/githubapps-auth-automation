param(
    [ValidateSet("windows", "linux", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"

# 공통 설정
$Dist = "dist"
$Bin = "ghapps-auth"
$LinuxImage = "$Bin-img"
$LinuxContainer = "$Bin-container"

# 현재 스크립트 경로로 이동
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Write-Host "📂 현재 디렉토리: $(Get-Location)"

# dist 디렉토리 준비
New-Item -ItemType Directory -Path $Dist -Force | Out-Null

# 기존 dist 실행파일 정리
if ($Target -in @("all", "windows")) {
    Remove-Item "$Dist\$Bin.exe" -Force -ErrorAction SilentlyContinue
}
if ($Target -in @("all", "linux")) {
    Remove-Item "$Dist\$Bin" -Force -ErrorAction SilentlyContinue
}

# ✅ [1/2] Windows용 빌드
if ($Target -in @("all", "windows")) {
    Write-Host "`n💻 [Windows] 실행파일 빌드 중..."
    py -m PyInstaller -F main.py --name $Bin

    Move-Item ".\dist\$Bin.exe" ".\$Dist\" -Force

    @("build", "__pycache__") + (Get-ChildItem -Filter "*.spec").Name |
        ForEach-Object {
            if (Test-Path $_) {
                Remove-Item $_ -Recurse -Force
                Write-Host "🧽 삭제됨: $_"
            }
        }
}

# 🐳 [2/2] Linux용 빌드 (Docker)
if ($Target -in @("all", "linux")) {
    Write-Host "`n🐧 [Linux] 실행파일 빌드 중 (Docker)..."
    docker build -t $LinuxImage .
    docker create --name $LinuxContainer $LinuxImage | Out-Null
    docker cp "${LinuxContainer}:/app/dist/$Bin" "$Dist/"
    docker rm $LinuxContainer | Out-Null
}

# 결과 확인
Write-Host "`n📦 최종 dist 디렉토리:"
Get-ChildItem $Dist | Format-Table Name, LastWriteTime

Write-Host "`n🎉 선택된 환경($Target) 빌드 완료!"
