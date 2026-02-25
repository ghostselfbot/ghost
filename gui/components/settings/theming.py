import sys
import ttkbootstrap as ttk
import utils.console as console
from utils.files import open_path_in_explorer, get_themes_path
from gui.components import SettingsPanel, RoundedButton, RoundedFrame, DropdownMenu
from gui.helpers.style import Style

class ThemingPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None, bot_controller=None):
        super().__init__(root, parent, "Theming", images.get("theming"), width=width)
        self.cfg = config
        self.root = root
        self.images = images
        self.theme_tk_entries = []
        self.themes = self.cfg.get_themes()
        self.menu_themes = [str(theme) for theme in self.themes]
        self.theme_dict = self.cfg.theme.to_dict()
        self.bot_controller = bot_controller
        self.user = None
        self.user_avatar = None
        self.embed_image = None
        
    def _save_theme(self, _=None):
        for index, (key, _) in enumerate(self.theme_dict.items()):
            self.cfg.theme.set(key, self.theme_tk_entries[index].get())
            
        self.cfg.theme.save(notify=False)
        self.cfg.save(notify=False)
        
    def _set_theme(self, theme):
        print(f"Setting theme to: {theme}")
        self.cfg.set_theme(theme, save=False)
        self.cfg.save(notify=True)
        
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
        
    def _schedule_preview_update(self, *_):
        if hasattr(self, "_preview_after_id") and self._preview_after_id:
            self.root.after_cancel(self._preview_after_id)

        self._preview_after_id = self.root.after(300, self._update_preview_live)

    def _update_preview_live(self):
        for index, (key, _) in enumerate(self.theme_dict.items()):
            value = self.theme_tk_entries[index].get()
            setattr(self.cfg.theme, key, value)

        try:
            self.embed_image = self.bot_controller.get_avatar_from_url(self.cfg.theme.image, size=70, radius=5)
        except Exception:
            self.embed_image = None

        if hasattr(self, "preview_canvas"):
            self.preview_canvas.delete("all")

        self._draw_preview_contents()
       
    def _draw_preview_contents(self):
        canvas = self.preview_canvas
        canvas.delete("all")

        font = ttk.font.Font(family="Host Grotesk", size=12)

        if self.user_avatar:
            canvas.create_image(25, 25, image=self.user_avatar, anchor="center")

            username = self.user.display_name if self.user else "Username"
            canvas.create_text(55, 15, text=username, fill=self.root.style.colors.get("fg"), font=("Host Grotesk", 14, "bold"), anchor="w")
            
            canvas.create_text(55 + font.measure(username) + 10, 16, text="04:20", fill=Style.DARK_GREY.value, font=("Host Grotesk", 11), anchor="w")

        embed_wrapper = RoundedFrame(canvas, radius=8, background=self.root.style.colors.get("secondary"))
        canvas.create_window(55, 32, window=embed_wrapper, anchor="nw")
        embed_wrapper.grid_columnconfigure(1, weight=1)
        current_row = 0

        colour_strip = RoundedFrame(embed_wrapper, radius=(8, 0, 0, 8), width=5, background=self.cfg.theme.colour or "#5865F2")
        colour_strip.grid(row=0, column=0, sticky=ttk.NS, rowspan=3)

        title_text = self.cfg.theme.title or ""
        emoji_text = self.cfg.theme.emoji or ""

        if title_text:
            title = ttk.Label(embed_wrapper, text=f"{emoji_text} {title_text}".strip(), font=("Host Grotesk", 14, "bold"))
            title.configure(background=self.root.style.colors.get("secondary"), foreground=self.root.style.colors.get("fg"))
            title.grid(row=current_row, column=1, sticky=ttk.NW, padx=10, pady=(8, 5))
            current_row += 1

        description = ttk.Label(embed_wrapper, text=""".abuse ~ Abusive commands
.account ~ Account commands
.fun ~ Fun commands
.img ~ Image commands
.info ~ Info commands
.mod ~ Moderation commands
.nsfw ~ NSFW commands
.sniper ~ Sniper commands
.text ~ Text commands
.theming ~ Theme commands
.util ~ Utility commands

There are 166 commands!""", font=("Host Grotesk", 12))
        description.configure(background=self.root.style.colors.get("secondary"), foreground=self.root.style.colors.get("fg"))
        description.grid(row=current_row, column=1, sticky=ttk.NW, padx=10, pady=(0 if title_text else 8, 10))
        current_row += 1

        footer_text = getattr(self.cfg.theme, "footer", "") or ""

        if footer_text:
            footer_label = ttk.Label(embed_wrapper, text=footer_text, font=("Host Grotesk", 12))
            footer_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
            footer_label.grid(row=current_row, column=1, sticky=ttk.W, padx=10, pady=(0, 10))
            current_row += 1
            
        if self.embed_image:
            embed_image_label = ttk.Label(embed_wrapper, image=self.embed_image)
            embed_image_label.configure(background=self.root.style.colors.get("secondary"))
            embed_image_label.grid(row=0, column=2, rowspan=current_row, sticky=ttk.NE, padx=10, pady=10)
            
    def draw_preview(self, parent):
        wrapper = RoundedFrame(parent, radius=10,
                            background=self.root.style.colors.get("dark"))
        wrapper.grid(row=0, column=1, sticky=ttk.NS, padx=(10, 0))
        wrapper.grid_propagate(True)

        self.preview_canvas = ttk.Canvas(wrapper, highlightthickness=0, width=360)
        self.preview_canvas.configure(
            background=self.root.style.colors.get("dark"))
        self.preview_canvas.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)

        self._draw_preview_contents()
        
    def draw(self):
        self.body.grid_remove()
        
        wrapper = RoundedFrame(self.wrapper, radius=10, background=self.root.style.colors.get("dark"))
        wrapper.grid(row=0, column=0, sticky=ttk.NSEW)
        wrapper.grid_columnconfigure(0, weight=1)
        
        self.user = self.bot_controller.get_user()
        if self.user:
            avatar_url = self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
            self.user_avatar = self.bot_controller.get_avatar_from_url(avatar_url, size=40, radius=40//2)
        
        try:
            self.embed_image = self.bot_controller.get_avatar_from_url(self.cfg.theme.image, size=70, radius=5)
        except Exception as e:
            print(f"Failed to load embed image: {e}")
            self.embed_image = None
        
        self.themes = self.cfg.get_themes()
        self.theme_dict = self.cfg.theme.to_dict()
        
        #-------
        
        create_label = ttk.Label(wrapper, text="New theme name")
        create_label.configure(background=self.root.style.colors.get("dark"))
        
        self.create_entry = ttk.Entry(wrapper, font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.create_entry.grid(row=1, column=0, sticky="we", padx=(10, 5), pady=(10, 0))
        self.create_entry.bind("<KeyRelease>", lambda e: self.toggle_create_theme_button(self.create_entry.get().strip() != ""))
        
        self.create_button = RoundedButton(wrapper, text="+", command=lambda _: self._create_theme(self.create_entry.get()), style="success.TButton", pady=2)
        self.create_button.grid(row=1, column=1, sticky=ttk.E, padx=(0, 10), pady=(10, 0))
        self.create_button.set_state("disabled")
        
        #-------
        
        select_label = ttk.Label(wrapper, text="Select theme")
        select_label.configure(background=self.root.style.colors.get("dark"))
            
        self.select_menu = DropdownMenu(wrapper, options=self.menu_themes, command=self._set_theme)
        self.select_menu.set_selected(self.cfg.theme.name)
        self.select_menu.draw().grid(row=3, column=0, columnspan=2, sticky="we", padx=(10, 10), pady=(10, 0))
    
        #-------
    
        ttk.Separator(wrapper, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="we", padx=(10, 10), pady=(15, 15))
        
        #-------
        
        start_row = 5  # where your fields begin

        for index, (key, value) in enumerate(self.theme_dict.items()):
            row = start_row + (index * 2)

            entry = ttk.Entry(wrapper, font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
            entry.insert(0, value)

            label = ttk.Label(
                wrapper,
                text=key.capitalize(),
                font=("Host Grotesk", 12 if sys.platform != "darwin" else 13)
            )
            label.configure(background=self.root.style.colors.get("dark"))

            label.grid(row=row, column=0, sticky=ttk.W, padx=10, pady=(0, 2))
            entry.grid(row=row + 1, column=0, columnspan=2, sticky="we", padx=10, pady=(0, 10))

            entry.bind("<KeyRelease>", self._schedule_preview_update)
            entry.bind("<Return>", self._save_theme)
            entry.bind("<FocusOut>", self._save_theme)

            self.theme_tk_entries.append(entry)
            
        row_now = start_row + (len(self.theme_dict) * 2)
            
        #-------
        
        ttk.Separator(wrapper, orient="horizontal").grid(row=row_now, column=0, columnspan=3, sticky="we", padx=(10, 10), pady=(5, 15))
        
        #-------
        
        buttons_frame = RoundedFrame(wrapper, radius=(0, 0, 15, 15), style="dark.TFrame", parent_background=self.root.style.colors.get("bg"))
        buttons_frame.grid(row=row_now + 1, column=0, columnspan=3, sticky="we")
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        save_theme_label = ttk.Label(buttons_frame, text="Remember to save your changes!", font=("Host Grotesk", 12, "italic"))
        save_theme_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        save_theme_button = RoundedButton(buttons_frame, text="Save", style="success.TButton", command=self._save_theme)
        delete_theme_button = RoundedButton(buttons_frame, text="Delete", style="danger.TButton", command=self._delete_theme)
        # open_folder_button = RoundedButton(buttons_frame, image=self.images.get("folder-open"), style="secondary.TButton", command=lambda _: open_path_in_explorer(get_themes_path()))
        open_folder_button = self._draw_open_folder_button(buttons_frame)

        # save_theme_label.grid(row=0, column=0, columnspan=2, sticky=ttk.W, padx=(10, 0), pady=(0, 10))
        save_theme_button.grid(row=0, column=1, sticky=ttk.E, pady=(0, 10))
        delete_theme_button.grid(row=0, column=2, sticky=ttk.E, padx=5, pady=(0, 10))
        open_folder_button.grid(row=0, column=3, sticky=ttk.E, padx=(0, 11), pady=(0, 10))
        
        self.draw_preview(self.wrapper)
        
        return self.wrapper