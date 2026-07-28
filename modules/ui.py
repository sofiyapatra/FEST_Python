"""
User interface management for FEST application.
Handles all UI components, screens, and navigation.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from modules.theme import ThemeManager
from modules.data import DataManager
from modules.auth import AuthManager
from modules.visualizations import VisualizationManager
from modules.queries import QueryManager

class UIManager:
    """Manages all UI screens and components."""

    def __init__(self, root, theme_manager, auth_manager):
        self.root = root
        self.theme = theme_manager
        self.auth = auth_manager
        self.data = DataManager()
        self.viz = VisualizationManager(theme_manager)
        self.queries = QueryManager()

        # UI state
        self.current_screen = None

        # Option labels
        self.OPTION_LABELS = [
            "Add Student", "Edit Student", "Delete Record",
            "GPA Formula", "Swarm Plot", "Major Count Plot",
            "Grade Pie Chart", "Student Profile", "Student ID Card",
            "Queries", "Dean's List", "Statistics Dashboard"
        ]

        self.OPTION_COLORS = [
            "#C49B5A", "#A8843E", "#8C3A2E", "#B8860B", "#6E1E22",
            "#5C4A2A", "#9C6B30", "#556B2F", "#7C2D12", "#3E3226",
            "#C49B5A", "#2A6B4A"
        ]

    def clear_screen(self):
        """Clear all widgets from the root window."""
        for w in self.root.winfo_children():
            w.destroy()
        self.root.unbind("<Key>")
        self.current_screen = None

    def make_label(self, parent, text, size=11, bold=False, color=None, **kw):
        """Create a styled label with no background box."""
        family = "Georgia" if bold and size >= 14 else "Segoe UI"
        font_weight = "bold" if bold else "normal"
        color = color or self.theme.get_color('text')
        bg = parent.cget('bg') if hasattr(parent, 'cget') else self.theme.get_color('bg')
        return tk.Label(parent, text=text, font=(family, size, font_weight),
                       fg=color, bg=bg, **kw)

    def make_button(self, parent, text, cmd, color=None, width=200, height=50):
        """Create a flat, borderless button with rounded corners."""
        bg = parent.cget('bg') if hasattr(parent, 'cget') else self.theme.get_color('bg')
        color = color or self.theme.get_color('accent')
        fg = '#2A241E' if not self.theme.is_dark else self.theme.get_color('text')

        cv = tk.Canvas(parent, width=width, height=height,
                      bg=bg, highlightthickness=0, bd=0)

        def _draw(hover=False):
            cv.delete("all")
            r = min(height // 2, 20)
            c = self.theme.get_color('accent_light') if hover else color

            x1, y1, x2, y2 = 1, 1, width - 1, height - 1

            # Draw rounded rectangle without extra borders
            cv.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=c, outline=c)
            cv.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=c, outline=c)
            cv.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=c, outline=c)
            cv.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=c, outline=c)
            cv.create_rectangle(x1+r, y1, x2-r, y2, fill=c, outline=c)
            cv.create_rectangle(x1, y1+r, x2, y2-r, fill=c, outline=c)

            cv.create_text(width // 2, height // 2, text=text,
                          fill=fg, font=('Segoe UI', 12, 'bold'))

        _draw()

        def on_enter(e):
            cv.config(cursor="hand2")
            _draw(hover=True)

        def on_leave(e):
            cv.config(cursor="")
            _draw()

        def on_click(e):
            if cmd:
                cmd()

        cv.bind("<Enter>", on_enter)
        cv.bind("<Leave>", on_leave)
        cv.bind("<Button-1>", on_click)

        return cv

    def make_ornamental_divider(self, parent, width=300, color=None):
        """Create an ornamental divider with minimal background."""
        color = color or self.theme.get_color('accent')
        bg = parent.cget('bg') if hasattr(parent, 'cget') else self.theme.get_color('bg')

        cv = tk.Canvas(parent, width=width, height=20,
                      bg=bg, highlightthickness=0)
        midy = 10
        midx = width // 2

        cv.create_line(0, midy, midx - 20, midy, fill=color, width=1)
        cv.create_line(midx + 20, midy, width, midy, fill=color, width=1)
        cv.create_polygon(midx, 2, midx + 8, midy, midx, 18, midx - 8, midy,
                         fill=color, outline="")

        return cv

    def show_welcome(self):
        """Display the welcome screen."""
        self.clear_screen()
        self.root.title("FEST Summer 2026")

        # Header
        hdr = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x", pady=40)

        tk.Frame(hdr, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        title_frame = tk.Frame(hdr, bg=self.theme.get_color('panel'))
        title_frame.pack(pady=30)

        self.make_label(title_frame, "FEST", 48, bold=True,
                       color=self.theme.get_color('accent')).pack()
        self.make_label(title_frame, "Summer 2026 · Academic Records",
                       12, color=self.theme.get_color('text_secondary')).pack()

        self.make_ornamental_divider(title_frame, width=200).pack(pady=10)

        # Body
        body = tk.Frame(self.root, bg=self.theme.get_color('bg'))
        body.pack(expand=True, pady=20)

        self.make_label(body, "Please register or login to continue",
                       12, color=self.theme.get_color('text_secondary')).pack(pady=5)

        btn_frame = tk.Frame(body, bg=self.theme.get_color('bg'))
        btn_frame.pack(pady=30)

        self.make_button(btn_frame, "Register", self.show_register,
                        width=250, height=60).pack(pady=10)
        self.make_button(btn_frame, "Login", self.show_login,
                        width=250, height=60).pack(pady=10)

        # Footer
        footer = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=self.theme.get_color('border'), height=1).pack(fill="x")
        self.make_label(footer, "FEST · Vanderbilt University 2026",
                       10, color=self.theme.get_color('text_secondary')).pack(pady=10)

    def show_register(self):
        """Display the registration screen."""
        self.clear_screen()
        self.root.title("FEST — Register")

        # Header
        hdr = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        header_content = tk.Frame(hdr, bg=self.theme.get_color('panel'))
        header_content.pack(pady=20)

        self.make_label(header_content, "Create Account", 18, bold=True,
                       color=self.theme.get_color('accent')).pack()
        self.make_ornamental_divider(header_content, width=200).pack(pady=5)

        # Body
        body = tk.Frame(self.root, bg=self.theme.get_color('bg'))
        body.pack(expand=True, padx=40)

        form_frame = tk.Frame(body, bg=self.theme.get_color('bg'))
        form_frame.pack(pady=20)

        # User ID - flat entry
        self.make_label(form_frame, "User ID", 11).pack(anchor="w")
        id_entry = self._create_entry(form_frame)
        id_entry.pack(pady=(5, 15), fill="x")

        # Password
        self.make_label(form_frame, "Password", 11).pack(anchor="w")
        pw_entry = self._create_entry(form_frame, show="●")
        pw_entry.pack(pady=(5, 15), fill="x")

        # Confirm Password
        self.make_label(form_frame, "Confirm Password", 11).pack(anchor="w")
        pw2_entry = self._create_entry(form_frame, show="●")
        pw2_entry.pack(pady=(5, 25), fill="x")

        def do_register():
            success, message = self.auth.register(
                id_entry.get(), pw_entry.get(), pw2_entry.get()
            )
            if success:
                messagebox.showinfo("Success", message)
                self.show_login()
            else:
                messagebox.showerror("Error", message)

        self.make_button(form_frame, "Register", do_register,
                        width=280, height=55).pack(pady=10)

        link_frame = tk.Frame(body, bg=self.theme.get_color('bg'))
        link_frame.pack(pady=10)
        self.make_label(link_frame, "Already have an account?", 11,
                       color=self.theme.get_color('text_secondary')).pack(side="left")
        self._create_link(link_frame, "Login", self.show_login).pack(side="left")

        pw2_entry.bind("<Return>", lambda _: do_register())

        self._create_footer()

    def show_login(self):
        """Display the login screen."""
        self.clear_screen()
        self.root.title("FEST — Login")

        # Header
        hdr = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        header_content = tk.Frame(hdr, bg=self.theme.get_color('panel'))
        header_content.pack(pady=20)

        self.make_label(header_content, "Sign In", 18, bold=True,
                       color=self.theme.get_color('accent')).pack()
        self.make_ornamental_divider(header_content, width=200).pack(pady=5)

        # Body
        body = tk.Frame(self.root, bg=self.theme.get_color('bg'))
        body.pack(expand=True, padx=40)

        form_frame = tk.Frame(body, bg=self.theme.get_color('bg'))
        form_frame.pack(pady=20)

        # User ID
        self.make_label(form_frame, "User ID", 11).pack(anchor="w")
        id_entry = self._create_entry(form_frame)
        id_entry.pack(pady=(5, 15), fill="x")

        # Password
        self.make_label(form_frame, "Password", 11).pack(anchor="w")
        pw_entry = self._create_entry(form_frame, show="●")
        pw_entry.pack(pady=(5, 25), fill="x")

        def do_login():
            success, message = self.auth.login(id_entry.get(), pw_entry.get())
            if success:
                self.show_menu()
            else:
                messagebox.showerror("Login Failed", message)

        self.make_button(form_frame, "Login", do_login,
                        width=280, height=55).pack(pady=10)
        pw_entry.bind("<Return>", lambda _: do_login())

        link_frame = tk.Frame(body, bg=self.theme.get_color('bg'))
        link_frame.pack(pady=10)
        self.make_label(link_frame, "Don't have an account?", 11,
                       color=self.theme.get_color('text_secondary')).pack(side="left")
        self._create_link(link_frame, "Register here", self.show_register).pack(side="left")

        self._create_footer()

    def show_menu(self):
        """Display the main menu."""
        self.clear_screen()
        self.root.title(f"FEST — Menu ({self.auth.current_user})")

        # Header
        hdr = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        header_row = tk.Frame(hdr, bg=self.theme.get_color('panel'))
        header_row.pack(fill="x", padx=20, pady=15)

        user_frame = tk.Frame(header_row, bg=self.theme.get_color('panel'))
        user_frame.pack(side="left")
        self.make_label(user_frame, f"Logged in as: {self.auth.current_user}",
                       13, bold=True, color=self.theme.get_color('accent')).pack(side="left")

        theme_text = "☀️ Light" if self.theme.is_dark else "🌙 Dark"
        self.make_button(user_frame, theme_text, self._toggle_theme,
                        width=120, height=35).pack(side="left", padx=20)

        self.make_button(header_row, "Logout", self.do_logout,
                        width=120, height=35).pack(side="right")

        # Body
        body = tk.Frame(self.root, bg=self.theme.get_color('bg'))
        body.pack(expand=True, fill="both", padx=30, pady=20)

        self.make_label(body, "Main Menu", 18, bold=True,
                       color=self.theme.get_color('accent')).pack()
        self.make_ornamental_divider(body, width=260).pack(pady=10)
        self.make_label(body, "Click a button or press 0–9, D for Dean's List, S for Statistics",
                       11, color=self.theme.get_color('text_secondary')).pack(pady=10)

        grid = tk.Frame(body, bg=self.theme.get_color('bg'))
        grid.pack(pady=10)

        # Restore the border + inner frame styling for menu buttons
        for i in range(len(self.OPTION_LABELS)):
            r, c = divmod(i, 2)
            color = self.OPTION_COLORS[i % len(self.OPTION_COLORS)]
            tag = str(i) if i < 10 else ("D" if i == 10 else "S")

            # Colored border frame
            border = tk.Frame(grid, bg=color, padx=2, pady=2)
            border.grid(row=r, column=c, padx=10, pady=8)

            # Inner frame with card background
            inner = tk.Frame(border, bg=self.theme.get_color('card'))
            inner.pack()

            # Button uses the card color, so the text uses the border color
            self.make_button(
                inner,
                text=f"  [{tag}]  {self.OPTION_LABELS[i]}  ",
                cmd=lambda n=i: self._handle_option(n),
                color=self.theme.get_color('card'),
                width=290, height=60
            ).pack()

        def on_key(e):
            ch = e.char
            if ch in "0123456789":
                self._handle_option(int(ch))
            elif ch.lower() == "d":
                self._handle_option(10)
            elif ch.lower() == "s":
                self._handle_option(11)

        self.root.bind("<Key>", on_key)

        self._create_footer(show_close=False)

    def _handle_option(self, n):
        """Handle menu option selection."""
        from modules.operations import OperationsManager
        ops = OperationsManager(self.root, self.theme, self.data, self.viz, self.queries)

        dispatch = {
            0: ops.add_student,
            1: ops.edit_student,
            2: ops.delete_student,
            3: ops.gpa_formula,
            4: ops.swarm_plot,
            5: ops.countplot,
            6: ops.piechart,
            7: ops.student_profile,
            8: ops.student_id_card,
            9: ops.queries,
            10: ops.deans_list,
            11: ops.statistics_dashboard,
        }
        dispatch.get(n, lambda: None)()

    def _toggle_theme(self):
        """Toggle between dark and light mode."""
        self.theme.toggle_mode()
        self.show_menu()

    def do_logout(self):
        """Log out the current user."""
        self.auth.logout()
        self.show_welcome()

    def _create_entry(self, parent, show=""):
        """Create a flat entry widget without accent border."""
        e = tk.Entry(parent, font=('Segoe UI', 12),
                    bg=self.theme.get_color('card'),
                    fg=self.theme.get_color('text'),
                    insertbackground=self.theme.get_color('highlight'),
                    relief="flat",
                    show=show)
        return e

    def _create_link(self, parent, text, cmd):
        """Create a clickable text link."""
        return tk.Button(parent, text=text, command=cmd,
                        font=('Segoe UI', 11, 'underline'),
                        fg=self.theme.get_color('accent'),
                        bg=self.theme.get_color('bg'),
                        activeforeground=self.theme.get_color('accent_light'),
                        activebackground=self.theme.get_color('bg'),
                        relief="flat", cursor="hand2", bd=0)

    def _create_footer(self, show_close=True):
        """Create a consistent footer."""
        footer = tk.Frame(self.root, bg=self.theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=self.theme.get_color('border'), height=1).pack(fill="x")

        footer_content = tk.Frame(footer, bg=self.theme.get_color('panel'))
        footer_content.pack(pady=8)

        if show_close:
            self.make_button(footer_content, "Close", self.root.destroy,
                           width=120, height=35).pack(side="right", padx=10)

        self.make_label(footer_content, "FEST · Vanderbilt University 2026",
                       10, color=self.theme.get_color('text_secondary')).pack(side="left")