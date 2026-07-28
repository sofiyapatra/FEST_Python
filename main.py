# main.py - Entry point with mode switching
import tkinter as tk
from tkinter import messagebox, ttk
import os
from modules.auth import AuthManager
from modules.data import DataManager
from modules.ui import UIManager, ThemeManager
from modules.visualizations import VisualizationManager
from modules.queries import QueryManager


class FESTApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FEST Summer 2026")

        # Initialize managers
        self.theme = ThemeManager()
        self.auth = AuthManager()
        self.data = DataManager()
        self.ui = UIManager(self.root, self.theme, self.auth)
        self.viz = VisualizationManager(self.theme)
        self.queries = QueryManager()

        # Set up window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.resizable(True, True)

        # Apply theme
        self.theme.apply_theme(self.root)

        # Show welcome screen
        self.ui.show_welcome()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FESTApp()
    app.run()