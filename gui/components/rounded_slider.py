import ttkbootstrap as ttk

from gui.components.rounded_frame import RoundedFrame


class RoundedSlider(ttk.Canvas):
    def __init__(self, parent, from_=0, to=100, value=None, command=None, parent_background=None, **kwargs):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.style = self.root.style
        self.from_ = float(from_)
        self.to = float(to)
        self.value = self.from_ if value is None else float(value)
        self.command = command
        self.parent_background = parent_background or self._get_parent_background()
        self.track_color = kwargs.pop("track_color", self.style.colors.get("secondary"))
        self.fill_color = kwargs.pop("fill_color", self.style.colors.get("primary"))
        self.thumb_color = kwargs.pop("thumb_color", self.fill_color)
        self.track_height = kwargs.pop("track_height", 6)
        self.thumb_radius = kwargs.pop("thumb_radius", 8)

        canvas_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"orient", "bootstyle", "style", "padx", "pady", "background", "foreground"}
        }
        canvas_kwargs.setdefault("height", self.thumb_radius * 2 + 4)
        super().__init__(parent, highlightthickness=0, bd=0, **canvas_kwargs)
        super().configure(background=self.parent_background)
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._update_from_event)
        self.bind("<B1-Motion>", self._update_from_event)

    def _get_parent_background(self):
        if isinstance(self.parent, RoundedFrame):
            return self.parent.frame_background
        try:
            style_name = self.parent.cget("style")
            return self.style.lookup(style_name, "background") or self.style.colors.get("bg")
        except Exception:
            return self.style.colors.get("bg")

    def _track_bounds(self):
        padding = self.thumb_radius
        return padding, self.winfo_width() - padding

    def _fraction(self):
        if self.to == self.from_:
            return 0
        return min(max((self.value - self.from_) / (self.to - self.from_), 0), 1)

    def _draw_rounded_rectangle(self, left, top, right, bottom, color):
        radius = min((bottom - top) / 2, (right - left) / 2)
        self.create_rectangle(left + radius, top, right - radius, bottom, fill=color, outline=color)
        self.create_rectangle(left, top + radius, right, bottom - radius, fill=color, outline=color)
        self.create_oval(left, top, left + radius * 2, bottom, fill=color, outline=color)
        self.create_oval(right - radius * 2, top, right, bottom, fill=color, outline=color)

    def _draw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < self.thumb_radius * 2 or height < self.track_height:
            return

        left, right = self._track_bounds()
        center_y = height / 2
        track_top = center_y - self.track_height / 2
        track_bottom = center_y + self.track_height / 2
        thumb_x = left + (right - left) * self._fraction()

        self._draw_rounded_rectangle(left, track_top, right, track_bottom, self.track_color)
        self._draw_rounded_rectangle(left, track_top, thumb_x, track_bottom, self.fill_color)
        self.create_oval(
            thumb_x - self.thumb_radius,
            center_y - self.thumb_radius,
            thumb_x + self.thumb_radius,
            center_y + self.thumb_radius,
            fill=self.thumb_color,
            outline=self.parent_background,
            width=2,
        )

    def _update_from_event(self, event):
        left, right = self._track_bounds()
        fraction = min(max((event.x - left) / max(right - left, 1), 0), 1)
        self.set(self.from_ + (self.to - self.from_) * fraction)

    def set(self, value):
        self.value = min(max(float(value), self.from_), self.to)
        self._draw()
        if self.command:
            self.command(str(self.value))

    def get(self):
        return self.value

    def set_parent_background(self, parent_background):
        self.parent_background = parent_background
        super().configure(background=parent_background)
        self._draw()