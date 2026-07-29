"""
Operations management for FEST application.
Handles all CRUD operations and student management features.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class OperationsManager:
    """Manages all student operations and features."""

    def __init__(self, root, theme_manager, data_manager, viz_manager, query_manager):
        self.root = root
        self.theme = theme_manager
        self.data = data_manager
        self.viz = viz_manager
        self.query_manager = query_manager  # Store as query_manager

        # Color constants
        self.GRADE_PALETTE = {
            "A (90-100)": self.theme.get_color('accent'),
            "B (80-89)": "#B8860B",
            "C (70-79)": "#8B6F35",
            "D (60-69)": "#7C2D12",
            "F (0-59)": "#6E1E22",
        }

    def add_student(self):
        """Add a new student record."""
        top = self._create_popup("Add New Student")

        form = tk.Frame(top, bg=self.theme.get_color('bg'))
        form.pack(padx=30, pady=10)
        form.columnconfigure(1, weight=1)

        field_defs = [
            ("Student ID", ""), ("Full Name", ""), ("Major", ""),
            ("Course Code", ""), ("Course Title", ""), ("Points (0-100)", "")
        ]
        entries = []
        for i, (lbl, _) in enumerate(field_defs):
            entries.append(self._create_form_row(form, lbl, i))

        sid_e, name_e, major_e, code_e, title_e, pts_e = entries

        # GPA preview
        gpa_var = tk.StringVar(value="—")
        tk.Label(form, text="Grade / GPA", font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('bg')).grid(row=6, column=0, sticky="e", padx=(0, 12), pady=8)
        tk.Label(form, textvariable=gpa_var, font=('Segoe UI', 12, 'bold'),
                fg=self.theme.get_color('success'),
                bg=self.theme.get_color('bg')).grid(row=6, column=1, sticky="w")

        def update_gpa(*_):
            try:
                letter, gpa = self.data.points_to_grade(pts_e.get())
                gpa_var.set(f"{letter}  /  {gpa:.1f}")
            except (ValueError, TypeError):
                gpa_var.set("—")

        pts_e.bind("<KeyRelease>", update_gpa)

        def do_add():
            text_vals = [e.get().strip() for e in entries[:-1]]
            if not all(text_vals):
                messagebox.showerror("Error", "All fields are required.", parent=top)
                return
            try:
                pts = float(pts_e.get())
                assert 0 <= pts <= 100
            except (ValueError, AssertionError):
                messagebox.showerror("Error", "Points must be 0-100.", parent=top)
                return

            letter, gpa = self.data.points_to_grade(pts)
            self.data.append_student({
                "student_id": text_vals[0], "name": text_vals[1],
                "major": text_vals[2], "course_code": text_vals[3],
                "course_title": text_vals[4], "points": f"{pts:.1f}",
                "gpa": f"{gpa:.1f}",
            })
            messagebox.showinfo("Success", f"Added {text_vals[1]} ({letter} / {gpa:.1f} GPA)",
                              parent=top)
            for e in entries:
                e.delete(0, "end")
            gpa_var.set("—")

        self._add_buttons(top, [("Add Student", do_add), ("Close", top.destroy)])

    def edit_student(self):
        """Edit an existing student record."""
        top = self._create_popup("Edit Student Record", width=820)

        records = self.data.load_students()
        tree, refresh = self._create_treeview(top, records)

        def open_edit_form():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a row to edit.", parent=top)
                return
            idx = int(sel[0])
            rec = records[idx]

            win = self._create_popup("Edit Record", width=520, height=490)
            form = tk.Frame(win, bg=self.theme.get_color('bg'))
            form.pack(padx=30)
            form.columnconfigure(1, weight=1)

            field_defs = [
                ("Student ID", "student_id"), ("Full Name", "name"),
                ("Major", "major"), ("Course Code", "course_code"),
                ("Course Title", "course_title"), ("Points (0-100)", "points")
            ]
            entries = {}
            for i, (lbl, key) in enumerate(field_defs):
                entries[key] = self._create_form_row(form, lbl, i, initial=rec[key])

            gpa_var = tk.StringVar(value=rec.get("gpa", "—"))
            tk.Label(form, text="Grade / GPA", font=('Segoe UI', 11),
                    fg=self.theme.get_color('text_secondary'),
                    bg=self.theme.get_color('bg')).grid(
                        row=len(field_defs), column=0, sticky="e", padx=(0, 12), pady=8)
            tk.Label(form, textvariable=gpa_var, font=('Segoe UI', 12, 'bold'),
                    fg=self.theme.get_color('success'),
                    bg=self.theme.get_color('bg')).grid(row=len(field_defs), column=1, sticky="w")

            def update_gpa(*_):
                try:
                    letter, gpa = self.data.points_to_grade(entries["points"].get())
                    gpa_var.set(f"{letter}  /  {gpa:.1f}")
                except (ValueError, TypeError):
                    gpa_var.set("—")

            entries["points"].bind("<KeyRelease>", update_gpa)
            update_gpa()

            def do_save():
                text_vals = {k: entries[k].get().strip() for k in entries if k != "points"}
                if not all(text_vals.values()):
                    messagebox.showerror("Error", "All fields are required.", parent=win)
                    return
                try:
                    pts = float(entries["points"].get())
                    assert 0 <= pts <= 100
                except (ValueError, AssertionError):
                    messagebox.showerror("Error", "Points must be 0-100.", parent=win)
                    return

                letter, gpa = self.data.points_to_grade(pts)
                records[idx] = {
                    "student_id": text_vals["student_id"], "name": text_vals["name"],
                    "major": text_vals["major"], "course_code": text_vals["course_code"],
                    "course_title": text_vals["course_title"], "points": f"{pts:.1f}",
                    "gpa": f"{gpa:.1f}",
                }
                self.data.save_students(records)
                refresh()
                messagebox.showinfo("Success", "Record updated.", parent=win)
                win.destroy()

            self._add_buttons(win, [("Save Changes", do_save), ("Cancel", win.destroy)])

        self._add_buttons(top, [("Edit Selected", open_edit_form), ("Close", top.destroy)])

    def delete_student(self):
        """Delete student records."""
        top = self._create_popup("Delete Student Records", width=820)

        records = self.data.load_students()
        tree, refresh = self._create_treeview(top, records, multi=True)

        def do_delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select at least one record.", parent=top)
                return
            indices = {int(item) for item in sel}
            if not messagebox.askyesno("Confirm Delete",
                                      f"Delete {len(indices)} record(s)? This cannot be undone.",
                                      parent=top):
                return
            new_recs = [r for i, r in enumerate(records) if i not in indices]
            records.clear()
            records.extend(new_recs)
            self.data.save_students(records)
            refresh()
            messagebox.showinfo("Deleted", f"{len(indices)} record(s) removed.", parent=top)

        self._add_buttons(top, [("Delete Selected", do_delete), ("Close", top.destroy)])

    def gpa_formula(self):
        """Edit GPA formula - FIXED with instruction text and proper entry boxes."""
        top = self._create_popup("GPA Grading Scale", width=580, height=720)

        # Instruction text
        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)

        # Header with instruction
        header_frame = tk.Frame(top, bg=self.theme.get_color('panel'))
        header_frame.pack(fill="x")
        tk.Frame(header_frame, bg=self.theme.get_color('accent'), height=2).pack(fill="x")
        ui.make_label(header_frame, "GPA Calculation Scale", 15, bold=True,
                     color=self.theme.get_color('accent')).pack(pady=(10, 2))
        ui.make_label(header_frame, "Select a row, edit Min/Max, then click Save Row",
                     11, color=self.theme.get_color('text_secondary')).pack(pady=(0, 10))

        # Treeview for GPA scale
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                       background=self.theme.get_color('card'),
                       foreground=self.theme.get_color('text'),
                       fieldbackground=self.theme.get_color('card'),
                       rowheight=30)
        style.configure("Custom.Treeview.Heading",
                       background=self.theme.get_color('panel'),
                       foreground=self.theme.get_color('accent'),
                       font=('Segoe UI', 10, 'bold'))

        tree_frame = tk.Frame(top, bg=self.theme.get_color('bg'))
        tree_frame.pack(fill="both", expand=True, padx=18, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("range", "letter", "gpa"),
                           show="headings", style="Custom.Treeview", height=13)
        for col, head, w in [("range", "Points Range", 180),
                             ("letter", "Letter Grade", 150),
                             ("gpa", "GPA Points", 140)]:
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)

        def refresh_tree():
            tree.delete(*tree.get_children())
            for i, (lo, hi, letter, gpa) in enumerate(self.data.gpa_scale):
                tree.insert("", "end", iid=str(i),
                           values=(f"{lo} – {hi}", letter, f"{gpa:.1f}"))
        refresh_tree()

        # Edit panel - FIXED with proper entry boxes
        edit_panel = tk.Frame(top, bg=self.theme.get_color('panel'))
        edit_panel.pack(fill="x", padx=18, pady=8)
        tk.Frame(edit_panel, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        info_row = tk.Frame(edit_panel, bg=self.theme.get_color('panel'))
        info_row.pack(fill="x", padx=14, pady=10)

        letter_var = tk.StringVar(value="—")
        gpa_lbl_var = tk.StringVar(value="—")

        tk.Label(info_row, text="Selected Grade:", font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=5)
        tk.Label(info_row, textvariable=letter_var, font=('Segoe UI', 12, 'bold'),
                fg=self.theme.get_color('accent'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=5)
        tk.Label(info_row, text="GPA:", font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=(20, 5))
        tk.Label(info_row, textvariable=gpa_lbl_var, font=('Segoe UI', 12, 'bold'),
                fg=self.theme.get_color('success'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=5)

        input_row = tk.Frame(edit_panel, bg=self.theme.get_color('panel'))
        input_row.pack(fill="x", padx=14, pady=5)

        tk.Label(input_row, text="Min:", font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=5)

        # Min entry with wrapper
        min_wrap = tk.Frame(input_row, bg=self.theme.get_color('highlight'), padx=1, pady=1)
        min_wrap.pack(side="left", padx=5)
        min_e = tk.Entry(min_wrap, font=('Segoe UI', 12),
                        bg=self.theme.get_color('card'),
                        fg=self.theme.get_color('text'),
                        insertbackground=self.theme.get_color('highlight'),
                        relief="flat", width=6)
        min_e.pack()

        tk.Label(input_row, text="Max:", font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('panel')).pack(side="left", padx=5)

        # Max entry with wrapper
        max_wrap = tk.Frame(input_row, bg=self.theme.get_color('highlight'), padx=1, pady=1)
        max_wrap.pack(side="left", padx=5)
        max_e = tk.Entry(max_wrap, font=('Segoe UI', 12),
                        bg=self.theme.get_color('card'),
                        fg=self.theme.get_color('text'),
                        insertbackground=self.theme.get_color('highlight'),
                        relief="flat", width=6)
        max_e.pack()

        selected_idx = [None]

        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            selected_idx[0] = idx
            lo, hi, letter, gpa = self.data.gpa_scale[idx]
            letter_var.set(letter)
            gpa_lbl_var.set(f"{gpa:.1f}")
            min_e.delete(0, "end")
            min_e.insert(0, str(lo))
            max_e.delete(0, "end")
            max_e.insert(0, str(hi))

        tree.bind("<<TreeviewSelect>>", on_select)

        def save_row():
            idx = selected_idx[0]
            if idx is None:
                messagebox.showwarning("Select", "Select a row first.", parent=top)
                return
            try:
                lo = int(min_e.get().strip())
                hi = int(max_e.get().strip())
                assert 0 <= lo <= 100 and 0 <= hi <= 100 and lo <= hi
            except (ValueError, AssertionError):
                messagebox.showerror("Invalid Input",
                                   "Min and Max must be whole numbers 0-100, with Min ≤ Max.",
                                   parent=top)
                return
            _, _, letter, gpa = self.data.gpa_scale[idx]
            self.data.gpa_scale[idx] = (lo, hi, letter, gpa)
            self.data.save_gpa_scale()
            refresh_tree()
            tree.selection_set(str(idx))
            messagebox.showinfo("Saved", f"Range for {letter} updated to {lo} – {hi}.", parent=top)

        def reset_defaults():
            if not messagebox.askyesno("Reset", "Reset all ranges back to defaults?", parent=top):
                return
            self.data.reset_gpa_scale()
            refresh_tree()
            selected_idx[0] = None
            letter_var.set("—")
            gpa_lbl_var.set("—")
            min_e.delete(0, "end")
            max_e.delete(0, "end")
            messagebox.showinfo("Reset", "Grading scale reset to defaults.", parent=top)

        btn_row = tk.Frame(edit_panel, bg=self.theme.get_color('panel'))
        btn_row.pack(pady=10)

        ui.make_button(btn_row, "Save Row", save_row,
                      width=130, height=40).pack(side="left", padx=5)
        ui.make_button(btn_row, "Reset Defaults", reset_defaults,
                      width=130, height=40).pack(side="left", padx=5)

        self._add_buttons(top, [("Close", top.destroy)])

    def swarm_plot(self):
        """Display swarm plot."""
        self.viz.create_swarm_plot(self.root, self.theme)

    def countplot(self):
        """Display major count plot."""
        self.viz.create_countplot(self.root, self.theme)

    def piechart(self):
        """Display grade pie chart."""
        self.viz.create_piechart(self.root, self.theme)

    def student_profile(self):
        """Display student profile viewer."""
        self._show_student_profile()

    def student_id_card(self):
        """Display student ID card."""
        self._show_student_id_card()

    def queries(self):
        """Display academic queries."""
        # Fix: Call show_queries on the query_manager instance
        self.query_manager.show_queries(self.root, self.theme, self.data)

    def deans_list(self):
        """Display Dean's List."""
        self.query_manager.show_deans_list(self.root, self.theme, self.data)

    def statistics_dashboard(self):
        """Display comprehensive statistics dashboard."""
        self._show_statistics_dashboard()

    def _show_student_profile(self):
        """Display student profile viewer - FIXED with flat buttons and proper navigation."""
        records = self.data.load_students()
        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        student_dict = {}
        for r in records:
            sid = r["student_id"]
            if sid not in student_dict:
                student_dict[sid] = []
            student_dict[sid].append(r)

        student_ids = list(student_dict.keys())
        total = len(student_ids)
        current_idx = [0]

        top = self._create_popup("Student Profile Viewer", width=760, height=640)
        top.resizable(True, True)
        tk.Frame(top, bg=self.theme.get_color('accent'), height=3).pack(fill="x")

        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)

        # Top bar with search
        topbar = tk.Frame(top, bg=self.theme.get_color('panel'))
        topbar.pack(fill="x")
        tk.Frame(topbar, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        ui.make_label(topbar, "Student Profile", 15, bold=True).pack(
            side="left", padx=18, pady=12)

        search_bar = tk.Frame(topbar, bg=self.theme.get_color('panel'))
        search_bar.pack(side="right", padx=18, pady=10)

        ui.make_label(search_bar, "Search ID:", 11,
                     color=self.theme.get_color('text_secondary')).pack(side="left", padx=(0, 6))
        srch_wrap = tk.Frame(search_bar, bg=self.theme.get_color('highlight'), padx=1, pady=1)
        srch_wrap.pack(side="left")
        srch_entry = tk.Entry(srch_wrap, font=('Segoe UI', 11),
                             bg=self.theme.get_color('card'),
                             fg=self.theme.get_color('text'),
                             insertbackground=self.theme.get_color('highlight'),
                             relief="flat", width=14)
        srch_entry.pack()

        def do_search():
            sid = srch_entry.get().strip()
            if not sid:
                return
            if sid in student_dict:
                show_student(student_ids.index(sid))
            else:
                messagebox.showwarning("Not Found", f"Student ID '{sid}' not found.", parent=top)

        ui.make_button(search_bar, "Search", do_search,
                      width=110, height=38).pack(side="left", padx=(8, 0))
        srch_entry.bind("<Return>", lambda _: do_search())

        # Profile card
        card = tk.Frame(top, bg=self.theme.get_color('panel'), padx=24, pady=18)
        card.pack(fill="x", padx=20, pady=(14, 6))
        tk.Frame(card, bg=self.theme.get_color('accent'), height=2).pack(fill="x", pady=(0, 12))

        id_var = tk.StringVar()
        name_var = tk.StringVar()
        major_var = tk.StringVar()

        def info_row(icon, var, fg_color):
            row = tk.Frame(card, bg=self.theme.get_color('panel'))
            row.pack(fill="x", pady=4)
            tk.Label(row, text=icon, font=('Segoe UI', 14, 'bold'),
                    fg=self.theme.get_color('text_secondary'),
                    bg=self.theme.get_color('panel'), width=3, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var, font=('Segoe UI', 14, 'bold'),
                    fg=fg_color, bg=self.theme.get_color('panel'), anchor="w").pack(side="left")

        info_row("ID", id_var, self.theme.get_color('accent'))
        info_row("👤", name_var, self.theme.get_color('text'))
        info_row("📚", major_var, self.theme.get_color('text_secondary'))

        # Course table
        tbl_hdr = tk.Frame(top, bg=self.theme.get_color('bg'))
        tbl_hdr.pack(fill="x", padx=20, pady=(6, 2))
        ui.make_label(tbl_hdr, "Exam Scores", 12, bold=True,
                     color=self.theme.get_color('text_secondary')).pack(anchor="w")

        tbl_frame = tk.Frame(top, bg=self.theme.get_color('bg'))
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        cols = ("course_code", "course_title", "points", "letter", "gpa")
        heads = ("Course Code", "Course Title", "Points (/ 100)", "Letter", "GPA")
        widths = (110, 220, 130, 80, 80)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Profile.Treeview",
                       background=self.theme.get_color('card'),
                       foreground=self.theme.get_color('text'),
                       fieldbackground=self.theme.get_color('card'),
                       rowheight=30)
        style.configure("Profile.Treeview.Heading",
                       background=self.theme.get_color('panel'),
                       foreground=self.theme.get_color('accent'),
                       font=('Segoe UI', 10, 'bold'))
        style.map("Profile.Treeview",
                 background=[("selected", self.theme.get_color('accent'))],
                 foreground=[("selected", '#FFFFFF')])

        tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                           style="Profile.Treeview", height=7)
        for col, head, w in zip(cols, heads, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Navigation bar - FIXED with flat buttons and proper text
        nav = tk.Frame(top, bg=self.theme.get_color('panel'))
        nav.pack(fill="x")
        tk.Frame(nav, bg=self.theme.get_color('border'), height=1).pack(fill="x")

        inner_nav = tk.Frame(nav, bg=self.theme.get_color('panel'))
        inner_nav.pack(pady=10)

        counter_var = tk.StringVar()

        # Create flat navigation buttons with proper text
        prev_btn = tk.Button(inner_nav, text="◀ Previous",
                            font=('Segoe UI', 12),
                            bg=self.theme.get_color('panel'),
                            fg=self.theme.get_color('text'),
                            relief="flat",
                            cursor="hand2",
                            state="disabled")
        prev_btn.pack(side="left", padx=10)

        tk.Label(inner_nav, textvariable=counter_var,
                font=('Segoe UI', 12, 'bold'),
                fg=self.theme.get_color('text'),
                bg=self.theme.get_color('panel'),
                width=10, anchor="center").pack(side="left", padx=16)

        next_btn = tk.Button(inner_nav, text="Next ▶",
                            font=('Segoe UI', 12),
                            bg=self.theme.get_color('panel'),
                            fg=self.theme.get_color('text'),
                            relief="flat",
                            cursor="hand2")
        next_btn.pack(side="left", padx=10)

        ui.make_button(inner_nav, "Close", top.destroy,
                      width=110, height=46).pack(side="left", padx=20)

        def show_student(idx):
            current_idx[0] = idx
            sid = student_ids[idx]
            recs = student_dict[sid]
            first = recs[0]

            id_var.set(f"  {first['student_id']}")
            name_var.set(f"  {first['name']}")
            major_var.set(f"  {first['major']}")

            tree.delete(*tree.get_children())
            for r in recs:
                try:
                    letter, _ = self.data.points_to_grade(float(r["points"]))
                except (ValueError, TypeError):
                    letter = "—"
                tree.insert("", "end", values=(
                    r["course_code"], r["course_title"],
                    r["points"], letter, r["gpa"],
                ))

            counter_var.set(f"{idx + 1}  /  {total}")

            # Update button states
            prev_btn.config(state="normal" if idx > 0 else "disabled")
            next_btn.config(state="normal" if idx < total - 1 else "disabled")

            # Update button commands
            prev_btn.config(command=lambda: show_student(idx - 1) if idx > 0 else None)
            next_btn.config(command=lambda: show_student(idx + 1) if idx < total - 1 else None)

        show_student(0)

    def _show_student_id_card(self):
        """Display student ID card - FIXED with default avatar and flat buttons."""
        records = self.data.load_students()
        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        student_dict = {}
        for r in records:
            sid = r["student_id"]
            if sid not in student_dict:
                student_dict[sid] = []
            student_dict[sid].append(r)

        student_ids = list(student_dict.keys())
        total = len(student_ids)
        current = [0]

        VU_GOLD = self.theme.get_color('accent')
        VU_BLACK = "#121212"
        CARD_W = 520
        CARD_H = 295

        top = tk.Toplevel(self.root)
        top.title("Student ID Card")
        top.configure(bg=self.theme.get_color('bg'))
        top.resizable(False, False)
        top.grab_set()
        top.geometry("780x600")

        tk.Frame(top, bg=self.theme.get_color('accent'), height=3).pack(fill="x")

        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)

        # Top bar with search
        topbar = tk.Frame(top, bg=self.theme.get_color('panel'))
        topbar.pack(fill="x")
        tk.Frame(topbar, bg=self.theme.get_color('accent'), height=2).pack(fill="x")

        ui.make_label(topbar, "Student ID Card", 15, bold=True).pack(
            side="left", padx=18, pady=10)

        srch_row = tk.Frame(topbar, bg=self.theme.get_color('panel'))
        srch_row.pack(side="right", padx=18, pady=8)
        ui.make_label(srch_row, "Search ID:", 11,
                     color=self.theme.get_color('text_secondary')).pack(side="left", padx=(0, 6))
        sw = tk.Frame(srch_row, bg=self.theme.get_color('highlight'), padx=1, pady=1)
        sw.pack(side="left")
        srch_e = tk.Entry(sw, font=('Segoe UI', 11),
                         bg=self.theme.get_color('card'),
                         fg=self.theme.get_color('text'),
                         insertbackground=self.theme.get_color('highlight'),
                         relief="flat", width=13)
        srch_e.pack()

        def do_search():
            sid = srch_e.get().strip()
            if not sid:
                return
            if sid in student_dict:
                show_card(student_ids.index(sid))
            else:
                messagebox.showwarning("Not Found", f"Student ID '{sid}' not found.", parent=top)

        ui.make_button(srch_row, "Search", do_search,
                      width=100, height=36).pack(side="left", padx=(8, 0))
        srch_e.bind("<Return>", lambda _: do_search())

        # Card frame
        card_outer = tk.Frame(top, bg=VU_GOLD)
        card_outer.pack(pady=24)

        card_body = tk.Frame(card_outer, bg=VU_BLACK, width=CARD_W, height=CARD_H)
        card_body.pack(padx=3, pady=3)
        card_body.pack_propagate(False)

        def make_default_avatar(parent, name, size=110):
            """Create a simple default avatar with initials."""
            cv = tk.Canvas(parent, width=size, height=size,
                          bg=VU_BLACK, highlightthickness=0)
            cx = size // 2
            cy = size // 2

            # Circle background
            cv.create_oval(5, 5, size-5, size-5,
                          fill=self.theme.get_color('accent'),
                          outline=VU_GOLD, width=2)

            # Initials
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            if not initials:
                initials = "?"
            cv.create_text(cx, cy, text=initials,
                          font=('Georgia', int(size*0.4), 'bold'),
                          fill=VU_BLACK)

            return cv

        def make_barcode(parent, seed_str, w=CARD_W, h=34):
            seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) & 0xFFFFFFFF
            rng = np.random.default_rng(seed)
            cv = tk.Canvas(parent, width=w, height=h, bg=VU_GOLD, highlightthickness=0)
            x = 10
            while x < w - 10:
                bw = int(rng.choice([1, 1, 2, 2, 3]))
                gp = int(rng.choice([1, 2, 3]))
                cv.create_rectangle(x, 3, x+bw, h-8, fill=VU_BLACK, outline="")
                x += bw + gp
            cv.create_text(w//2, h-3, text=seed_str, anchor="s",
                          fill=VU_BLACK, font=("Courier New", 7, "bold"))
            return cv

        def populate_card(sid):
            for w in card_body.winfo_children():
                w.destroy()
            first = student_dict[sid][0]
            recs = student_dict[sid]

            # Gold header
            hdr = tk.Frame(card_body, bg=VU_GOLD, height=58)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            tk.Label(hdr, text="V", font=("Georgia", 36, "bold"),
                    fg=VU_BLACK, bg=VU_GOLD).pack(side="left", padx=(12, 2), pady=2)
            hi = tk.Frame(hdr, bg=VU_GOLD)
            hi.pack(side="left", pady=6)
            tk.Label(hi, text="VANDERBILT UNIVERSITY",
                    font=("Georgia", 13, "bold"), fg=VU_BLACK, bg=VU_GOLD).pack(anchor="w")
            tk.Label(hi, text="Student Identification Card",
                    font=("Segoe UI", 8), fg="#4a3800", bg=VU_GOLD).pack(anchor="w")
            tk.Label(hdr, text="2026", font=("Segoe UI", 10, "bold"),
                    fg=VU_BLACK, bg=VU_GOLD).pack(side="right", padx=12)

            # Body
            body = tk.Frame(card_body, bg=VU_BLACK)
            body.pack(fill="both", expand=True, padx=12, pady=8)

            # Left: avatar
            left = tk.Frame(body, bg=VU_BLACK)
            left.pack(side="left", padx=(0, 12))
            make_default_avatar(left, first["name"]).pack()
            tk.Label(left, text="S T U D E N T",
                    font=("Segoe UI", 7, "bold"), fg=VU_GOLD, bg=VU_BLACK).pack(pady=(4, 0))

            # Divider
            tk.Frame(body, bg=VU_GOLD, width=2).pack(side="left", fill="y", padx=(0, 12))

            # Right: info
            right = tk.Frame(body, bg=VU_BLACK)
            right.pack(side="left", fill="both", expand=True)
            tk.Label(right, text=first["name"], font=("Georgia", 16, "bold"),
                    fg="white", bg=VU_BLACK, wraplength=250, justify="left").pack(anchor="w")
            tk.Label(right, text=first["major"], font=("Segoe UI", 11),
                    fg=VU_GOLD, bg=VU_BLACK).pack(anchor="w", pady=(3, 0))
            tk.Label(right, text="Vanderbilt University · Nashville, TN",
                    font=("Segoe UI", 8), fg="#7a7a7a", bg=VU_BLACK).pack(anchor="w", pady=(2, 6))
            tk.Frame(right, bg=VU_GOLD, height=1).pack(fill="x", pady=(0, 6))
            tk.Label(right, text="STUDENT ID", font=("Segoe UI", 7, "bold"),
                    fg="#8a8a8a", bg=VU_BLACK).pack(anchor="w")
            tk.Label(right, text=first["student_id"], font=("Courier New", 15, "bold"),
                    fg=VU_GOLD, bg=VU_BLACK).pack(anchor="w")
            tk.Label(right, text=f"Enrolled courses: {len(recs)}",
                    font=("Segoe UI", 8), fg="#7a7a7a", bg=VU_BLACK).pack(anchor="w", pady=(6, 0))

            # Barcode
            make_barcode(card_body, first["student_id"]).pack(fill="x")

        # Navigation - FIXED with flat buttons
        tk.Frame(top, bg=self.theme.get_color('border'), height=1).pack(fill="x")
        nav = tk.Frame(top, bg=self.theme.get_color('panel'))
        nav.pack(fill="x")
        inner_nav = tk.Frame(nav, bg=self.theme.get_color('panel'))
        inner_nav.pack(pady=18)

        counter_var = tk.StringVar(value="")

        prev_btn = tk.Button(inner_nav, text="◀ Previous",
                            font=('Segoe UI', 12),
                            bg=self.theme.get_color('panel'),
                            fg=self.theme.get_color('text'),
                            relief="flat",
                            cursor="hand2",
                            state="disabled")
        prev_btn.pack(side="left", padx=12)

        tk.Label(inner_nav, textvariable=counter_var,
                font=('Segoe UI', 13, 'bold'),
                fg=self.theme.get_color('text'),
                bg=self.theme.get_color('panel'),
                width=10, anchor="center").pack(side="left", padx=16)

        next_btn = tk.Button(inner_nav, text="Next ▶",
                            font=('Segoe UI', 12),
                            bg=self.theme.get_color('panel'),
                            fg=self.theme.get_color('text'),
                            relief="flat",
                            cursor="hand2")
        next_btn.pack(side="left", padx=12)

        ui.make_button(inner_nav, "Close", top.destroy,
                      width=140, height=48).pack(side="left", padx=20)

        def show_card(i):
            current[0] = i
            populate_card(student_ids[i])
            counter_var.set(f"{i + 1}  /  {total}")
            prev_btn.config(state="normal" if i > 0 else "disabled")
            next_btn.config(state="normal" if i < total - 1 else "disabled")
            prev_btn.config(command=lambda: show_card(i - 1) if i > 0 else None)
            next_btn.config(command=lambda: show_card(i + 1) if i < total - 1 else None)

        show_card(0)

    def _show_statistics_dashboard(self):
        """Display the statistics dashboard - FIXED with proper scrolling."""
        stats = self.data.get_student_statistics()
        if not stats:
            messagebox.showwarning("No Data", "No student records found.")
            return

        top = self._create_popup("📊 Statistics Dashboard", width=1000, height=700)
        top.configure(bg=self.theme.get_color('bg'))
        top.resizable(True, True)

        # Header
        hdr = tk.Frame(top, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=self.theme.get_color('accent'), height=3).pack(fill="x")

        title_frame = tk.Frame(hdr, bg=self.theme.get_color('panel'))
        title_frame.pack(pady=15)
        tk.Label(title_frame, text="📊 Academic Statistics Dashboard",
                font=('Georgia', 18, 'bold'),
                fg=self.theme.get_color('accent'),
                bg=self.theme.get_color('panel')).pack()

        # Create scrollable container with proper scrolling behavior
        container = tk.Frame(top, bg=self.theme.get_color('bg'))
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # Create canvas with scrollbar
        canvas = tk.Canvas(container, bg=self.theme.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # Create frame inside canvas
        scroll_frame = tk.Frame(canvas, bg=self.theme.get_color('bg'))

        # Bind mousewheel for scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def on_arrow_keys(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")

        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)

        # Update scroll region when frame changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", configure_scroll_region)

        # Create window in canvas
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind events
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Up>", on_arrow_keys)
        canvas.bind_all("<Down>", on_arrow_keys)

        # Clean up bindings when window closes
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Up>")
            canvas.unbind_all("<Down>")
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close)

        # Overview cards - FIXED: no vertical stretching
        overview_frame = tk.Frame(scroll_frame, bg=self.theme.get_color('bg'))
        overview_frame.pack(fill="x", pady=10)

        metrics = [
            ("🎓 Total Students", stats["total_students"]),
            ("📚 Total Courses", stats["total_courses"]),
            ("📈 Average GPA", f"{stats['avg_gpa']:.2f}"),
            ("🏆 Top GPA", f"{stats['max_gpa']:.2f}"),
            ("📉 Lowest GPA", f"{stats['min_gpa']:.2f}"),
            ("⭐ Student Avg GPA", f"{stats['avg_student_gpa']:.2f}"),
        ]

        # Create grid with fixed height to prevent stretching
        for i, (label, value) in enumerate(metrics):
            card = tk.Frame(overview_frame, bg=self.theme.get_color('card'),
                           relief="flat", bd=1)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            card.configure(height=80)
            card.grid_propagate(False)  # Prevent stretching

            tk.Label(card, text=label, font=('Segoe UI', 10),
                    fg=self.theme.get_color('text_secondary'),
                    bg=self.theme.get_color('card')).pack(pady=(10, 0))
            tk.Label(card, text=str(value), font=('Georgia', 18, 'bold'),
                    fg=self.theme.get_color('accent'),
                    bg=self.theme.get_color('card')).pack()

        # Grade distribution
        dist_frame = tk.Frame(scroll_frame, bg=self.theme.get_color('bg'))
        dist_frame.pack(fill="x", pady=15)

        tk.Label(dist_frame, text="📊 Grade Distribution",
                font=('Georgia', 14, 'bold'),
                fg=self.theme.get_color('text'),
                bg=self.theme.get_color('bg')).pack(anchor="w")

        grade_frame = tk.Frame(dist_frame, bg=self.theme.get_color('card'))
        grade_frame.pack(fill="x", pady=5)

        grade_colors = {
            "A": self.theme.get_color('accent'),
            "B": "#B8860B",
            "C": "#8B6F35",
            "D": "#7C2D12",
            "F": "#6E1E22",
        }

        total_grades = sum(stats["grade_distribution"].values())
        for grade, count in stats["grade_distribution"].items():
            pct = (count / total_grades * 100) if total_grades > 0 else 0
            frame = tk.Frame(grade_frame, bg=self.theme.get_color('card'))
            frame.pack(side="left", padx=15, pady=10)

            tk.Label(frame, text=grade, font=('Georgia', 16, 'bold'),
                    fg=grade_colors.get(grade, self.theme.get_color('text')),
                    bg=self.theme.get_color('card')).pack()
            tk.Label(frame, text=f"{count} ({pct:.1f}%)",
                    font=('Segoe UI', 10),
                    fg=self.theme.get_color('text_secondary'),
                    bg=self.theme.get_color('card')).pack()

        # Top students
        if stats["top_students"]:
            top_frame = tk.Frame(scroll_frame, bg=self.theme.get_color('bg'))
            top_frame.pack(fill="x", pady=15)

            tk.Label(top_frame, text="🏆 Top 5 Students",
                    font=('Georgia', 14, 'bold'),
                    fg=self.theme.get_color('text'),
                    bg=self.theme.get_color('bg')).pack(anchor="w")

            top_table = tk.Frame(top_frame, bg=self.theme.get_color('card'))
            top_table.pack(fill="x", pady=5)

            headers = ["Rank", "Student ID", "GPA"]
            for i, header in enumerate(headers):
                tk.Label(top_table, text=header, font=('Segoe UI', 10, 'bold'),
                        fg=self.theme.get_color('accent'),
                        bg=self.theme.get_color('panel')).grid(
                            row=0, column=i, padx=20, pady=5, sticky="w")

            for rank, (sid, gpa) in enumerate(stats["top_students"], 1):
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                label = medals.get(rank, f"#{rank}")
                tk.Label(top_table, text=label,
                        font=('Segoe UI', 11),
                        fg=self.theme.get_color('text'),
                        bg=self.theme.get_color('card')).grid(
                            row=rank, column=0, padx=20, pady=3, sticky="w")
                tk.Label(top_table, text=sid,
                        font=('Segoe UI', 11),
                        fg=self.theme.get_color('text'),
                        bg=self.theme.get_color('card')).grid(
                            row=rank, column=1, padx=20, pady=3, sticky="w")
                tk.Label(top_table, text=f"{gpa:.2f}",
                        font=('Segoe UI', 11, 'bold'),
                        fg=self.theme.get_color('accent'),
                        bg=self.theme.get_color('card')).grid(
                            row=rank, column=2, padx=20, pady=3, sticky="w")

        # Major distribution
        if stats["major_distribution"]:
            major_frame = tk.Frame(scroll_frame, bg=self.theme.get_color('bg'))
            major_frame.pack(fill="x", pady=15)

            tk.Label(major_frame, text="🎯 Major Distribution",
                    font=('Georgia', 14, 'bold'),
                    fg=self.theme.get_color('text'),
                    bg=self.theme.get_color('bg')).pack(anchor="w")

            major_text = ", ".join([f"{m}: {c}" for m, c in stats["major_distribution"].items()])
            tk.Label(major_frame, text=major_text,
                    font=('Segoe UI', 11),
                    fg=self.theme.get_color('text_secondary'),
                    bg=self.theme.get_color('card'),
                    wraplength=900).pack(fill="x", pady=5)

        self._add_buttons(top, [("Close", on_close)])

    def _create_popup(self, title, width=600, height=520):
        """Create a popup window."""
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry(f"{width}x{height}")
        top.configure(bg=self.theme.get_color('bg'))
        top.resizable(False, False)
        top.grab_set()
        return top

    def _create_form_row(self, parent, label, row, initial=""):
        """Create a form row with label and entry."""
        tk.Label(parent, text=label, font=('Segoe UI', 11),
                fg=self.theme.get_color('text_secondary'),
                bg=self.theme.get_color('bg')).grid(
                    row=row, column=0, sticky="e", padx=(0, 12), pady=8)

        wrap = tk.Frame(parent, bg=self.theme.get_color('highlight'), padx=1, pady=1)
        wrap.grid(row=row, column=1, sticky="ew", pady=8)

        e = tk.Entry(wrap, font=('Segoe UI', 12),
                    bg=self.theme.get_color('card'),
                    fg=self.theme.get_color('text'),
                    insertbackground=self.theme.get_color('highlight'),
                    relief="flat", width=28)
        e.insert(0, initial)
        e.pack()
        return e

    def _create_treeview(self, parent, records, multi=False):
        """Create a treeview for displaying records."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                       background=self.theme.get_color('card'),
                       foreground=self.theme.get_color('text'),
                       fieldbackground=self.theme.get_color('card'),
                       rowheight=30)
        style.configure("Custom.Treeview.Heading",
                       background=self.theme.get_color('panel'),
                       foreground=self.theme.get_color('accent'),
                       font=('Segoe UI', 10, 'bold'))
        style.map("Custom.Treeview",
                 background=[("selected", self.theme.get_color('accent'))],
                 foreground=[("selected", '#FFFFFF')])

        cols = ("student_id", "name", "major", "course_code", "course_title", "points", "gpa")
        heads = ("Student ID", "Name", "Major", "Code", "Course Title", "Pts", "GPA")
        widths = (95, 130, 90, 68, 150, 48, 48)

        frame = tk.Frame(parent, bg=self.theme.get_color('bg'))
        frame.pack(fill="both", expand=True, padx=14, pady=10)

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                           style="Custom.Treeview", height=10,
                           selectmode="extended" if multi else "browse")

        for col, head, w in zip(cols, heads, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def refresh():
            tree.delete(*tree.get_children())
            for i, r in enumerate(records):
                tree.insert("", "end", iid=str(i),
                           values=(r["student_id"], r["name"], r["major"],
                                  r["course_code"], r["course_title"],
                                  r["points"], r["gpa"]))
        refresh()
        return tree, refresh

    def _add_buttons(self, parent, button_list):
        """Add buttons to a window."""
        btn_frame = tk.Frame(parent, bg=self.theme.get_color('bg'))
        btn_frame.pack(pady=15)

        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)
        for text, cmd in button_list:
            ui.make_button(btn_frame, text, cmd,
                          width=200, height=45).pack(side="left", padx=8)

    def student_organizations(self):
    
        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)

        p
        top = self._create_popup("Student Organizations", width=900, height=650)
        top.resizable(True, True)

        
        accent_color = "#7C3AED"  

        # ── Header ──────────────────────────────────────────────────────────────
        tk.Frame(top, bg=accent_color, height=5).pack(fill="x")
        hdr = tk.Frame(top, bg=self.theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=accent_color, height=2).pack(fill="x")

        ui.make_label(hdr, "Student Organizations", 16, bold=True,
                      color=self.theme.get_color('text')).pack(anchor="w", padx=18, pady=(12, 2))
        ui.make_label(hdr, "Manage campus clubs and organizations", 10,
                      color=self.theme.get_color('text_secondary')).pack(anchor="w", padx=18, pady=(0, 12))

        # ── Statistics Cards ──────────────────────────────────────────────────
        stats = tk.Frame(top, bg=self.theme.get_color('bg'))
        stats.pack(fill="x", padx=20, pady=(10, 15))

        cards = [
            ("Total Clubs", "5"),
            ("Total Members", "89"),
            ("Average GPA", "3.71")
        ]

        for title, value in cards:
            card = tk.Frame(stats, bg=self.theme.get_color('card'), padx=20, pady=15)
            card.pack(side="left", padx=10, fill="x", expand=True)

            tk.Label(card, text=title, font=("Segoe UI", 10),
                     fg=self.theme.get_color('text_secondary'),
                     bg=self.theme.get_color('card')).pack()
            tk.Label(card, text=value, font=("Segoe UI", 22, "bold"),
                     fg=self.theme.get_color('accent'),
                     bg=self.theme.get_color('card')).pack()

        # ── Search Bar ────────────────────────────────────────────────────────
        search_frame = tk.Frame(top, bg=self.theme.get_color('bg'))
        search_frame.pack(fill="x", padx=20)

        ui.make_label(search_frame, "Search Clubs", 11, bold=True,
                      color=self.theme.get_color('text')).pack(anchor="w")

        search = tk.Entry(search_frame, font=("Segoe UI", 11),
                          bg=self.theme.get_color('card'),
                          fg=self.theme.get_color('text'),
                          insertbackground=self.theme.get_color('highlight'),
                          relief="flat")
        search.pack(fill="x", pady=(5, 10))

        # ── Club Table ────────────────────────────────────────────────────────
        columns = ("club", "members", "gpa")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Org.Treeview",
                        background=self.theme.get_color('card'),
                        foreground=self.theme.get_color('text'),
                        fieldbackground=self.theme.get_color('card'),
                        rowheight=30)
        style.configure("Org.Treeview.Heading",
                        background=self.theme.get_color('panel'),
                        foreground=self.theme.get_color('accent'),
                        font=('Segoe UI', 10, 'bold'))
        style.map("Org.Treeview",
                  background=[("selected", self.theme.get_color('accent'))],
                  foreground=[("selected", 'white')])

        tree = ttk.Treeview(top, columns=columns, show="headings",
                            style="Org.Treeview", height=12)
        tree.heading("club", text="Club Name")
        tree.heading("members", text="Members")
        tree.heading("gpa", text="Average GPA")
        tree.column("club", width=500)
        tree.column("members", width=120, anchor="center")
        tree.column("gpa", width=150, anchor="center")

        clubs_data = [
            ("ACM Programming Club", 24, "3.74"),
            ("Cybersecurity Club", 18, "3.69"),
            ("IEEE", 20, "3.58"),
            ("Robotics Club", 15, "3.82"),
            ("Women in STEM", 12, "3.91"),
        ]

        for club in clubs_data:
            tree.insert("", "end", values=club)

        tree.pack(fill="both", expand=True, padx=20)

        # ── Search Function ──────────────────────────────────────────────────
        def filter_clubs(event=None):
            text = search.get().lower()
            tree.delete(*tree.get_children())
            for club in clubs_data:
                if text in club[0].lower():
                    tree.insert("", "end", values=club)

        search.bind("<KeyRelease>", filter_clubs)

        # ── Button Functions ─────────────────────────────────────────────────
        def selected_club():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a club.", parent=top)
                return None
            return tree.item(selected)["values"]

        def view_members():
            club = selected_club()
            if not club:
                return
            messagebox.showinfo(
                club[0],
                f"""Club Name: {club[0]}
    Members: {club[1]}
    Average GPA: {club[2]}

    Faculty Advisor: Coming Soon
    President: Coming Soon
    Vice President: Coming Soon
    Treasurer: Coming Soon""",
                parent=top
            )

        def statistics():
            messagebox.showinfo(
                "Club Statistics",
                """Total Clubs: 5
    Largest Club: ACM Programming Club
    Highest GPA: Women in STEM (3.91)
    Average Club GPA: 3.71""",
                parent=top
            )

        # ── Buttons ──────────────────────────────────────────────────────────
        btns = tk.Frame(top, bg=self.theme.get_color('bg'))
        btns.pack(fill="x", padx=20, pady=18)

        ui.make_button(btns, "👥 Members", view_members,
                       color="#7C3AED", width=140, height=45).pack(side="left", padx=5)
        ui.make_button(btns, "📊 Statistics", statistics,
                       color="#15803D", width=150, height=45).pack(side="left", padx=5)

        # ── Footer Close ─────────────────────────────────────────────────────
        # Reuse your existing footer (or a simple close button)
        footer = tk.Frame(top, bg=self.theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=self.theme.get_color('border'), height=1).pack(fill="x")
        btn_frame = tk.Frame(footer, bg=self.theme.get_color('panel'))
        btn_frame.pack(pady=8)
        ui.make_button(btn_frame, "Close", top.destroy,
                       width=120, height=35).pack()

    def tutoring(self):
        """Display the Tutoring Finder window."""
        from modules.ui import UIManager
        ui = UIManager(self.root, self.theme, None)

        # Tutoring data (moved inside the method)
        major_tutoring = {
            "Biology": [
                "Monday | 8:00 PM - 9:00 PM\n"
                "Subjects: CHEM/BSCI/MATH\n"
                "Location: Commons Center, Fireside Lounge",
                "Tuesday | 7:00 PM - 8:00 PM\n"
                "Subjects: CHEM/BSCI/PHYS\n"
                "Location: Commons Center, Fireside Lounge"
            ],
            "Chemistry": [
                "Monday | 8:00 PM - 9:00 PM\n"
                "Subjects: CHEM/BSCI/MATH\n"
                "Location: Commons Center, Fireside Lounge",
                "Tuesday | 7:00 PM - 8:00 PM\n"
                "Subjects: CHEM/BSCI/PHYS\n"
                "Location: Commons Center, Fireside Lounge",
                "CHEM 1602 Roundtable\n"
                "Monday | 7:00 PM - 8:00 PM\n"
                "Location: Commons Center, Fireside Lounge",
                "CHEM 1602 Roundtable\n"
                "Tuesday | 6:00 PM - 7:00 PM\n"
                "Location: Commons Center, Fireside Lounge"
            ],
            "Mathematics": [
                "Monday | 8:00 PM - 9:00 PM\n"
                "Subjects: CHEM/BSCI/MATH\n"
                "Location: Commons Center, Fireside Lounge"
            ],
            "Physics": [
                "Tuesday | 7:00 PM - 8:00 PM\n"
                "Subjects: CHEM/BSCI/PHYS\n"
                "Location: Commons Center, Fireside Lounge"
            ],
            "Economics": [
                "Economics tutoring is available.\n"
                "See the Tutoring Center for the current weekly schedule."
            ],
            "Neuroscience": [
                "Neuroscience tutoring is available.\n"
                "See the Tutoring Center for the current weekly schedule."
            ]
        }

        # Create popup
        top = self._create_popup("University Tutoring Finder", width=650, height=600)
        top.resizable(False, False)

        # Accent bar
        tk.Frame(top, bg="#7377FF", height=3).pack(fill="x")

        # Header
        ui.make_label(top, "University Tutoring Finder", 18, bold=True,
                      color=self.theme.get_color('accent')).pack(pady=10)
        ui.make_label(top, "Select Your Major:", 12,
                      color=self.theme.get_color('text_secondary')).pack()

        # Dropdown
        major_var = tk.StringVar(value="Chemistry")
        majors = list(major_tutoring.keys())

        # Style the OptionMenu using theme colors
        option_menu = tk.OptionMenu(top, major_var, *majors)
        option_menu.config(
            bg=self.theme.get_color('card'),
            fg=self.theme.get_color('text'),
            activebackground=self.theme.get_color('highlight'),
            activeforeground=self.theme.get_color('text'),
            relief="flat",
            font=('Segoe UI', 11)
        )
        option_menu.pack(pady=10)

        # Output text box
        output = tk.Text(
            top,
            height=18,
            width=75,
            font=('Segoe UI', 10),
            bg=self.theme.get_color('card'),
            fg=self.theme.get_color('text'),
            relief="flat",
            padx=10,
            pady=10
        )
        output.pack(padx=10, pady=10)

        def show_tutoring():
            output.delete("1.0", tk.END)
            major = major_var.get()
            if major in major_tutoring:
                output.insert(tk.END, f"=== {major} Tutoring ===\n\n")
                for session in major_tutoring[major]:
                    output.insert(tk.END, session + "\n\n")
            else:
                output.insert(tk.END, "No tutoring information available.")

        # Find Tutoring button
        btn_frame = tk.Frame(top, bg=self.theme.get_color('bg'))
        btn_frame.pack(pady=10)
        ui.make_button(btn_frame, "Find Tutoring", show_tutoring,
                       color="#7377FF", width=200, height=45).pack()

        # Footer close button
        footer = tk.Frame(top, bg=self.theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=self.theme.get_color('border'), height=1).pack(fill="x")
        btn_frame2 = tk.Frame(footer, bg=self.theme.get_color('panel'))
        btn_frame2.pack(pady=8)
        ui.make_button(btn_frame2, "Close", top.destroy,
                       width=120, height=35).pack()
