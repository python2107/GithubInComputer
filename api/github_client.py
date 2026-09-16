import requests
import json
import os
import time
from urllib.parse import quote


class GitHubClient:
    API_BASE = "https://api.github.com"

    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"token {token}"
        self.session.headers["Accept"] = "application/vnd.github.v3+json"
        self.cache = {}

    def _cache_key(self, method, url, params):
        return f"{method}:{url}:{json.dumps(params, sort_keys=True, default=str)}"

    def _get(self, path, params=None, use_cache=False, cache_ttl=60):
        url = self.API_BASE + path if path.startswith("/") else path
        key = self._cache_key("GET", url, params)
        if use_cache and key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["time"] < cache_ttl:
                return entry["data"]
        try:
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if use_cache:
                self.cache[key] = {"time": time.time(), "data": data}
            return data
        except requests.RequestException as e:
            return {"error": str(e)}

    def _post(self, path, json_data=None):
        url = self.API_BASE + path if path.startswith("/") else path
        try:
            resp = self.session.post(url, json=json_data, timeout=15)
            resp.raise_for_status()
            return resp.json() if resp.text else {"success": True}
        except requests.RequestException as e:
            return {"error": str(e)}

    def _put(self, path, json_data=None):
        url = self.API_BASE + path if path.startswith("/") else path
        try:
            resp = self.session.put(url, json=json_data, timeout=15)
            resp.raise_for_status()
            return resp.json() if resp.text else {"success": True}
        except requests.RequestException as e:
            return {"error": str(e)}

    def _delete(self, path):
        url = self.API_BASE + path if path.startswith("/") else path
        try:
            resp = self.session.delete(url, timeout=15)
            resp.raise_for_status()
            return {"success": True}
        except requests.RequestException as e:
            return {"error": str(e)}

    def _patch(self, path, json_data=None):
        url = self.API_BASE + path if path.startswith("/") else path
        try:
            resp = self.session.patch(url, json=json_data, timeout=15)
            resp.raise_for_status()
            return resp.json() if resp.text else {"success": True}
        except requests.RequestException as e:
            return {"error": str(e)}

    def clear_cache(self):
        self.cache.clear()

    def authenticated(self):
        if not self.token:
            return False
        data = self._get("/user")
        return "login" in data

    def get_user(self):
        return self._get("/user", use_cache=True)

    def get_user_profile(self, username):
        return self._get(f"/users/{quote(username)}", use_cache=True)

    def list_repos(self, username=None, page=1, per_page=30):
        if username:
            return self._get(f"/users/{quote(username)}/repos", params={"page": page, "per_page": per_page}, use_cache=True)
        return self._get("/user/repos", params={"page": page, "per_page": per_page}, use_cache=True)

    def get_repo(self, owner, repo):
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}", use_cache=True)

    def get_readme(self, owner, repo):
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/readme", use_cache=True)

    def get_contents(self, owner, repo, path="", ref=None):
        params = {"ref": ref} if ref else {}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/contents/{path}", params=params, use_cache=True)

    def list_commits(self, owner, repo, sha=None, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        if sha:
            params["sha"] = sha
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/commits", params=params, use_cache=True)

    def list_issues(self, owner, repo, state="open", page=1, per_page=30):
        params = {"state": state, "page": page, "per_page": per_page}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/issues", params=params, use_cache=True)

    def get_issue(self, owner, repo, number):
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/issues/{number}", use_cache=True)

    def list_prs(self, owner, repo, state="open", page=1, per_page=30):
        params = {"state": state, "page": page, "per_page": per_page}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/pulls", params=params, use_cache=True)

    def get_pr(self, owner, repo, number):
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/pulls/{number}", use_cache=True)

    def list_notifications(self, all=False, page=1, per_page=30):
        params = {"all": "true" if all else "false", "page": page, "per_page": per_page}
        return self._get("/notifications", params=params)

    def search_repos(self, query, page=1, per_page=30):
        params = {"q": query, "page": page, "per_page": per_page}
        return self._get("/search/repositories", params=params, use_cache=True)

    def search_users(self, query, page=1, per_page=30):
        params = {"q": query, "page": page, "per_page": per_page}
        return self._get("/search/users", params=params, use_cache=True)

    def get_rate_limit(self):
        return self._get("/rate_limit", use_cache=True)

    def create_repo(self, name, description="", private=False, auto_init=True):
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        return self._post("/user/repos", json_data=data)

    def star_repo(self, owner, repo):
        result = self._put(f"/user/starred/{quote(owner)}/{quote(repo)}")
        if "success" in result:
            self.clear_cache()
        return result

    def unstar_repo(self, owner, repo):
        result = self._delete(f"/user/starred/{quote(owner)}/{quote(repo)}")
        if "success" in result:
            self.clear_cache()
        return result

    def is_starred(self, owner, repo):
        url = f"{self.API_BASE}/user/starred/{quote(owner)}/{quote(repo)}"
        try:
            resp = self.session.get(url, timeout=15)
            return resp.status_code == 204
        except requests.RequestException:
            return False

    def watch_repo(self, owner, repo):
        result = self._put(f"/repos/{quote(owner)}/{quote(repo)}/subscription", json_data={"subscribed": True})
        if "success" in result:
            self.clear_cache()
        return result

    def unwatch_repo(self, owner, repo):
        result = self._delete(f"/repos/{quote(owner)}/{quote(repo)}/subscription")
        if "success" in result:
            self.clear_cache()
        return result

    def fork_repo(self, owner, repo, organization=None):
        data = {"organization": organization} if organization else None
        return self._post(f"/repos/{quote(owner)}/{quote(repo)}/forks", json_data=data)

    def create_issue(self, owner, repo, title, body=""):
        data = {"title": title, "body": body}
        return self._post(f"/repos/{quote(owner)}/{quote(repo)}/issues", json_data=data)

    def create_pull_request(self, owner, repo, title, head, base, body=""):
        data = {"title": title, "head": head, "base": base, "body": body}
        return self._post(f"/repos/{quote(owner)}/{quote(repo)}/pulls", json_data=data)

    def list_starred_repos(self, username=None, page=1, per_page=30):
        if username:
            return self._get(f"/users/{quote(username)}/starred", params={"page": page, "per_page": per_page}, use_cache=True)
        return self._get("/user/starred", params={"page": page, "per_page": per_page}, use_cache=True)

    def list_releases(self, owner, repo, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/releases", params=params, use_cache=True)

    def list_tags(self, owner, repo, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/tags", params=params, use_cache=True)

    def list_workflows(self, owner, repo, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/repos/{quote(owner)}/{quote(repo)}/actions/workflows", params=params, use_cache=True)

    def list_workflow_runs(self, owner, repo, workflow_id=None, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        path = f"/repos/{quote(owner)}/{quote(repo)}/actions/runs"
        if workflow_id:
            path = f"/repos/{quote(owner)}/{quote(repo)}/actions/workflows/{workflow_id}/runs"
        return self._get(path, params=params, use_cache=True)

    def get_org(self, org):
        return self._get(f"/orgs/{quote(org)}", use_cache=True)

    def list_org_repos(self, org, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/orgs/{quote(org)}/repos", params=params, use_cache=True)

    def list_org_members(self, org, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/orgs/{quote(org)}/members", params=params, use_cache=True)

    def list_org_teams(self, org, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}
        return self._get(f"/orgs/{quote(org)}/teams", params=params, use_cache=True)

    @staticmethod
    def decode_content(content_item):
        import base64
        if not isinstance(content_item, dict):
            return ""
        encoded = content_item.get("content", "")
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded).decode("utf-8", errors="replace")
        except Exception:
            return ""
