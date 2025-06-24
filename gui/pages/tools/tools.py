import os, sys
import ttkbootstrap as ttk

from gui.components import RoundedFrame
from gui.pages.tools.spypet_page import SpyPetPage
from gui.pages.tools.message_logger_page import MessageLoggerPage
from gui.pages.tools.user_lookup_page import UserLookupPage

class ToolsPage:
    def __init__(self, root, bot_controller, images, layout):
        self.root = root
        self.bot_controller = bot_controller
        self.images = images
        self.layout = layout
        
        self.spypet_page = SpyPetPage(self, root, bot_controller, images, layout)
        self.message_logger_page = MessageLoggerPage(self, root, bot_controller, images, layout)
        self.user_lookup_page = UserLookupPage(self, root, bot_controller, images, layout)
        
        self.pages = [
            {
                "name": "spy.pet",
                "page": self.spypet_page,
                "command": self.draw_spypet
            },
            {
                "name": "Message Logger",
                "page": self.message_logger_page,
                "command": self.draw_message_logger
            },
            {
                "name": "User Lookup",
                "page": self.user_lookup_page,
                "command": self.draw_user_lookup
            }
        ]
        
    def draw_spypet(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.spypet_page.draw(main)
        # 🔧 FIX: re-fetch main each time
        self.layout.sidebar.set_button_command("tools", self.draw_spypet)
        
    def draw_message_logger(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.message_logger_page.draw(main)
        # 🔧 FIX: re-fetch main each time
        self.layout.sidebar.set_button_command("tools", self.draw_message_logger)
        
    def draw_user_lookup(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.user_lookup_page.draw(main)
        # 🔧 FIX: re-fetch main each time
        self.layout.sidebar.set_button_command("tools", self.draw_user_lookup)
        
    def draw(self, parent):
        for page in self.pages:
            button = ttk.Button(
                parent,
                text=page["name"],
                command=page["command"],
                style="dark.TButton"
            )
            button.pack(side=ttk.TOP, fill=ttk.X, padx=(20, 20), pady=(0, 10))