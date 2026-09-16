import tkinter as tk


class Topbar(tk.Frame):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.theme = theme
        self.configure(bg=theme.get("bg_secondary"), height=50)
        self.pack_propagate(False)
        self.build()

    def build(self):
        self.search_entry = tk.Entry(
            self,
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            insertbackground=self.theme.get("fg"),
            relief="flat",
            font=self.theme.get("font_main"),
            width=40,
        )
        self.search_entry.pack(side="left", padx=(16, 8), pady=10)
        self.search_entry.bind("<Return>", self.on_search)

        search_btn = tk.Button(
            self,
            text="Search",
            command=self.on_search,
            bg=self.theme.get("bg_tertiary"),
            fg=self.theme.get("fg"),
            activebackground=self.theme.get("border"),
            activeforeground=self.theme.get("fg"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
        )
        search_btn.pack(side="left", padx=4, pady=10)

        self.user_label = tk.Label(
            self,
            text="Not logged in",
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg_muted"),
            font=self.theme.get("font_main"),
        )
        self.user_label.pack(side="right", padx=16, pady=10)

        theme_btn = tk.Button(
            self,
            text="Theme",
            command=self.app.toggle_theme,
            bg=self.theme.get("bg_tertiary"),
            fg=self.theme.get("fg"),
            activebackground=self.theme.get("border"),
            activeforeground=self.theme.get("fg"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=self.theme.get("font_main"),
        )
        theme_btn.pack(side="right", padx=8, pady=10)

    def on_search(self, event=None):
        query = self.search_entry.get().strip()
        if query:
            self.app.show_search(query)

    def set_user(self, username):
        self.user_label.configure(text=username or "Not logged in")
