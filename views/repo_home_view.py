import tkinter as tk
import threading
import base64
from .base_view import BaseView
from widgets import MarkdownViewer


class RepoHomeView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.owner = ""
        self.repo = ""
        self.build()

    def build(self):
        self.header = tk.Frame(self, bg=self.theme.get("bg"))
        self.header.pack(fill="x", padx=24, pady=(24, 8))

        self.name_label = tk.Label(
            self.header,
            text="Select a repository",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.name_label.pack(side="left")

        self.actions = tk.Frame(self.header, bg=self.theme.get("bg"))
        self.actions.pack(side="right")

        self.star_btn = self._action_btn("Star", self.toggle_star)
        self.watch_btn = self._action_btn("Watch", self.toggle_watch)
        self.fork_btn = self._action_btn("Fork", self.fork_repo)
        self.push_btn = self._action_btn("Push", self.push_repo)

        self.tabs = tk.Frame(self.header, bg=self.theme.get("bg"))
        self.tabs.pack(side="left", padx=(24, 0), pady=(8, 0))

        for tab, label in (("code", "Code"), ("issues", "Issues"), ("prs", "Pull requests"), ("actions", "Actions"), ("releases", "Releases"), ("commits", "Commits"), ("settings", "Settings")):
            btn = tk.Button(
                self.tabs,
                text=label,
                command=lambda t=tab: self.on_tab(t),
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                activebackground=self.theme.get("bg_secondary"),
                activeforeground=self.theme.get("fg"),
                relief="flat",
                bd=0,
                cursor="hand2",
                font=self.theme.get("font_main"),
                padx=12,
                pady=4,
            )
            btn.pack(side="left", padx=(0, 4))

        self.about_frame = tk.Frame(self, bg=self.theme.get("bg"))
        self.about_frame.pack(fill="x", padx=24, pady=(8, 0))

        self.desc_label = tk.Label(
            self.about_frame,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            wraplength=600,
            justify="left",
        )
        self.desc_label.pack(side="left")

        self.content = tk.Frame(self, bg=self.theme.get("bg"))
        self.content.pack(fill="both", expand=True, padx=24, pady=(16, 24))

        self.readme_label = tk.Label(
            self.content,
            text="README",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            padx=12,
            pady=8,
        )
        self.readme_label.pack(fill="x")

        self.readme = MarkdownViewer(self.content, self.theme, height=20)
        self.readme.pack(fill="both", expand=True)

        self.stats_label = tk.Label(
            self.content,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_subtle"),
            font=self.theme.get("font_main"),
            anchor="w",
        )
        self.stats_label.pack(fill="x", pady=(8, 0))

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.refresh()

    def refresh(self):
        if not self.owner or not self.repo:
            return
        self.name_label.configure(text=f"{self.owner} / {self.repo}")
        self.readme.set_text("Loading README...")

        def load():
            if not self.app.client:
                self.after(0, lambda: self.populate({}, {}))
                return
            data = self.app.client.get_repo(self.owner, self.repo)
            readme = self.app.client.get_readme(self.owner, self.repo)
            starred = self.app.client.is_starred(self.owner, self.repo)
            self.after(0, lambda: self.populate(data, readme, starred))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, data, readme, starred=False):
        if isinstance(data, dict) and "error" not in data:
            self.desc_label.configure(text=data.get("description") or "No description provided.")
            stats = []
            for k, label in (("stargazers_count", "★ stars"), ("forks_count", "⑂ forks"), ("open_issues_count", "! issues"), ("language", "● language")):
                val = data.get(k)
                if val:
                    stats.append(f"{label}: {val}")
            self.stats_label.configure(text="  |  ".join(stats))
            self._set_action_text(self.star_btn, "Unstar" if starred else "Star")
            self._set_action_text(self.watch_btn, "Unwatch" if data.get("subscribed") else "Watch")
        elif isinstance(data, dict) and "error" in data:
            self.desc_label.configure(text=f"Error: {data['error']}")

        readme_text = ""
        if isinstance(readme, dict) and "content" in readme:
            try:
                readme_text = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
            except Exception:
                readme_text = "Unable to decode README."
        elif isinstance(readme, dict) and "error" in readme:
            readme_text = f"Error loading README: {readme['error']}"
        else:
            readme_text = "No README found."
        self.readme.set_text(readme_text)

    def on_tab(self, tab):
        if tab == "code":
            self.app.show_view("code_browser", owner=self.owner, repo=self.repo)
        elif tab == "issues":
            self.app.show_view("issue_list", owner=self.owner, repo=self.repo)
        elif tab == "prs":
            self.app.show_view("pr_list", owner=self.owner, repo=self.repo)
        elif tab == "actions":
            self.app.show_actions(self.owner, self.repo)
        elif tab == "releases":
            self.app.show_releases(self.owner, self.repo)
        elif tab == "settings":
            self.app.show_repo_settings(self.owner, self.repo)
        elif tab == "commits":
            self.app.show_view("commits", owner=self.owner, repo=self.repo)

    def _action_btn(self, text, command):
        btn = tk.Button(
            self.actions,
            text=text,
            command=command,
            bg=self.theme.get("bg_tertiary"),
            fg=self.theme.get("fg"),
            activebackground=self.theme.get("border"),
            activeforeground=self.theme.get("fg"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=10,
            pady=4,
        )
        btn.pack(side="left", padx=(0, 8))
        return btn

    def _set_action_text(self, btn, text):
        btn.configure(text=text)

    def toggle_star(self):
        if not self.app.client:
            return
        current = self.star_btn.cget("text")
        if current == "Star":
            result = self.app.client.star_repo(self.owner, self.repo)
            if "error" not in result:
                self._set_action_text(self.star_btn, "Unstar")
        else:
            result = self.app.client.unstar_repo(self.owner, self.repo)
            if "error" not in result:
                self._set_action_text(self.star_btn, "Star")
        self.refresh()

    def toggle_watch(self):
        if not self.app.client:
            return
        current = self.watch_btn.cget("text")
        if current == "Watch":
            result = self.app.client.watch_repo(self.owner, self.repo)
            if "error" not in result:
                self._set_action_text(self.watch_btn, "Unwatch")
        else:
            result = self.app.client.unwatch_repo(self.owner, self.repo)
            if "error" not in result:
                self._set_action_text(self.watch_btn, "Watch")
        self.refresh()

    def fork_repo(self):
        if not self.app.client:
            return
        result = self.app.client.fork_repo(self.owner, self.repo)
        if "error" not in result:
            full_name = result.get("full_name")
            if full_name:
                owner, repo = full_name.split("/", 1)
                self.app.open_repo(owner, repo)

    def push_repo(self):
        self.app.show_push_dialog(self.owner, self.repo)
