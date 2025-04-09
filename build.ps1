$ErrorActionPreference = "Stop"

# 공통 설정
$Dist = "dist"
$Bin = "ghapps-auth"
$Image = "$Bin-img"
$Container = "$Bin-container"

# 현재 스크립트 경로로 이동
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Write-Host "📂 현재 디렉토리: $(Get-Location)"

# dist 디렉토리 생성
New-Item -ItemType Directory -Path $Dist -Force | Out-Null

# 🧹 기존 dist 실행파일 정리
Remove-Item "$Dist\$Bin" -Force -ErrorAction SilentlyContinue
Remove-Item "$Dist\$Bin.exe" -Force -ErrorAction SilentlyContinue

# ✅ 윈도우용 실행파일 빌드
Write-Host "`n💻 [1/2] Windows용 실행파일 빌드 중..."
py -m PyInstaller -F main.py --name $Bin

# exe 결과 dist로 이동
Move-Item ".\dist\$Bin.exe" ".\$Dist\" -Force

# 빌드 중 생성된 임시 파일 정리
@("build", "__pycache__") + (Get-ChildItem -Filter "*.spec").Name |
    ForEach-Object {
        if (Test-Path $_) {
            Remove-Item $_ -Recurse -Force
            Write-Host "🧽 삭제됨: $_"
        }
    }

# 🐳 리눅스용 실행파일 빌드 (Docker 이용)
Write-Host "`n🐧 [2/2] Linux용 실행파일 빌드 중 (Docker)..."

docker build -t $Image .

docker create --name $Container $Image

# 결과 복사 (리눅스 바이너리)
docker cp "${Container}:/app/dist/$Bin" "$Dist/"

docker rm $Container

# ✅ 결과 확인
Write-Host "`n📦 최종 dist 디렉토리:"
Get-ChildItem $Dist | Format-Table Name, Length

Write-Host "`n🎉 Windows/Linux 빌드 완료!"
