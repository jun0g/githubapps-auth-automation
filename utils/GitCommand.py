import os
import git
import logging
import traceback
import sys  # 추가

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def add_safe_directory(local_repo_path: str):
    try:
        safe_path = local_repo_path.replace("\\", "\\\\")
        repo = git.Repo(local_repo_path)
        config_reader = repo.config_reader()

        try:
            existing_safe_dirs = config_reader.get_value("safe", "directory", default="").split("\n")
        except:
            existing_safe_dirs = []

        if safe_path in existing_safe_dirs:
            logging.info(f"[config] Safe.directory already set: {safe_path}")
            return

        config_writer = repo.config_writer()
        config_writer.set_value("safe", "directory", safe_path)
        config_writer.release()
        logging.info(f"[config] Added safe.directory: {safe_path}")

    except git.exc.GitError as e:
        logging.error(f"[config] Failed to add safe.directory: \n{e}")
        sys.exit(1)

def get_changed_files(local_repo_path: str, min_revision: str, max_revision: str, target_path: str = None, diff_filter: str = "ACMR"):
    try:
        repo = git.Repo(local_repo_path)

        if not min_revision or not max_revision:
            logging.warning("[diff] Skipped diff: min_revision or max_revision is empty.")
            return []

        diff_args = [
            f"--diff-filter={diff_filter}",
            "--name-only",
            min_revision,
            max_revision
        ]
        if target_path:
            diff_args += ["--", target_path]

        result = repo.git.diff(*diff_args)
        changed_files = [line.strip() for line in result.splitlines() if line.strip()]

        if changed_files:
            logging.info("[diff] List of changed files:\n" + "\n".join(f" - {f}" for f in changed_files))
        else:
            logging.info("[diff] No changed files found.")

        return changed_files

    except git.exc.GitCommandError as diff_error:
        logging.error(f"[diff] Git diff error: \n{diff_error.stderr}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"[diff] Failed to get diff:\n{traceback.format_exc()}")
        sys.exit(1)

def update_lfs_files(local_subdir_path: str):
    try:
        logging.info(f"[lfs] Update Git LFS files from subdir: {local_subdir_path}")
        repo = git.Repo(local_subdir_path, search_parent_directories=True)
        repo_root = repo.git.rev_parse("--show-toplevel")
        logging.info(f"[lfs] Git repository root: {repo_root}")

        result = git.Git(local_subdir_path).execute(["git", "lfs", "pull"])
        logging.info("[lfs] Completed git lfs pull")
        if result:
            logging.debug(f"[lfs] Output:\n{result}")

    except git.exc.GitCommandError as ge:
        logging.error(f"[lfs] GitCommandError:\n{ge.stderr}")
        sys.exit(1)
    except git.exc.InvalidGitRepositoryError:
        logging.error(f"[lfs] Invalid Git repository (no .git found in hierarchy): {local_subdir_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"[lfs] Exception during git lfs pull:\n{traceback.format_exc()}")
        sys.exit(1)

def commit_changes(commit_message: str, local_repo_path: str, build_agent: str):
    repo = None
    try:
        logging.info(f"[commit] Initializing repo at {local_repo_path}")
        repo = git.Repo(local_repo_path)
        author = git.Actor(build_agent, "no-reply_cq_devops@wemade.com")

        logging.info("[commit] Adding all changes to staging.")
        repo.git.add(A=True)

        diff_status = repo.index.diff("HEAD")
        if not diff_status:
            logging.info("[commit] No changes detected. Skipping commit.")
            return

        logging.info(f"[commit] Changes detected: {diff_status}")
        logging.info(f"[commit] Committing with message: {commit_message}")
        repo.index.commit(commit_message, author=author, committer=author)
        logging.info("[commit] Commit completed successfully.")

    except Exception as e:
        logging.error(f"[commit] Failed Git Commit: \n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        if repo is not None:
            logging.info("[commit] Closing repository to release resources.")
            repo.close()

def push_changes(branch: str, local_repo_path: str, remote_name: str, RepoURL: str):
    try:
        repo = git.Repo(local_repo_path)

        if remote_name in repo.remotes:
            remote = repo.remotes[remote_name]
        elif "origin" in repo.remotes:
            remote = repo.remotes["origin"]
        else:
            logging.info(f"[setup] No remote found. Creating remote '{remote_name}' with URL: {RepoURL}")
            remote = repo.create_remote(remote_name, RepoURL)

        remote.push(branch)
        logging.info(f"[push] Completed push to remote '{remote_name}'.")
        return True

    except Exception as e:
        logging.error(f"[push] Failed Git Push: \n{e}")
        sys.exit(1)

def fetch_repo(auth_git_url: str, remote_name: str, branch: str, local_repo_path: str):
    try:
        if not os.path.exists(os.path.join(local_repo_path, ".git")):
            logging.info("[clone] Local Repository does not exist. Run git clone.")
            git.Repo.clone_from(auth_git_url, local_repo_path)
        else:
            logging.info("[fetch] Local Repository exists. Run git fetch/reset.")
            repo = git.Repo(local_repo_path)

            if remote_name in repo.remotes:
                remote = repo.remotes[remote_name]
            elif "origin" in repo.remotes:
                remote = repo.remotes["origin"]
            else:
                clean_url = auth_git_url.split("x-access-token:")[0] + auth_git_url.split("@", 1)[1]
                logging.info(f"[setup] No remote found. Creating remote '{remote_name}' with URL: {clean_url}")
                remote = repo.create_remote(remote_name, clean_url)

            repo.git.update_environment(GIT_TERMINAL_PROMPT="0")

            try:
                remote.fetch(branch)
                repo.git.reset("--hard", f"{remote_name}/{branch}")
                logging.info("[fetch] Completed fetch and reset to remote branch.")
            except git.exc.GitCommandError as fetch_error:
                logging.warning(f"[fetch] Fetch encountered an issue: {fetch_error.stderr}")
                sys.exit(1)

            add_safe_directory(local_repo_path)

    except Exception as e:
        logging.error(f"[clone/fetch] Failed git clone or git fetch: \n{traceback.format_exc()}")
        sys.exit(1)

def pull_repo(auth_git_url: str, remote_name: str, branch: str, local_repo_path: str):
    try:
        if not os.path.exists(os.path.join(local_repo_path, ".git")):
            logging.info("[clone] Local Repository does not exist. Run git clone.")
            git.Repo.clone_from(auth_git_url, local_repo_path)
        else:
            logging.info("[pull] Local Repository exists. Run git pull.")
            repo = git.Repo(local_repo_path)

            if remote_name in repo.remotes:
                remote = repo.remotes[remote_name]
            elif "origin" in repo.remotes:
                remote = repo.remotes["origin"]
            else:
                clean_url = auth_git_url.split("x-access-token:")[0] + auth_git_url.split("@", 1)[1]
                logging.info(f"[setup] No remote found. Creating remote '{remote_name}' with URL: {clean_url}")
                remote = repo.create_remote(remote_name, clean_url)

            repo.git.update_environment(GIT_TERMINAL_PROMPT="0")

            try:
                remote.pull(branch)
                logging.info("[pull] Completed pull and reset to remote branch.")
            except git.exc.GitCommandError as pull_error:
                logging.warning(f"[pull] Pull encountered an issue: {pull_error.stderr}")
                sys.exit(1)

            add_safe_directory(local_repo_path)

    except Exception as e:
        logging.error(f"[clone/pull] Failed git clone or git pull: \n{traceback.format_exc()}")
        sys.exit(1)
