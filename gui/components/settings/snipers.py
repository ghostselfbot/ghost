import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, RoundedFrame

class SnipersPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "Snipers", images.get("snipers"), width=width, collapsed=False)
        self.cfg = config
        self.images = images
        self.snipers = None
        self.snipers_tk_entries = {}
        self.placeholder = "Paste webhook URL here..."
        
    def _save_sniper(self, sniper_name):
        sniper = self.cfg.get_sniper(sniper_name)
        
        if not sniper:
            return
        
        sniper.enabled = self.snipers_tk_entries[sniper_name]["enabled"].get()
        sniper.ignore_invalid = self.snipers_tk_entries[sniper_name]["ignore_invalid"].get()
        sniper.webhook = self.snipers_tk_entries[sniper_name]["webhook"].get()
        
        sniper.save(notify=False)
        
    def _draw_card(self, sniper):
        card = RoundedFrame(self.body, radius=(10, 10, 10, 10), bootstyle="secondary.TFrame")
        self.snipers_tk_entries[sniper.name] = {}

        header = ttk.Frame(card, style="secondary.TFrame")
        header.grid(row=0, column=0, sticky=ttk.NSEW, pady=(10, 5), padx=10)

        title = ttk.Label(header, text=sniper.name.capitalize() + " Sniper", font=("Host Grotesk", 16, "bold"))
        title.configure(background=self.root.style.colors.get("secondary"))
        title.grid(row=0, column=0, sticky=ttk.NSEW)

        entries = [
            {
                "label": "Enabled",
                "type": "checkbox",
                "value": sniper.enabled,
                "config_key": "enabled"
            },
            {
                "label": "Ignore Invalid",
                "type": "checkbox",
                "value": sniper.ignore_invalid,
                "config_key": "ignore_invalid"
            },
            {
                "label": "Webhook",
                "type": "entry",
                "value": sniper.webhook,
                "config_key": "webhook"
            }
        ]

        for i, entry in enumerate(entries):
            if entry["type"] == "checkbox":
                checkbox_wrapper = ttk.Frame(card, style="secondary.TFrame")
                checkbox_wrapper.grid(row=i + 1, column=0, sticky=ttk.NSEW, pady=(2, 0), padx=10)

                # ✅ Use BooleanVar to properly track state
                var = ttk.BooleanVar(value=entry["value"])
                
                checkbox = ttk.Checkbutton(
                    checkbox_wrapper,
                    style="success.TCheckbutton",
                    variable=var,  # ✅ Bind to BooleanVar
                    command=lambda sniper_name=sniper.name: self._save_sniper(sniper_name),
                    tristatevalue=None
                )
                checkbox.grid(row=0, column=0, sticky=ttk.W)

                # ✅ Force checkbox state update
                if entry["value"]:
                    checkbox.state(["selected", "!alternate"])  # Remove alternate state
                else:
                    checkbox.state(["!selected", "!alternate"])  # Ensure it's not in an indeterminate state

                self.snipers_tk_entries[sniper.name][entry["config_key"]] = var

                label = ttk.Label(checkbox_wrapper, text=" " + entry["label"])
                label.configure(background=self.root.style.colors.get("secondary"))
                label.grid(row=0, column=0, sticky=ttk.W, padx=(15, 10), ipadx=10)
                
            else:
                label = ttk.Label(card, text=entry["label"])
                label.configure(background=self.root.style.colors.get("secondary"))
                label.grid(row=i + 1, column=0, sticky=ttk.W, pady=(10, 5), padx=10)

                textbox = ttk.Entry(card, font=("Host Grotesk",))
                textbox.insert(0, entry["value"])
                textbox.grid(row=i + 2, column=0, sticky=ttk.EW, pady=(0, 10), padx=10, columnspan=2)

                textbox.bind("<Return>", lambda event, sniper_name=sniper.name: self._save_sniper(sniper_name))
                textbox.bind("<FocusOut>", lambda event, sniper_name=sniper.name: self._save_sniper(sniper_name))

                self.snipers_tk_entries[sniper.name][entry["config_key"]] = textbox

        card.grid_rowconfigure(i + 2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        return card
        
    def draw(self):
        self.snipers = self.cfg.get_snipers()
        
        if not self.snipers:
            console.log_to_gui("error", "No snipers found.")
            return
        
        row, column = 0, 0
        
        for sniper in self.snipers:
            card = self._draw_card(sniper)
            card.grid(row=row, column=column, sticky=ttk.NSEW, padx=(10, 5) if column == 0 else (5, 10), pady=10)
            
            column += 1
            
            if column > 1:
                column = 0
                row += 1
                
        self.body.grid_rowconfigure(row, weight=1)
                
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(row, weight=1)
        
        return self.wrapper
        