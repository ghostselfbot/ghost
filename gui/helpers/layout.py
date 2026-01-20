import sys
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from gui.components import RoundedFrame

def resize(root, width, height):
    root.minsize(width, height)
    root.geometry(f"{width}x{height}")
    # self.root.resizable(False, False)
    
def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")
    root.focus_force()

class Layout:
    def __init__(self, root, sidebar, titlebar):
        self.root = root
        self.width = root.winfo_width()
        self.height = root.winfo_height()
        self.sidebar = sidebar
        self.titlebar = titlebar
        self.border_color = "#171616"
        
    def main(self, scrollable=False, padx=10, pady=10):
        width = self.width - (self.width // 100)

        border = RoundedFrame(
            self.root,
            radius=(0, 0, 25, 0),  # ALL corners here
            background=self.border_color
        )
        border.pack(fill=ttk.BOTH, expand=True)

        outer = RoundedFrame(
            border,
            radius=(25, 25, 25, 25),  # only internal shaping
            background=self.root.style.colors.get("bg")
        )
        outer.pack(
            fill=ttk.BOTH,
            expand=True,
            padx=(0, 8),
            pady=(0, 8)
        )

        # SAFE ZONE: keeps native widgets away from rounded corners
        safe = ttk.Frame(
            outer,
            style="TFrame"
        )
        safe.pack(fill=ttk.BOTH, expand=True, padx=15, pady=15)

        # INNER: scrolling container (optional)
        if scrollable:
            inner = ScrolledFrame(
                safe,
                width=width,
                height=self.height
            )
            inner.pack(fill=ttk.BOTH, expand=True)
            content_parent = inner
        else:
            content_parent = safe

        # CONTENT FRAME
        main = ttk.Frame(
            content_parent,
            width=width,
            height=self.height
        )
        main.pack(
            fill=ttk.BOTH,
            expand=True,
            padx=(8, 22) if scrollable else padx,
            pady=8 if scrollable else pady
        )

        return main

    
    def clear_everything(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) or isinstance(widget, ScrolledFrame) or isinstance(widget, ttk.Canvas) or isinstance(widget, RoundedFrame):
                widget.destroy()

        titlebar = self.titlebar.draw()
        titlebar.pack(fill=ttk.X, side=ttk.TOP)

        sidebar = self.sidebar.draw()
        sidebar.pack(side=ttk.LEFT, fill=ttk.BOTH)
        
    hide_titlebar  = lambda self: self.root.overrideredirect(True) if sys.platform != "linux" else None
    show_titlebar  = lambda self: self.root.overrideredirect(False) if sys.platform != "linux" else None
    stick_window   = lambda self: self.root.attributes("-topmost", True)
    unstick_window = lambda self: self.root.attributes("-topmost", False)
        
    def resize(self, width=None, height=None):
        if height is not None:
            self.height = height
        if width is not None:
            self.width = width

        resize(self.root, self.width, self.height)
        
    def center_window(self, width=None, height=None):
        if height is not None:
            self.height = height
        if width is not None:
            self.width = width

        center_window(self.root, self.width, self.height)