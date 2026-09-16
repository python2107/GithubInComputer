import tkinter as tk
from tkinter import ttk, filedialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, save_config
from theme import Theme
from api import GitHubClient
from git import LocalRepo
from widgets import Sidebar, Topbar
from views import (
    LoginView,
    DashboardView,
    RepoListView,
    RepoHomeView,
    CodeBrowserView,
    CommitsView,
    IssueListView,
    IssueDetailView,
    PRListView,
    PRDetailView,
    ProfileView,
    CopilotView,
    StarsView,
    ExploreView,
    ReleasesView,
    ActionsView,
    OrganizationView,
    RepoSettingsView,
    SearchView,
    NotificationsView,
    InsightsView,
    SettingsView,
)


class ViewManager:
    def __init__(self, parent, app, theme):
        self.parent = parent
        self.app = app
        self.theme = theme
        self.views = {}
        self.container = tk.Frame(parent, bg=theme.get("bg"))
        self.container.pack(fill="both", expand=True)

    def register(self, name, view_class):
        view = view_class(self.container, self.app, self.theme)
        self.views[name] = view
        view.place(relwidth=1, relheight=1)
        view.place_forget()

    def show(self, name, **kwargs):
        if name not in self.views:
            return
        for v in self.views.values():
            v.place_forget()
        view = self.views[name]
        if hasattr(view, "set_repo") and ("owner" in kwargs or "repo" in kwargs):
            view.set_repo(kwargs.get("owner"), kwargs.get("repo"))
        if hasattr(view, "set_issue") and "number" in kwargs:
            view.set_issue(kwargs.get("owner"), kwargs.get("repo"), kwargs.get("number"))
        if hasattr(view, "set_pr") and "number" in kwargs:
            view.set_pr(kwargs.get("owner"), kwargs.get("repo"), kwargs.get("number"))
        if hasattr(view, "set_query") and "query" in kwargs:
            view.set_query(kwargs.get("query"))
        if hasattr(view, "load_user") and "username" in kwargs:
            view.load_user(kwargs.get("username"))
        if hasattr(view, "set_org") and "org" in kwargs:
            view.set_org(kwargs.get("org"))
        view.place(relwidth=1, relheight=1)
        view.lift()
        if hasattr(view, "refresh"):
            view.refresh()


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitHub Desktop")
        self.root.geometry("1280x800")
        self.config = load_config()
        self.theme = Theme(self.config.get("theme", "dark"))
        self.style = ttk.Style()
        self.apply_theme()

        self.client = None
        self.user = None
        self.topbar = None
        self.sidebar = None
        self.view_manager = None

        self.build_ui()
        self.root.mainloop()

    def build_ui(self):
        self.setup_client()

        self.main_frame = tk.Frame(self.root, bg=self.theme.get("bg"))
        self.main_frame.pack(fill="both", expand=True)

        self.topbar = Topbar(self.main_frame, self, self.theme)
        self.topbar.pack(fill="x", side="top")
        self.topbar.set_user(self.user.get("login") if self.user else None)

        self.body = tk.Frame(self.main_frame, bg=self.theme.get("bg"))
        self.body.pack(fill="both", expand=True, side="top")

        self.sidebar = Sidebar(self.body, self, self.theme)
        self.sidebar.pack(fill="y", side="left")

        self.content = tk.Frame(self.body, bg=self.theme.get("bg"))
        self.content.pack(fill="both", expand=True, side="left")

        self.view_manager = ViewManager(self.content, self, self.theme)
        self.register_views()

        self.show_view("login")

    def apply_theme(self):
        self.theme.apply_ttk(self.style)
        self.root.configure(bg=self.theme.get("bg"))

    def reload_theme(self, name):
        self.theme = Theme(name)
        self.apply_theme()
        self.config["theme"] = name
        view_name = getattr(self, "current_view", "login")
        view_kwargs = getattr(self, "current_kwargs", {})
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_ui()
        if view_name != "login":
            self.show_view(view_name, **view_kwargs)
        else:
            self.show_view("login")

    def setup_client(self):
        token = self.config.get("token", "")
        if token:
            self.client = GitHubClient(token)
            self.user = self.client.get_user()
            if isinstance(self.user, dict) and "error" in self.user:
                self.user = None
        else:
            self.client = None
            self.user = None
        if self.topbar:
            self.topbar.set_user(self.user.get("login") if self.user else None)

    def save_config(self):
        save_config(self.config)

    def register_views(self):
        self.view_manager.register("login", LoginView)
        self.view_manager.register("dashboard", DashboardView)
        self.view_manager.register("repo_list", RepoListView)
        self.view_manager.register("repo_home", RepoHomeView)
        self.view_manager.register("code_browser", CodeBrowserView)
        self.view_manager.register("commits", CommitsView)
        self.view_manager.register("issue_list", IssueListView)
        self.view_manager.register("issue_detail", IssueDetailView)
        self.view_manager.register("pr_list", PRListView)
        self.view_manager.register("pr_detail", PRDetailView)
        self.view_manager.register("profile", ProfileView)
        self.view_manager.register("copilot", CopilotView)
        self.view_manager.register("stars", StarsView)
        self.view_manager.register("explore", ExploreView)
        self.view_manager.register("releases", ReleasesView)
        self.view_manager.register("actions", ActionsView)
        self.view_manager.register("organization", OrganizationView)
        self.view_manager.register("repo_settings", RepoSettingsView)
        self.view_manager.register("search", SearchView)
        self.view_manager.register("notifications", NotificationsView)
        self.view_manager.register("insights", InsightsView)
        self.view_manager.register("settings", SettingsView)

    def show_view(self, name, **kwargs):
        self.current_view = name
        self.current_kwargs = kwargs
        self.view_manager.show(name, **kwargs)
        self.sidebar.set_active(name if name in self.sidebar.buttons else "dashboard")

    def open_repo(self, owner, repo):
        self.show_view("repo_home", owner=owner, repo=repo)

    def show_search(self, query):
        self.show_view("search", query=query)

    def show_profile(self, username):
        self.show_view("profile", username=username)

    def show_org(self, org):
        self.show_view("organization", org=org)

    def show_releases(self, owner, repo):
        self.show_view("releases", owner=owner, repo=repo)

    def show_actions(self, owner, repo):
        self.show_view("actions", owner=owner, repo=repo)

    def show_repo_settings(self, owner, repo):
        self.show_view("repo_settings", owner=owner, repo=repo)

    def toggle_theme(self):
        new_theme = "light" if self.config.get("theme") == "dark" else "dark"
        self.config["theme"] = new_theme
        self.save_config()
        self.root.after(100, lambda: self.reload_theme(new_theme))

    def show_create_repo_dialog(self):
        from tkinter import simpledialog, messagebox
        dialog = tk.Toplevel(self.root)
        dialog.title("Create a new repository")
        dialog.configure(bg=self.theme.get("bg"))
        dialog.geometry("420x280")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Repository name", bg=self.theme.get("bg"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x", padx=16, pady=(16, 4))
        name_entry = tk.Entry(dialog, bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        name_entry.pack(fill="x", padx=16, ipady=6)

        tk.Label(dialog, text="Description (optional)", bg=self.theme.get("bg"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        desc_entry = tk.Entry(dialog, bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        desc_entry.pack(fill="x", padx=16, ipady=6)

        private_var = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text="Private repository", variable=private_var, bg=self.theme.get("bg"), fg=self.theme.get("fg"), selectcolor=self.theme.get("bg_tertiary"), activebackground=self.theme.get("bg"), font=self.theme.get("font_main")).pack(anchor="w", padx=16, pady=(12, 0))

        status = tk.Label(dialog, text="", bg=self.theme.get("bg"), fg=self.theme.get("danger"), font=self.theme.get("font_main"))
        status.pack(pady=(12, 0))

        def do_create():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            if not name:
                status.configure(text="Repository name is required")
                return
            if not self.client:
                status.configure(text="Please sign in first")
                return
            result = self.client.create_repo(name, desc, private_var.get())
            if "error" in result:
                status.configure(text=f"Error: {result['error']}")
            else:
                dialog.destroy()
                messagebox.showinfo("Repository created", f"Created {result.get('full_name', name)}")
                self.show_view("repo_list")

        tk.Button(dialog, text="Create repository", command=do_create, bg=self.theme.get("success"), fg="#ffffff", activebackground=self.theme.get("success_hover"), relief="flat", bd=0, cursor="hand2", font=self.theme.get("font_main"), padx=16, pady=6).pack(pady=(16, 0))

    def show_push_dialog(self, owner, repo):
        from tkinter import messagebox
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Push {owner}/{repo}")
        dialog.configure(bg=self.theme.get("bg"))
        dialog.geometry("520x340")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Local repository path", bg=self.theme.get("bg"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x", padx=16, pady=(16, 4))
        path_frame = tk.Frame(dialog, bg=self.theme.get("bg"))
        path_frame.pack(fill="x", padx=16)
        path_entry = tk.Entry(path_frame, bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        path_entry.pack(side="left", fill="x", expand=True, ipady=6)

        def browse():
            d = filedialog.askdirectory()
            if d:
                path_entry.delete(0, "end")
                path_entry.insert(0, d)

        browse_btn = tk.Button(path_frame, text="Browse", command=browse, bg=self.theme.get("bg_tertiary"), fg=self.theme.get("fg"), relief="flat", bd=0, cursor="hand2", font=self.theme.get("font_main"), padx=8, pady=4)
        browse_btn.pack(side="right", padx=(8, 0))

        tk.Label(dialog, text="Remote", bg=self.theme.get("bg"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        remote_entry = tk.Entry(dialog, bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        remote_entry.insert(0, "origin")
        remote_entry.pack(fill="x", padx=16, ipady=6)

        tk.Label(dialog, text="Branch", bg=self.theme.get("bg"), fg=self.theme.get("fg"), font=self.theme.get("font_main"), anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        branch_entry = tk.Entry(dialog, bg=self.theme.get("bg_secondary"), fg=self.theme.get("fg"), insertbackground=self.theme.get("fg"), relief="flat", font=self.theme.get("font_main"))
        branch_entry.pack(fill="x", padx=16, ipady=6)

        status = tk.Label(dialog, text="", bg=self.theme.get("bg"), fg=self.theme.get("fg_muted"), font=self.theme.get("font_main"), anchor="w", wraplength=460, justify="left")
        status.pack(fill="x", padx=16, pady=(12, 0))

        def run_git(op, label):
            path = path_entry.get().strip()
            remote = remote_entry.get().strip() or "origin"
            branch = branch_entry.get().strip()
            if not path:
                status.configure(text="Local path is required", fg=self.theme.get("danger"))
                return
            repo = LocalRepo(path)
            if not repo.is_repo():
                status.configure(text="Selected path is not a git repository", fg=self.theme.get("danger"))
                return
            ssh = self.config.get("ssh_key_path", "")
            if op == "push":
                result = repo.push(remote, branch, ssh)
            elif op == "pull":
                result = repo.pull(remote, branch, ssh)
            else:
                result = repo.fetch(remote, ssh)
            color = self.theme.get("success") if result.get("code") == 0 else self.theme.get("danger")
            text = f"{label}:\n" + (result.get("stdout") or result.get("stderr"))
            status.configure(text=text, fg=color)

        btn_frame = tk.Frame(dialog, bg=self.theme.get("bg"))
        btn_frame.pack(fill="x", padx=16, pady=(16, 0))
        for op, label in (("push", "Push"), ("pull", "Pull"), ("fetch", "Fetch")):
            tk.Button(btn_frame, text=label, command=lambda o=op, l=label: run_git(o, l), bg=self.theme.get("accent"), fg="#ffffff", activebackground=self.theme.get("accent_hover"), relief="flat", bd=0, cursor="hand2", font=self.theme.get("font_main"), padx=12, pady=6).pack(side="left", padx=(0, 8))


if __name__ == "__main__":
    App()
