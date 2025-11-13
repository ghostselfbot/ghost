import sys
import time
import math
import ttkbootstrap as ttk
import discord

from gui.components import RoundedFrame
import tkinter.font as tkFont

class MessageLogEntry:
    def __init__(self, parent, root, bot_controller, avatars, log_entry):
        self.parent = parent
        self.root = root
        self.bot_controller = bot_controller
        self.avatars = avatars
        self.author, self.message, self.delete_time = log_entry

        self.frame = None
        self.content_label = None
        self.selected = False

        self._draw()

    def _autoresize_text(self, text_widget):
        px_width = text_widget.winfo_width()
        if px_width <= 1:
            text_widget.after(50, lambda: self._autoresize_text(text_widget))
            return

        font = tkFont.Font(font=("Host Grotesk", 10 if sys.platform != "darwin" else 12))
        char_width = font.measure("0")
        max_chars = max(1, px_width // char_width) + 15
        text = text_widget.get("1.0", "end-1c")

        lines = text.split("\n")
        total_lines = 0
        for line in lines:
            total_lines += math.ceil(len(line) / max_chars) or 1

        text_widget.configure(height=total_lines)

    def _draw(self):
        try:
            # Outer frame
            self.frame = RoundedFrame(
                self.parent,
                radius=(8, 8, 8, 8),
                bootstyle="secondary.TFrame",
                parent_background=self.root.style.colors.get("dark")
            )
            self.frame.pack(fill=ttk.X, pady=(0, 8), padx=(0, 8), expand=True)

            # Inner content
            content_frame = ttk.Frame(self.frame, style="secondary.TFrame")
            content_frame.pack(fill=ttk.BOTH, expand=True, padx=(12, 20), pady=10)

            # Author line
            author_frame = ttk.Frame(content_frame, style="secondary.TFrame")
            author_frame.pack(fill=ttk.X, pady=(0, 8))

            # Avatar
            if self.author.avatar:
                if self.author.id not in self.avatars:
                    try:
                        self.avatars[self.author.id] = self.bot_controller.get_avatar_from_url(
                            str(self.author.avatar.url), size=28, radius=14
                        )
                    except Exception:
                        self.avatars[self.author.id] = None

                if self.avatars[self.author.id]:
                    avatar_label = ttk.Label(author_frame, image=self.avatars[self.author.id])
                    avatar_label.configure(background=self.root.style.colors.get("secondary"))
                    avatar_label.pack(side=ttk.LEFT, padx=(0, 5))

            # Author name
            author_label = ttk.Label(
                author_frame,
                text=self.author.display_name,
                font=("Host Grotesk", 12 if sys.platform != "darwin" else 14, "bold")
            )
            author_label.configure(background=self.root.style.colors.get("secondary"), foreground="white")
            author_label.pack(side=ttk.LEFT)

            # Time
            formatted_time = time.strftime("%H:%M:%S", time.localtime(self.delete_time))
            time_label = ttk.Label(
                author_frame,
                text=formatted_time,
                font=("Host Grotesk", 8 if sys.platform != "darwin" else 10)
            )
            time_label.configure(background=self.root.style.colors.get("secondary"), foreground="lightgrey")
            time_label.pack(side=ttk.LEFT, padx=(5, 0), pady=(2, 0))

            # Channel info
            channel_label_text = (
                f"Deleted in DMs"
                if isinstance(self.message.channel, discord.DMChannel)
                else f"Deleted in {self.message.guild.name} > #{self.message.channel.name}"
            )
            channel_label = ttk.Label(
                content_frame,
                text=channel_label_text,
                font=("Host Grotesk", 8 if sys.platform != "darwin" else 10, "italic")
            )
            channel_label.configure(background=self.root.style.colors.get("secondary"), foreground="lightgrey")
            channel_label.pack(fill=ttk.X, pady=(0, 8))

            self.content_label = ttk.Text(content_frame, font=("Host Grotesk", 10 if sys.platform != "darwin" else 12), wrap="word", state="normal")
            self.content_label.insert("1.0", self.message.content or "[No text content]")
            self.content_label.configure(
                background=self.root.style.colors.get("secondary"),
                foreground="white" if self.message.content else "grey",
                border=False,
                borderwidth=0,
                highlightthickness=0
            )
            
            self.content_label.pack(fill=ttk.X)
            
            self.root.after(100, lambda: self._autoresize_text(self.content_label))
            self.content_label.bind("<Configure>", lambda e: self._autoresize_text(self.content_label))
            self.content_label.bind_all(
                "<Control-c>" if sys.platform != "darwin" else "<Command-c>", 
                lambda _: self.content_label.event_generate("<<Copy>>")
            )

            # Attachments
            if self.message.attachments:
                attachments_label = ttk.Label(
                    content_frame,
                    text=f"📎 {len(self.message.attachments)} attachment(s)",
                    font=("Host Grotesk", 9, "italic")
                )
                attachments_label.configure(background=self.root.style.colors.get("secondary"), foreground="lightgrey")
                attachments_label.pack(fill=ttk.X, pady=(4, 0))

            self.frame.bind("<Button-1>", self.on_click)

        except Exception as e:
            print(f"Error displaying log: {e}")

    def on_click(self, event):
        pass