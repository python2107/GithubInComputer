import tkinter as tk


class Sidebar(tk.Frame):
    NAV_ITEMS = [
        ("dashboard", "Dashboard"),
        ("repo_list", "Repositories"),
        ("stars", "Stars"),
        ("explore", "Explore"),
        ("search", "Search"),
        ("copilot", "Copilot"),
        ("notifications", "Notifications"),
        ("profile", "Profile"),
        ("organization", "Organization"),
        ("login", "Settings"),
    ]

    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.theme = theme
        self.buttons = {}
        self.configure(bg=theme.get("bg_secondary"), width=220)
        self.pack_propagate(False)
        self.build()

    def build(self):
        tk.Label(
            self,
            text="",
            bg=self.theme.get("bg_secondary"),
            height=1,
        ).pack(fill="x", pady=8)

        self.title_label = tk.Label(
            self,
            text="GitHub",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=("Segoe UI", 16, "bold"),
            padx=16,
        )
        self.title_label.pack(fill="x", pady=(0, 16))

        for view_name, label in self.NAV_ITEMS:
            btn = tk.Label(
                self,
                text=label,
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
                padx=16,
                pady=8,
                cursor="hand2",
                anchor="w",
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, name=view_name: self.on_click(name))
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(b))
            btn.bind("<Leave>", lambda e, b=btn, name=view_name: self.on_leave(b, name))
            self.buttons[view_name] = btn

        self.set_active("dashboard")

    def on_click(self, name):
        self.app.show_view(name)
        self.set_active(name)

    def on_enter(self, btn):
        btn.configure(bg=self.theme.get("bg_tertiary"))

    def on_leave(self, btn, name):
        if name == getattr(self, "_active", None):
            btn.configure(bg=self.theme.get("selected"), fg=self.theme.get("fg"))
        else:
            btn.configure(bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"))

    def set_active(self, name):
        self._active = name
        for key, btn in self.buttons.items():
            if key == name:
                btn.configure(bg=self.theme.get("selected"), fg=self.theme.get("fg"))
            else:
                btn.configure(bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg_muted"))
