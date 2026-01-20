import sys
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

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
        
    def main(self, scrollable=False, padx=25, pady=25):
        width = self.width - (self.width // 100)
        wrapper = self.root
        
        if scrollable:
            wrapper = ScrolledFrame(self.root, width=width, height=self.height)
            wrapper.pack(fill=ttk.BOTH, expand=True)
            
            # main = ttk.Frame(wrapper)
            # main.pack(fill=ttk.BOTH, expand=True, padx=23, pady=23)

        main = ttk.Frame(wrapper, width=width, height=self.height)
        main.pack(fill=ttk.BOTH, expand=True, padx=(23, 32) if scrollable else padx, pady=23 if scrollable else pady)

        return main
    
    def clear_everything(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
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