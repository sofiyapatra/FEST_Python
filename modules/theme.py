"""
Theme management for FEST application.
Handles dark/light mode switching with refined color palettes.
"""


class ThemeManager:
    """Manages application theming with dark/light mode support."""

    def __init__(self):
        self.is_dark = True  # Default to dark mode

        # Dark Mode Palette - Sophisticated dark academic theme
        self.dark = {
            'bg': '#1A1A1A',  # Deep charcoal background
            'panel': '#2A2A2A',  # Slightly lighter for panels
            'card': '#333333',  # Card background
            'surface': '#3D3D3D',  # Surface elements
            'text': '#E8E0D8',  # Warm cream text
            'text_secondary': '#B8B0A8',  # Muted text
            'accent': '#C49B5A',  # Warm gold accent
            'accent_light': '#D4B87A',  # Lighter gold
            'accent_dark': '#A8843E',  # Darker gold
            'border': '#4A4A4A',  # Borders
            'success': '#6B8F5E',  # Muted green
            'error': '#8C3A2E',  # Muted red
            # 'highlight': '#C49B5A',  # Focus/highlight
        }

        # Light Mode Palette - Warm cream academic theme
        self.light = {
            'bg': '#F5F0E8',  # Cream background
            'panel': '#EBE5DB',  # Slightly darker cream
            'card': '#E0D8CC',  # Card background
            'surface': '#D5CCC0',  # Surface elements
            'text': '#2A241E',  # Dark brown text
            'text_secondary': '#6B6358',  # Muted brown
            'accent': '#8B6F35',  # Rich bronze
            'accent_light': '#A8843E',  # Lighter bronze
            'accent_dark': '#6B5530',  # Darker bronze
            'border': '#C8BFA8',  # Borders
            'success': '#5C7A4A',  # Muted green
            'error': '#8C3A2E',  # Muted red
            # 'highlight': '#8B6F35',  # Focus/highlight
        }

        self.current_palette = self.dark

        # Font configuration
        self.fonts = {
            'heading': ('Georgia', 18, 'bold'),
            'subheading': ('Georgia', 14, 'bold'),
            'body': ('Segoe UI', 11, 'normal'),
            'body_bold': ('Segoe UI', 11, 'bold'),
            'small': ('Segoe UI', 9, 'normal'),
            'mono': ('Courier New', 11, 'normal'),
        }

    def toggle_mode(self):
        """Switch between dark and light mode."""
        self.is_dark = not self.is_dark
        self.current_palette = self.dark if self.is_dark else self.light
        return self.current_palette

    def get_color(self, key):
        """Get a color from the current palette."""
        return self.current_palette.get(key, '#000000')

    def apply_theme(self, widget):
        """Apply current theme to a widget and all of its children."""
        bg = self.get_color("bg")

        widgets = [widget]

        while widgets:
            current = widgets.pop()

            try:
                current.configure(bg=bg)
            except:
                pass

            widgets.extend(current.winfo_children())

    def create_styled_widget(self, parent, widget_type, **kwargs):
        """Create a widget with current theme styling."""
        # Apply background to parent if not specified
        if 'bg' not in kwargs:
            kwargs['bg'] = self.get_color('bg')

        # Create the widget
        widget = widget_type(parent, **kwargs)

        # Apply theme to child
        self.apply_theme(widget)
        return widget