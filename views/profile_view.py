import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class ProfileView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.username = ""
        self.repo_cards = []
        self.build()

    def build(self):
        self.header = tk.Frame(self, bg=self.theme.get("bg"))
        self.header.pack(fill="x", padx=24, pady=(24, 12))

        self.name_label = tk.Label(
            self.header,
            text="Profile",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.name_label.pack(side="left")

        self.search_entry = tk.Entry(
            self.header,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=24,
        )
        self.search_entry.pack(side="right", padx=8, pady=4)
        self.search_entry.bind("<Return>", lambda e: self.load_user(self.search_entry.get().strip()))

        search_btn = tk.Button(
            self.header,
            text="View",
            command=lambda: self.load_user(self.search_entry.get().strip()),
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
        search_btn.pack(side="right")

        self.info_frame = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        self.info_frame.pack(fill="x", padx=24, pady=12)

        self.bio_label = tk.Label(
            self.info_frame,
            text="",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            wraplength=600,
        )
        self.bio_label.pack(fill="x", padx=12, pady=12)

        tk.Label(
            self,
            text="Repositories",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(12, 8))

        self.canvas = tk.Canvas(self, bg=self.theme.get("bg"), highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=self.theme.get("bg"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def refresh(self):
        username = self.username or (self.app.user.get("login") if self.app.user else "")
        self.load_user(username)

    def load_user(self, username):
        self.username = username
        if not username:
            return
        self.name_label.configure(text=f"Profile: {username}")
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []

        def load():
            user = self.app.client.get_user_profile(username) if self.app.client else {}
            repos = self.app.client.list_repos(username, per_page=20) if self.app.client else []
            self.after(0, lambda: self.populate(user, repos))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, user, repos):
        if isinstance(user, dict) and "error" in user:
            self.bio_label.configure(text=f"Error: {user['error']}")
            return
        if user:
            parts = [f"Name: {user.get('name') or user.get('login')}",
                     f"Bio: {user.get('bio') or 'No bio'}",
                     f"Location: {user.get('location') or 'N/A'}",
                     f"Public repos: {user.get('public_repos', 0)} · Followers: {user.get('followers', 0)} · Following: {user.get('following', 0)}"]
            self.bio_label.configure(text="\n".join(parts))

        if isinstance(repos, dict) and "error" in repos:
            tk.Label(self.inner, text=f"Error: {repos['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=20)
            return
        for repo in repos:
            card = RepoCard(self.inner, self.app, self.theme, repo)
            card.pack(fill="x", padx=24, pady=(0, 12))
            self.repo_cards.append(card)
