import os, sys
import webbrowser
import ttkbootstrap as ttk

from gui.components import RoundedFrame
from gui.pages.tools.surveillance_page import SurveillancePage
from gui.pages.tools.message_logger_page import MessageLoggerPage
from gui.pages.tools.user_lookup_page import UserLookupPage
from gui.pages.tools.password_gen import PasswordGenPage
from gui.pages.tools.auto_afk_reply_page import AutoAFKReplyPage
from gui.pages.tools.backups_page import BackupsPage
from gui.helpers.style import Style

class ToolsPage:
    def __init__(self, root, bot_controller, images, layout, position_resize_grips):
        self.root = root
        self.bot_controller = bot_controller
        self.images = images
        self.layout = layout
        self.position_resize_grips = position_resize_grips
        self.hover_colour = self.root.style.colors.get("secondary")
        
        self.surveillance_page = SurveillancePage(self, root, bot_controller, images, layout)
        self.message_logger_page = MessageLoggerPage(self, root, bot_controller, images, layout)
        self.user_lookup_page = UserLookupPage(self, root, bot_controller, images, layout)
        self.password_gen_page = PasswordGenPage(self, root, bot_controller, images, layout)
        self.auto_afk_reply_page = AutoAFKReplyPage(self, root, bot_controller, images, layout)
        self.backups_page = BackupsPage(self, root, bot_controller, images, layout)
        
        self.pages = [
            {
                "name": "Surveillance",
                "description": "Search a user’s message history across mutual servers",
                "page": self.surveillance_page,
                "command": self.draw_surveillance,
                "icon": self.images.get("surveillance")
            },
            {
                "name": "Message Logger",
                "description": "Logs every deleted message sent in your servers",
                "page": self.message_logger_page,
                "command": self.draw_message_logger,
                "icon": self.images.get("message_logger")
            },
            {
                "name": "Auto AFK Reply",
                "description": "Automatically reply to DMs when you're away from the keyboard",
                "page": self.auto_afk_reply_page,
                "command": self.draw_auto_afk_reply,
                "icon": self.images.get("auto_afk_reply")
            },
            {
                "name": "Backups",
                "description": "Create and restore backups of your Discord account, friends, and servers",
                "page": self.backups_page,
                "command": self.draw_backups,
                "icon": self.images.get("backups")
            },
            {
                "name": "User Lookup",
                "description": "Look up information about a user by their ID",
                "page": self.user_lookup_page,
                "command": self.draw_user_lookup,
                "icon": self.images.get("user_lookup")
            },
            {
                "name": "Password Generator",
                "description": "Generate strong, random passwords with customizable options",
                "page": self.password_gen_page,
                "command": self.draw_password_gen,
                "icon": self.images.get("password_gen")
            },
            {
                "name": "Telemetry Stats",
                "description": "View anonymous telemetry data collected from Ghost users",
                "page": None,
                "command": self.open_telemetry_stats,
                "icon": self.images.get("telemetry")
            }
        ]
        
    def draw_password_gen(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.password_gen_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_password_gen)
        self.position_resize_grips()
        
    def draw_surveillance(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.surveillance_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_surveillance)
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
        
    def draw_auto_afk_reply(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.auto_afk_reply_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_auto_afk_reply)
        self.position_resize_grips()
        
    def draw_backups(self):
        self.layout.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main()
        self.backups_page.draw(main)
        self.layout.sidebar.set_button_command("tools", self.draw_backups)
        self.position_resize_grips() 
        
    def open_telemetry_stats(self):
        webbrowser.open("https://www.ghostt.cc/stats/")
        
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
        page_wrapper = RoundedFrame(parent, radius=15, bootstyle="dark.TFrame")

        page_icon_wrapper = RoundedFrame(page_wrapper, radius=15, background=Style.SETTINGS_PILL_HOVER.value)
        page_icon_wrapper.pack(side=ttk.LEFT, padx=(10, 10), pady=(10, 10))

        page_icon = ttk.Label(page_icon_wrapper, image=page["icon"], background=Style.SETTINGS_PILL_HOVER.value)
        page_icon.pack(side=ttk.LEFT, padx=10, pady=10)
        
        text_wrapper = RoundedFrame(page_wrapper, radius=0, bootstyle="dark.TFrame")
        text_wrapper.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True, padx=(0, 10), pady=(10, 10))
        
        title = ttk.Label(text_wrapper, text=page["name"], font=("Host Grotesk", 14, "bold"), background=self.root.style.colors.get("dark"))
        title.pack(anchor=ttk.W)
        
        description = ttk.Label(text_wrapper, text=page["description"], font=("Host Grotesk", 11), background=self.root.style.colors.get("dark"))
        description.pack(anchor=ttk.W, pady=(2, 0))
        
        page_wrapper.bind("<Button-1>", lambda e: page["command"]())
        page_icon.bind("<Button-1>", lambda e: page["command"]())
        title.bind("<Button-1>", lambda e: page["command"]())
        description.bind("<Button-1>", lambda e: page["command"]())
        text_wrapper.bind("<Button-1>", lambda e: page["command"]())
        page_icon_wrapper.bind("<Button-1>", lambda e: page["command"]())
        
        # Bind hover effects to the entire page card
        self._bind_hover_effects(page_wrapper, targets=[page_wrapper, title, description, text_wrapper], hover_bg=self.hover_colour, normal_bg=self.root.style.colors.get("dark"))
        self._bind_hover_effects(title, targets=[page_wrapper, title, description, text_wrapper], hover_bg=self.hover_colour, normal_bg=self.root.style.colors.get("dark"))
        self._bind_hover_effects(description, targets=[page_wrapper, title, description, text_wrapper], hover_bg=self.hover_colour, normal_bg=self.root.style.colors.get("dark"))
        self._bind_hover_effects(text_wrapper, targets=[page_wrapper, title, description, text_wrapper], hover_bg=self.hover_colour, normal_bg=self.root.style.colors.get("dark"))
        self._bind_hover_effects(page_icon_wrapper, targets=[page_wrapper, title, description, text_wrapper], hover_bg=self.hover_colour, normal_bg=self.root.style.colors.get("dark"))
        return page_wrapper
        
    def draw(self, parent):
        title = ttk.Label(parent, text="Tools", font=("Host Grotesk", 24, "bold"))
        title.configure(background=self.root.style.colors.get("bg"))
        title.pack(pady=(0, 15), anchor=ttk.W)
        
        for index, page in enumerate(self.pages):
            page_card = self._draw_page_card(parent, page)
            page_card.pack(fill=ttk.X, pady=(0, 10))