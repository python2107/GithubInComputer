import tkinter as tk


class RepoCard(tk.Frame):
    def __init__(self, parent, app, theme, repo, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.theme = theme
        self.repo = repo
        self.configure(bg=theme.get("bg_secondary"), highlightbackground=theme.get("border"), highlightthickness=1)
        self.build()

    def build(self):
        name = self.repo.get("full_name") or self.repo.get("name", "Unknown")
        desc = self.repo.get("description") or "No description provided."
        lang = self.repo.get("language") or ""
        stars = self.repo.get("stargazers_count", 0)
        forks = self.repo.get("forks_count", 0)
        is_private = self.repo.get("private", False)

        header = tk.Frame(self, bg=self.theme.get("bg_secondary"))
        header.pack(fill="x", padx=12, pady=(12, 4))

        name_label = tk.Label(
            header,
            text=name,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("link"),
            font=self.theme.get("font_header"),
            cursor="hand2",
        )
        name_label.pack(side="left")
        name_label.bind("<Button-1>", self.open_repo)

        if is_private:
            tk.Label(
                header,
                text="Private",
                bg=self.theme.get("bg_tertiary"),
                fg=self.theme.get("fg_muted"),
                font=("Segoe UI", 8),
                padx=6,
                pady=2,
            ).pack(side="left", padx=(8, 0))

        desc_label = tk.Label(
            self,
            text=desc,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            wraplength=500,
            justify="left",
            anchor="w",
        )
        desc_label.pack(fill="x", padx=12, pady=(4, 8))

        meta = tk.Frame(self, bg=self.theme.get("bg_secondary"))
        meta.pack(fill="x", padx=12, pady=(0, 12))

        if lang:
            tk.Label(
                meta,
                text=f"● {lang}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_subtle"),
                font=self.theme.get("font_main"),
            ).pack(side="left", padx=(0, 12))

        star_btn = tk.Button(
            meta,
            text=f"★ {stars}",
            command=self.star_repo,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_subtle"),
            activebackground=self.theme.get("bg_tertiary"),
            activeforeground=self.theme.get("fg"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
        )
        star_btn.pack(side="left", padx=(0, 12))

        tk.Label(
            meta,
            text=f"⑂ {forks}",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_subtle"),
            font=self.theme.get("font_main"),
        ).pack(side="left")

    def star_repo(self):
        name = self.repo.get("full_name", "")
        if not name or "/" not in name or not self.app.client:
            return
        owner, repo = name.split("/", 1)
        self.app.client.star_repo(owner, repo)

    def open_repo(self, event=None):
        owner, repo = self.repo.get("full_name", "/").split("/", 1)
        self.app.open_repo(owner, repo)
