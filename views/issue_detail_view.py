import tkinter as tk
import threading
from .base_view import BaseView
from widgets import MarkdownViewer


class IssueDetailView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.owner = ""
        self.repo = ""
        self.number = 0
        self.build()

    def build(self):
        self.canvas = tk.Canvas(self, bg=self.theme.get("bg"), highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=self.theme.get("bg"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.title_label = tk.Label(
            self.inner,
            text="Issue",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=24, pady=(24, 4))

        self.meta_label = tk.Label(
            self.inner,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
        )
        self.meta_label.pack(fill="x", padx=24, pady=(4, 12))

        self.body_viewer = MarkdownViewer(self.inner, self.theme, height=12)
        self.body_viewer.pack(fill="x", padx=24, pady=(8, 24))

    def set_issue(self, owner, repo, number):
        self.owner = owner
        self.repo = repo
        self.number = number
        self.refresh()

    def refresh(self):
        if not self.owner or not self.repo or not self.number:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Issue #{self.number}")
        self.body_viewer.set_text("Loading...")

        def load():
            issue = self.app.client.get_issue(self.owner, self.repo, self.number) if self.app.client else {}
            self.after(0, lambda: self.populate(issue))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, issue):
        if isinstance(issue, dict) and "error" in issue:
            self.title_label.configure(text=f"Error: {issue['error']}")
            return
        if not issue:
            self.title_label.configure(text="Issue not found")
            return
        self.title_label.configure(text=issue.get("title", "Untitled"))
        user = issue.get("user", {}).get("login", "")
        state = issue.get("state", "")
        created = issue.get("created_at", "")[:10]
        self.meta_label.configure(text=f"#{self.number} · {state} · opened by {user} on {created}")
        self.body_viewer.set_text(issue.get("body") or "No description provided.")
