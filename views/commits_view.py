import tkinter as tk
import threading
from .base_view import BaseView


class CommitsView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.owner = ""
        self.repo = ""
        self.build()

    def build(self):
        self.header = tk.Frame(self, bg=self.theme.get("bg"))
        self.header.pack(fill="x", padx=24, pady=(24, 12))

        self.title_label = tk.Label(
            self.header,
            text="Commits",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.branch_label = tk.Label(
            self.header,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
        )
        self.branch_label.pack(side="left", padx=(16, 0))

        self.canvas = tk.Canvas(self, bg=self.theme.get("bg"), highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=self.theme.get("bg"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.refresh()

    def refresh(self):
        for child in list(self.inner.winfo_children()):
            child.destroy()
        if not self.owner or not self.repo:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Commits")
        self.branch_label.configure(text="default branch")

        def load():
            commits = self.app.client.list_commits(self.owner, self.repo, per_page=50) if self.app.client else []
            self.after(0, lambda: self.populate(commits))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, commits):
        if isinstance(commits, dict) and "error" in commits:
            tk.Label(
                self.inner,
                text=f"Error: {commits['error']}",
                bg=self.theme.get("bg"),
                fg=self.theme.get("danger"),
                font=self.theme.get("font_main"),
            ).pack(pady=40)
            return
        if not commits:
            tk.Label(
                self.inner,
                text="No commits found.",
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(pady=40)
            return

        for commit in commits:
            data = commit.get("commit", {})
            msg = data.get("message", "").split("\n")[0]
            author = data.get("author", {}).get("name", "Unknown")
            date = data.get("author", {}).get("date", "")[:10]
            sha = commit.get("sha", "")[:7]

            frame = tk.Frame(self.inner, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
            frame.pack(fill="x", padx=24, pady=(0, 8))

            tk.Label(
                frame,
                text=msg,
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg"),
                font=self.theme.get("font_main"),
                anchor="w",
                wraplength=700,
            ).pack(fill="x", padx=12, pady=(12, 4))

            meta = tk.Frame(frame, bg=self.theme.get("bg_secondary"))
            meta.pack(fill="x", padx=12, pady=(0, 12))
            tk.Label(
                meta,
                text=f"{author} · {date} · {sha}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(side="left")
