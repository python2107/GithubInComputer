import tkinter as tk
import threading
from .base_view import BaseView
from widgets import RepoCard


class ExploreView(BaseView):
    TOPICS = [
        ("stars:>1000 language:python", "Popular Python"),
        ("stars:>1000 language:javascript", "Popular JavaScript"),
        ("stars:>1000 language:rust", "Popular Rust"),
        ("stars:>1000 language:go", "Popular Go"),
        ("trending", "Trending (search)"),
    ]

    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.repo_cards = []
        self.build()

    def build(self):
        tk.Label(
            self,
            text="Explore",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(24, 12))

        topics = tk.Frame(self, bg=self.theme.get("bg"))
        topics.pack(fill="x", padx=24, pady=8)

        for query, label in self.TOPICS:
            btn = tk.Button(
                topics,
                text=label,
                command=lambda q=query: self.load_topic(q),
                bg=self.theme.get("bg_tertiary"),
                fg=self.theme.get("fg"),
                activebackground=self.theme.get("border"),
                activeforeground=self.theme.get("fg"),
                relief="flat",
                bd=0,
                cursor="hand2",
                font=self.theme.get("font_main"),
                padx=12,
                pady=6,
            )
            btn.pack(side="left", padx=(0, 8))

        self.results_frame = tk.Frame(self, bg=self.theme.get("bg"))
        self.results_frame.pack(fill="both", expand=True, padx=24, pady=12)

    def refresh(self):
        self.load_topic("stars:>1000 language:python")

    def load_topic(self, query):
        for card in self.repo_cards:
            card.destroy()
        self.repo_cards = []
        for child in list(self.results_frame.winfo_children()):
            child.destroy()

        if not self.app.client:
            tk.Label(self.results_frame, text="Please sign in to explore.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
            return

        def load():
            if query == "trending":
                result = self.app.client.search_repos("stars:>100 created:>2024-01-01", per_page=20)
            else:
                result = self.app.client.search_repos(query, per_page=20)
            self.after(0, lambda: self.populate(result))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, result):
        items = result.get("items", []) if isinstance(result, dict) else []
        if isinstance(result, dict) and "error" in result:
            tk.Label(self.results_frame, text=f"Error: {result['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=40)
            return
        if not items:
            tk.Label(self.results_frame, text="No repositories found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
            return
        for repo in items:
            card = RepoCard(self.results_frame, self.app, self.theme, repo)
            card.pack(fill="x", pady=(0, 12))
            self.repo_cards.append(card)
