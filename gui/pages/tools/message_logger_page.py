import ttkbootstrap as ttk
from gui.components import RoundedFrame, ToolPage

class MessageLoggerPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Message Logger")

    def draw_content(self, wrapper):
        title = ttk.Label(wrapper, text=self.title, font=("Host Grotesk", 16, "bold"))
        title.pack(side=ttk.TOP, anchor=ttk.W, padx=(20, 0), pady=(20, 0))

        # Any additional widgets go here