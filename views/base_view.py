import tkinter as tk


class BaseView(tk.Frame):
    def __init__(self, parent, app, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.theme = theme
        self.configure(bg=theme.get("bg"))

    def refresh(self):
        """Override in subclasses to refresh content when view becomes active."""
        pass

    def show_message(self, text, msg_type="info"):
        """Display a temporary message overlay."""
        label = tk.Label(
            self,
            text=text,
            bg=self.theme.get("bg_secondary"),
            fg=self.theme.get("fg"),
            font=self.theme.get("font_main"),
            padx=20,
            pady=10,
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
        self.after(2000, label.destroy)
