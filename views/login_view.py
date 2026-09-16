import tkinter as tk
from tkinter import filedialog
from .base_view import BaseView


class LoginView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.build()

    def build(self):
        container = tk.Frame(self, bg=self.theme.get("bg"))
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text="Sign in to GitHub",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(0, 8))

        tk.Label(
            container,
            text="Configure your token and preferences",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
        ).pack(pady=(0, 24))

        form = tk.Frame(container, bg=self.theme.get("bg"))
        form.pack()

        self._labeled_entry(form, "Personal access token", "token_entry", show="*")
        self._labeled_entry(form, "SSH key path (optional)", "ssh_entry")
        self._theme_select(form)

        self.status_label = tk.Label(
            container,
            text="",
            bg=self.theme.get("bg"),
            fg=self.theme.get("danger"),
            font=self.theme.get("font_main"),
        )
        self.status_label.pack(pady=(16, 0))

        save_btn = tk.Button(
            container,
            text="Sign in",
            command=self.save_config,
            bg=self.theme.get("success"),
            fg="#ffffff",
            activebackground=self.theme.get("success_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=20,
            pady=8,
        )
        save_btn.pack(pady=(24, 0))

        # Pre-fill
        cfg = self.app.config
        self.token_entry.insert(0, cfg.get("token", ""))
        self.ssh_entry.insert(0, cfg.get("ssh_key_path", ""))
        theme_name = cfg.get("theme", "dark")
        self.theme_var.set(theme_name)

    def _labeled_entry(self, parent, label, attr, show=None):
        tk.Label(
            parent,
            text=label,
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_main"),
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        entry = tk.Entry(
            parent,
            show=show,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=40,
        )
        entry.pack(fill="x", ipady=6)
        setattr(self, attr, entry)

    def _theme_select(self, parent):
        tk.Label(
            parent,
            text="Theme",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_main"),
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        self.theme_var = tk.StringVar(value="dark")
        row = tk.Frame(parent, bg=self.theme.get("bg"))
        row.pack(fill="x")
        for t in ("dark", "light"):
            tk.Radiobutton(
                row,
                text=t.capitalize(),
                variable=self.theme_var,
                value=t,
                bg=self.theme.get("bg"),
                fg=self.theme.get("fg"),
                selectcolor=self.theme.get("bg_tertiary"),
                activebackground=self.theme.get("bg"),
                activeforeground=self.theme.get("fg"),
                font=self.theme.get("font_main"),
            ).pack(side="left", padx=(0, 12))

    def save_config(self):
        token = self.token_entry.get().strip()
        ssh = self.ssh_entry.get().strip()
        theme = self.theme_var.get()
        self.app.config.update({"token": token, "ssh_key_path": ssh, "theme": theme})
        self.app.save_config()
        self.app.setup_client()
        if self.app.client and self.app.client.authenticated():
            self.status_label.configure(text="Authenticated successfully", fg=self.theme.get("success"))
            if self.app.config.get("theme") != self.theme.name:
                self.app.root.after(200, lambda: self.app.reload_theme(self.app.config.get("theme")))
            else:
                self.app.root.after(200, lambda: self.app.show_view("dashboard"))
        else:
            self.status_label.configure(text="Invalid token or network error", fg=self.theme.get("danger"))
