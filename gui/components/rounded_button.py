import sys
import ttkbootstrap as ttk
from gui.components import RoundedFrame

class RoundedButton(ttk.Canvas):
    def __init__(self, parent, radius=(8, 8, 8, 8), text=None, image=None, command=None, **kwargs):
        canvas_kwargs = {}
        for key in kwargs:
            if key not in ["padx", "pady", "bootstyle", "style"]:
                canvas_kwargs[key] = kwargs[key]
        super().__init__(parent, highlightthickness=0, bd=0, **canvas_kwargs)
        
        bootstyle = kwargs.get("bootstyle") or kwargs.get("style") or "primary.TButton"
        self.parent = parent
        self.radius = radius if not isinstance(radius, int) else (radius, radius, radius, radius)
        self.root = parent.winfo_toplevel()
        self.style = self.root.style
        self.padx = kwargs.get("padx", 2)
        self.pady = kwargs.get("pady", 0 if sys.platform != "darwin" else 1)

        self.configure(background=self._get_parent_background())

        # Store the original background color
        self.original_bg = self.style.colors.get(bootstyle.split(".")[0]) if kwargs.get("background") is None else kwargs.get("background")

        # Create the rounded frame
        self.frame = RoundedFrame(self, radius=radius, bootstyle=bootstyle, background=self.original_bg)
        self.frame.pack(fill=ttk.BOTH)

        # Create the label inside the rounded frame
        self.button = ttk.Label(self.frame, text=text, image=image, style=bootstyle, anchor="center", borderwidth=0, relief="flat", font=("Host Grotesk", "10") if sys.platform != "darwin" else ("Host Grotesk", ) if not kwargs.get("font") else kwargs.get("font"))
        self.button.pack(fill=ttk.BOTH, expand=True, padx=self.padx, pady=self.pady)

        # Bind events for clicking
        if command:
            self.button.bind("<Button-1>", command)
            self.frame.bind("<Button-1>", command)

        # Bind events for hover effects
        self.frame.bind("<Enter>", self._hover_enter)
        self.frame.bind("<Leave>", self._hover_leave)
        self.button.bind("<Enter>", self._hover_enter)
        self.button.bind("<Leave>", self._hover_leave)

    def _get_parent_background(self):
        parent = self.parent
        if isinstance(parent, ttk.Frame):
            style = parent.cget("style")
            return self.style.lookup(style, "background")
        elif isinstance(parent, RoundedFrame):
            return parent.frame_background
        else:
            try:
                return parent.cget("background")
            except:
                return self.style.colors.get("dark")

    def _darken_color(self, hex_color, factor=0.9):
        """Darken color for hover effect without progressive darkening"""
        if not hex_color.startswith("#"):
            return hex_color  # Ensure it's a valid hex color

        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))  # Extract RGB values
        darkened_rgb = tuple(max(0, int(value * factor)) for value in rgb)  # Apply factor safely
        return f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"

    def _hover_enter(self, event=None):
        """ Apply hover effect """
        hover_color = self._darken_color(self.original_bg, 0.9)
        self.frame.set_background(hover_color)
        self.button.configure(background=hover_color)

    def _hover_leave(self, event=None):
        """ Reset to original color """
        self.frame.set_background(self.original_bg)
        self.button.configure(background=self.original_bg)