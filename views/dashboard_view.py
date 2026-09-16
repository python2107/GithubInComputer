import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class DashboardView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.repo_cards = []
        self.build()

    def build(self):
        tk.Label(
            self,
            text="Dashboard",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(24, 12))

        self.welcome = tk.Label(
            self,
            text="Welcome back",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
        )
        self.welcome.pack(fill="x", padx=24, pady=(0, 16))

        top_row = tk.Frame(self, bg=self.theme.get("bg"))
        top_row.pack(fill="x", padx=24, pady=8)

        actions = [
            ("New repository", self.app.show_create_repo_dialog, ()),
            ("Search", self.app.show_view, ("search",)),
            ("Notifications", self.app.show_view, ("notifications",)),
        ]
        for label, cmd, args in actions:
            btn = tk.Button(
                top_row,
                text=label,
                command=lambda c=cmd, a=args: c(*a),
                bg=self.theme.get("bg_tertiary"),
                fg=self.theme.get("fg"),
                activebackground=self.theme.get("border"),
                relief="flat",
                bd=0,
                cursor="hand2",
                font=self.theme.get("font_main"),
                padx=12,
                pady=6,
            )
            btn.pack(side="left", padx=(0, 12))

        tk.Label(
            self,
            text="Recent repositories",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(16, 8))

        self.repos_frame = tk.Frame(self, bg=self.theme.get("bg"))
        self.repos_frame.pack(fill="both", expand=True, padx=24, pady=8)

    def refresh(self):
        user = self.app.user or {}
        self.welcome.configure(text=f"Welcome back, {user.get('login') or 'guest'}")
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []

        if not self.app.client or not self.app.client.token:
            tk.Label(
                self.repos_frame,
                text="Please sign in to view your repositories.",
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(pady=20)
            return

        def load():
            repos = self.app.client.list_repos(per_page=10)
            self.after(0, lambda: self.populate(repos))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, repos):
        if isinstance(repos, dict) and "error" in repos:
            tk.Label(
                self.repos_frame,
                text=f"Error: {repos['error']}",
                bg=self.theme.get("bg"),
                fg=self.theme.get("danger"),
                font=self.theme.get("font_main"),
            ).pack(pady=20)
            return
        if not repos:
            tk.Label(
                self.repos_frame,
                text="No repositories found.",
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(pady=20)
            return
        for repo in repos:
            card = RepoCard(self.repos_frame, self.app, self.theme, repo)
            card.pack(fill="x", pady=(0, 12))
            self.repo_cards.append(card)
