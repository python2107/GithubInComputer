import tkinter as tk
import threading
import os
from .base_view import BaseView
from widgets import FileTree


class CodeBrowserView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.owner = ""
        self.repo = ""
        self.path = ""
        self.build()

    def build(self):
        self.header = tk.Frame(self, bg=self.theme.get("bg"))
        self.header.pack(fill="x", padx=24, pady=(24, 8))

        self.title_label = tk.Label(
            self.header,
            text="Code",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.breadcrumb = tk.Label(
            self.header,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
        )
        self.breadcrumb.pack(side="left", padx=(16, 0))

        self.body = tk.Frame(self, bg=self.theme.get("bg"))
        self.body.pack(fill="both", expand=True, padx=24, pady=(8, 24))
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=2)

        self.tree_frame = tk.Frame(self.body, bg=self.theme.get("bg_secondary"), width=280)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.tree_frame.grid_propagate(False)

        self.file_tree = FileTree(self.tree_frame, self.app, self.theme, self.on_file_select)
        self.file_tree.pack(fill="both", expand=True)

        self.content_frame = tk.Frame(self.body, bg=self.theme.get("bg_secondary"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.file_name_label = tk.Label(
            self.content_frame,
            text="Select a file",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            padx=12,
            pady=8,
        )
        self.file_name_label.grid(row=0, column=0, sticky="ew")

        self.text = tk.Text(
            self.content_frame,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_mono"),
            relief="flat",
            state="disabled",
            padx=12,
            pady=12,
            wrap="none",
        )
        self.text.grid(row=1, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=self.text.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.text.configure(yscrollcommand=self.scrollbar.set)

    def set_repo(self, owner, repo, path=""):
        self.owner = owner
        self.repo = repo
        self.path = path
        self.refresh()

    def refresh(self):
        if not self.owner or not self.repo:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo}")
        self.breadcrumb.configure(text=f"/{self.path}")

        def load():
            data = self.app.client.get_contents(self.owner, self.repo, self.path) if self.app.client else []
            self.after(0, lambda: self.populate(data))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, data):
        if isinstance(data, dict) and "error" in data:
            self.file_tree.clear()
            return
        if not isinstance(data, list):
            data = []
        items = []
        for item in data:
            items.append({
                "name": item.get("name"),
                "type": "dir" if item.get("type") == "dir" else "file",
                "path": item.get("path", ""),
            })
        self.file_tree.load(items)

    def on_file_select(self, item):
        path = item.get("path", "")
        if item.get("type") == "dir":
            self.path = path
            self.breadcrumb.configure(text=f"/{self.path}")
            self.refresh()
            return

        self.file_name_label.configure(text=path)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "Loading...")
        self.text.configure(state="disabled")

        def load():
            data = self.app.client.get_contents(self.owner, self.repo, path) if self.app.client else {}
            if isinstance(data, dict) and "content" in data:
                import base64
                try:
                    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                except Exception as e:
                    content = f"Error decoding file: {e}"
            else:
                content = "Unable to load file content."
            self.after(0, lambda: self.show_content(content))

        threading.Thread(target=load, daemon=True).start()

    def show_content(self, content):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")
