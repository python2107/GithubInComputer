import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class SearchView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.query = ""
        self.repo_cards = []
        self.build()

    def build(self):
        header = tk.Frame(self, bg=self.theme.get("bg"))
        header.pack(fill="x", padx=24, pady=(24, 12))

        tk.Label(
            header,
            text="Search GitHub",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(side="left")

        self.entry = tk.Entry(
            header,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=40,
        )
        self.entry.pack(side="left", padx=(24, 8), pady=4)
        self.entry.bind("<Return>", lambda e: self.do_search())

        search_btn = tk.Button(
            header,
            text="Search",
            command=self.do_search,
            bg=self.theme.get("accent"),
            fg="#ffffff",
            activebackground=self.theme.get("accent_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=16,
            pady=4,
        )
        search_btn.pack(side="left")

        self.type_var = tk.StringVar(value="repositories")
        for val, label in (("repositories", "Repositories"), ("users", "Users")):
            tk.Radiobutton(
                header,
                text=label,
                variable=self.type_var,
                value=val,
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg"),
                selectcolor=self.theme.get("bg_tertiary"),
                activebackground=self.theme.get("bg"),
                font=self.theme.get("font_main"),
                command=self.do_search,
            ).pack(side="left", padx=(16, 0))

        self.results_frame = tk.Frame(self, bg=self.theme.get("bg"))
        self.results_frame.pack(fill="both", expand=True, padx=24, pady=12)

    def set_query(self, query):
        self.query = query
        self.entry.delete(0, "end")
        self.entry.insert(0, query)
        self.do_search()

    def do_search(self):
        query = self.entry.get().strip()
        if not query:
            return
        self.query = query
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []
        for child in list(self.results_frame.winfo_children()):
            child.destroy()

        kind = self.type_var.get()

        def load():
            if kind == "repositories":
                result = self.app.client.search_repos(query) if self.app.client else {"items": []}
                self.after(0, lambda: self.populate_repos(result))
            else:
                result = self.app.client.search_users(query) if self.app.client else {"items": []}
                self.after(0, lambda: self.populate_users(result))

        threading.Thread(target=load, daemon=True).start()

    def populate_repos(self, result):
        items = result.get("items", [])
        if not items:
            tk.Label(self.results_frame, text="No repositories found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=20)
            return
        for repo in items:
            card = RepoCard(self.results_frame, self.app, self.theme, repo)
            card.pack(fill="x", pady=(0, 12))
            self.repo_cards.append(card)

    def populate_users(self, result):
        items = result.get("items", [])
        if not items:
            tk.Label(self.results_frame, text="No users found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=20)
            return
        for user in items:
            frame = tk.Frame(self.results_frame, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
            frame.pack(fill="x", pady=(0, 12))
            lbl = tk.Label(
                frame,
                text=user.get("login", "Unknown"),
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("link"),
                font=self.theme.get("font_header"),
                cursor="hand2",
                padx=12,
                pady=12,
            )
            lbl.pack(anchor="w")
            lbl.bind("<Button-1>", lambda e, u=user.get("login"): self.app.show_profile(u))
            self.repo_cards.append(frame)
