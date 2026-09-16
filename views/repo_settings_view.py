import tkinter as tk
import threading
from .base_view import BaseView


class RepoSettingsView(BaseView):
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
            text="Repository settings",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.content = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        self.content.pack(fill="both", expand=True, padx=24, pady=(12, 24))

        self.status = tk.Label(
            self.content,
            text="Enter owner/repo to manage settings.",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            padx=16,
            pady=16,
        )
        self.status.pack(anchor="nw")

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.refresh()

    def refresh(self):
        for child in list(self.content.winfo_children()):
            child.destroy()
        if not self.owner or not self.repo:
            self.status = tk.Label(
                self.content,
                text="No repository selected.",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
                padx=16,
                pady=16,
            )
            self.status.pack(anchor="nw")
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Settings")

        def load():
            data = self.app.client.get_repo(self.owner, self.repo) if self.app.client else {}
            self.after(0, lambda: self.populate(data))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, data):
        if isinstance(data, dict) and "error" in data:
            tk.Label(self.content, text=f"Error: {data['error']}", bg=self.theme.get("bg_secondary"), fg=self.theme.get("danger"), font=self.theme.get("font_main"), padx=16, pady=16).pack(anchor="nw")
            return

        visibility = "private" if data.get("private") else "public"

        # Visibility
        vis_frame = tk.Frame(self.content, bg=self.theme.get("bg_secondary"))
        vis_frame.pack(fill="x", padx=16, pady=12)
        tk.Label(vis_frame, text=f"Visibility: {visibility}", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x")

        # Description
        desc_frame = tk.Frame(self.content, bg=self.theme.get("bg_secondary"))
        desc_frame.pack(fill="x", padx=16, pady=12)
        tk.Label(desc_frame, text="Description", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x")
        desc_entry = tk.Entry(desc_frame, bg=self.theme.get("bg"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        desc_entry.insert(0, data.get("description", ""))
        desc_entry.pack(fill="x", ipady=6)

        # Topics / homepage placeholders
        tk.Label(self.content, text="Topics, homepage URL, and branch protection can be added here as API calls.", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main"), anchor="w", wraplength=700, justify="left", padx=16).pack(fill="x", pady=(0, 12))

        # Buttons
        btn_frame = tk.Frame(self.content, bg=self.theme.get("bg_secondary"))
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        def save_description():
            new_desc = desc_entry.get().strip()
            if not self.app.client:
                return
            result = self.app.client._patch(f"/repos/{self.owner}/{self.repo}", {"description": new_desc})
            color = self.theme.get("success") if "error" not in result else self.theme.get("danger")
            self.status.configure(text="Saved description" if "error" not in result else f"Error: {result['error']}", fg=color)

        tk.Button(btn_frame, text="Save description", command=save_description, bg=self.theme.get("accent"), fg="#ffffff", activebackground=self.theme.get("accent_hover"), relief="flat", bd=0, cursor="hand2", font=self.theme.get("font_main"), padx=12, pady=6).pack(side="left", padx=(0, 8))

        def delete_repo():
            from tkinter import messagebox
            ok = messagebox.askyesno("Delete repository", f"Are you sure you want to delete {self.owner}/{self.repo}? This cannot be undone.")
            if ok and self.app.client:
                result = self.app.client._delete(f"/repos/{self.owner}/{self.repo}")
                if "error" not in result:
                    messagebox.showinfo("Deleted", f"Repository {self.owner}/{self.repo} deleted.")
                    self.app.show_view("repo_list")
                else:
                    self.status.configure(text=f"Error: {result['error']}", fg=self.theme.get("danger"))

        tk.Button(btn_frame, text="Delete repository", command=delete_repo, bg=self.theme.get("danger"), fg="#ffffff", activebackground=self.theme.get("danger"), relief="flat", bd=0, cursor="hand2", font=self.theme.get("font_main"), padx=12, pady=6).pack(side="left")
