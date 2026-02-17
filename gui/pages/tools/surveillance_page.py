import sys, time
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from gui.components import ToolPage, RoundedFrame, RoundedButton
from utils.console import get_formatted_time
from gui.helpers.style import Style

class SurveillancePage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Surveillance", frame=None)
        self.wrapper = None
        self.search_entry = None  # Initialize search entry to None
        self.user_id = None
        self.user = None
        self.user_avatar = None
        self.user_wrapper = None
        self.mutual_guilds = []
        self.surveillance = self.bot_controller.surveillance
        self.log_wrapper = None
        self.search_placeholder_text = "Search a Discord user ID..."
        self.console = []
        self.textarea = None
        self.avatar = None
        self.darwin_font_size = 12
        self.non_darwin_font_size = 10
        self.reset_button_disabled = False
        self.messages_textarea = None
        self.messages_textarea_updating = False
        self.messages_formatted = []
        self.current_search = ""
        self.messages_all = []
        self.messages_displayed = []
        self.total_messages = 0
        self.user_total_messages = 0
        self.focused_textarea = None
        
    def _set_focused_textarea(self, widget):
        self.focused_textarea = widget

    def _redraw_user_wrapper(self):
        if self.user_wrapper:
            self.user_wrapper.destroy()
        self.user_wrapper = self._draw_user_wrapper(self.user_progress_wrapper)
        self.user_wrapper.pack(side=ttk.BOTTOM, fill=ttk.BOTH, expand=True)
        self.user_wrapper.set_width(200)

    def _check_mutual_guilds(self):
        if not self.mutual_guilds:
            self.root.after(100, lambda: self._check_mutual_guilds())
        else:
            self.add_log("info", f"Found {len(self.mutual_guilds)} mutual guilds for user ID: {self.user_id}")
            self._redraw_user_wrapper()

    def _get_user(self, user_id):
        if user_id is None or not user_id.isdigit():
            self.add_log("error", "Invalid user ID. Please enter a valid Discord user ID.")
            return
        
        if user_id == self.user_id or self.surveillance.member_id == user_id:
            self.add_log("info", "You are already viewing this user.")
            return
        else:
            self.add_log("warning", f"Switching to user ID: {user_id}")
            self._reset_surveillance()
        
        self.user_id = user_id
        self.surveillance.set_member_id(user_id)
        user = self.bot_controller.get_user_from_id(int(user_id))
        self.user = user
        
        avatar_url = self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
        print(avatar_url)
        self.user_avatar = self.bot_controller.get_avatar_from_url(avatar_url, size=65, radius=65//2)
        self.user_banner_colour = self.images.get_majority_color_from_url(avatar_url)
        
        self._check_mutual_guilds()
        self._redraw_user_wrapper()

    def _search(self):
        pass
                
    def _configure_start_stop_button(self, running):
        try:
            if running:
                self.start_stop_button.configure(image=self.images.get("stop"), bootstyle="danger")
            else:
                self.start_stop_button.configure(image=self.images.get("play"), bootstyle="primary")
        except Exception as e:
            print(f"Error configuring start/stop button: {e}")
                
    def _check_surveillance_running(self):
        if self.surveillance.running:
            self.search_placeholder_text = "Search for a message..."
            self.messages_textarea_updating = True
            self.root.after(50, lambda: self._disable_reset_button())
            self.root.after(50, lambda: self._configure_start_stop_button(True))

            if not self.search_button.winfo_ismapped():
                self.search_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 10), pady=10)
        else:
            self.search_placeholder_text = "Search a Discord user ID..."
            self.messages_textarea_updating = False
            self.root.after(50, lambda: self._enable_reset_button())
            self.root.after(50, lambda: self._configure_start_stop_button(False))

            if self.search_button.winfo_ismapped():
                self.search_button.grid_forget()
        
        if not self.surveillance.running and len(self.messages_all) > 0:
            self.search_placeholder_text = "Search for a message..."
            if not self.search_button.winfo_ismapped():
                self.search_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 10), pady=10)
        # elif self.surveillance.running and len(self.messages_all) > 0:
        #     self.search_placeholder_text = "Search for a message..."
                
        try:
            self.search_entry.configure(foreground="grey")
            self.search_var.set("")
            self.search_entry.delete(0, ttk.END)
            self.search_entry.insert(0, self.search_placeholder_text)
        except Exception as e:
            print(f"Error resetting search entry: {e}")
            
    def _disable_reset_button(self):
        self.reset_button_disabled = True
        try:
            if hasattr(self, 'reset_button_wrapper') and self.reset_button_wrapper:
                self.reset_button_wrapper.set_background(background=self.root.style.colors.get("dark"))
            if hasattr(self, 'reset_button') and self.reset_button:
                self.reset_button.configure(background=self.root.style.colors.get("dark"))
        except Exception as e:
            print(f"Error disabling reset button: {e}")

    def _enable_reset_button(self):
        self.reset_button_disabled = False
        try:
            if hasattr(self, 'reset_button_wrapper') and self.reset_button_wrapper:
                self.reset_button_wrapper.set_background(background=self.root.style.colors.get("danger"))
            if hasattr(self, 'reset_button') and self.reset_button:
                self.reset_button.configure(background=self.root.style.colors.get("danger"))
        except Exception as e:
            print(f"Error enabling reset button: {e}")
                
    def _toggle_surveillance(self):
        search_text = self.search_entry.get().strip()
        
        if not self.surveillance.running:
            if self.user and int(self.user.id) == int(self.surveillance.member_id):
                self.bot_controller.start_surveillance()
            elif not search_text or search_text == self.search_placeholder_text:
                self.add_log("error", "Please enter a valid Discord user ID to start Surveillance.")
                return
            else:
                self._get_user(search_text)
                if not self.user:
                    self.add_log("error", "Failed to fetch user. Please check the user ID.")
                    return
                
                self.bot_controller.start_surveillance()
                self.add_log("info", f"Surveillance started for user ID: {self.user_id}")
                
            self.messages_textarea_updating = True
            self.root.after(50, lambda: self.update_messages())
        else:
            self.bot_controller.stop_surveillance()
            self.add_log("info", "Surveillance stopped.")
            
        self._check_surveillance_running()

    def _reset_surveillance(self):
        if self.surveillance.running:
            self.add_log("warning", "You cannot reset Surveillance while it is running. Please stop it first.")
            return
        print("Resetting Surveillance...")
        self.clear()
        self.surveillance.reset()
        self.user_id = None
        self.user = None
        self.user_avatar = None
        self.mutual_guilds = []
        self._redraw_user_wrapper()
        self.clear_messages()
        self._check_surveillance_running()
        self._update_progress_labels(0, 0)
        
        self.root.after(150, self._disable_reset_button)

    def _draw_start_stop_button(self, parent):
        def _hover_enter(_):
            wrapper.set_background(background=Style.PRIMARY_BTN_HOVER.value if not self.surveillance.running else "#de2d1b")
            self.start_stop_button.configure(background=Style.PRIMARY_BTN_HOVER.value if not self.surveillance.running else "#de2d1b")
            
        def _hover_leave(_):
            wrapper.set_background(background=self.root.style.colors.get("primary") if not self.surveillance.running else self.root.style.colors.get("danger"))
            self.start_stop_button.configure(background=self.root.style.colors.get("primary") if not self.surveillance.running else self.root.style.colors.get("danger"))
        
        wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), bootstyle="primary" if not self.surveillance.running else "danger")
        wrapper.bind("<Enter>", _hover_enter)
        wrapper.bind("<Leave>", _hover_leave)
        wrapper.bind("<Button-1>", lambda e: self._toggle_surveillance())
        
        self.start_stop_button = ttk.Label(wrapper, image=self.images.get("play"), style="primary")
        self.start_stop_button.configure(background=self.root.style.colors.get("primary"))
        self.start_stop_button.pack(side=ttk.LEFT, padx=15, pady=14)
        self.start_stop_button.bind("<Button-1>", lambda e: self._toggle_surveillance())
        self.start_stop_button.bind("<Enter>", _hover_enter)
        self.start_stop_button.bind("<Leave>", _hover_leave)
        
        return wrapper

    def _draw_reset_button(self, parent):
        def _reset(_):
            if not self.reset_button_disabled:
                self._reset_surveillance()
        
        def _hover_enter(_):
            self.reset_button_wrapper.set_background(background="#de2d1b" if not self.reset_button_disabled else self.root.style.colors.get("dark"))
            self.reset_button.configure(background="#de2d1b" if not self.reset_button_disabled else self.root.style.colors.get("dark"))
            
        def _hover_leave(_):
            self.reset_button_wrapper.set_background(background=self.root.style.colors.get("danger") if not self.reset_button_disabled else self.root.style.colors.get("dark"))
            self.reset_button.configure(background=self.root.style.colors.get("danger") if not self.reset_button_disabled else self.root.style.colors.get("dark"))
        
        self.reset_button_wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), bootstyle="danger" if not self.reset_button_disabled else "dark")
        self.reset_button_wrapper.bind("<Button-1>", _reset)
        self.reset_button_wrapper.bind("<Enter>", _hover_enter)
        self.reset_button_wrapper.bind("<Leave>", _hover_leave)
        
        self.reset_button = ttk.Label(self.reset_button_wrapper, image=self.images.get("reset"), style="danger" if not self.reset_button_disabled else "dark")
        self.reset_button.configure(background=self.root.style.colors.get("danger") if not self.reset_button_disabled else self.root.style.colors.get("dark"))
        self.reset_button.pack(side=ttk.LEFT, padx=15, pady=14)
        self.reset_button.bind("<Button-1>", _reset)
        self.reset_button.bind("<Enter>", _hover_enter)
        self.reset_button.bind("<Leave>", _hover_leave)
        
        return self.reset_button_wrapper

    def _draw_search_bar(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")

        def on_focus_in(event):
            if self.search_entry.get() == self.search_placeholder_text:
                self.search_entry.delete(0, ttk.END)
                self.search_entry.configure(foreground="white")

        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, self.search_placeholder_text)
                self.search_entry.configure(foreground="grey")

        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_change())

        self.search_entry = ttk.Entry(
            entry_wrapper,
            bootstyle="dark.TFrame",
            textvariable=self.search_var,
            font=("Host Grotesk", 12)
        )
        self.search_entry.grid(row=0, column=0, sticky=ttk.EW, padx=(18, 0), pady=10, columnspan=2, ipady=10)

        self.search_entry.insert(0, self.search_placeholder_text)
        self.search_entry.configure(foreground="grey")
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)

        self.search_button = ttk.Label(entry_wrapper, image=self.images.get("search"), style="dark.TButton")
        self.search_button.bind("<Button-1>", lambda e: self._on_search_change())

        entry_wrapper.columnconfigure(1, weight=1)
        return entry_wrapper

    def _draw_header(self, parent):
        header = ttk.Frame(parent)
        
        search_bar = self._draw_search_bar(header)
        search_bar.grid(row=0, column=0, sticky=ttk.EW, padx=(0, 5))
        
        start_stop_button = self._draw_start_stop_button(header)
        start_stop_button.grid(row=0, column=1, sticky=ttk.E)
        
        reset_button = self._draw_reset_button(header)
        reset_button.grid(row=0, column=2, sticky=ttk.E, padx=(5, 0))
        
        header.grid_columnconfigure(0, weight=1)
        
        return header

    def update(self):
        try:
            self.textarea.delete("1.0", "end")
            
            for time, prefix, text in self.console:
                # self.textarea.insert("end", f"[{time}] ", "timestamp")
                self.textarea.insert("end", f"[{prefix}] ", f"prefix_{prefix.lower()}")
                self.textarea.insert("end", f"{text}\n", "log_text")
            
            self.textarea.yview_moveto(1)
        except:
            print("Surveillance console tried to update without being drawn.")
            
    def clear(self):
        self.console = []
        try:
            self.textarea.delete("1.0", "end")
        except:
            print("Surveillance console tried to clear without being drawn.")

    def add_log(self, prefix, text):
        time = get_formatted_time()
        self.console.append((time, str(prefix).upper(), text))
        self.update()

    def _load_tags(self):
        self.textarea.tag_config("timestamp", foreground=Style.DARK_GREY.value, font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("log_text",  foreground=Style.LIGHT_GREY.value, font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        
        self.textarea.tag_config("prefix_sniper",  foreground="red",     font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("sniper_key",     foreground="#eceb18", font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_command", foreground="#0b91ff", font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_info",    foreground="#2aefef", font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_success", foreground="#4fee4c", font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_warning", foreground="#eceb18", font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_error",   foreground="red",     font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_cli",     foreground="pink",    font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))
        self.textarea.tag_config("prefix_rpc",     foreground="pink",    font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size))

    def _draw_log_wrapper(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame", custom_size=True)
        
        self.textarea = ttk.Text(wrapper, wrap="word", height=20,
            font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size)
        )
        self.textarea.config(
            border=0,
            background=self.root.style.colors.get("dark"),
            foreground=Style.LIGHT_GREY.value,
            highlightcolor=self.root.style.colors.get("dark"),
            highlightbackground=self.root.style.colors.get("dark"),
            state="normal"
        )

        self.textarea.pack(fill="both", expand=True, padx=5, pady=5)
        self._load_tags()
        
        return wrapper

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
            avatar_label.create_oval(9, 8, 85, 85, fill=self.root.style.colors.get("dark"), outline="")
            avatar_label.create_image(65//2 + 15, 65//2 + 15, image=self.user_avatar, anchor="center")
            
            avatar_label.place(x=0, y=85-50, width=100, height=200)
            
        if self.user:
            user_info_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
            user_info_wrapper.pack(side=ttk.TOP, fill=ttk.X, pady=(35, 0), padx=(10, 10))
            user_info_wrapper.configure(height=50)
            
            display_name = ttk.Label(user_info_wrapper, text=self.user.display_name, font=("Host Grotesk", 16 if sys.platform != "darwin" else 18, "bold"))
            display_name.configure(background=self.root.style.colors.get("dark"))
            display_name.place(relx=0, rely=0)
            
            username = ttk.Label(user_info_wrapper, text=f"{self.user.name}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
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
                mutual_guilds_subtitle = ttk.Label(wrapper, text="No Mutual Guilds", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
                mutual_guilds_subtitle.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
                mutual_guilds_subtitle.place(relx=.7, rely=0.65, relwidth=1, anchor="center")
        
        return wrapper

    def clear_messages(self):
        if self.messages_textarea:
            self.messages_textarea.delete("1.0", "end")
            self.messages_formatted = []
            self.messages_all = []
            self.messages_displayed = []
            self.current_search = ""
            self.messages_textarea_updating = False

            # Reset placeholder for search bar
            # self.search_placeholder_text = "Search a Discord user ID..." if not self.surveillance.running else "Search for a message..."
            # if self.search_entry:
            #     self.search_entry.configure(foreground="grey")
            #     self.search_var.set("")  # Resets the actual entry content
            #     self.search_entry.delete(0, ttk.END)
            #     self.search_entry.insert(0, self.search_placeholder_text)

            print("Messages fully cleared.")
        else:
            print("Messages textarea not found. Cannot clear messages.")
            
    def _on_search_change(self):
        query = self.search_var.get().strip()

        if query == self.search_placeholder_text or query == "":
            self.current_search = ""
        else:
            self.current_search = query.lower()

        self._apply_message_filter()

    def _apply_message_filter(self):
        if not self.messages_textarea or len(self.messages_all) == 0:
            return

        try:
            self.messages_textarea.delete("1.0", "end")
            self.messages_displayed = []

            for msg in self.messages_all:
                formatted = f"[{msg[0]}] [{msg[1]}] [{msg[2]}]: {msg[3]}"
                if not self.current_search or self.current_search in formatted.lower():
                    self.messages_displayed.append(msg)
                    self.messages_textarea.insert("end", f"{formatted}\n")

            self.messages_textarea.update_idletasks()
        except:
            pass
    
    def update_messages(self):
        if self.messages_textarea_updating and self.messages_textarea:
            try:
                data = self.surveillance.data
                current_yview = self.messages_textarea.yview()
                at_bottom = current_yview[1] >= 0.999

                new_msgs = []

                for guild, channels in data.items():
                    for channel, channel_data in channels.items():
                        for message in channel_data.get("messages", []):
                            timestamp = message.get("timestamp", None)
                            try:
                                ts = time.strftime("%d/%m/%Y %H:%M:%S", time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")) if timestamp else "Unknown"
                            except:
                                ts = timestamp
                            content = message.get("content", "")
                            msg = (ts, guild, channel, content)

                            if msg not in self.messages_all:
                                self.messages_all.append(msg)
                                new_msgs.append(msg)

                for msg in new_msgs:
                    formatted = f"[{msg[0]}] [{msg[1]}] [{msg[2]}]: {msg[3]}"
                    if self.current_search.lower() in formatted.lower():
                        self.messages_displayed.append(msg)
                        self.messages_textarea.insert("end", f"{formatted}\n")

                if at_bottom:
                    self.messages_textarea.see("end")
                else:
                    self.messages_textarea.yview_moveto(current_yview[0])

                self.messages_textarea.update_idletasks()
            except Exception as e:
                pass

            self.root.after(500, self.update_messages)

    def _draw_messages_wrapper(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame", custom_size=True)
        
        self.messages_textarea = ttk.Text(wrapper, wrap="word", height=20,
            font=("JetBrainsMono NF Bold", self.non_darwin_font_size if sys.platform != "darwin" else self.darwin_font_size)
        )
        self.messages_textarea.config(
            border=0,
            background=self.root.style.colors.get("dark"),
            foreground=Style.LIGHT_GREY.value,
            highlightcolor=self.root.style.colors.get("dark"),
            highlightbackground=self.root.style.colors.get("dark"),
            state="normal"
        )

        self.messages_textarea.pack(fill="both", expand=True, padx=5, pady=5)
        
        return wrapper
    
    def _update_progress_labels(self, total, user_total):
        if self.total_messages_label:
            self.total_messages = total
            self.total_messages_label.configure(text=f"Total: {total}")
        if self.total_user_messages_label:
            self.user_total_messages = user_total
            self.total_user_messages_label.configure(text=f"Sent by user: {user_total}")

    def _draw_progress_wrapper(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame", custom_size=True)
        
        self.total_messages_label = ttk.Label(wrapper, text="Total: 0", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.total_messages_label.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
        self.total_messages_label.place(relx=0.05, rely=0.13, relwidth=1, anchor="nw")
        
        self.total_user_messages_label = ttk.Label(wrapper, text="Sent by user: 0", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.total_user_messages_label.configure(background=self.root.style.colors.get("dark"), foreground=Style.LIGHT_GREY.value)
        self.total_user_messages_label.place(relx=0.05, rely=0.43 if sys.platform == "darwin" else 0.45, relwidth=1, anchor="nw")
        
        return wrapper

    def draw_content(self, wrapper):
        self.wrapper = wrapper
        
        header = self._draw_header(wrapper)
        header.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 10))

        self.msgs_logs_wrapper = ttk.Frame(wrapper)
        self.msgs_logs_wrapper.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True, padx=(0, 5))
        self.msgs_logs_wrapper.columnconfigure(0, weight=1)
        self.msgs_logs_wrapper.rowconfigure(0, weight=1)
        self.msgs_logs_wrapper.rowconfigure(1, weight=0)

        self.messages_wrapper = self._draw_messages_wrapper(self.msgs_logs_wrapper)
        self.messages_wrapper.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.log_wrapper = self._draw_log_wrapper(self.msgs_logs_wrapper)
        self.log_wrapper.set_height(150)
        self.log_wrapper.grid(row=1, column=0, sticky="ew")

        self.user_progress_wrapper = ttk.Frame(wrapper)
        self.user_progress_wrapper.pack(side=ttk.RIGHT, fill=ttk.Y, expand=False, padx=(5, 0))
        
        self.progress_wrapper = self._draw_progress_wrapper(self.user_progress_wrapper)
        self.progress_wrapper.set_height(55)
        self.progress_wrapper.set_width(200)  # fixed width
        self.progress_wrapper.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 10))

        self.user_wrapper = self._draw_user_wrapper(self.user_progress_wrapper)
        self.user_wrapper.set_width(200)  # fixed width
        self.user_wrapper.pack(side=ttk.BOTTOM, fill=ttk.BOTH, expand=True)
        
        self.update()
        
        if self.surveillance.running or len(self.messages_all) > 0:
            print("Surveillance is running, updating messages...")
            self._check_surveillance_running()
            self._update_progress_labels(self.surveillance.total_messages, self.surveillance.user_total_messages)
            
        if self._disable_reset_button:
            self._disable_reset_button()
        else:
            self._enable_reset_button()

        self.messages_textarea.bind("<Button-1>", lambda e: self._set_focused_textarea(self.messages_textarea))
        self.messages_textarea.bind("<FocusIn>", lambda e: self.textarea.tag_remove("sel", "1.0", "end"))

        self.textarea.bind("<Button-1>", lambda e: self._set_focused_textarea(self.textarea))
        self.textarea.bind("<FocusIn>", lambda e: self.messages_textarea.tag_remove("sel", "1.0", "end"))

        self.root.bind_all("<Command-c>", lambda e: self.focused_textarea.event_generate("<<Copy>>") if self.focused_textarea else None)