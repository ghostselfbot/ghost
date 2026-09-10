import abc
import os
import json
import time
import asyncio
import threading
import discord
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame

from gui.components import ToolPage, RoundedFrame, RoundedButton
from gui.helpers import Style
from utils.files import get_application_support, open_file_in_editor


class BackupsPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Backups", frame=None)
        self.images = images
        self.cfg = bot_controller.cfg
        self.backups_dir = os.path.join(get_application_support(), "backups")
        self.backup_list_frame = None
        self.status_label = None

    def _ensure_backups_dir(self):
        os.makedirs(self.backups_dir, exist_ok=True)

    def _get_backups(self):
        self._ensure_backups_dir()
        backups = []
        for f in os.listdir(self.backups_dir):
            if f.endswith(".json"):
                path = os.path.join(self.backups_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    stat = os.stat(path)
                    backups.append({
                        "name": f,
                        "path": path,
                        "type": data.get("type", f.replace(".json", "")),
                        "created_at": data.get("created_at"),
                        "size": stat.st_size,
                        "time": stat.st_mtime,
                        "data": data,
                    })
                except Exception:
                    pass
        backups.sort(key=lambda b: b["time"], reverse=True)
        return backups

    def _format_time(self, timestamp):
        if timestamp:
            return time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(timestamp))
        return "Unknown"

    def _set_status(self, text):
        if self.status_label:
            self.status_label.configure(text=text)

    def _run_async(self, coro):
        def _worker():
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(coro)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error: {e}"))
            finally:
                loop.close()
        threading.Thread(target=_worker, daemon=True).start()

    def _run_on_bot_loop(self, coro):
        loop = getattr(self.bot_controller, "loop", None)
        if loop and getattr(loop, "is_running", lambda: False)():
            future = asyncio.run_coroutine_threadsafe(coro, loop)

            def _done(f):
                try:
                    f.result()
                except Exception as e:
                    self.root.after(0, lambda: self._set_status(f"Error: {e}"))

            future.add_done_callback(_done)
            return

        self._run_async(coro)

    def _pick_account(self, backup_type, callback):
        bot = getattr(self.bot_controller, "bot", None)
        if not bot or not getattr(bot, "is_ready", lambda: False)():
            self._set_status("No bot connected. Start the bot first.")
            return
        callback(bot, self.cfg.get("token"))

    def _create_backup_account(self):
        self._pick_account("account", self._do_backup_account)

    def _do_backup_account(self, bot, token):
        self._set_status("Backing up account...")
        async def _do():
            try:
                user = bot.user
                data = {
                    "created_at": time.time(),
                    "type": "account",
                    "info": {
                        "id": user.id,
                        "name": user.name,
                        "display_name": user.display_name,
                        "accent_colour": str(user.accent_colour) if getattr(user, "accent_colour", None) else None,
                        "avatar": str(user.avatar.url) if getattr(user, "avatar", None) else None,
                        "banner": str(user.banner.url) if getattr(user, "banner", None) else None,
                        "bio": getattr(user, "bio", None) or None,
                    },
                }
                self._ensure_backups_dir()
                path = os.path.join(self.backups_dir, "account.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                self.root.after(0, lambda: self._set_status(f"Account backed up ({user.name})"))
                self.root.after(0, self._refresh_backup_list)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Failed: {e}"))
        self._run_async(_do())

    def _create_backup_friends(self):
        self._pick_account("friends", self._do_backup_friends)

    def _do_backup_friends(self, bot, token):
        self._set_status("Backing up friends...")
        async def _do():
            try:
                friends = []
                for relationship in bot.friends:
                    if relationship.type == discord.RelationshipType.friend:
                        friends.append({"username": relationship.user.name, "id": relationship.user.id})
                data = {
                    "created_at": time.time(),
                    "type": "friends",
                    "list": friends,
                }
                self._ensure_backups_dir()
                path = os.path.join(self.backups_dir, "friends.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                self.root.after(0, lambda: self._set_status(f"Friends backed up ({len(friends)} friends)"))
                self.root.after(0, self._refresh_backup_list)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Failed: {e}"))
        self._run_async(_do())

    def _create_backup_guilds(self):
        self._pick_account("guilds", self._do_backup_guilds)

    def _do_backup_guilds(self, bot, token):
        self._set_status("Backing up guilds...")
        async def _do():
            try:
                guilds = []
                for guild in bot.guilds:
                    try:
                        invite = getattr(guild, "vanity_url", None) if getattr(guild, "vanity_url", None) else None
                        if not invite:
                            me = getattr(guild, "me", None)
                            channels = getattr(guild, "channels", []) or []
                            for channel in channels:
                                if not isinstance(channel, discord.TextChannel):
                                    continue
                                try:
                                    perms_ok = bool(me) and channel.permissions_for(me).create_instant_invite
                                except Exception:
                                    perms_ok = False
                                if not perms_ok:
                                    continue
                                try:
                                    invite = await channel.create_invite(max_age=0, max_uses=1, unique=True)
                                except Exception:
                                    invite = None
                                if invite:
                                    break

                        guilds.append({
                            "name": getattr(guild, "name", "Unknown"),
                            "id": getattr(guild, "id", None),
                            "invite": str(invite) if invite else "None",
                        })
                    except Exception:
                        guilds.append({
                            "name": getattr(guild, "name", "Unknown"),
                            "id": getattr(guild, "id", None),
                            "invite": "None",
                        })
                    await asyncio.sleep(0.75)
                data = {
                    "created_at": time.time(),
                    "type": "guilds",
                    "list": guilds,
                }
                self._ensure_backups_dir()
                path = os.path.join(self.backups_dir, "guilds.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                self.root.after(0, lambda: self._set_status(f"Guilds backed up ({len(guilds)} servers)"))
                self.root.after(0, self._refresh_backup_list)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Failed: {e}"))
        self._run_on_bot_loop(_do())

    def _view_backup(self, backup_info):
        # data = backup_info["data"]
        # display = json.dumps(data, indent=2)
        # win = ttk.Toplevel(self.root)
        # win.title(f"Backup - {backup_info['name']}")
        # win.geometry("500x400")
        # win.configure(bg=self.root.style.colors.get("bg"))
        # text = ttk.ScrolledText(win, wrap=ttk.WORD, font=("Consolas", 10))
        # text.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)
        # text.insert("1.0", display)
        # text.configure(state="disabled")
        open_file_in_editor(backup_info["path"])

    def _restore_backup(self, backup_info):
        btype = backup_info["type"]
        if btype == "account":
            Messagebox.show_info("Account backups are for reference only.\nNo restore action needed.", title="Restore")
            return
        if btype == "friends":
            result = str(Messagebox.yesno(
                "This will send friend requests to all users in the backup.\n\n"
                "This could result in a ban. Continue?",
                title="Restore Friends"
            )).lower()
            if result != "yes":
                return
            self._pick_account("friends", lambda bot, token: self._do_restore_friends(backup_info, bot, token))
            return
        elif btype == "guilds":
            invites = [g["invite"] for g in backup_info["data"].get("list", []) if g.get("invite") and g["invite"] != "None"]
            if not invites:
                Messagebox.show_info("No invite links found in this backup.", title="Restore Guilds")
                return
            msg = "Join these servers manually:\n\n" + "\n".join(invites)
            win = ttk.Toplevel(self.root)
            win.title("Guild Invites")
            win.geometry("500x350")
            win.configure(bg=self.root.style.colors.get("bg"))
            text = ttk.ScrolledText(win, wrap=ttk.WORD, font=("Consolas", 10))
            text.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)
            text.insert("1.0", msg)
            text.configure(state="disabled")

    def _do_restore_friends(self, backup_info, bot, token):
        self._set_status("Restoring friends...")
        async def _do():
            try:
                import requests as _req
                if not token:
                    self.root.after(0, lambda: self._set_status("Failed: No token configured"))
                    return
                headers = {
                    "Authorization": token,
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                restored = 0
                for entry in backup_info["data"].get("list", []):
                    try:
                        user_resp = _req.get(f"https://discord.com/api/v9/users/{entry['id']}", headers=headers)
                        if user_resp.status_code == 200:
                            user = discord.User(state=bot._connection, data=user_resp.json())
                            user.send_friend_request()
                            restored += 1
                        await asyncio.sleep(1)
                    except Exception:
                        pass
                self.root.after(0, lambda: self._set_status(f"Restored {restored} friend requests"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Failed: {e}"))
        self._run_async(_do())

    def _delete_backup(self, backup_info):
        # result = str(Messagebox.yesno(
        #     f"Delete backup '{backup_info['name']}'?",
        #     title="Delete Backup"
        # )).lower()
        # if result != "yes":
        #     return
        try:
            os.remove(backup_info["path"])
            self._set_status(f"Deleted: {backup_info['name']}")
            self._refresh_backup_list()
        except Exception as e:
            self._set_status(f"Delete failed: {e}")

    def _refresh_backup_list(self):
        if not self.backup_list_frame:
            return
        for child in self.backup_list_frame.winfo_children():
            child.destroy()
        self._draw_backup_entries()

    def _draw_backup_entries(self):
        backups = self._get_backups()
        if not backups:
            empty = ttk.Label(self.backup_list_frame, text="No backups yet. Create one above.", font=("Host Grotesk", 11))
            empty.configure(background=self.root.style.colors.get("secondary"), foreground=Style.DARK_GREY.value)
            empty.pack(pady=20)
            return

        type_colors = {"account": "#5865f2", "friends": "#4fee4c", "guilds": "#fee75c"}
        for backup in backups:
            card = RoundedFrame(self.backup_list_frame, radius=(8, 8, 8, 8), background=Style.SETTINGS_PILL_HOVER.value, parent_background=self.root.style.colors.get("secondary"))
            card.pack(fill=ttk.X, pady=(0, 5))

            inner = RoundedFrame(card, radius=0, background=Style.SETTINGS_PILL_HOVER.value, parent_background=Style.SETTINGS_PILL_HOVER.value)
            inner.pack(fill=ttk.BOTH, padx=12, pady=8)

            name_frame = RoundedFrame(inner, radius=0, background=Style.SETTINGS_PILL_HOVER.value, parent_background=Style.SETTINGS_PILL_HOVER.value)
            name_frame.grid(row=0, column=0, sticky=ttk.W)

            btype = backup.get("type", "unknown")
            color = type_colors.get(btype, Style.LIGHT_GREY.value)
            type_label = ttk.Label(name_frame, text=btype.upper(), font=("Host Grotesk", 12, "bold"), foreground=color)
            type_label.configure(background=Style.SETTINGS_PILL_HOVER.value)
            type_label.pack(side=ttk.LEFT, padx=(0, 5))

            # name_label = ttk.Label(name_frame, text=backup["name"], font=("Host Grotesk", 11, "bold"))
            # name_label.configure(background=Style.SETTINGS_PILL_HOVER.value)
            # name_label.pack(side=ttk.LEFT)

            info_text = self._format_time(backup["created_at"])
            info_label = ttk.Label(inner, text=f"Last updated {info_text}", font=("Host Grotesk", 10))
            info_label.configure(background=Style.SETTINGS_PILL_HOVER.value, foreground=Style.LIGHT_GREY.value)
            info_label.grid(row=1, column=0, sticky=ttk.W)

            btn_frame = RoundedFrame(inner, radius=0, background=Style.SETTINGS_PILL_HOVER.value, parent_background=Style.SETTINGS_PILL_HOVER.value)
            btn_frame.grid(row=0, column=1, rowspan=2, sticky=ttk.E)

            view_btn = RoundedButton(btn_frame, text="View", bootstyle="primary.TButton", command=lambda e, b=backup: self._view_backup(b), padx=1, pady=1, font=("Host Grotesk", 10))
            view_btn.pack(side=ttk.LEFT, padx=(0, 5))

            # restore_btn = RoundedButton(btn_frame, text="Restore", bootstyle="success.TButton", command=lambda e, b=backup: self._restore_backup(b), padx=2, pady=1, font=("Host Grotesk", 10))
            # restore_btn.pack(side=ttk.LEFT, padx=(0, 10))

            delete_btn = RoundedButton(btn_frame, text="Delete", bootstyle="danger.TButton", command=lambda e, b=backup: self._delete_backup(b), padx=1, pady=1, font=("Host Grotesk", 10))
            delete_btn.pack(side=ttk.LEFT)

            inner.grid_columnconfigure(0, weight=1)

    @abc.abstractmethod
    def draw_content(self, main_wrapper):
        wrapper = RoundedFrame(main_wrapper, radius=15, bootstyle="dark.TFrame")
        wrapper.pack(fill=ttk.BOTH, expand=True)
        
        inner_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
        inner_wrapper.pack(fill=ttk.BOTH, expand=True, padx=20, pady=20)
        
        create_wrapper = RoundedFrame(inner_wrapper, radius=10, bootstyle="secondary.TFrame")
        create_wrapper.pack(fill=ttk.X, pady=(0, 10))
        create_wrapper.grid_columnconfigure(0, weight=1)
        
        create_label = ttk.Label(create_wrapper, text="Create Backup", font=("Host Grotesk", 16, "bold"))
        create_label.configure(background=self.root.style.colors.get("secondary"))
        create_label.grid(row=0, column=0, sticky=ttk.W, pady=10, padx=(10, 0))

        btn_row = ttk.Frame(create_wrapper, style="secondary.TFrame")
        btn_row.grid(row=0, column=1, sticky=ttk.W, pady=10, padx=(0, 5))

        for text, cmd in [("Account", self._create_backup_account), ("Friends", self._create_backup_friends), ("Guilds", self._create_backup_guilds)]:
            btn = RoundedButton(btn_row, text=text, bootstyle="primary.TButton", command=lambda e, c=cmd: c(), font=("Host Grotesk", 12))
            btn.pack(side=ttk.LEFT, padx=(0, 5))

        backups_wrapper = RoundedFrame(inner_wrapper, radius=10, bootstyle="secondary.TFrame")
        backups_wrapper.pack(fill=ttk.BOTH, expand=True)

        backups_label = ttk.Label(backups_wrapper, text="Available Backups", font=("Host Grotesk", 16, "bold"))
        backups_label.configure(background=self.root.style.colors.get("secondary"))
        # backups_label.pack(anchor=ttk.W, pady=(10, 5), padx=10)
        backups_label.grid(row=0, column=0, sticky=ttk.W, pady=(10, 5), padx=(10, 0))
        
        self.status_label = ttk.Label(backups_wrapper, text="", font=("Host Grotesk", 10))
        self.status_label.configure(background=self.root.style.colors.get("secondary"), foreground=Style.LIGHT_GREY.value)
        self.status_label.grid(row=0, column=1, sticky=ttk.E, padx=(0, 10), pady=(10, 5))

        self.backup_list_frame = ScrolledFrame(backups_wrapper, bootstyle="secondary.TFrame", autohide=True)
        self.backup_list_frame.container.configure(style="secondary.TFrame")
        # self.backup_list_frame.pack(fill=ttk.BOTH, expand=True, padx=10)
        self.backup_list_frame.grid(row=1, column=0, sticky=ttk.NSEW, padx=10, pady=(5, 10), columnspan=2)
        backups_wrapper.grid_columnconfigure(0, weight=1)
        backups_wrapper.grid_rowconfigure(1, weight=1)

        self._draw_backup_entries()
