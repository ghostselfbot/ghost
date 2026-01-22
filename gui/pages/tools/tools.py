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
                "description": "Get messages sent by a user in mutual guilds",
                "page": self.spypet_page,
                "command": self.draw_spypet
            },
            {
                "name": "Message Logger",
                "description": "Logs every deleted message sent",
                "page": self.message_logger_page,
                "command": self.draw_message_logger
            },
            {
                "name": "User Lookup",
                "description": "Look up information about a user by their ID",
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
        
    def _draw_page_card(self, parent, page):
        page_wrapper = RoundedFrame(parent, radius=15, bootstyle="secondary.TFrame")
        page_wrapper.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())

        page_title = ttk.Label(page_wrapper, text=page["name"], font=("Host Grotesk", 14 if sys.platform != "darwin" else 18, "bold"), justify=ttk.CENTER)
        page_title.configure(background=self.root.style.colors.get("secondary"))
        page_title.grid(row=0, column=0, pady=(25, 5))
        page_title.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())

        page_description = ttk.Label(page_wrapper, text=page["description"], wraplength=150, justify=ttk.CENTER)
        page_description.configure(background=self.root.style.colors.get("secondary"))
        page_description.grid(row=1, column=0, pady=(0, 25))
        page_description.bind("<Button-1>", lambda e, cmd=page["command"]: cmd())
        
        # page_icon = ttk.Label(page_wrapper, image=self.images.get("right-chevron"))
        # page_icon.configure(background=self.root.style.colors.get("secondary"))
        # page_icon.grid(row=0, column=1, sticky=ttk.E, padx=(0, 20), pady=15)
        
        page_wrapper.grid_columnconfigure(0, weight=1)
        page_wrapper.grid_rowconfigure(0, weight=1)
        page_wrapper.grid_rowconfigure(1, weight=1)
        self._bind_hover_effects(page_wrapper, [page_title, page_wrapper, page_description], self.hover_colour, self.root.style.colors.get("secondary"))
        self._bind_hover_effects(page_title, [page_title, page_wrapper, page_description], self.hover_colour, self.root.style.colors.get("secondary"))
        self._bind_hover_effects(page_description, [page_title, page_wrapper, page_description], self.hover_colour, self.root.style.colors.get("secondary"))
        # self._bind_hover_effects(page_icon, [page_title, page_wrapper, page_icon], self.hover_colour, self.root.style.colors.get("secondary"))
        
        return page_wrapper
        
    def draw(self, parent):
        title = ttk.Label(parent, text="Tools", font=("Host Grotesk", 20 if sys.platform != "darwin" else 24, "bold"))
        title.configure(background=self.root.style.colors.get("bg"))
        # title.pack(pady=(0, 15), anchor=ttk.W)
        title.grid(row=0, column=0, sticky=ttk.W, pady=(0, 15))
        
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        # create a grid for the page cards, two columns
        row, col = 1, 0
        for page in self.pages:
            card = self._draw_page_card(parent, page)
            card.grid(row=row, column=col, sticky=ttk.NSEW, padx=5, pady=5)
            col += 1
            if col > 1:
                col = 0
                row += 1