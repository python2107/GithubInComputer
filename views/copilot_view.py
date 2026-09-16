import tkinter as tk
from .base_view import BaseView


class CopilotView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.build()

    def build(self):
        tk.Label(
            self,
            text="GitHub Copilot",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(24, 12))

        card = tk.Frame(self, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(
            card,
            text="Copilot is not available through the public REST API.",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_header"),
            anchor="w",
            wraplength=700,
        ).pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(
            card,
            text=(
                "This page is a placeholder for Copilot integration.\n\n"
                "The real-time code completion and chat features of GitHub Copilot\n"
                "require the official Copilot extension/CLI and are not exposed\n"
                "as public REST endpoints. You can use this area to:\n\n"
                "  · Display Copilot subscription status (manual)\n"
                "  · Open Copilot settings in browser\n"
                "  · Provide instructions for installing the Copilot CLI\n"
            ),
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
            anchor="w",
            justify="left",
            wraplength=700,
        ).pack(fill="x", padx=16, pady=(0, 16))

        btn_row = tk.Frame(card, bg=self.theme.get("bg_secondary"))
        btn_row.pack(fill="x", padx=16, pady=(0, 16))

        tk.Button(
            btn_row,
            text="Open Copilot in browser",
            command=self.open_browser,
            bg=self.theme.get("accent"),
            fg="#ffffff",
            activebackground=self.theme.get("accent_hover"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
            padx=14,
            pady=6,
        ).pack(side="left", padx=(0, 8))

        self.status_var = tk.StringVar(value="Status: not connected")
        tk.Label(
            btn_row,
            textvariable=self.status_var,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_subtle"),
            font=self.theme.get("font_main"),
        ).pack(side="left", padx=(16, 0))

    def open_browser(self):
        import webbrowser
        webbrowser.open("https://github.com/copilot")
