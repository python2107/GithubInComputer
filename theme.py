"""Theme and styling constants for the tkinter GitHub app."""

THEMES = {
    "dark": {
        "name": "dark",
        "bg": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_tertiary": "#21262d",
        "fg": "#c9d1d9",
        "fg_muted": "#8b949e",
        "fg_subtle": "#6e7681",
        "border": "#30363d",
        "accent": "#2f81f7",
        "accent_hover": "#388bfd",
        "success": "#238636",
        "success_hover": "#2ea043",
        "danger": "#da3633",
        "warning": "#d29922",
        "link": "#58a6ff",
        "code_bg": "#161b22",
        "selected": "#1f6feb",
        "font_main": ("Segoe UI", 10),
        "font_mono": ("Consolas", 10),
        "font_title": ("Segoe UI", 14, "bold"),
        "font_header": ("Segoe UI", 12, "bold"),
    },
    "light": {
        "name": "light",
        "bg": "#ffffff",
        "bg_secondary": "#f6f8fa",
        "bg_tertiary": "#eaeef2",
        "fg": "#24292f",
        "fg_muted": "#57606a",
        "fg_subtle": "#6e7781",
        "border": "#d0d7de",
        "accent": "#0969da",
        "accent_hover": "#0860ca",
        "success": "#1a7f37",
        "success_hover": "#1f883d",
        "danger": "#cf222e",
        "warning": "#9a6700",
        "link": "#0969da",
        "code_bg": "#f6f8fa",
        "selected": "#ddf4ff",
        "font_main": ("Segoe UI", 10),
        "font_mono": ("Consolas", 10),
        "font_title": ("Segoe UI", 14, "bold"),
        "font_header": ("Segoe UI", 12, "bold"),
    },
}


class Theme:
    def __init__(self, name="dark"):
        self.name = name
        self.colors = THEMES.get(name, THEMES["dark"])

    def get(self, key, default=None):
        return self.colors.get(key, default)

    def set(self, key, value):
        self.colors[key] = value

    def apply_ttk(self, style):
        """Apply basic ttk theme configuration."""
        style.theme_use("clam")
        bg = self.get("bg")
        fg = self.get("fg")
        accent = self.get("accent")
        border = self.get("border")
        bg_sec = self.get("bg_secondary")

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=self.get("font_main"))
        style.configure("TButton",
                        background=accent,
                        foreground="#ffffff",
                        bordercolor=accent,
                        font=self.get("font_main"),
                        padding=(12, 6))
        style.map("TButton",
                  background=[("active", self.get("accent_hover")), ("pressed", accent)],
                  foreground=[("active", "#ffffff")])
        style.configure("TEntry", fieldbackground=bg_sec, foreground=fg, insertcolor=fg, bordercolor=border)
        style.configure("TNotebook", background=bg, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", background=bg_sec, foreground=fg, padding=(12, 6))
        style.map("TNotebook.Tab", background=[("selected", bg)])
        style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, rowheight=28)
        style.configure("Treeview.Heading", background=bg_sec, foreground=fg, font=self.get("font_header"))
        style.map("Treeview", background=[("selected", self.get("selected"))])
        style.configure("Vertical.TScrollbar", background=bg_sec, troughcolor=bg, bordercolor=border)

    def button(self, widget):
        """Configure a tk Button to look like GitHub's primary button."""
        widget.configure(
            bg=self.get("accent"),
            fg="#ffffff",
            activebackground=self.get("accent_hover"),
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            font=self.get("font_main"),
            padx=12,
            pady=6,
        )

    def button_secondary(self, widget):
        widget.configure(
            bg=self.get("bg_tertiary"),
            fg=self.get("fg"),
            activebackground=self.get("border"),
            activeforeground=self.get("fg"),
            bd=1,
            relief="solid",
            cursor="hand2",
            font=self.get("font_main"),
            padx=12,
            pady=6,
        )

    def link(self, widget):
        widget.configure(
            fg=self.get("link"),
            bg=self.get("bg"),
            cursor="hand2",
            font=self.get("font_main"),
        )

    def card(self, widget):
        widget.configure(
            bg=self.get("bg_secondary"),
            highlightbackground=self.get("border"),
            highlightthickness=1,
        )
