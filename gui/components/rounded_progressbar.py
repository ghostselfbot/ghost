import ttkbootstrap as ttk

from gui.components.rounded_frame import RoundedFrame


class RoundedProgressbar(ttk.Canvas):
    def __init__(self, parent, radius=8, **kwargs):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.style = self.root.style
        self.maximum = float(kwargs.pop("maximum", 100))
        self.value = float(kwargs.pop("value", 0))
        self.mode = kwargs.pop("mode", "determinate")
        self.bootstyle = kwargs.pop("bootstyle", kwargs.pop("style", "primary"))
        self.track_color = kwargs.pop("track_color", self.style.colors.get("secondary"))
        self.bar_color = kwargs.pop("bar_color", self._get_bootstyle_color())
        self.radius = radius
        self._animation_id = None
        self._animation_value = 0

        canvas_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"padx", "pady", "background", "foreground"}
        }
        canvas_kwargs.setdefault("height", 16)
        super().__init__(parent, highlightthickness=0, bd=0, **canvas_kwargs)
        super().configure(background=kwargs.get("background", self._get_parent_background()))
        self.bind("<Configure>", self._draw)

    def _get_bootstyle_color(self):
        style_name = self.bootstyle.split(".")[0].lower()
        return self.style.colors.get(style_name) or self.style.colors.get("primary")

    def _get_parent_background(self):
        if isinstance(self.parent, RoundedFrame):
            return self.parent.frame_background
        try:
            style_name = self.parent.cget("style")
            return self.style.lookup(style_name, "background") or self.style.colors.get("bg")
        except Exception:
            return self.style.colors.get("bg")

    def _rounded_rectangle(self, left, top, right, bottom, color):
        if right <= left or bottom <= top:
            return

        radius = self.radius
        radius = min(radius, (right - left) / 2, (bottom - top) / 2)
        if radius == 0:
            self.create_rectangle(left, top, right, bottom, fill=color, outline=color)
            return

        self.create_rectangle(left + radius, top, right - radius, bottom, fill=color, outline=color)
        self.create_rectangle(left, top + radius, right, bottom - radius, fill=color, outline=color)
        self.create_arc(left, top, left + radius * 2, top + radius * 2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(right - radius * 2, top, right, top + radius * 2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(right - radius * 2, bottom - radius * 2, right, bottom, start=270, extent=90, fill=color, outline=color)
        self.create_arc(left, bottom - radius * 2, left + radius * 2, bottom, start=180, extent=90, fill=color, outline=color)

    def _draw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 or height < 2:
            return

        self._rounded_rectangle(0, 0, width, height, self.track_color)
        if self.mode == "indeterminate":
            segment_width = max(height * 2, width / 4)
            left = (width + segment_width) * self._animation_value / 100 - segment_width
            self._rounded_rectangle(left, 0, left + segment_width, height, self.bar_color)
            return

        progress = min(max(self.value / self.maximum, 0), 1) if self.maximum else 0
        self._rounded_rectangle(0, 0, width * progress, height, self.bar_color)

    def configure(self, cnf=None, **kwargs):
        options = dict(cnf or {})
        options.update(kwargs)
        redraw = False

        for option in ("maximum", "value", "mode", "bootstyle", "track_color", "bar_color"):
            if option not in options:
                continue
            value = options.pop(option)
            if option in {"maximum", "value"}:
                value = float(value)
            if option == "bootstyle":
                self.bootstyle = value
                self.bar_color = self._get_bootstyle_color()
            else:
                setattr(self, option, value)
            redraw = True

        result = super().configure(options) if options else None
        if redraw:
            self._draw()
        return result

    config = configure

    def cget(self, key):
        if key in {"maximum", "value", "mode", "bootstyle", "track_color", "bar_color"}:
            return getattr(self, key)
        return super().cget(key)

    def step(self, amount=1):
        self.configure(value=self.value + amount)

    def start(self, interval=50):
        self.stop()
        self.mode = "indeterminate"
        self._animation_interval = max(int(interval), 1)
        self._animate()

    def _animate(self):
        self._animation_value = (self._animation_value + 2) % 200
        self._draw()
        self._animation_id = self.after(self._animation_interval, self._animate)

    def stop(self):
        if self._animation_id is not None:
            self.after_cancel(self._animation_id)
            self._animation_id = None