"""
Query management for FEST application.
Handles academic queries and Dean's List functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd


class QueryManager:
    """Manages academic queries and reports."""

    def __init__(self):
        self.deans_threshold = 3.5

    def show_queries(self, root, theme, data_manager):
        """Display the queries interface."""
        records = data_manager.load_students()
        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        student_dict = {}
        for r in records:
            student_dict.setdefault(r["student_id"], []).append(r)

        def grade_letter(r):
            try:
                letter, _ = data_manager.points_to_grade(float(r["points"]))
                return letter
            except (ValueError, TypeError):
                return None

        def distinct_students(pred):
            return len({r["student_id"] for r in records if pred(r)})

        def avg_points(pred):
            vals = [float(r["points"]) for r in records if pred(r)]
            return sum(vals) / len(vals) if vals else None

        def avg_gpa(pred):
            vals = [float(r["gpa"]) for r in records if pred(r)]
            return sum(vals) / len(vals) if vals else None

        def plural(n, word="student"):
            return f"{n} {word}{'s' if n != 1 else ''}"

        # Queries
        queries = [
            ("How many Computer Science students earned an A+?",
             plural(distinct_students(lambda r: r["major"] == "Computer Science" and grade_letter(r) == "A+"))),
            ("How many Mechanical Engineering students took a programming course?",
             plural(distinct_students(
                 lambda r: r["major"] == "Mechanical Engineering" and "program" in r["course_title"].lower()))),
            ("How many students took a programming class?",
             plural(distinct_students(lambda r: "program" in r["course_title"].lower()))),
            ("Average GPA of Computer Science majors?",
             f"{avg_gpa(lambda r: r['major'] == 'Computer Science'):.2f} GPA" if avg_gpa(
                 lambda r: r['major'] == 'Computer Science') else "No data"),
            ("Which major has the highest average GPA?",
             self._get_top_major(records)),
            ("How many students failed Circuit Analysis?",
             plural(distinct_students(lambda r: r["course_title"] == "Circuit Analysis" and grade_letter(r) == "F"))),
            ("Total unique students enrolled?",
             plural(len(student_dict))),
            ("Average score in Calculus I?",
             f"{avg_points(lambda r: r['course_title'] == 'Calculus I'):.1f} / 100" if avg_points(
                 lambda r: r['course_title'] == 'Calculus I') else "No data"),
            ("Students scoring 90+ in Introduction to Business?",
             plural(distinct_students(
                 lambda r: r["course_title"] == "Introduction to Business" and float(r["points"]) >= 90))),
            ("Course with lowest average score?",
             self._get_lowest_course(records)),
        ]

        self._display_queries(root, theme, queries)

    def show_deans_list(self, root, theme, data_manager):
        """Display the Dean's List."""
        records = data_manager.load_students()
        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        student_dict = {}
        for r in records:
            student_dict.setdefault(r["student_id"], []).append(r)

        honorees = []
        for sid, recs in student_dict.items():
            try:
                gpas = [float(r["gpa"]) for r in recs]
            except (ValueError, TypeError):
                continue
            if not gpas:
                continue
            avg = sum(gpas) / len(gpas)
            if avg >= self.deans_threshold:
                first = recs[0]
                honorees.append({
                    "student_id": sid, "name": first["name"],
                    "major": first["major"], "gpa": avg,
                    "courses": len(recs),
                })
        honorees.sort(key=lambda h: h["gpa"], reverse=True)

        self._display_deans_list(root, theme, honorees)

    def _get_top_major(self, records):
        """Find major with highest average GPA."""
        majors = sorted({r["major"] for r in records})
        major_gpa = {}
        for m in majors:
            vals = [float(r["gpa"]) for r in records if r["major"] == m]
            if vals:
                major_gpa[m] = sum(vals) / len(vals)
        if major_gpa:
            top = max(major_gpa, key=major_gpa.get)
            return f"{top}  ({major_gpa[top]:.2f} avg GPA)"
        return "No data"

    def _get_lowest_course(self, records):
        """Find course with lowest average score."""
        titles = sorted({r["course_title"] for r in records})
        title_pts = {}
        for t in titles:
            vals = [float(r["points"]) for r in records if r["course_title"] == t]
            if vals:
                title_pts[t] = sum(vals) / len(vals)
        if title_pts:
            low = min(title_pts, key=title_pts.get)
            return f"{low}  ({title_pts[low]:.1f} avg pts)"
        return "No data"

    def _display_queries(self, root, theme, queries):
        """Display queries in a scrollable window."""
        top = tk.Toplevel(root)
        top.title("FEST — Academic Insights")
        top.geometry("820x700")
        top.configure(bg=theme.get_color('bg'))
        top.resizable(True, True)

        # Header
        tk.Frame(top, bg=theme.get_color('accent'), height=5).pack(fill="x")
        hdr = tk.Frame(top, bg=theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=theme.get_color('accent'), height=2).pack(fill="x")

        from modules.ui import UIManager
        ui = UIManager(root, theme, None)
        ui.make_label(hdr, "Academic Insights", 16, bold=True,
                      color=theme.get_color('accent')).pack(anchor="w", padx=18, pady=10)

        # Scrollable content
        container = tk.Frame(top, bg=theme.get_color('bg'))
        container.pack(fill="both", expand=True, padx=16, pady=10)

        canvas = tk.Canvas(container, bg=theme.get_color('bg'), highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=theme.get_color('bg'))

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Display each query
        for i, (question, answer) in enumerate(queries, 1):
            card = tk.Frame(scroll_frame, bg=theme.get_color('card'))
            card.pack(fill="x", pady=5)

            accent = tk.Frame(card, bg=theme.get_color('accent'), width=4)
            accent.pack(side="left", fill="y")

            body = tk.Frame(card, bg=theme.get_color('card'), padx=14, pady=10)
            body.pack(side="left", fill="both", expand=True)

            ui.make_label(body, f"Q{i}. {question}", 11, bold=True,
                          wraplength=680, justify="left").pack(anchor="w")
            tk.Label(body, text=f"→ {answer}", font=('Segoe UI', 12, 'bold'),
                     fg=theme.get_color('accent'), bg=theme.get_color('card'),
                     wraplength=680, justify="left").pack(anchor="w", pady=(4, 0))

        # Footer
        footer = tk.Frame(top, bg=theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=theme.get_color('border'), height=1).pack(fill="x")

        btn_frame = tk.Frame(footer, bg=theme.get_color('panel'))
        btn_frame.pack(pady=8)
        ui.make_button(btn_frame, "Close", top.destroy,
                       width=120, height=35).pack()

    def _display_deans_list(self, root, theme, honorees):
        """Display the Dean's List."""
        top = tk.Toplevel(root)
        top.title("FEST — Dean's List")
        top.geometry("820x720")
        top.configure(bg=theme.get_color('bg'))
        top.resizable(True, True)

        # Header
        tk.Frame(top, bg=theme.get_color('accent'), height=5).pack(fill="x")
        hdr = tk.Frame(top, bg=theme.get_color('panel'))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=theme.get_color('accent'), height=2).pack(fill="x")

        from modules.ui import UIManager
        ui = UIManager(root, theme, None)

        ui.make_label(hdr, "Dean's List", 22, bold=True,
                      color=theme.get_color('accent')).pack(pady=(14, 2))
        ui.make_ornamental_divider(hdr, width=300)
        ui.make_label(hdr, "Vanderbilt University · Summer 2026 Honor Roll",
                      11, color=theme.get_color('text_secondary')).pack(pady=(2, 4))
        ui.make_label(hdr,
                      f"Students with {self.deans_threshold:.1f}+ GPA · {len(honorees)} honorees",
                      10, color=theme.get_color('text_secondary')).pack(pady=(0, 14))

        # Scrollable content
        container = tk.Frame(top, bg=theme.get_color('bg'))
        container.pack(fill="both", expand=True, padx=18, pady=10)

        canvas = tk.Canvas(container, bg=theme.get_color('bg'), highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=theme.get_color('bg'))

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        MEDALS = {0: ("🥇", theme.get_color('accent')),
                  1: ("🥈", "#C9C4B8"),
                  2: ("🥉", "#C08552")}

        if not honorees:
            ui.make_label(scroll_frame, "No students currently meet the Dean's List threshold.",
                          12, color=theme.get_color('text_secondary')).pack(pady=40)
        else:
            for i, h in enumerate(honorees):
                medal, medal_color = MEDALS.get(i, ("", theme.get_color('accent')))

                row_outer = tk.Frame(scroll_frame,
                                     bg=theme.get_color('accent') if i < 3 else theme.get_color('border'),
                                     padx=1, pady=1)
                row_outer.pack(fill="x", pady=6)

                row = tk.Frame(row_outer, bg=theme.get_color('card'), padx=16, pady=12)
                row.pack(fill="x")

                left = tk.Frame(row, bg=theme.get_color('card'), width=54)
                left.pack(side="left")
                left.pack_propagate(False)
                tk.Label(left, text=medal or f"#{i + 1}",
                         font=('Segoe UI', 18 if medal else 13, 'bold'),
                         fg=medal_color, bg=theme.get_color('card')).pack()

                mid = tk.Frame(row, bg=theme.get_color('card'))
                mid.pack(side="left", fill="x", expand=True, padx=10)
                tk.Label(mid, text=h["name"], font=('Georgia', 14, 'bold'),
                         fg=theme.get_color('text'), bg=theme.get_color('card'),
                         anchor="w").pack(anchor="w")
                tk.Label(mid, text=f"{h['major']} · ID: {h['student_id']} · {h['courses']} courses",
                         font=('Segoe UI', 9),
                         fg=theme.get_color('text_secondary'),
                         bg=theme.get_color('card'), anchor="w").pack(anchor="w")

                right = tk.Frame(row, bg=theme.get_color('card'))
                right.pack(side="right")
                tk.Label(right, text=f"{h['gpa']:.2f}", font=('Georgia', 18, 'bold'),
                         fg=theme.get_color('accent'), bg=theme.get_color('card')).pack()
                tk.Label(right, text="AVG GPA", font=('Segoe UI', 8, 'bold'),
                         fg=theme.get_color('text_secondary'),
                         bg=theme.get_color('card')).pack()

        # Footer
        footer = tk.Frame(top, bg=theme.get_color('panel'))
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=theme.get_color('border'), height=1).pack(fill="x")

        btn_frame = tk.Frame(footer, bg=theme.get_color('panel'))
        btn_frame.pack(pady=8)
        ui.make_button(btn_frame, "Close", top.destroy,
                       width=120, height=35).pack()