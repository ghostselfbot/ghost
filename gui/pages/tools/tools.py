import os, sys
import ttkbootstrap as ttk

from gui.components import RoundedFrame
from gui.pages.tools.spypet_page import SpyPetPage
from gui.pages.tools.message_logger_page import MessageLoggerPage
from gui.pages.tools.user_lookup_page import UserLookupPage

class ToolsPage:
    def __init__(self, root, bot_controller, images, layout, position_resize_grips):
        self.root = root
        self.bot_controller = bot_controller
        self.images = images
        self.layout = layout
        self.position_resize_grips = position_resize_grips
        self.hover_colour = "#282a2a"
        
        self.spypet_page = SpyPetPage(self, root, bot_controller, images, layout)
        self.message_logger_page = MessageLoggerPage(self, root, bot_controller, images, layout)
        self.user_lookup_page = UserLookupPage(self, root, bot_controller, images, layout)
        
        self.pages = [
            {
                "name": "ghetto spy.pet",
                "description": "A tool to look up every message sent by a user you share mutual servers with.",
                "page": self.spypet_page,
                "command": self.draw_spypet
            },
            {
                "name": "Message Logger",
                "description": "A tool to log deleted messages from every server you're in.",
                "page": self.message_logger_page,
                "command": self.draw_message_logger
            },
            {
                "name": "User Lookup",
                "description": "A tool to look up a user's information.",
                "page": self.user_lookup_page,
                "command": self.draw_user_lookup
            }
        ]
        
    def draw_spypet(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.spypet_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_spypet)
        self.position_resize_grips()
        
    def draw_message_logger(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.message_logger_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_message_logger)
        self.position_resize_grips()
        
    def draw_user_lookup(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.user_lookup_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_user_lookup)
        self.position_resize_grips()
        
    def _bind_hover_effects(self, widget, targets, hover_bg, normal_bg):
        def on_enter(_):
            for target in targets:
                if isinstance(target, RoundedFrame):
                    target.set_background(background=hover_bg)
                else:
                    target.configure(background=hover_bg)

        def on_leave(_):
            for target in targets:
                if isinstance(target, RoundedFrame):
                    target.set_background(background=normal_bg)
                else:
                    target.configure(background=normal_bg)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def draw(self, parent):
        for page in self.pages:
            page_wrapper = RoundedFrame(parent, radius=15, bootstyle="secondary.TFrame")
            page_wrapper.pack(fill="x", expand=True, pady=(0, 10))
            page_wrapper.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())

            page_title = ttk.Label(page_wrapper, text=page["name"], font=("Host Grotesk", 14 if sys.platform != "darwin" else 18, "bold"))
            page_title.configure(background=self.root.style.colors.get("secondary"))
            page_title.grid(row=0, column=0, sticky=ttk.NSEW, padx=15, pady=10)
            page_title.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())

            # page_description = ttk.Label(page_wrapper, text=page["description"], font=("Host Grotesk", 12 if sys.platform != "darwin" else 16), wraplength=450)
            # page_description.configure(background=self.root.style.colors.get("secondary"))
            # page_description.grid(row=1, column=0, sticky=ttk.NSEW, padx=15, pady=(0, 15))
            # page_description.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())
            
            page_icon = ttk.Label(page_wrapper, image=self.images.get("right-chevron"))
            page_icon.configure(background=self.root.style.colors.get("secondary"))
            page_icon.grid(row=0, column=1, sticky=ttk.E, padx=(0, 20), pady=15)
            
            page_wrapper.grid_columnconfigure(1, weight=1)
            self._bind_hover_effects(page_wrapper, [page_title, page_wrapper, page_icon], self.hover_colour, self.root.style.colors.get("secondary"))
            self._bind_hover_effects(page_title, [page_title, page_wrapper, page_icon], self.hover_colour, self.root.style.colors.get("secondary"))
            self._bind_hover_effects(page_icon, [page_title, page_wrapper, page_icon], self.hover_colour, self.root.style.colors.get("secondary"))