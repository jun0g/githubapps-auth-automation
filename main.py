import argparse
import logging
from utils.AccessToken import get_access_token
from utils.GitCommand import fetch_repo, pull_repo, commit_changes, push_changes, get_changed_files, update_lfs_files

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", encoding='utf-8')

ALL_ARGUMENTS = {
    "APP_ID": "GitHub App ID",
    "KEY_PATH": "GitHub App 개인 키 경로",
    "INSTALL_ID": "설치(Installation) ID",
    "LocalRepoPath": "로컬 저장소 경로",
    "RepoURL": "GitHub Repository URL",
    "RemoteName": "GitHub Origin RemoteName",
    "Branch": "GitHub Repository Branch",
    "BuildAgent": "빌드 에이전트 이름",
    "CommitMessage": "커밋 메시지",
    "min_revision": "최소 리비전",
    "max_revision": "최대 리비전",
    "target_path": "비교할 디렉토리",
    "diff_filter": "비교 옵션 default=ACMR"
}

REQUIRED_ARGUMENTS = {
    "clone": ["APP_ID", "KEY_PATH", "INSTALL_ID", "LocalRepoPath", "RepoURL", "RemoteName", "Branch"],
    "pull": ["APP_ID", "KEY_PATH", "INSTALL_ID", "LocalRepoPath", "RepoURL", "RemoteName", "Branch"],
    "commit": ["CommitMessage", "LocalRepoPath", "BuildAgent"],
    "push": ["Branch", "LocalRepoPath", "RemoteName", "RepoURL"],
    "token": ["APP_ID", "KEY_PATH", "INSTALL_ID"],
    "diff": ["LocalRepoPath", "min_revision", "max_revision"],
    "lfs": ["LocalRepoPath"],
}

def main():
    parser = argparse.ArgumentParser(description="GitHub App Git 작업 자동화 스크립트")

    subparsers = parser.add_subparsers(dest="mode", required=True, help="실행 모드 선택")

    for mode, required_args in REQUIRED_ARGUMENTS.items():
        mode_parser = subparsers.add_parser(mode, help=f"{mode} 모드 실행")

        for arg in required_args:
            mode_parser.add_argument(f"--{arg}", type=str, required=True, help=ALL_ARGUMENTS[arg])

        # 필요하지 않은 매개변수는 자동으로 optional로 추가
        optional_args = set(ALL_ARGUMENTS.keys()) - set(required_args)
        for arg in optional_args:
            mode_parser.add_argument(f"--{arg}", type=str, required=False, help=ALL_ARGUMENTS[arg])

    # 입력값 파싱
    args = parser.parse_args()

    if args.mode == "token":
        logging.info("mode is [token] - Get AccessToken.")
        access_token = get_access_token(args.APP_ID, args.KEY_PATH, args.INSTALL_ID)
        print(access_token)
    
    elif args.mode == "clone":
        access_token = get_access_token(args.APP_ID, args.KEY_PATH, args.INSTALL_ID)
        auth_git_url = f"https://x-access-token:{access_token}@{args.RepoURL.split('//', 1)[-1]}"
        print(auth_git_url)

        logging.info("mode is [clone/fetch] - Sync the local repository.")
        fetch_repo(auth_git_url, args.RemoteName, args.Branch, args.LocalRepoPath)

    elif args.mode == "pull":
        access_token = get_access_token(args.APP_ID, args.KEY_PATH, args.INSTALL_ID)
        auth_git_url = f"https://x-access-token:{access_token}@{args.RepoURL.split('//', 1)[-1]}"
        print(auth_git_url)

        logging.info("mode is [clone/pull] - Sync the local repository.")
        pull_repo(auth_git_url, args.RemoteName, args.Branch, args.LocalRepoPath)

    elif args.mode == "commit":
        logging.info("mode is [commit] - Commit diff.")
        commit_changes(args.CommitMessage, args.LocalRepoPath, args.BuildAgent)
    
    elif args.mode == "push":
        logging.info("mode is [push] - Push diff.")
        push_changes(args.Branch, args.LocalRepoPath, args.RemoteName, args.RepoURL)

    elif args.mode == "diff":
        logging.info("mode is [diff] - Return commit diff.")

        # diff-filter 기본값 적용
        diff_filter = args.diff_filter if args.diff_filter else "ACMR"

        # target_path는 필수가 아니므로 기본값 None
        target_path = args.target_path if args.target_path else None

        changed_files = get_changed_files(
            args.LocalRepoPath,
            args.min_revision,
            args.max_revision,
            target_path,
            diff_filter
        )
        print("\n".join(changed_files))
        # return changed_files

    elif args.mode == "lfs":
        logging.info("mode is [lfs] - git lfs pull.")
        update_lfs_files(args.LocalRepoPath)

if __name__ == "__main__":
    main()
