import ttkbootstrap as ttk
import utils.console as console
from utils.files import open_path_in_explorer, get_themes_path
from gui.components import SettingsPanel, RoundedButton, RoundedFrame, DropdownMenu
from gui.helpers.style import Style

class ThemingPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "Theming", images.get("theming"), width=width)
        self.cfg = config
        self.root = root
        self.images = images
        self.theme_tk_entries = []
        self.themes = self.cfg.get_themes()
        self.menu_themes = [str(theme) for theme in self.themes]
        self.theme_dict = self.cfg.theme.to_dict()
        
    def _save_theme(self, _=None):
        for index, (key, _) in enumerate(self.theme_dict.items()):
            self.cfg.theme.set(key, self.theme_tk_entries[index].get())
            
        self.cfg.theme.save(notify=False)
        self.cfg.save(notify=False)
        
    def _set_theme(self, theme):
        print(f"Setting theme to: {theme}")
        # self.select_menu.set_selected(theme)
        self.cfg.set_theme(theme, save=False)
        self.cfg.save(notify=True)
        # self.select_menu.configure(text=theme)
        # self.cfg.set_theme(theme, save=False)
        # self.cfg.save(notify=True)
        
        # self.create_entry.delete(0, "end")
        # self.select_menu.configure(text=theme)
        
        # self.theme_dict = self.cfg.theme.to_dict()
        
        # for index, (key, value) in enumerate(self.theme_dict.items()):
        #     self.theme_tk_entries[index].delete(0, "end")
        #     self.theme_tk_entries[index].insert(0, value)
            
        # self.message_style_entry.configure(text=self.cfg.config["message_settings"]["style"])
        
    def _delete_theme(self, _):
        if self.cfg.theme.name.lower() == "ghost" or len(self.themes) == 1:
            return console.print_error("You can't delete the default theme!")
        
        self.cfg.delete_theme(self.cfg.theme.name)
        
    def _create_theme(self, theme_name):
        if theme_name is None or theme_name == "":
            return console.error("Theme name can't be empty!")
        
        success = self.cfg.create_theme(theme_name)
        
        if isinstance(success, bool) and not success:
            return console.error("Theme already exists!")
        
        self.cfg.set_theme(success.name, save=False)
        self.cfg.save(notify=True)
        
        # self.create_entry.delete(0, "end")
        # self.select_menu.configure(text=success.name)
        
        # self.theme_dict = self.cfg.theme.to_dict()
        
        # for index, (key, value) in enumerate(self.theme_dict.items()):
        #     self.theme_tk_entries[index].delete(0, "end")
        #     self.theme_tk_entries[index].insert(0, value)
        
    def _set_message_style(self, style):
        self.message_style_entry.configure(text=style)
        self._save_theme()
        
    def _draw_open_folder_button(self, parent):
        def _hover_enter(_):
            wrapper.set_background(background=Style.SETTINGS_PILL_HOVER.value)
            open_folder_button.configure(background=Style.SETTINGS_PILL_HOVER.value)
            
        def _hover_leave(_):
            wrapper.set_background(background=self.root.style.colors.get("secondary"))
            open_folder_button.configure(background=self.root.style.colors.get("secondary"))
        
        wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), bootstyle="secondary")
        wrapper.bind("<Button-1>", lambda e: open_path_in_explorer(get_themes_path()))
        wrapper.bind("<Enter>", _hover_enter)
        wrapper.bind("<Leave>", _hover_leave)
        
        open_folder_button = ttk.Label(wrapper, image=self.images.get("folder-open"), style="secondary")
        open_folder_button.configure(background=self.root.style.colors.get("secondary"))
        open_folder_button.pack(side=ttk.LEFT, padx=10, pady=7)
        open_folder_button.bind("<Button-1>", lambda e: open_path_in_explorer(get_themes_path()))
        open_folder_button.bind("<Enter>", _hover_enter)
        open_folder_button.bind("<Leave>", _hover_leave)
        
        return wrapper
        
    def toggle_create_theme_button(self, state):
        if state:
            self.create_button.set_state("normal")
        else:
            self.create_button.set_state("disabled")
        
    def draw(self):
        self.themes = self.cfg.get_themes()
        self.theme_dict = self.cfg.theme.to_dict()
        
        #-------
        
        create_label = ttk.Label(self.body, text="New theme name")
        create_label.configure(background=self.root.style.colors.get("dark"))
        create_label.grid(row=0, column=0, sticky=ttk.W, padx=(10, 0), pady=(10, 0))
        
        self.create_entry = ttk.Entry(self.body, font=("Host Grotesk",))
        self.create_entry.grid(row=0, column=1, sticky="we", padx=(10, 10), pady=(10, 0))
        self.create_entry.bind("<KeyRelease>", lambda e: self.toggle_create_theme_button(self.create_entry.get().strip() != ""))
        
        self.create_button = RoundedButton(self.body, text="Create", command=lambda _: self._create_theme(self.create_entry.get()), style="success.TButton")
        self.create_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 11), pady=(10, 0))
        self.create_button.set_state("disabled")
        
        #-------
        
        select_label = ttk.Label(self.body, text="Select theme")
        select_label.configure(background=self.root.style.colors.get("dark"))
        select_label.grid(row=1, column=0, sticky=ttk.NW, padx=(10, 0), pady=(15, 0))
        
        # self.select_menu = ttk.Menubutton(self.body, text=self.cfg.theme.name, bootstyle="secondary")
        # self.select_menu.menu = ttk.Menu(self.select_menu, tearoff=0)
        # self.select_menu["menu"] = self.select_menu.menu
        
        # for theme in self.themes:
        #     self.select_menu.menu.add_command(label=str(theme), command=lambda theme=theme.name: self._set_theme(theme))
            
        self.select_menu = DropdownMenu(self.body, options=self.menu_themes, command=self._set_theme)
        self.select_menu.set_selected(self.cfg.theme.name)
        self.select_menu.draw().grid(row=1, column=1, columnspan=2, sticky="we", padx=(10, 10), pady=(10, 0))
        
        #-------
        
        # message_style_label = ttk.Label(self.body, text="Message style")
        # message_style_label.configure(background=self.root.style.colors.get("dark"))
        # message_style_label.grid(row=2, column=0, sticky=ttk.W, padx=(10, 0), pady=(10, 0))
        
        # self.message_style_entry = ttk.Menubutton(self.body, text=self.cfg.config["message_settings"]["style"], bootstyle="secondary")
        # self.message_style_entry.menu = ttk.Menu(self.message_style_entry, tearoff=0)
        # self.message_style_entry["menu"] = self.message_style_entry.menu
        
        # for style in ["codeblock", "image", "embed"]:
        #     self.message_style_entry.menu.add_command(label=style, command=lambda style=style: self._set_message_style(style))
            
        # self.message_style_entry.grid(row=2, column=1, columnspan=2, sticky="we", padx=(10, 10), pady=(10, 0))
        
        #-------
        
        ttk.Separator(self.body, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="we", padx=(10, 10), pady=(15, 5))
        
        #-------
        
        for index, (key, value) in enumerate(self.theme_dict.items()):
            padding = (10, 2)
            entry = ttk.Entry(self.body, font=("Host Grotesk",))
            entry.insert(0, value)

            if index == 0:
                padding = (padding[0], (10, 2))
            elif index == len(self.theme_dict) - 1:
                padding = (padding[0], (2, 10))

            label = ttk.Label(self.body, text=key.capitalize(), font=("Host Grotesk",))
            label.configure(background=self.root.style.colors.get("dark"))

            label.grid(row=index + 4, column=0, sticky=ttk.W, padx=padding[0], pady=padding[1])
            entry.grid(row=index + 4, column=1, columnspan=2, sticky="we", padx=padding[0], pady=padding[1])
            entry.bind("<Return>", self._save_theme)
            entry.bind("<FocusOut>", self._save_theme)

            self.body.grid_columnconfigure(1, weight=1)
            self.theme_tk_entries.append(entry)
            
        #-------
        
        ttk.Separator(self.body, orient="horizontal").grid(row=len(self.theme_dict) + 5, column=0, columnspan=3, sticky="we", padx=(10, 10), pady=(5, 15))
        
        #-------
        
        buttons_frame = RoundedFrame(self.body, radius=(0, 0, 15, 15), style="dark.TFrame", parent_background=self.root.style.colors.get("bg"))
        buttons_frame.grid(row=len(self.theme_dict) + 6, column=0, columnspan=3, sticky="we")
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        save_theme_label = ttk.Label(buttons_frame, text="Remember to save your changes!", font=("Host Grotesk", 12, "italic"))
        save_theme_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        save_theme_button = RoundedButton(buttons_frame, text="Save", style="success.TButton", command=self._save_theme)
        delete_theme_button = RoundedButton(buttons_frame, text="Delete", style="danger.TButton", command=self._delete_theme)
        # open_folder_button = RoundedButton(buttons_frame, image=self.images.get("folder-open"), style="secondary.TButton", command=lambda _: open_path_in_explorer(get_themes_path()))
        open_folder_button = self._draw_open_folder_button(buttons_frame)

        save_theme_label.grid(row=len(self.theme_dict) + 6, column=0, columnspan=2, sticky=ttk.W, padx=(10, 0), pady=(0, 10))
        save_theme_button.grid(row=len(self.theme_dict) + 6, column=1, sticky=ttk.E, pady=(0, 10))
        delete_theme_button.grid(row=len(self.theme_dict) + 6, column=2, sticky=ttk.E, padx=5, pady=(0, 10))
        open_folder_button.grid(row=len(self.theme_dict) + 6, column=3, sticky=ttk.E, padx=(0, 11), pady=(0, 10))
        
        return self.wrapper