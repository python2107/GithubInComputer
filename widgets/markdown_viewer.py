import tkinter as tk
import re


class MarkdownViewer(tk.Text):
    def __init__(self, parent, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.configure(
            bg=theme.get("bg_secondary"),
            fg=theme.get("fg"),
            font=theme.get("font_main"),
            wrap="word",
            relief="flat",
            padx=12,
            pady=12,
            state="disabled",
            cursor="arrow",
        )
        self.tag_configure("h1", font=("Segoe UI", 18, "bold"), foreground=theme.get("fg"), spacing3=8)
        self.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground=theme.get("fg"), spacing3=6)
        self.tag_configure("h3", font=("Segoe UI", 12, "bold"), foreground=theme.get("fg"), spacing3=4)
        self.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.tag_configure("code", font=theme.get("font_mono"), background=theme.get("code_bg"), foreground=theme.get("fg"))
        self.tag_configure("link", foreground=theme.get("link"), underline=True)
        self.tag_configure("blockquote", foreground=theme.get("fg_muted"), lmargin1=16, lmargin2=16)

    def set_text(self, text):
        self.configure(state="normal")
        self.delete("1.0", "end")
        if not text:
            return
        for line in text.split("\n"):
            self._render_line(line)
        self.configure(state="disabled")

    def _render_line(self, raw):
        line = raw.rstrip()
        if not line:
            self.insert("end", "\n")
            return

        # Heading
        if line.startswith("# "):
            self.insert("end", line[2:] + "\n", "h1")
            return
        if line.startswith("## "):
            self.insert("end", line[3:] + "\n", "h2")
            return
        if line.startswith("### "):
            self.insert("end", line[4:] + "\n", "h3")
            return

        # Blockquote
        if line.startswith("> "):
            self.insert("end", line[2:] + "\n", "blockquote")
            return

        # Inline formatting
        pos = 0
        while pos < len(line):
            # Code block inline
            m = re.search(r"`([^`]+)`", line[pos:])
            # Bold
            b = re.search(r"\*\*([^*]+)\*\*", line[pos:])
            # Italic
            i = re.search(r"\*([^*]+)\*", line[pos:])
            # Link
            l = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line[pos:])

            matches = []
            if m:
                matches.append((m.start(), m.end(), "code", m.group(1)))
            if b:
                matches.append((b.start(), b.end(), "bold", b.group(1)))
            if i:
                matches.append((i.start(), i.end(), "italic", i.group(1)))
            if l:
                matches.append((l.start(), l.end(), "link", l.group(1)))

            if not matches:
                self.insert("end", line[pos:])
                break

            matches.sort()
            start, end, tag, content = matches[0]
            self.insert("end", line[pos:pos + start])
            self.insert("end", content, tag)
            pos = pos + end

        self.insert("end", "\n")
