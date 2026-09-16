import tkinter as tk
import threading
from .base_view import BaseView


class PRListView(BaseView):
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
            text="Pull requests",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.state_var = tk.StringVar(value="open")
        for val, label in (("open", "Open"), ("closed", "Closed"), ("all", "All")):
            tk.Radiobutton(
                self.header,
                text=label,
                variable=self.state_var,
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

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.refresh()

    def refresh(self):
        for child in list(self.inner.winfo_children()):
            child.destroy()
        if not self.owner or not self.repo:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Pull requests")

        def load():
            prs = self.app.client.list_prs(self.owner, self.repo, state=self.state_var.get(), per_page=30) if self.app.client else []
            self.after(0, lambda: self.populate(prs))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, prs):
        if isinstance(prs, dict) and "error" in prs:
            tk.Label(self.inner, text=f"Error: {prs['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=40)
            return
        if not prs:
            tk.Label(self.inner, text="No pull requests found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
            return

        for pr in prs:
            number = pr.get("number")
            title = pr.get("title", "Untitled")
            state = pr.get("state", "")
            user = pr.get("user", {}).get("login", "")
            head = pr.get("head", {}).get("ref", "")
            base = pr.get("base", {}).get("ref", "")

            frame = tk.Frame(self.inner, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
            frame.pack(fill="x", padx=24, pady=(0, 8))

            title_lbl = tk.Label(
                frame,
                text=f"#{number} {title}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("link"),
                font=self.theme.get("font_header"),
                cursor="hand2",
                anchor="w",
                wraplength=700,
            )
            title_lbl.pack(fill="x", padx=12, pady=(12, 4))
            title_lbl.bind("<Button-1>", lambda e, n=number: self.open_pr(n))

            tk.Label(
                frame,
                text=f"{state} by {user} · {head} → {base}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 12))

    def open_pr(self, number):
        self.app.show_view("pr_detail", owner=self.owner, repo=self.repo, number=number)
