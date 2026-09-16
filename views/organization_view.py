import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class OrganizationView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.org = ""
        self.repo_cards = []
        self.build()

    def build(self):
        self.header = tk.Frame(self, bg=self.theme.get("bg"))
        self.header.pack(fill="x", padx=24, pady=(24, 12))

        self.name_label = tk.Label(
            self.header,
            text="Organization",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.name_label.pack(side="left")

        self.entry = tk.Entry(
            self.header,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=24,
        )
        self.entry.pack(side="right", padx=8)
        self.entry.bind("<Return>", lambda e: self.load_org(self.entry.get().strip()))

        tk.Button(
            self.header,
            text="View",
            command=lambda: self.load_org(self.entry.get().strip()),
            bg=self.theme.get("accent"),
            fg="#ffffff",
            activebackground=self.theme.get("accent_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=12,
            pady=4,
        ).pack(side="right")

        self.info_frame = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        self.info_frame.pack(fill="x", padx=24, pady=12)

        self.info_label = tk.Label(
            self.info_frame,
            text="Enter an organization name.",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            wraplength=600,
            padx=12,
            pady=12,
        )
        self.info_label.pack(fill="x")

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

    def set_org(self, org):
        self.load_org(org)

    def load_org(self, org):
        self.org = org
        if not org:
            return
        self.name_label.configure(text=f"Organization: {org}")
        self.entry.delete(0, "end")
        self.entry.insert(0, org)
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []

        def load():
            data = self.app.client.get_org(org) if self.app.client else {}
            repos = self.app.client.list_org_repos(org, per_page=30) if self.app.client else []
            self.after(0, lambda: self.populate(data, repos))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, data, repos):
        if isinstance(data, dict) and "error" in data:
            self.info_label.configure(text=f"Error: {data['error']}")
            return
        if data:
            parts = [
                f"Name: {data.get('name') or data.get('login')}",
                f"Description: {data.get('description') or 'N/A'}",
                f"Location: {data.get('location') or 'N/A'}",
                f"Public repos: {data.get('public_repos', 0)}",
                f"Members: {data.get('followers', 0)}",
            ]
            self.info_label.configure(text="\n".join(parts))

        if isinstance(repos, dict) and "error" in repos:
            tk.Label(self.inner, text=f"Error: {repos['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=20)
            return
        for repo in repos:
            card = RepoCard(self.inner, self.app, self.theme, repo)
            card.pack(fill="x", padx=24, pady=(0, 12))
            self.repo_cards.append(card)
