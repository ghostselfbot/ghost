import ttkbootstrap as ttk

from gui.helpers.style import Style
from gui.components import RoundedFrame, ToolPage, RoundedButton, RoundedSwitch, DropdownMenu
from utils.config import Config

class AutoAFKReplyPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Auto AFK Reply")
        self.cfg = Config()
        self.afk_cfg = self.cfg.get("afk") if self.cfg.get("afk") else {"afk_response": "I'm away from the keyboard right now, I'll get back to you as soon as I can.", "afk_times": [8, 18], "enabled": False}
        self.afk_response_entry = None
        self.afk_start_entry = None
        self.afk_end_entry = None
        self.afk_start_period_menu = None
        self.afk_end_period_menu = None
        self.auto_toggle_switch = None

    def _validate_afk_hour(self, value):
        if value == "":
            return True

        if not value.isdigit():
            return False

        return 1 <= int(value) <= 12

    def _hour_to_display(self, hour):
        hour = int(hour) % 24
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12

        if display_hour == 0:
            display_hour = 12

        return display_hour, period

    def _display_to_hour(self, hour_value, period_value, fallback):
        try:
            hour = int(hour_value)
        except (TypeError, ValueError):
            return fallback

        if hour < 1 or hour > 12:
            return fallback

        if period_value == "AM":
            return 0 if hour == 12 else hour

        if period_value == "PM":
            return 12 if hour == 12 else hour + 12

        return fallback

    def _get_afk_times(self):
        afk_times = self.afk_cfg.get("afk_times", [8, 18])

        if isinstance(afk_times, dict):
            return afk_times.get("start", 8), afk_times.get("end", 18)

        if isinstance(afk_times, (list, tuple)) and len(afk_times) >= 2:
            return afk_times[0], afk_times[1]

        return 8, 18

    def _draw_time_selector(self, parent, selected_hour, selected_period):
        wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), background=Style.ENTRY_BG.value, parent_background=self.root.style.colors.get("dark"))
        wrapper.grid_columnconfigure(1, weight=1, minsize=82)
        validate_command = (self.root.register(self._validate_afk_hour), "%P")

        entry = ttk.Entry(wrapper, width=3, font=("Host Grotesk", 12))
        entry.configure(foreground=self.root.style.colors.get("fg"), validate="key", validatecommand=validate_command)
        entry.insert(0, str(selected_hour))
        entry.grid(row=0, column=0, sticky=ttk.W, padx=(5, 0), pady=5)
        entry.bind("<Return>", lambda event: self._save_cfg())
        entry.bind("<FocusOut>", lambda event: self._save_cfg())

        menu = DropdownMenu(wrapper, options=["AM", "PM"], command=lambda _option: self._save_cfg())
        menu.set_selected(selected_period)
        menu.draw().grid(row=0, column=1, sticky=ttk.EW, padx=(0, 5), pady=5)

        return wrapper, entry, menu
        
    def draw_navigation(self, parent):
        wrapper = ttk.Frame(parent)

        tools_label = ttk.Label(wrapper, text="Tools", font=("Host Grotesk", 24, "bold"), foreground=Style.LIGHT_GREY.value)
        tools_label.grid(row=0, column=0, sticky=ttk.W)
        tools_label.bind("<Button-1>", lambda e: self.go_back())

        back_button = ttk.Label(wrapper, image=self.images.get("right-chevron-small"))
        back_button.bind("<Button-1>", lambda e: self.go_back())
        back_button.grid(row=0, column=1, sticky=ttk.W, padx=(10, 10))

        page_name = ttk.Label(wrapper, text=self.title, font=("Host Grotesk", 24, "bold"))
        page_name.grid(row=0, column=2, sticky=ttk.W)
        page_name.bind("<Button-1>", lambda e: self.go_back())

        wrapper.grid_columnconfigure(2, weight=1)

        return wrapper
    
    def _save_cfg(self):
        self.afk_cfg["enabled"] = self.auto_toggle_switch.variable.get()
        self.afk_cfg["afk_response"] = self.afk_response_entry.get()

        start_fallback, end_fallback = self._get_afk_times()
        self.afk_cfg["afk_times"] = [
            self._display_to_hour(self.afk_start_entry.get(), self.afk_start_period_menu.value(), start_fallback),
            self._display_to_hour(self.afk_end_entry.get(), self.afk_end_period_menu.value(), end_fallback),
        ]
        
        self.cfg.set("afk", self.afk_cfg, save=False)
        self.cfg.save()
    
    def draw_content(self, wrapper):
        content_wrapper = RoundedFrame(wrapper, radius=(15, 15, 15, 15), background=self.root.style.colors.get("bg"))
        content_wrapper.pack(fill=ttk.BOTH, expand=True)
        
        # indefinite_toggle_wrapper = RoundedFrame(content_wrapper, radius=(10, 10, 10, 10), bootstyle="dark.TFrame")
        # indefinite_toggle_wrapper.pack(fill=ttk.X, pady=(0, 10))
        # indefinite_toggle_wrapper.bind("<Button-1>", lambda e: self.indefinite_toggle_switch.invoke())
        # indefinite_toggle_wrapper.grid_columnconfigure(0, weight=1)

        # indefinite_toggle_label = ttk.Label(indefinite_toggle_wrapper, text="Enable AFK replies indefinitely", font=("Host Grotesk", 16, "bold"))
        # indefinite_toggle_label.configure(background=self.root.style.colors.get("dark"))
        # indefinite_toggle_label.grid(row=0, column=0, sticky=ttk.W, padx=(10, 0), pady=10)
        # indefinite_toggle_label.bind("<Button-1>", lambda e: self.indefinite_toggle_switch.invoke())
        
        # self.indefinite_toggle_switch = RoundedSwitch(indefinite_toggle_wrapper, variable=ttk.BooleanVar(value=self.afk_cfg.get("enabled", False)))
        # self.indefinite_toggle_switch.grid(row=0, column=1, sticky=ttk.E, padx=(0, 10), pady=10)
        # self.indefinite_toggle_switch.configure(command=self._save_cfg)
        
        auto_toggle_wrapper = RoundedFrame(content_wrapper, radius=(10, 10, 10, 10), bootstyle="dark.TFrame")
        auto_toggle_wrapper.pack(fill=ttk.X, pady=(0, 10))
        auto_toggle_wrapper.bind("<Button-1>", lambda e: self.auto_toggle_switch.invoke())
        auto_toggle_wrapper.grid_columnconfigure(0, weight=1)
        
        auto_toggle_label = ttk.Label(auto_toggle_wrapper, text="Enable automatic AFK replies", font=("Host Grotesk", 16, "bold"))
        auto_toggle_label.configure(background=self.root.style.colors.get("dark"))
        auto_toggle_label.grid(row=0, column=0, sticky=ttk.W, padx=(10, 0), pady=10)
        auto_toggle_label.bind("<Button-1>", lambda e: self.auto_toggle_switch.invoke())
        
        self.auto_toggle_switch = RoundedSwitch(auto_toggle_wrapper, variable=ttk.BooleanVar(value=self.afk_cfg.get("enabled", False)))
        self.auto_toggle_switch.grid(row=0, column=1, sticky=ttk.E, padx=(0, 10), pady=10)
        self.auto_toggle_switch.configure(command=self._save_cfg)
        
        if self.afk_cfg["enabled"]:
            self.auto_toggle_switch.state(["!alternate", "selected"])
        else:
            self.auto_toggle_switch.state(["!alternate", "!selected"])
            
        afk_response_wrapper = RoundedFrame(content_wrapper, style="dark.TFrame", radius=(10, 10, 10, 10))
        afk_response_wrapper.pack(fill=ttk.X, pady=(0, 10))
        afk_response_wrapper.grid_columnconfigure(0, weight=1)

        response_label = ttk.Label(afk_response_wrapper, text="AFK Response Message", font=("Host Grotesk", 16, "bold"))
        response_label.configure(background=self.root.style.colors.get("dark"))
        response_label.grid(row=0, column=0, sticky=ttk.W, padx=10, pady=(10, 5))
        
        response_desc = ttk.Label(afk_response_wrapper, text="This message will be sent automatically when someone DMs you while you're away.")
        response_desc.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
        response_desc.grid(row=1, column=0, sticky=ttk.W, padx=10, pady=(0, 5))
        
        self.afk_response_entry = ttk.Entry(afk_response_wrapper, font=("Host Grotesk", 12))
        self.afk_response_entry.configure(foreground=self.root.style.colors.get("fg"))
        self.afk_response_entry.insert(0, self.afk_cfg["afk_response"])
        self.afk_response_entry.grid(row=2, column=0, sticky="we", padx=10, pady=(5, 10))
        self.afk_response_entry.bind("<Return>", lambda event: self._save_cfg())


        afk_time_wrapper = RoundedFrame(content_wrapper, style="dark.TFrame", radius=(10, 10, 10, 10))
        afk_time_wrapper.pack(fill=ttk.X, pady=(0, 10))
        afk_time_wrapper.grid_columnconfigure(0, weight=1)
        afk_time_wrapper.grid_columnconfigure(2, weight=1)
        
        afk_time_label = ttk.Label(afk_time_wrapper, text="AFK Time Range", font=("Host Grotesk", 16, "bold"))
        afk_time_label.configure(background=self.root.style.colors.get("dark"))
        afk_time_label.grid(row=0, column=0, columnspan=3, sticky=ttk.W, padx=10, pady=(10, 5))
        
        afk_time_desc = ttk.Label(afk_time_wrapper, text="Set your start and end times for when you're usually AFK.")
        afk_time_desc.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
        afk_time_desc.grid(row=1, column=0, columnspan=3, sticky=ttk.W, padx=10, pady=(0, 5))

        start_hour, end_hour = self._get_afk_times()
        start_display_hour, start_period = self._hour_to_display(start_hour)
        end_display_hour, end_period = self._hour_to_display(end_hour)

        start_wrapper, self.afk_start_entry, self.afk_start_period_menu = self._draw_time_selector(
            afk_time_wrapper,
            start_display_hour,
            start_period,
        )
        start_wrapper.grid(row=2, column=0, sticky=ttk.W, padx=10, pady=10)

        to_label = ttk.Label(afk_time_wrapper, text="to")
        to_label.configure(background=self.root.style.colors.get("dark"))
        to_label.grid(row=2, column=1, sticky=ttk.NS, pady=10)

        end_wrapper, self.afk_end_entry, self.afk_end_period_menu = self._draw_time_selector(
            afk_time_wrapper,
            end_display_hour,
            end_period,
        )
        end_wrapper.grid(row=2, column=2, sticky=ttk.E, padx=10, pady=10)
        
        