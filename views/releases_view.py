import tkinter as tk
import threading
from .base_view import BaseView


class ReleasesView(BaseView):
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
            text="Releases",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

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
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Releases")

        def load():
            releases = self.app.client.list_releases(self.owner, self.repo, per_page=30) if self.app.client else []
            tags = self.app.client.list_tags(self.owner, self.repo, per_page=30) if self.app.client else []
            self.after(0, lambda: self.populate(releases, tags))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, releases, tags):
        if isinstance(releases, dict) and "error" in releases:
            tk.Label(self.inner, text=f"Error: {releases['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=40)
            return
        if not releases:
            tk.Label(self.inner, text="No releases found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
        else:
            for rel in releases:
                frame = tk.Frame(self.inner, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
                frame.pack(fill="x", padx=24, pady=(0, 8))
                tk.Label(
                    frame,
                    text=rel.get("name") or rel.get("tag_name", "Untitled"),
                    bg=self.theme.get("bg_secondary"),
                    fg=self.theme.get("fg"),
                    font=self.theme.get("font_header"),
                    anchor="w",
                ).pack(fill="x", padx=12, pady=(12, 4))
                tk.Label(
                    frame,
                    text=f"Tag: {rel.get('tag_name')} · {rel.get('created_at', '')[:10]} · {'Pre-release' if rel.get('prerelease') else 'Release'}",
                    bg=self.theme.get("bg_secondary"),
                    fg=self.theme.get("fg_muted"),
                    font=self.theme.get("font_main"),
                    anchor="w",
                ).pack(fill="x", padx=12, pady=(0, 12))

        tk.Label(
            self.inner,
            text="Tags",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(16, 8))

        if not tags:
            tk.Label(self.inner, text="No tags found.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=20)
        else:
            for tag in tags:
                frame = tk.Frame(self.inner, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
                frame.pack(fill="x", padx=24, pady=(0, 8))
                tk.Label(
                    frame,
                    text=tag.get("name", ""),
                    bg=self.theme.get("bg_secondary"),
                    fg=self.theme.get("link"),
                    font=self.theme.get("font_main"),
                    anchor="w",
                ).pack(fill="x", padx=12, pady=12)
