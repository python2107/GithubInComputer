import tkinter as tk
import threading
from .base_view import BaseView


class NotificationsView(BaseView):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, app, theme, *args, **kwargs)
        self.build()

    def build(self):
        header = tk.Frame(self, bg=self.theme.get("bg"))
        header.pack(fill="x", padx=24, pady=(24, 12))

        tk.Label(
            header,
            text="Notifications",
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_title"),
            anchor="w",
        ).pack(side="left")

        self.all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            header,
            text="Show all",
            variable=self.all_var,
            bg=self.theme.get("bg"),
            fg=self.theme.get("fg"),
            selectcolor=self.theme.get("bg_tertiary"),
            activebackground=self.theme.get("bg"),
            font=self.theme.get("font_main"),
            command=self.refresh,
        ).pack(side="right")

        self.canvas = tk.Canvas(self, bg=self.theme.get("bg"), highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=self.theme.get("bg"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def refresh(self):
        for child in list(self.inner.winfo_children()):
            child.destroy()
        if not self.app.client or not self.app.client.token:
            tk.Label(self.inner, text="Please sign in to view notifications.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
            return

        def load():
            notes = self.app.client.list_notifications(all=self.all_var.get()) if self.app.client else []
            self.after(0, lambda: self.populate(notes))

        threading.Thread(target=load, daemon=True).start()

    def populate(self, notes):
        if isinstance(notes, dict) and "error" in notes:
            tk.Label(self.inner, text=f"Error: {notes['error']}", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main")).pack(pady=40)
            return
        if not notes:
            tk.Label(self.inner, text="No notifications.", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main")).pack(pady=40)
            return

        for note in notes:
            subject = note.get("subject", {})
            repo = note.get("repository", {}).get("full_name", "")
            title = subject.get("title", "Untitled")
            reason = note.get("reason", "")
            unread = note.get("unread", False)

            frame = tk.Frame(self.inner, bg=self.theme.get("bg_secondary"), highlightbackground=self.theme.get("border"), highlightthickness=1)
            frame.pack(fill="x", padx=24, pady=(0, 8))

            title_lbl = tk.Label(
                frame,
                text=title,
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg"),
                font=self.theme.get("font_header"),
                anchor="w",
                wraplength=700,
            )
            title_lbl.pack(fill="x", padx=12, pady=(12, 4))

            tk.Label(
                frame,
                text=f"{repo} · {reason} · {'Unread' if unread else 'Read'}",
                bg=self.theme.get("bg_secondary"),
                fg=self.theme.get("fg_muted"),
                font=self.theme.get("font_main"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 12))
