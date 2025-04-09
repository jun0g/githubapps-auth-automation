# GitHub Apps 인증 도구
##### githubapps-auth-automation

`githubapps-auth-automation`는 **GitHub Apps를 이용하여 Git 저장소를 인증하고 자동화된 Git 작업을 수행하는 CLI 도구**입니다.  
git 작업 - **git clone, fetch/reset, commit/push, diff, lfs pull**를 지원하며, **GitHub Apps 인증으로 보안성 및 편리성을 향상**시킬 수 있습니다.

## 주요 기능
- **GitHub Apps 인증 지원**: GitHub Apps을 활용하여 보안 인증 수행.
- **CI/CD 자동화**: 특정 환경에서 빌드 및 배포 자동화 가능.
- **AccessToken 발급**: 인증에 필요한 AccessToken을 별도 발급 가능.
- **저장소 동기화**: 기존 저장소를 **Clone** 또는 최신 상태로 **Fetch & Reset** 수행.
- **자동 커밋 및 푸시**: 로컬 변경 사항을 자동으로 **Commit & Push**.
- **변경된 파일 목록 체크**: min/max revision으로 변경된 파일 목록 확인.
- **lfs pull**: lfs 파일 pull 기능 수행.

## 설치 방법

1. **Python 설치**
   - Python 3.13 이상이 필요합니다.  
   - [Python 설치 가이드](https://www.python.org/downloads/) 참고.

2. **소스 코드 다운로드 및 의존성 설치**
   ```bash
   git clone https://github.com/jun0g/githubapps-auth-automation.git

   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **빌드**
    - Powershell이 설치된 환경에서 `build.ps1`을 실행하여 실행 파일을 생성할 수 있습니다.
    ```bash
    # PowerShell에서 실행 (Windows/Linux 공통)
    ./build.ps1

    # 리눅스 실행파일만 빌드
    ./build.ps1 -Target linux

    # 윈도우 실행파일만 빌드
    ./build.ps1 -Target windows
    ```
    - 또는 직접 PyInstaller 명령어를 사용할 수 있습니다.
    ```bash
    python -m PyInstaller -F main.py --name ghapps-auth
    ```

4. **빌드된 인증 도구 확인**
   ```bash
   cd ./dist
   ./ghapps-auth -h    # 또는 Windows에서는 ghapps-auth.exe -h
   ```

## 사용 방법
```bash
ghapps-auth <모드> [옵션]
```

### 실행 모드

| 모드      | 설명                              |
|-----------|-----------------------------------|
| `token`   | AccessToken 발급                   |
| `clone`   | Git 저장소를 **Clone** 또는 **Fetch/Reset** 수행 |
| `commit`  | 변경 사항을 **Commit** 수행         |
| `push`    | 변경 사항을 **Push** 수행           |
| `diff`    | 변경 사항 파일 목록 출력            |
| `lfs`     | lfs pull                          |

※ 각 모드에서 사용하지 않는 매개변수를 입력하더라도 오류가 발생하지 않도록 제작되었습니다.

#### token - Token 값 가져오기
```bash
ghapps-auth token \
    --APP_ID=<GitHub App ID> \
    --KEY_PATH=<GitHub App 개인 키 경로> \
    --INSTALL_ID=<설치(Installation) ID>
```

#### clone - 저장소 동기화 모드
```bash
ghapps-auth clone \
    --APP_ID=<GitHub App ID> \
    --KEY_PATH=<개인 키 경로> \
    --INSTALL_ID=<설치 ID> \
    --LocalRepoPath=<로컬 저장소 경로> \
    --RepoURL=<GitHub 저장소 URL> \
    --Branch=<브랜치> \
    --RemoteName=<원격 저장소 이름>
```

#### commit - 변경 사항 커밋 모드
```bash
ghapps-auth commit \
    --CommitMessage=<커밋 메세지> \
    --LocalRepoPath=<로컬 저장소 경로> \
    --BuildAgent=<빌드 에이전트 이름>
```

#### push - 변경 사항 푸시 모드
```bash
ghapps-auth push \
    --Branch=<브랜치> \
    --LocalRepoPath=<로컬 저장소 경로> \
    --RemoteName=<원격 저장소 이름> \
    --RepoURL=<GitHub 저장소 URL>
```

#### diff - 변경된 파일 목록 확인
```bash
ghapps-auth diff \
    --LocalRepoPath=<로컬 저장소 경로> \
    --min_revision=<최소 리비전> \
    --max_revision=<최대 리비전> \
    --target_path=<비교할 디렉토리>
```

#### lfs - git lfs pull
```bash
ghapps-auth lfs \
    --LocalRepoPath=<로컬 저장소 경로>
```

## 지원 플랫폼
- Windows
- Linux (Linux 환경에서 빌드 시)
  - 실행 경로 예: `./exe/ghapps-auth`
