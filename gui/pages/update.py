from io import BytesIO
import re
import threading
import webbrowser

import requests
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from gui.components import RoundedFrame, RoundedButton, RoundedProgressbar
from gui.helpers import Style

class UpdatePage:
    def __init__(self, root, master):
        self.root = root
        self.master = master
        self.installing = False
        self._changelog_image_cache = {}

    def _build_markdown_tags(self, text_widget):
        base_font = ("Host Grotesk", 12)
        text_widget.tag_configure("heading1", font=("Host Grotesk", 16, "bold"), spacing1=10, spacing3=8)
        text_widget.tag_configure("heading2", font=("Host Grotesk", 14, "bold"), spacing1=8, spacing3=6)
        text_widget.tag_configure("heading3", font=("Host Grotesk", 13, "bold"), spacing1=6, spacing3=4)
        text_widget.tag_configure("bold", font=("Host Grotesk", 12, "bold"))
        text_widget.tag_configure("italic", font=("Host Grotesk", 12, "italic"))
        text_widget.tag_configure("underline", font=("Host Grotesk", 12, "underline"))
        text_widget.tag_configure("inline_code", font=("JetBrains Mono", 11), background=self.root.style.colors.get("secondary"), foreground=self.root.style.colors.get("text"))
        text_widget.tag_configure("blockquote", lmargin1=0, lmargin2=0, foreground="#b3b3b3")
        text_widget.tag_configure("bullet", lmargin1=18, lmargin2=36)
        text_widget.tag_configure("plain", font=base_font)
        text_widget.tag_configure("warning", font=("Host Grotesk", 13, "bold"), foreground="#facc15", spacing1=6, spacing3=4)
        text_widget.tag_configure("note", font=("Host Grotesk", 13, "bold"), foreground="#158bfa", spacing1=6, spacing3=4)

    def _insert_inline_markdown(self, text_widget, line, base_tags=()):
        patterns = [
            (r"<img\b[^>]*?\bsrc=[\"']([^\"']+)[\"'][^>]*?/?>", "image"),
            (r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)", "image"),
            (r"<ins>(.*?)</ins>", "underline"),
            (r"`([^`]+)`", "inline_code"),
            (r"\*\*([^*]+)\*\*", "bold"),
            (r"(?<!\*)\*([^*]+)\*(?!\*)", "italic"),
            (r"_([^_]+)_", "italic"),
            (r"\[([^\]]+)\]\(([^)]+)\)", "link"),
        ]

        matches = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, line):
                matches.append((match.start(), match.end(), tag, match))

        matches.sort(key=lambda item: item[0])

        index = 0
        while index < len(line):
            overlapping = next((item for item in matches if item[0] == index), None)
            if overlapping:
                _, end, tag, match = overlapping
                if tag == "image":
                    url = match.group(1) if match.re.pattern.startswith("<img") else match.group(2)
                    self._insert_changelog_image(text_widget, url)
                elif tag == "link":
                    display = match.group(1)
                    text_widget.insert("end", display, base_tags + ("link",))
                else:
                    text_widget.insert("end", match.group(1), base_tags + (tag,))
                index = end
                continue

            text_widget.insert("end", line[index], base_tags)
            index += 1

    def _insert_changelog_image(self, text_widget, url):
        photo = self._changelog_image_cache.get(url)
        if photo is None:
            try:
                response = requests.get(url, timeout=10, headers={"User-Agent": "Ghost"})
                response.raise_for_status()
                with Image.open(BytesIO(response.content)) as image:
                    image = image.convert("RGBA")
                    image.thumbnail((220, 180), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
            except Exception:
                text_widget.insert("end", "[image unavailable]")
                return

            self._changelog_image_cache[url] = photo

        text_widget.image_create("end", image=photo)

    @staticmethod
    def _is_table_row(line):
        return line.count("|") >= 1 and not line.startswith(">")

    @staticmethod
    def _is_table_separator(line):
        cells = line.strip().strip("|").split("|")
        return len(cells) >= 1 and all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells)

    @staticmethod
    def _table_cells(line):
        return line.strip().strip("|").split("|")

    def _render_table_row(self, text_widget, line):
        cells = self._table_cells(line)
        for index, cell in enumerate(cells):
            self._insert_inline_markdown(text_widget, cell.strip())
            if index < len(cells) - 1:
                text_widget.insert("end", "    ")
        text_widget.insert("end", "\n")

    def _render_markdown(self, text_widget, markdown_text):
        self._build_markdown_tags(text_widget)
        text_widget.tag_configure("link", foreground="#8b5cf6", underline=True)

        in_code_block = False
        skipping_admonition = False
        lines = markdown_text.splitlines()
        line_index = 0
        while line_index < len(lines):
            raw_line = lines[line_index]
            line = raw_line.rstrip()

            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block:
                    text_widget.insert("end", "\n")
                continue

            if in_code_block:
                text_widget.insert("end", raw_line + "\n", ("inline_code",))
                line_index += 1
                continue

            stripped = line.strip()
            if (
                self._is_table_row(stripped)
                and line_index + 1 < len(lines)
                and self._is_table_separator(lines[line_index + 1].strip())
            ):
                self._render_table_row(text_widget, stripped)
                line_index += 2
                while line_index < len(lines) and self._is_table_row(lines[line_index].strip()):
                    self._render_table_row(text_widget, lines[line_index])
                    line_index += 1
                continue
            if skipping_admonition:
                if not stripped:
                    skipping_admonition = False
                line_index += 1
                continue
            if not stripped:
                text_widget.insert("end", "\n")
                line_index += 1
                continue

            if stripped.startswith("# "):
                text_widget.insert("end", stripped[2:] + "\n", ("heading1",))
                line_index += 1
                continue
            if stripped.startswith("## "):
                text_widget.insert("end", stripped[3:] + "\n", ("heading2",))
                line_index += 1
                continue
            if stripped.startswith("### "):
                text_widget.insert("end", stripped[4:] + "\n", ("heading3",))
                line_index += 1
                continue
            admonition = re.match(r"^>\s*(WARNING|NOTE)\s*$", stripped)
            if admonition:
                skipping_admonition = True
                line_index += 1
                continue
            if stripped.startswith(("- ", "* ")):
                prefix = "• " if stripped.startswith(("- ", "* ")) else ""
                text_widget.insert("end", prefix)
                self._insert_inline_markdown(text_widget, stripped[2:])
                text_widget.insert("end", "\n", ("bullet",))
                line_index += 1
                continue
            if stripped.startswith(">"):
                blockquote_content = stripped[1:].strip()
                self._insert_inline_markdown(text_widget, blockquote_content, ("blockquote",))
                text_widget.insert("end", "\n", ("blockquote",))
                line_index += 1
                continue

            self._insert_inline_markdown(text_widget, stripped)
            text_widget.insert("end", "\n", ("plain",))
            line_index += 1

    def _set_install_progress(self, status, progress):
        if not self.installing:
            return

        self.install_status.configure(text=status)
        if progress is None:
            if self.install_progress.cget("mode") != "indeterminate":
                self.install_progress.configure(mode="indeterminate")
                self.install_progress.start(12)
            return

        if self.install_progress.cget("mode") == "indeterminate":
            self.install_progress.stop()
            self.install_progress.configure(mode="determinate")
        self.install_progress.configure(value=progress)

    def _install_update(self, update_info):
        self.installing = True
        self.install_button.set_state("disabled")
        self.skip_button.set_state("disabled")
        self.install_progress_frame.pack_configure(before=self.full_changelog_button, fill=ttk.X, pady=(0, 12))
        self._set_install_progress("Starting update", 0)

        def report(status, progress):
            self.root.after(0, self._set_install_progress, status, progress)

        def install():
            try:
                installed = update_info.install(progress_callback=report, exit_on_success=False)
            except Exception as exc:
                self.root.after(0, self._update_failed, str(exc))
                return

            if installed:
                self.root.after(0, self._finish_install)
            else:
                self.root.after(0, self._update_failed, "Could not install the update. Check the console for details.")

        threading.Thread(target=install, daemon=True).start()

    def _finish_install(self):
        self.install_status.configure(text="Closing Ghost")
        self.root.after(100, self.master.quit)

    def _update_failed(self, message):
        self.installing = False
        self.install_progress.stop()
        self.install_progress.configure(mode="determinate", value=0)
        self.install_status.configure(text=message)
        self.install_button.set_state("normal")
        self.skip_button.set_state("normal")

    def draw(self, wrapper):
        update_info = getattr(self.master, "update_info", None)

        title_wrapper = ttk.Frame(wrapper)
        title_wrapper.pack(anchor="w", padx=15, pady=(15, 0), fill=ttk.X)
        title_wrapper.grid_columnconfigure(0, weight=1)

        title = ttk.Label(title_wrapper, text=f"Ghost v{update_info.latest_version}" if update_info else "New update available", font=("Host Grotesk", 24, "bold"))
        title.grid(row=0, column=0, sticky=ttk.W)
        
        # version_pill = RoundedFrame(title_wrapper, radius=10, bootstyle="secondary.TFrame")
        # version_pill.grid(row=0, column=1, padx=(10, 0), sticky=ttk.E)
        
        # version_label = ttk.Label(version_pill, text=f"{update_info.latest_version}" if update_info else "Version unknown", font=("Host Grotesk", 12, "bold"))
        # version_label.configure(background=self.root.style.colors.get("secondary"))
        # version_label.pack(padx=10, pady=5)

        version_text = "A new version is ready to install."
        if update_info:
            version_text = f"A new version of Ghost is ready to install. See whats new below."

        ttk.Label(wrapper, text=version_text, wraplength=500, justify="left").pack(anchor="w", padx=15)
        
        card = RoundedFrame(wrapper, radius=(18, 18, 0, 0), background=self.root.style.colors.get("secondary"))
        card.pack(fill=ttk.BOTH, expand=True, padx=15, pady=(24, 0))

        changelog_label = ttk.Label(card, text="Changelog", font=("Host Grotesk", 14, "bold"))
        changelog_label.configure(background=self.root.style.colors.get("secondary"))
        changelog_label.pack(anchor="w", pady=(10, 10), padx=10)

        if update_info and update_info.changelog:
            changelog_frame = RoundedFrame(card, radius=(0, 0, 18, 18), background=self.root.style.colors.get("dark"), parent_background=self.root.style.colors.get("bg"))
            changelog_frame.pack(fill=ttk.BOTH, expand=True)

            changelog = ttk.tk.Text(changelog_frame, height=7, wrap="word", borderwidth=0, highlightthickness=0)
            self._render_markdown(changelog, update_info.changelog.strip())
            changelog.configure(state="disabled", background=self.root.style.colors.get("dark"), foreground=self.root.style.colors.get("text"), borderwidth=0, highlightthickness=0, font=("Host Grotesk", 12))
            changelog.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)

        button_row = ttk.Frame(wrapper)
        button_row.pack(fill=ttk.X, padx=15, pady=(24, 15))

        self.install_progress_frame = ttk.Frame(button_row)
        self.install_progress_frame.pack(fill=ttk.X)

        self.install_status = ttk.Label(self.install_progress_frame, text="", font=("Host Grotesk", 11))
        self.install_status.pack(side=ttk.TOP, anchor="w", pady=(0, 6))
        self.install_progress = RoundedProgressbar(self.install_progress_frame, mode="determinate", maximum=100, value=0, bootstyle="primary")
        self.install_progress.pack(side=ttk.TOP, fill=ttk.X)
        self.install_progress_frame.pack_forget()

        self.full_changelog_button = RoundedButton(
            button_row,
            text="Full Changelog",
            command=lambda e: webbrowser.open(update_info.full_changelog_url) if update_info else None,
            bootstyle="secondary.TButton",
        )
        self.full_changelog_button.pack(side=ttk.LEFT)

        self.install_button = RoundedButton(button_row, text="Install & Restart", command=lambda e: self._install_update(update_info) if update_info else None, bootstyle="primary.TButton")
        self.install_button.pack(side=ttk.RIGHT)

        self.skip_button = RoundedButton(button_row, text="Skip", command=lambda e: self.master._continue_after_update_prompt(), bootstyle="secondary.TButton")
        self.skip_button.pack(side=ttk.RIGHT, padx=(0, 10))
