import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class RepoListView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.repo_cards = []
        self.build()

    def build(self):
        header = tk.Frame(self, bg=self.theme.get("bg"))
        header.pack(fill="x", padx=24, pady=(24, 12))

        tk.Label(
            header,
            text="Repositories",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(side="left")

        self.filter_var = tk.StringVar(value="all")
        for val, label in (("all", "All"), ("owner", "Owner"), ("member", "Member")):
            tk.Radiobutton(
                header,
                text=label,
                variable=self.filter_var,
                value=val,
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg"),
                selectcolor=self.theme.get("bg_tertiary"),
                activebackground=self.theme.get("bg"),
                font=self.theme.get("font_main"),
                command=self.refresh,
            ).pack(side="right", padx=(8, 0))

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
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []

        if not self.app.client or not self.app.client.token:
            tk.Label(
                self.inner,
                text="Please sign in to view repositories.",
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(pady=40)
            return

        def load():
            repos = self.app.client.list_repos(per_page=50)
            self.after(0, lambda: self.populate(repos))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, repos):
        if isinstance(repos, dict) and "error" in repos:
            tk.Label(
                self.inner,
                text=f"Error: {repos['error']}",
                bg=self.theme.get("bg"),
                fg=self.theme.get("danger"),
                font=self.theme.get("font_main"),
            ).pack(pady=40)
            return

        filt = self.filter_var.get()
        if filt == "owner":
            repos = [r for r in repos if r.get("owner", {}).get("login") == self.app.user.get("login")]
        elif filt == "member":
            repos = [r for r in repos if r.get("owner", {}).get("login") != self.app.user.get("login")]

        if not repos:
            tk.Label(
                self.inner,
                text="No repositories found.",
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
            ).pack(pady=40)
            return

        for repo in repos:
            card = RepoCard(self.inner, self.app, self.theme, repo)
            card.pack(fill="x", padx=24, pady=(0, 12))
            self.repo_cards.append(card)
