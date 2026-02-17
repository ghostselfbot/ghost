import sys
import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, RoundedButton, RoundedFrame

class RichPresencePanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None, bot_controller=None):
        super().__init__(root, parent, "Rich Presence", images.get("rich_presence"), width=width, collapsed=False)
        self.cfg = config
        self.rpc = self.cfg.get_rich_presence()
        self.rpc_tk_entries = {}
        self.rpc_entries = {
            "enabled": "Enabled",
            "name": "Name",
            "details": "Details",
            "details_url": "Details URL",
            "state": "State",
            "state_url": "State URL",
            "large_image": "Large Image Key",
            "large_text": "Large Text",
            "large_url": "Large Image URL",
            "small_image": "Small Image Key",
            "small_text": "Small Text",
            "small_url": "Small Image URL",
        }
        self.last_saved_state = {
            "enabled": self.rpc.enabled,
            "state": self.rpc.state,
            "details": self.rpc.details,
            "large_image": self.rpc.large_image,
            "large_text": self.rpc.large_text,
            "small_image": self.rpc.small_image,
            "small_text": self.rpc.small_text,
            "name": self.rpc.name,
            "state_url": self.rpc.state_url,
            "details_url": self.rpc.details_url,
            "large_url": self.rpc.large_url,
            "small_url": self.rpc.small_url
        }
        self.bot_controller = bot_controller
        self.images = images
        self.user_banner_colour = None
        self.user_avatar = None
        self.user = None
        self.preview_vars = {
            "name": ttk.StringVar(value=self.rpc.name),
            "details": ttk.StringVar(value=self.rpc.details),
            "state": ttk.StringVar(value=self.rpc.state),
            "large_image": ttk.StringVar(value=self.rpc.large_image)
        }
        
        self.large_image_label = None
        self.name_label = None
        self.details_label = None
        self.state_label = None

        self._preview_after_id = None
        self.PREVIEW_DEBOUNCE_MS = 500  # adjust if needed

        for var in self.preview_vars.values():
            var.trace_add("write", self._schedule_preview_update)
        
    def _save_rpc(self):
        for index, (key, value) in enumerate(self.rpc_entries.items()):
            tkinter_entry = self.rpc_tk_entries[key]
            if key == "enabled":
                self.rpc.enabled = tkinter_entry.instate(["selected"])
            else:
                self.rpc.set(key, tkinter_entry.get())
            
        self.rpc.save(notify=False)
        
    def _reset_rpc(self, _):
        self.rpc.reset_defaults()
        
    def _schedule_preview_update(self, *_):
        if self._preview_after_id is not None:
            self.root.after_cancel(self._preview_after_id)

        self._preview_after_id = self.root.after(
            self.PREVIEW_DEBOUNCE_MS,
            self._update_preview
        )
        
    def _update_preview(self):
        try:
            name = self.preview_vars["name"].get() or "Ghost"
            details = self.preview_vars["details"].get().strip()
            state = self.preview_vars["state"].get().strip()
            large_image_url = self.preview_vars["large_image"].get().strip()
            if large_image_url == "" or large_image_url.lower() == "none":
                large_image_url = "https://www.ghostt.cc/assets/ghost.png"

            self.name_label.configure(text=name)

            row = 1  # start under the name

            if details:
                self.details_label.configure(text=details)
                self.details_label.grid(row=row, column=0, sticky=ttk.W)
                row += 1
            else:
                self.details_label.grid_remove()

            if state:
                self.state_label.configure(text=state)
                self.state_label.grid(row=row, column=0, sticky=ttk.W)
                row += 1
            else:
                self.state_label.grid_remove()

            if large_image_url:
                large_img = self.images.load_image_from_url(large_image_url, (64, 64), 5)
                if large_img:
                    self.large_image_label.configure(image=large_img)
                    self.large_image_label.image = large_img

        except Exception as e:
            print(f"Error updating RPC preview: {e}")
        
    def _draw_preview(self, parent):
        wrapper = RoundedFrame(parent, radius=15, background=self.root.style.colors.get("secondary"))
        wrapper.pack(fill=ttk.X, expand=False, pady=(10, 0), padx=10)
        
        playing_label = ttk.Label(wrapper, text="Playing", font=("Host Grotesk", 10 if sys.platform != "darwin" else 12))
        playing_label.configure(background=self.root.style.colors.get("secondary"))
        playing_label.grid(row=0, column=0, sticky=ttk.W, padx=(5, 5), pady=(5, 0))
        
        large_image = self.images.load_image_from_url(self.rpc.large_image if self.rpc.large_image else "https://www.ghostt.cc/assets/ghost.png", (64, 64), 5)
        self.large_image_label = ttk.Label(wrapper, image=large_image, background=self.root.style.colors.get("secondary"))
        self.large_image_label.image = large_image
        self.large_image_label.grid(row=1, column=0, padx=(5, 5), pady=5)
        
        # small_image = self.images.load_image_from_url(self.rpc.small_image if self.rpc.small_image else "https://www.ghostt.cc/assets/ghost.png", (28, 28), 12)
        # self.small_image_label = ttk.Label(wrapper, image=small_image, background=self.root.style.colors.get("secondary"))
        # self.small_image_label.image = small_image
        # self.small_image_label.place(x=50, y=70, width=28, height=28)
        # self.small_image_label.lift() 
        
        details_wrapper = RoundedFrame(wrapper, radius=0, background=self.root.style.colors.get("secondary"))
        details_wrapper.grid(row=1, column=1, sticky=ttk.W, padx=(0, 5), pady=5)
        
        self.name_label = ttk.Label(details_wrapper, text=self.rpc.name or "Ghost", font=("Host Grotesk", 14, "bold"))
        self.name_label.configure(background=self.root.style.colors.get("secondary"))
        self.name_label.grid(row=0, column=0, sticky=ttk.W)
        
        self.details_label = ttk.Label(details_wrapper, text=self.rpc.details or "", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.details_label.configure(background=self.root.style.colors.get("secondary"))
        self.details_label.grid(row=1, column=0, sticky=ttk.W)
        
        self.state_label = ttk.Label(details_wrapper, text=self.rpc.state or "", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.state_label.configure(background=self.root.style.colors.get("secondary"))
        self.state_label.grid(row=2, column=0, sticky=ttk.W)
        
        time_elapsed_label = ttk.Label(details_wrapper, text="00:15", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        time_elapsed_label.configure(foreground="#68ae7c", background=self.root.style.colors.get("secondary"))
        time_elapsed_label.grid(row=3, column=0, sticky=ttk.W)
        
    def _draw_user_wrapper(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame", custom_size=True)
        wrapper.set_width(225)
        wrapper.grid(row=1, column=1, sticky=ttk.NSEW, padx=(10, 0))
        
        if self.user_avatar:
            accent_colour_banner = RoundedFrame(wrapper, radius=(15, 15, 0, 0), background=self.user_banner_colour, parent_background=self.root.style.colors.get("bg"))
            accent_colour_banner.set_height(85)
            accent_colour_banner.pack(side=ttk.TOP, fill=ttk.X)
            accent_colour_banner.columnconfigure(0, weight=1)
            
            avatar_label = ttk.Canvas(wrapper, width=100, height=200, background=self.user_banner_colour, highlightthickness=0)

            avatar_label.create_rectangle(0, 0, 100, 50, fill=self.user_banner_colour, outline="")
            avatar_label.create_rectangle(0, 50, 100, 200, fill=self.root.style.colors.get("dark"), outline="")
            
            # create an ovel the same size of the avatar but an extra 5px on each side and use the dark background color, this is to create a border
            avatar_label.create_oval(9, 8, 85, 85, fill=self.root.style.colors.get("dark"), outline="")
            avatar_label.create_image(65//2 + 15, 65//2 + 14, image=self.user_avatar, anchor="center")
            
            avatar_label.place(x=0, y=85-50, width=100, height=200)
            
        if self.user:
            user_info_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
            user_info_wrapper.pack(side=ttk.TOP, fill=ttk.X, pady=(35, 0), padx=(10, 10))
            user_info_wrapper.configure(height=50)
            
            display_name = ttk.Label(user_info_wrapper, text=self.user.display_name, font=("Host Grotesk", 16 if sys.platform != "darwin" else 18, "bold"))
            display_name.configure(background=self.root.style.colors.get("dark"))
            display_name.place(relx=0, rely=0)
            
            username = ttk.Label(user_info_wrapper, text=f"{self.user.name}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
            username.configure(background=self.root.style.colors.get("dark"), foreground="lightgrey")
            username.place(relx=0, rely=0.42 if sys.platform == "darwin" else 0.45)
            
            self._draw_preview(wrapper)
        
        return wrapper
        
    def draw(self):
        toggle_wrapper = RoundedFrame(self.wrapper, radius=(10, 10, 10, 10), bootstyle="dark.TFrame")
        toggle_wrapper.grid(row=0, column=0, columnspan=4, sticky="we", pady=(0, 10))
        toggle_wrapper.bind("<Button-1>", lambda e: self.toggle_checkbox.invoke())
        
        toggle_label = ttk.Label(toggle_wrapper, text="Enable Rich Presence")
        toggle_label.configure(background=self.root.style.colors.get("dark"))
        toggle_label.grid(row=0, column=0, sticky=ttk.W, padx=(10, 0), pady=10)
        toggle_label.bind("<Button-1>", lambda e: self.toggle_checkbox.invoke())
        
        self.toggle_checkbox = ttk.Checkbutton(toggle_wrapper, text="", style="success-round-toggle")
        self.toggle_checkbox.grid(row=0, column=1, sticky=ttk.E, padx=(0, 10), pady=10)
        self.toggle_checkbox.configure(command=self._save_rpc)
        
        toggle_wrapper.grid_columnconfigure(0, weight=1)
        
        self.user = self.bot_controller.get_user()
        if self.user:
            avatar_url = self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
            self.user_avatar = self.bot_controller.get_avatar_from_url(avatar_url, size=65, radius=65//2)
            self.user_banner_colour = self.images.get_majority_color_from_url(avatar_url)
        self._draw_user_wrapper(self.wrapper)
        
        if self.rpc.enabled:
            self.toggle_checkbox.state(["!alternate", "selected"])
        else:
            self.toggle_checkbox.state(["!alternate", "!selected"])
        
        self.rpc_tk_entries["enabled"] = self.toggle_checkbox
        padding = (10, 2)

        for index, (key, value) in enumerate(self.rpc_entries.items()):
            if key == "enabled":
                continue
            
            rpc_value = self.rpc.get(key)
            if key in self.preview_vars:
                entry = ttk.Entry(
                    self.body,
                    textvariable=self.preview_vars[key],
                    font=("Host Grotesk", 12 if sys.platform != "darwin" else 13)
                )
            else:
                entry = ttk.Entry(
                    self.body,
                    font=("Host Grotesk", 12 if sys.platform != "darwin" else 13)
                )
                entry.insert(0, rpc_value)

            entry.bind("<Return>", lambda event: self._save_rpc())
            entry.bind("<FocusOut>", lambda event: self._save_rpc())
                
            label = ttk.Label(self.body, text=value)
            label.configure(background=self.root.style.colors.get("dark"))
            
            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=padding[0], pady=(padding[1] + 8 if index == 1 else padding[1], padding[1]))
            entry.grid(row=index + 1, column=1, sticky="we", padx=padding[0], pady=(padding[1] + 8 if index == 1 else padding[1], padding[1]), columnspan=3)
            
            self.body.grid_columnconfigure(1, weight=1)
            self.rpc_tk_entries[key] = entry
            
        save_label = ttk.Label(self.body, text="A restart is required to apply changes!", font=("Host Grotesk", 12, "italic"))
        save_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        save_label.grid(row=len(self.rpc_entries) + 1, column=0, columnspan=2, sticky=ttk.W, padx=(10, 0), pady=10)
        
        # save_rpc_button = ttk.Button(self.body, text="Save", style="success.TButton", command=self._save_rpc)
        # save_rpc_button.grid(row=len(self.rpc_entries) + 1, column=2, sticky=ttk.E, pady=10)
        
        # reset_rpc_button = ttk.Button(self.body, text="Reset", style="danger.TButton", command=self._reset_rpc)
        reset_rpc_button = RoundedButton(self.body, text="Reset", style="danger.TButton", command=self._reset_rpc)
        reset_rpc_button.grid(row=len(self.rpc_entries) + 1, column=3, sticky=ttk.E, padx=(5, 11), pady=10)
        
        self._update_preview()
        return self.wrapper