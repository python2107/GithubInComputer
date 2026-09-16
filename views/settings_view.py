import tkinter as tk
from .base_view import BaseView


class SettingsView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.build()

    def build(self):
        tk.Label(
            self,
            text="Settings",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(24, 12))

        container = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        container.pack(fill="x", padx=24, pady=12)

        self.token_var = tk.StringVar(value=self.app.config.get("token", ""))
        self.ssh_var = tk.StringVar(value=self.app.config.get("ssh_key_path", ""))
        self.theme_var = tk.StringVar(value=self.app.config.get("theme", "dark"))

        self._row(container, "Token", self.token_var, show="*")
        self._row(container, "SSH key path", self.ssh_var)

        theme_frame = tk.Frame(container, bg=self.theme.get("bg_secondary"))
        theme_frame.pack(fill="x", padx=16, pady=12)
        tk.Label(theme_frame, text="Theme", bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x")
        for t in ("dark", "light"):
            tk.Radiobutton(
                theme_frame,
                text=t.capitalize(),
                variable=self.theme_var,
                value=t,
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg"),
                selectcolor=self.theme.get("bg_tertiary"),
                activebackground=self.theme.get("bg_secondary"),
                activeforeground=self.theme.get("fg"),
                font=self.theme.get("font_main"),
            ).pack(side="left", padx=(0, 12))

        save_btn = tk.Button(
            container,
            text="Save settings",
            command=self.save,
            bg=self.theme.get("success"),
            fg="#ffffff",
            activebackground=self.theme.get("success_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=16,
            pady=8,
        )
        save_btn.pack(anchor="w", padx=16, pady=(8, 16))

        self.status = tk.Label(
            container,
            text="",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("success"),
            font=self.theme.get("font_main"),
            anchor="w",
            padx=16,
        )
        self.status.pack(fill="x", pady=(0, 16))

    def _row(self, parent, label, var, show=None):
        frame = tk.Frame(parent, bg=self.theme.get("bg_secondary"))
        frame.pack(fill="x", padx=16, pady=12)
        tk.Label(
            frame,
            text=label,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_main"),
            anchor="w",
        ).pack(fill="x")
        tk.Entry(
            frame,
            textvariable=var,
            show=show,
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
        ).pack(fill="x", ipady=6)

    def save(self):
        new_theme = self.theme_var.get()
        self.app.config.update({
            "token": self.token_var.get().strip(),
            "ssh_key_path": self.ssh_var.get().strip(),
            "theme": new_theme,
        })
        self.app.save_config()
        self.app.setup_client()
        self.status.configure(text="Settings saved")
        if new_theme != self.theme.name:
            self.app.root.after(200, lambda: self.app.reload_theme(new_theme))
