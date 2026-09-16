import tkinter as tk


class FileTree(tk.Frame):
    def __init__(self, parent, app, theme, on_select, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.theme = theme
        self.on_select = on_select
        self.configure(bg=theme.get("bg_secondary"))
        self.items = []
        self.buttons = []
        self.canvas = tk.Canvas(self, bg=theme.get("bg_secondary"), highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=theme.get("bg_secondary"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self.on_inner_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def clear(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []

    def load(self, items):
        self.items = items
        self.clear()
        for item in items:
            icon = "📁" if item.get("type") == "dir" else "📄"
            btn = tk.Button(
                self.inner,
                text=f"{icon} {item.get('name', '')}",
                anchor="w",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg"),
                activebackground=self.theme.get("bg_tertiary"),
                activeforeground=self.theme.get("fg"),
                relief="flat",
                bd=0,
                cursor="hand2",
                font=self.theme.get("font_main"),
                padx=8,
                pady=4,
            )
            btn.pack(fill="x")
            btn.configure(command=lambda i=item, b=btn: self.select(i, b))
            self.buttons.append(btn)

    def select(self, item, btn):
        for b in self.buttons:
            b.configure(bg=self.theme.get("bg_secondary"))
        btn.configure(bg=self.theme.get("bg_tertiary"))
        self.on_select(item)
