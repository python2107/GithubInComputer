import tkinter as tk
import threading
from .base_view import BaseView
from widgets import MarkdownViewer


class PRDetailView(BaseView):
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
            text="Pull request",
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

    def set_pr(self, owner, repo, number):
        self.owner = owner
        self.repo = repo
        self.number = number
        self.refresh()

    def refresh(self):
        if not self.owner or not self.repo or not self.number:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — PR #{self.number}")
        self.body_viewer.set_text("Loading...")

        def load():
            pr = self.app.client.get_pr(self.owner, self.repo, self.number) if self.app.client else {}
            self.after(0, lambda: self.populate(pr))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, pr):
        if isinstance(pr, dict) and "error" in pr:
            self.title_label.configure(text=f"Error: {pr['error']}")
            return
        if not pr:
            self.title_label.configure(text="Pull request not found")
            return
        self.title_label.configure(text=pr.get("title", "Untitled"))
        user = pr.get("user", {}).get("login", "")
        state = pr.get("state", "")
        head = pr.get("head", {}).get("ref", "")
        base = pr.get("base", {}).get("ref", "")
        created = pr.get("created_at", "")[:10]
        self.meta_label.configure(text=f"#{self.number} · {state} · {head} → {base} · opened by {user} on {created}")
        self.body_viewer.set_text(pr.get("body") or "No description provided.")
