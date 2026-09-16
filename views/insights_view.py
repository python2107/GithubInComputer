import tkinter as tk
import threading
from .base_view import BaseView


class InsightsView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.owner = ""
        self.repo = ""
        self.build()

    def build(self):
        header = tk.Frame(self, bg=self.theme.get("bg"))
        header.pack(fill="x", padx=24, pady=(24, 12))

        self.title_label = tk.Label(
            header,
            text="Insights",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.repo_entry = tk.Entry(
            header,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=30,
        )
        self.repo_entry.pack(side="right", padx=8, pady=4)
        self.repo_entry.bind("<Return>", lambda e: self.parse_and_load(self.repo_entry.get()))

        load_btn = tk.Button(
            header,
            text="Load",
            command=lambda: self.parse_and_load(self.repo_entry.get()),
            bg=self.theme.get("accent"),
            fg="#ffffff",
            activebackground=self.theme.get("accent_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=12,
            pady=4,
        )
        load_btn.pack(side="right")

        self.content = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        self.content.pack(fill="both", expand=True, padx=24, pady=(12, 24))

        self.info_label = tk.Label(
            self.content,
            text="Enter owner/repo to see insights.",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            justify="left",
            padx=16,
            pady=16,
        )
        self.info_label.pack(anchor="nw")

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.repo_entry.delete(0, "end")
        self.repo_entry.insert(0, f"{owner}/{repo}")
        self.refresh()

    def parse_and_load(self, text):
        text = text.strip()
        if "/" in text:
            owner, repo = text.split("/", 1)
            self.set_repo(owner, repo)

    def refresh(self):
        for child in list(self.content.winfo_children()):
            child.destroy()
        self.info_label = tk.Label(
            self.content,
            text="Loading...",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            padx=16,
            pady=16,
        )
        self.info_label.pack(anchor="nw")

        def load():
            data = self.app.client.get_repo(self.owner, self.repo) if self.app.client else {}
            commits = self.app.client.list_commits(self.owner, self.repo, per_page=5) if self.app.client else []
            self.after(0, lambda: self.populate(data, commits))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, data, commits):
        for child in list(self.content.winfo_children()):
            child.destroy()
        if isinstance(data, dict) and "error" in data:
            tk.Label(self.content, text=f"Error: {data['error']}", bg=self.theme.get("bg_secondary"), fg=self.theme.get("danger"), font=self.theme.get("font_main"), padx=16, pady=16).pack(anchor="nw")
            return
        if not data:
            tk.Label(self.content, text="No data available.", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main"), padx=16, pady=16).pack(anchor="nw")
            return

        stats = [
            f"Repository: {data.get('full_name')}",
            f"Stars: {data.get('stargazers_count', 0)}",
            f"Forks: {data.get('forks_count', 0)}",
            f"Open issues: {data.get('open_issues_count', 0)}",
            f"Watchers: {data.get('watchers_count', 0)}",
            f"Language: {data.get('language') or 'N/A'}",
            f"Created: {data.get('created_at', '')[:10]}",
            f"Updated: {data.get('updated_at', '')[:10]}",
        ]
        tk.Label(
            self.content,
            text="\n".join(stats),
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_main"),
            justify="left",
            anchor="w",
            padx=16,
            pady=16,
        ).pack(anchor="nw")

        tk.Label(
            self.content,
            text="Recent commits",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            padx=16,
            pady=(16, 8),
        ).pack(anchor="nw", fill="x")

        for commit in commits[:5]:
            c = commit.get("commit", {})
            msg = c.get("message", "").split("\n")[0]
            author = c.get("author", {}).get("name", "")
            date = c.get("author", {}).get("date", "")[:10]
            tk.Label(
                self.content,
                text=f"{date} · {author}: {msg}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
                anchor="w",
                padx=24,
                pady=2,
            ).pack(anchor="nw", fill="x")
