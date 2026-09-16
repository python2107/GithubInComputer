import os
import subprocess
from datetime import datetime


class LocalRepo:
    def __init__(self, path=""):
        self.path = path

    def is_repo(self):
        if not self.path:
            return False
        return os.path.isdir(os.path.join(self.path, ".git"))

    def run(self, args):
        if not self.is_repo():
            return ""
        try:
            result = subprocess.run(
                ["git", "-C", self.path] + args,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def get_branches(self):
        out = self.run(["branch", "-a", "--format=%(refname:short)"])
        return [b.strip() for b in out.split("\n") if b.strip()]

    def get_current_branch(self):
        return self.run(["branch", "--show-current"])

    def get_log(self, max_count=30):
        fmt = "%H\t%an\t%ae\t%ad\t%s"
        out = self.run(["log", f"--max-count={max_count}", f"--pretty=format:{fmt}"])
        commits = []
        for line in out.split("\n"):
            parts = line.split("\t", 4)
            if len(parts) == 5:
                commits.append({
                    "sha": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                })
        return commits

    def get_files(self, path=""):
        target = os.path.join(self.path, path) if self.path else path
        if not os.path.isdir(target):
            return []
        items = []
        try:
            for entry in os.scandir(target):
                if entry.name.startswith("."):
                    continue
                items.append({
                    "name": entry.name,
                    "type": "dir" if entry.is_dir() else "file",
                    "path": os.path.join(path, entry.name).replace("\\", "/"),
                })
        except Exception:
            pass
        items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
        return items

    def read_file(self, path):
        target = os.path.join(self.path, path) if self.path else path
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def get_status(self):
        out = self.run(["status", "--short"])
        changes = []
        for line in out.split("\n"):
            if line.strip():
                changes.append({"status": line[:2].strip(), "file": line[3:].strip()})
        return changes

    def _env(self, ssh_key_path=""):
        env = os.environ.copy()
        if ssh_key_path and os.path.isfile(ssh_key_path):
            env["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"
        return env

    def _run_with_env(self, args, ssh_key_path=""):
        if not self.is_repo():
            return {"stdout": "", "stderr": "Not a git repository", "code": -1}
        try:
            result = subprocess.run(
                ["git", "-C", self.path] + args,
                capture_output=True,
                text=True,
                check=False,
                env=self._env(ssh_key_path),
            )
            return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "code": result.returncode}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "code": -1}

    def get_remotes(self):
        out = self.run(["remote", "-v"])
        remotes = {}
        for line in out.split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                remotes[parts[0]] = parts[1]
        return remotes

    def add_remote(self, name, url):
        return self._run_with_env(["remote", "add", name, url])

    def fetch(self, remote="origin", ssh_key_path=""):
        return self._run_with_env(["fetch", remote], ssh_key_path)

    def pull(self, remote="origin", branch="", ssh_key_path=""):
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return self._run_with_env(args, ssh_key_path)

    def push(self, remote="origin", branch="", ssh_key_path=""):
        args = ["push", remote]
        if branch:
            args.append(branch)
        return self._run_with_env(args, ssh_key_path)

    def clone(self, url, dest, ssh_key_path=""):
        return self._run_with_env(["clone", url, dest], ssh_key_path)

    def set_user_config(self, name, email):
        self._run_with_env(["config", "user.name", name])
        return self._run_with_env(["config", "user.email", email])
