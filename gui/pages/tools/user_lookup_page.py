import discord
import webbrowser
import sys
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from gui.components import RoundedFrame, ToolPage, RoundedButton
from gui.helpers import Style

class UserLookupPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="User Lookup", frame=None)
        self.search_entry = None  # Initialize search entry to None
        self.user = None
        self.user_avatar = None
        self.user_widget = None
        self.user_banner_colour = self.root.style.colors.get("secondary")
        self.search_results_widget = None
        self.wrapper = None  # Initialize wrapper to None
        self.is_friend = False
        self.mutual_guilds = []
        self.mutual_guilds_member_objects = []
        self.created_at = None
        
    def _search_user(self, user_id):
        if not user_id.isdigit():
            return  # Invalid user ID
        user_id_int = int(user_id)
        self.is_friend = self.bot_controller.is_friend(user_id_int)
        self.mutual_guilds = self.bot_controller.get_mutual_guilds(user_id_int)
        self.created_at = self.bot_controller.snowflake_to_timestamp(user_id_int)
        user = self.bot_controller.get_user_from_id(user_id_int)
        self.user, self.mutual_guilds_member_objects = user

        accent_value = getattr(getattr(self.user, "accent_colour", None), "value", None)
        if accent_value is not None:
            self.user_banner_colour = f"#{accent_value:06x}"
        else:
            self.user_banner_colour = self.root.style.colors.get("secondary")
        
        avatar_url = self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
        self.user_avatar = self.bot_controller.get_avatar_from_url(avatar_url, size=65, radius=65//2)
        self.user_banner_colour = self.images.get_majority_color_from_url(avatar_url)

        self._redraw_search_results()
        self._redraw_user_wrapper()

    def _draw_search_bar(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH)
        
        placeholder_text = "Search a Discord user ID..."
        
        def on_focus_in(event):
            if self.search_entry.get() == placeholder_text:
                self.search_entry.delete(0, ttk.END)
                self.search_entry.configure(foreground="white")
                
        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, placeholder_text)
                self.search_entry.configure(foreground="grey")
        
        self.search_entry = ttk.Entry(entry_wrapper, bootstyle="dark.TFrame", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.search_entry.grid(row=0, column=0, sticky=ttk.EW, padx=(18, 0), pady=10, columnspan=2, ipady=10)
        self.search_entry.configure(foreground="grey")
        self.search_entry.insert(0, placeholder_text)
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.search_entry.bind("<Return>", lambda e: self._search_user(self.search_entry.get()))
        
        search_button = ttk.Label(entry_wrapper, image=self.images.get("search"), style="dark.TButton")
        search_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 10), pady=10)
        search_button.bind("<Button-1>", lambda e: self._search_user(self.search_entry.get()))
        
        entry_wrapper.columnconfigure(1, weight=1)
        
        return entry_wrapper

    def _hover_reveal(self, container, widget):
        try:
            widget.pack_forget()
        except Exception:
            pass

        state = {"hide_job": None}

        def _is_pointer_inside():
            try:
                x_root = container.winfo_pointerx()
                y_root = container.winfo_pointery()
                w = container.winfo_containing(x_root, y_root)
            except Exception:
                return False

            while w is not None:
                if w == container:
                    return True
                w = getattr(w, "master", None)
            return False

        def _show(_event=None):
            if state["hide_job"] is not None:
                try:
                    container.after_cancel(state["hide_job"])
                except Exception:
                    pass
                state["hide_job"] = None
            if not widget.winfo_ismapped():
                widget.place(relx=1, rely=0.5, anchor="e", x=-1)  # Adjust the x offset as needed

        def _schedule_hide(_event=None):
            if state["hide_job"] is not None:
                try:
                    container.after_cancel(state["hide_job"])
                except Exception:
                    pass

            def _hide():
                state["hide_job"] = None
                if _is_pointer_inside():
                    return
                try:
                    widget.place_forget()
                except Exception:
                    pass

            state["hide_job"] = container.after(80, _hide)

        def _bind_recursive(w):
            try:
                w.bind("<Enter>", _show, add="+")
                w.bind("<Leave>", _schedule_hide, add="+")
            except Exception:
                pass
            for child in getattr(w, "winfo_children", lambda: [])():
                _bind_recursive(child)

        _bind_recursive(container)
        _bind_recursive(widget)

    def _redraw_search_results(self):
        if self.search_results_widget:
            self.search_results_widget.destroy()
        self.search_results_widget = self._draw_search_results(self.wrapper)
        self.search_results_widget.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)

    def _redraw_user_wrapper(self):
        if self.user_widget:
            self.user_widget.destroy()
        self.user_widget = self._draw_user_wrapper(self.wrapper)
        self.user_widget.pack(side=ttk.RIGHT, fill=ttk.Y, padx=(10, 0))

    def _draw_user_wrapper(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame", custom_size=True)
        wrapper.set_width(200)
        
        if self.user_avatar:
            accent_colour_banner = RoundedFrame(wrapper, radius=(15, 15, 0, 0), background=self.user_banner_colour, parent_background=self.root.style.colors.get("bg"))
            accent_colour_banner.set_height(85)
            accent_colour_banner.pack(side=ttk.TOP, fill=ttk.X)
            accent_colour_banner.columnconfigure(0, weight=1)
            
            avatar_label = ttk.Canvas(wrapper, width=100, height=200, background=self.user_banner_colour, highlightthickness=0)

            avatar_label.create_rectangle(0, 0, 100, 50, fill=self.user_banner_colour, outline="")
            avatar_label.create_rectangle(0, 50, 100, 200, fill=self.root.style.colors.get("dark"), outline="")
            
            # create an ovel the same size of the avatar but an extra 5px on each side and use the dark background color, this is to create a border
            avatar_label.create_oval(8, 8, 85, 85, fill=self.root.style.colors.get("dark"), outline="")
            avatar_label.create_image(65//2 + 15, 65//2 + 15, image=self.user_avatar, anchor="center")
            
            avatar_label.place(x=0, y=85-50, width=100, height=200)
            
        if self.user:
            user_info_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
            user_info_wrapper.pack(side=ttk.TOP, fill=ttk.X, pady=(35, 0), padx=(10, 10))
            user_info_wrapper.configure(height=50)
            
            # display_name = ttk.Label(user_info_wrapper, text=self.user.display_name, font=("Host Grotesk", 16 if sys.platform != "darwin" else 18, "bold"))
            # display_name.configure(background=self.root.style.colors.get("dark"))
            # display_name.place(relx=0, rely=0)
            
            display_name_col = ttk.Frame(user_info_wrapper, style="dark.TFrame")
            display_name_col.place(relx=0, rely=0)
            
            display_name = ttk.Label(display_name_col, text=self.user.display_name, font=("Host Grotesk", 16, "bold"))
            display_name.configure(background=self.root.style.colors.get("dark"))
            display_name.grid(row=0, column=0, sticky=ttk.W)
            
            if self.user.bot or self.is_friend:
                status_frame = RoundedFrame(display_name_col, radius=10, bootstyle="success.TFrame" if self.is_friend else "warning.TFrame")
                status_frame.grid(row=0, column=1, sticky=ttk.W, padx=(10, 0))
                
                status_label = ttk.Label(status_frame, text="Friend" if self.is_friend else "Bot", font=("Host Grotesk", 10))
                status_label.configure(background=self.root.style.colors.get("success") if self.is_friend else self.root.style.colors.get("warning"), foreground=self.root.style.colors.get("fg"))
                status_label.pack(padx=5, pady=1)
            
            username = ttk.Label(user_info_wrapper, text=f"{self.user.name}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
            username.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
            username.place(relx=0, rely=0.42 if sys.platform == "darwin" else 0.45)
            
            if self.mutual_guilds:
                mutual_guilds_subtitle = ttk.Label(wrapper, text="Mutual Guilds", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14, "bold"))
                mutual_guilds_subtitle.configure(background=self.root.style.colors.get("dark"), foreground="white")
                mutual_guilds_subtitle.pack(side=ttk.TOP, fill=ttk.X, padx=10)
                
                guilds_wrapper = ScrolledFrame(wrapper, bootstyle="dark.TFrame", autohide=True)
                guilds_wrapper.container.configure(style="dark.TFrame")
                guilds_wrapper.pack(side=ttk.TOP, fill=ttk.BOTH, pady=(3, 10), padx=(10, 10), expand=True)
                guilds_wrapper.columnconfigure(0, weight=1)
                
                row = 0
                for guild in self.mutual_guilds:
                    guild_frame = RoundedFrame(guilds_wrapper, radius=5, bootstyle="secondary.TFrame")
                    guild_frame.grid(row=row, column=0, sticky=ttk.EW, pady=(0, 5))
                    
                    guild_label = ttk.Label(guild_frame, text=guild.name, font=("Host Grotesk", 10 if sys.platform != "darwin" else 12))
                    guild_label.configure(background=self.root.style.colors.get("secondary"), foreground="white")
                    guild_label.grid(row=0, column=0, sticky=ttk.EW, padx=5, pady=5)
                    guild_frame.grid_columnconfigure(0, weight=1)
                    
                    row += 1
            else:
                mutual_guilds_subtitle = ttk.Label(wrapper, text="No Mutual Guilds", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
                mutual_guilds_subtitle.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
                mutual_guilds_subtitle.place(relx=.7, rely=0.65, relwidth=1, anchor="center")

        return wrapper

    def _draw_search_results(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        
        if not self.user:
            no_results_label = ttk.Label(wrapper, text="No user found. Please search for a valid Discord user ID.", font=("Host Grotesk", 12))
            no_results_label.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
            no_results_label.place(relx=.5, rely=.5, anchor="center")
        # elif self.user and self.mutual_guilds_member_objects:
        #     guilds_label = ttk.Label(wrapper, text="Mutual Guilds", font=("Host Grotesk", 14, "bold"))
        #     guilds_label.configure(background=self.root.style.colors.get("dark"), foreground="white")
        #     guilds_label.pack(side=ttk.TOP, fill=ttk.X, padx=10, pady=(10, 0))
            
        #     guilds_wrapper = ScrolledFrame(wrapper, bootstyle="dark.TFrame", autohide=True)
        #     guilds_wrapper.container.configure(style="dark.TFrame")
        #     guilds_wrapper.pack(side=ttk.TOP, fill=ttk.BOTH, pady=10, padx=10, expand=True)
        #     guilds_wrapper.container.columnconfigure(0, weight=1)
            
        #     for guild, member in self.mutual_guilds_member_objects:
        #         guild_frame = RoundedFrame(guilds_wrapper.container, radius=5, bootstyle="secondary.TFrame")
        #         guild_frame.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 5))
                
        #         guild_label = ttk.Label(guild_frame, text=guild.name, font=("Host Grotesk", 12, "bold"))
        #         guild_label.configure(background=self.root.style.colors.get("secondary"), foreground="white")
        #         guild_label.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=(5, 0))
                
        #         joined_at_label = ttk.Label(guild_frame, text=f"Joined at: {member.joined_at.strftime('%d/%m/%Y %H:%M:%S') if member.joined_at else 'Unknown'}", font=("Host Grotesk", 10))
        #         joined_at_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
        #         joined_at_label.pack(side=ttk.TOP, fill=ttk.X, padx=5)
                
        #         nickname_label = ttk.Label(guild_frame, text=f"Nickname: {member.nick if member.nick else 'None'}", font=("Host Grotesk", 10))
        #         nickname_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
        #         nickname_label.pack(side=ttk.TOP, fill=ttk.X, padx=5)
                
        #         roles_label = ttk.Label(guild_frame, text=f"Roles: {', '.join([role.name for role in member.roles[1:]]) if len(member.roles) > 1 else 'None'}", font=("Host Grotesk", 10))
        #         roles_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
        #         roles_label.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=(0, 5))
        
        else:
            scrolled_wrapper = ScrolledFrame(wrapper, bootstyle="dark.TFrame", autohide=True)
            scrolled_wrapper.container.configure(style="dark.TFrame")
            scrolled_wrapper.pack(side=ttk.TOP, fill=ttk.BOTH, pady=(10, 10), padx=(10, 10), expand=True)
            scrolled_wrapper.container.columnconfigure(0, weight=1)
            
            user_info = {
                "Display Name": self.user.display_name,
                "Username": self.user.name,
                "User ID": self.user.id,
                "Bot": self.user.bot,
                "Created At": self.created_at,
                "Mutual Guilds": len(self.mutual_guilds),
            }
            
            for key, value in user_info.items():
                info_frame = RoundedFrame(scrolled_wrapper.container, radius=5, bootstyle="secondary.TFrame")
                info_frame.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 5))
                
                key_label = ttk.Label(info_frame, text=f"{key}:", font=("Host Grotesk", 12, "bold"))
                key_label.configure(background=self.root.style.colors.get("secondary"), foreground="white")
                key_label.pack(side=ttk.LEFT, padx=(5, 0), pady=(5, 5))
                
                value_label = ttk.Label(info_frame, text=f"{value}", font=("Host Grotesk", 12))
                value_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
                value_label.pack(side=ttk.LEFT, padx=(5, 0), pady=(5, 5))
                
                copy_button = ttk.Label(info_frame, image=self.images.get("copy-tiny"), style="secondary.TButton")
                copy_button.bind("<Button-1>", lambda e, text=value: self.root.clipboard_clear() or self.root.clipboard_append(str(text)) or self.root.update())
                self._hover_reveal(info_frame, copy_button)
                
            # add two frames the same as above but for user avatar and avatar decoration. instead of showing the link add a button that opens it in the browser
            avatar_frame = RoundedFrame(scrolled_wrapper.container, radius=5, bootstyle="secondary.TFrame")
            avatar_frame.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 5))
            
            avatar_label = ttk.Label(avatar_frame, text="Avatar:", font=("Host Grotesk", 12, "bold"))
            avatar_label.configure(background=self.root.style.colors.get("secondary"), foreground="white")
            avatar_label.pack(side=ttk.LEFT, padx=(5, 0), pady=(5, 5))
            
            avatar_button = RoundedButton(avatar_frame, text="Open Avatar", command=lambda _: webbrowser.open(self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"), bootstyle="primary.TButton", radius=8, padx=2, pady=1, font=("Host Grotesk", 10))
            avatar_button.pack(side=ttk.LEFT, padx=(5, 0), pady=(5, 5))
            
            copy_avatar_button = ttk.Label(avatar_frame, image=self.images.get("copy-tiny"), style="secondary.TButton")
            copy_avatar_button.bind("<Button-1>", lambda e: self.root.clipboard_clear() or self.root.clipboard_append(str(self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png")) or self.root.update())
            self._hover_reveal(avatar_frame, copy_avatar_button)
        
        return wrapper

    def draw_content(self, wrapper):
        self.wrapper = wrapper
        search_bar = self._draw_search_bar(self.wrapper)
        search_bar.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 10))

        self.search_results_widget = self._draw_search_results(self.wrapper)
        self.search_results_widget.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)
        
        self.user_widget = self._draw_user_wrapper(self.wrapper)
        self.user_widget.pack(side=ttk.RIGHT, fill=ttk.Y, padx=(10, 0))