import tkinter as tk
import threading
from .base_view import BaseView


class ActionsView(BaseView):
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
            text="Actions",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.content = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        self.content.pack(fill="both", expand=True, padx=24, pady=(12, 24))

        self.status_label = tk.Label(
            self.content,
            text="Loading workflows...",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            padx=16,
            pady=16,
        )
        self.status_label.pack(anchor="nw")

    def set_repo(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.refresh()

    def refresh(self):
        for child in list(self.content.winfo_children()):
            child.destroy()
        self.status_label = tk.Label(
            self.content,
            text="Loading workflows...",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            padx=16,
            pady=16,
        )
        self.status_label.pack(anchor="nw")

        if not self.owner or not self.repo:
            return
        self.title_label.configure(text=f"{self.owner} / {self.repo} — Actions")

        def load():
            workflows = self.app.client.list_workflows(self.owner, self.repo) if self.app.client else {"workflows": []}
            runs = self.app.client.list_workflow_runs(self.owner, self.repo, per_page=10) if self.app.client else {"workflow_runs": []}
            self.after(0, lambda: self.populate(workflows, runs))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, workflows, runs):
        for child in list(self.content.winfo_children()):
            child.destroy()

        tk.Label(
            self.content,
            text="Workflows",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            padx=16,
            pady=(16, 8),
        ).pack(anchor="nw", fill="x")

        items = workflows.get("workflows", []) if isinstance(workflows, dict) else []
        if not items:
            tk.Label(self.content, text="No workflows found.", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main"), padx=16).pack(anchor="nw")
        for wf in items:
            tk.Label(
                self.content,
                text=f"{wf.get('name')} ({wf.get('state')})",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg"),
                font=self.theme.get("font_main"),
                anchor="w",
                padx=32,
                pady=2,
            ).pack(anchor="nw", fill="x")

        tk.Label(
            self.content,
            text="Recent runs",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            padx=16,
            pady=(16, 8),
        ).pack(anchor="nw", fill="x")

        run_items = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
        if not run_items:
            tk.Label(self.content, text="No recent runs.", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main"), padx=16).pack(anchor="nw")
        for run in run_items:
            color = self.theme.get("success") if run.get("conclusion") == "success" else self.theme.get("danger")
            tk.Label(
                self.content,
                text=f"{run.get('name')} — {run.get('status')} / {run.get('conclusion') or 'running'} · {run.get('created_at', '')[:10]}",
                bg=self.theme.get("bg_secondary"),
                fg=color,
                font=self.theme.get("font_main"),
                anchor="w",
                padx=32,
                pady=2,
            ).pack(anchor="nw", fill="x")
