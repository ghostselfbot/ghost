import abc
import sys
import ttkbootstrap as ttk
from gui.components import RoundedFrame

class ToolPage:
    def __init__(self, toolspage, root, bot_controller, images, layout, title, frame=True):
        self.toolspage = toolspage
        self.root = root
        self.bot_controller = bot_controller
        self.images = images
        self.layout = layout
        self.title = title
        self.frame = frame

    def go_back(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main(scrollable=True)
        self.toolspage.draw(main)
        self.layout.sidebar.set_button_command("tools", self.go_back)

    def draw_navigation(self, parent):
        wrapper = ttk.Frame(parent)

        back_button = ttk.Label(wrapper, image=self.images.get("left-chevron"))
        back_button.bind("<Button-1>", lambda e: self.go_back())
        back_button.grid(row=0, column=1, sticky=ttk.W, padx=(0, 10))

        page_name = ttk.Label(wrapper, text=self.title, font=("Host Grotesk", 14 if sys.platform != "darwin" else 16, "bold"))
        page_name.grid(row=0, column=2, sticky=ttk.W)

        return wrapper

    def draw(self, parent):
        # Draw shared navigation
        navigation = self.draw_navigation(parent)
        navigation.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 10))

        # Create shared content wrapper
        if self.frame:
            wrapper = RoundedFrame(parent, radius=10, style="dark.TFrame")
        else:
            wrapper = ttk.Frame(parent)
        wrapper.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True, pady=(10, 0))

        # Call subclass-specific content render
        self.draw_content(wrapper)

    @abc.abstractmethod
    def draw_content(self, wrapper):
        """Implemented by subclasses to draw page-specific content inside the wrapper."""
        pass
