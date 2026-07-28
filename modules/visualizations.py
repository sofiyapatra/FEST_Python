"""
Visualization management for FEST application.
Handles all matplotlib-based visualizations.
"""

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class VisualizationManager:
    """Manages all data visualizations."""

    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.has_seaborn = True
        try:
            import seaborn as sns
        except ImportError:
            self.has_seaborn = False

    def create_swarm_plot(self, root, theme):
        """Create a swarm plot of student scores."""
        from modules.data import DataManager
        data = DataManager()
        records = data.load_students()

        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        try:
            pts = [float(r["points"]) for r in records]
        except ValueError:
            messagebox.showerror("Data Error", "Invalid points values.")
            return

        # Create plot
        fig, ax = plt.subplots(figsize=(9.2, 5.4))
        fig.patch.set_facecolor(theme.get_color('bg'))
        ax.set_facecolor(theme.get_color('card'))

        # Style spines
        for spine in ax.spines.values():
            spine.set_color(theme.get_color('border'))

        # Set colors
        ax.tick_params(colors=theme.get_color('text_secondary'))
        ax.set_title("Student Score Distribution",
                    color=theme.get_color('text'),
                    fontsize=13, fontweight="bold", pad=12, family="Georgia")
        ax.set_xlabel("Course Code", color=theme.get_color('text_secondary'), fontsize=11)
        ax.set_ylabel("Points (out of 100)", color=theme.get_color('text_secondary'), fontsize=11)

        if self.has_seaborn:
            codes = [r["course_code"] for r in records]
            cats = [data.grade_category(p) for p in pts]
            df = pd.DataFrame({"Points": pts, "Course": codes, "Grade": cats})

            grade_palette = {
                "A (90-100)": theme.get_color('accent'),
                "B (80-89)": "#B8860B",
                "C (70-79)": "#8B6F35",
                "D (60-69)": "#7C2D12",
                "F (0-59)": "#6E1E22",
            }

            sns.swarmplot(data=df, x="Course", y="Points", hue="Grade",
                         palette=grade_palette, ax=ax, size=9,
                         linewidth=0.5, edgecolor=theme.get_color('bg'))

            leg = ax.get_legend()
            if leg:
                leg.get_frame().set_facecolor(theme.get_color('panel'))
                leg.get_frame().set_edgecolor(theme.get_color('border'))
                leg.set_title("Grade", prop={"size": 9})
                leg.get_title().set_color(theme.get_color('text_secondary'))
                for t in leg.get_texts():
                    t.set_color(theme.get_color('text'))

        self._show_plot(fig, "Swarm Plot", root)

    def create_countplot(self, root, theme):
        """Create a count plot of students per major."""
        from modules.data import DataManager
        data = DataManager()
        records = data.load_students()

        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        major_counts = {}
        for r in records:
            major = r["major"].strip()
            major_counts[major] = major_counts.get(major, 0) + 1

        majors = list(major_counts.keys())
        counts = [major_counts[m] for m in majors]

        fig, ax = plt.subplots(figsize=(9.2, 5.4))
        fig.patch.set_facecolor(theme.get_color('bg'))
        ax.set_facecolor(theme.get_color('card'))

        for spine in ax.spines.values():
            spine.set_color(theme.get_color('border'))

        ax.tick_params(colors=theme.get_color('text_secondary'))
        ax.set_title("Number of Students per Major",
                    color=theme.get_color('text'),
                    fontsize=13, fontweight="bold", pad=12, family="Georgia")
        ax.set_xlabel("Major", color=theme.get_color('text_secondary'), fontsize=11)
        ax.set_ylabel("Number of Students", color=theme.get_color('text_secondary'), fontsize=11)

        if self.has_seaborn:
            df = pd.DataFrame({"Major": majors, "Count": counts})
            df = df.sort_values("Count", ascending=False)
            sns.barplot(data=df, x="Major", y="Count", hue="Major",
                       palette="copper", ax=ax, legend=False,
                       edgecolor=theme.get_color('bg'), linewidth=0.8)
            for bar, count in zip(ax.patches, df["Count"]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       str(count), ha="center", va="bottom",
                       color=theme.get_color('text'), fontsize=11, fontweight="bold")
        else:
            gold_sequence = [theme.get_color('accent'), "#B8860B", "#8B6F35", "#7C2D12"]
            bars = ax.bar(majors, counts,
                         color=[gold_sequence[i % len(gold_sequence)]
                               for i in range(len(majors))],
                         edgecolor=theme.get_color('bg'), linewidth=0.8)
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       str(count), ha="center", va="bottom",
                       color=theme.get_color('text'), fontsize=11, fontweight="bold")

        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_ylim(0, max(counts) + 1.5)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout(pad=1.5)

        self._show_plot(fig, "Major Count Plot", root)

    def create_piechart(self, root, theme):
        """Create a pie chart of grade distribution."""
        from modules.data import DataManager
        data = DataManager()
        records = data.load_students()

        if not records:
            messagebox.showwarning("No Data", "No student records found.")
            return

        grade_counts = {}
        for r in records:
            try:
                letter, _ = data.points_to_grade(float(r["points"]))
                key = letter[0]
            except (ValueError, TypeError):
                key = "F"
            grade_counts[key] = grade_counts.get(key, 0) + 1

        ordered_keys = [k for k in ["A", "B", "C", "D", "F"] if k in grade_counts]
        labels = [f"Grade {k}" for k in ordered_keys]
        sizes = [grade_counts[k] for k in ordered_keys]
        colors = {
            "A": theme.get_color('accent'),
            "B": "#B8860B",
            "C": "#8B6F35",
            "D": "#7C2D12",
            "F": "#6E1E22",
        }
        pie_colors = [colors[k] for k in ordered_keys]

        explode_idx = sizes.index(max(sizes))
        explode = [0.08 if i == explode_idx else 0 for i in range(len(sizes))]

        fig, ax = plt.subplots(figsize=(9.8, 7.0))
        fig.patch.set_facecolor(theme.get_color('bg'))
        ax.set_facecolor(theme.get_color('bg'))

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, labels=None,
            autopct=lambda pct: f"{pct:.1f}%\n({round(pct * sum(sizes) / 100)})",
            colors=pie_colors, explode=explode,
            startangle=140, shadow=True,
            wedgeprops={"edgecolor": theme.get_color('bg'), "linewidth": 2},
            pctdistance=0.72, textprops={"fontsize": 11}
        )

        for at in autotexts:
            at.set_color(theme.get_color('text'))
            at.set_fontweight("bold")

        legend_labels = [f"Grade {k}  ({grade_counts[k]} student{'s' if grade_counts[k] != 1 else ''})"
                        for k in ordered_keys]
        leg = ax.legend(wedges, legend_labels, loc="center left",
                       bbox_to_anchor=(1.02, 0.5), frameon=True,
                       facecolor=theme.get_color('panel'),
                       edgecolor=theme.get_color('border'), fontsize=11)
        for text in leg.get_texts():
            text.set_color(theme.get_color('text'))

        ax.set_title(f"Letter Grade Distribution  (n = {sum(sizes)} students)",
                    color=theme.get_color('text'),
                    fontsize=13, fontweight="bold", pad=18, family="Georgia")

        plt.tight_layout()
        self._show_plot(fig, "Grade Distribution", root)

    def _show_plot(self, fig, title, root):
        """Display a plot in a new window."""
        top = tk.Toplevel()
        top.title(f"FEST — {title}")
        top.geometry("960x660")
        top.configure(bg=self.theme.get_color('bg'))
        top.resizable(True, True)

        # Accent bar
        tk.Frame(top, bg=self.theme.get_color('accent'), height=5).pack(fill="x")

        # Toolbar
        toolbar_frame = tk.Frame(top, bg=self.theme.get_color('panel'))
        toolbar_frame.pack(fill="x", side="bottom")

        def on_close():
            plt.close(fig)
            top.destroy()

        # Close button
        btn_frame = tk.Frame(toolbar_frame, bg=self.theme.get_color('panel'))
        btn_frame.pack(side="right", padx=10, pady=5)

        from modules.ui import UIManager
        ui = UIManager(root, self.theme, None)
        ui.make_button(btn_frame, "Close", on_close,
                      width=120, height=35).pack()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=top)
        NavigationToolbar2Tk(canvas, toolbar_frame).update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

        top.protocol("WM_DELETE_WINDOW", on_close)