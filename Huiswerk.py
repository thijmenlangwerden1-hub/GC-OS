import os
import json
import datetime as dt
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from tkcalendar import Calendar
import urllib.request
import webbrowser

# ============================================================
# THEMA'S
# ============================================================

THEMES = {
    "Wit": {
        "mode": "Light",
        "bg_root": "#f2f3f7",
        "bg_sidebar": "#ffffff",
        "bg_main": "#f7f8fb",
        "bg_card": "#ffffff",
        "text": "#111111",
        "sidebar_text": "#111111",
        "button_text": "#111111",
        "button_fg": "#e3e6ee",
        "button_hover": "#d2d6e4",
        "accent": "#007aff",
        "list_bg": "#ffffff",
        "list_fg": "#111111",
        "list_select": "#cfe3ff",
    },
    "Zwart": {
        "mode": "Dark",
        "bg_root": "#111111",
        "bg_sidebar": "#18181b",
        "bg_main": "#111111",
        "bg_card": "#1f1f23",
        "text": "#f5f5f7",
        "sidebar_text": "#f5f5f7",
        "button_text": "#f5f5f7",
        "button_fg": "#2b2b30",
        "button_hover": "#3a3a40",
        "accent": "#0a84ff",
        "list_bg": "#18181b",
        "list_fg": "#f5f5f7",
        "list_select": "#2f2f35",
    },
    "Rood": {
        "mode": "Light",
        "bg_root": "#ffe6e6",
        "bg_sidebar": "#ffcccc",
        "bg_main": "#fff0f0",
        "bg_card": "#ffffff",
        "text": "#4a0000",
        "sidebar_text": "#4a0000",
        "button_text": "#4a0000",
        "button_fg": "#ffb3b3",
        "button_hover": "#ff9999",
        "accent": "#ff1f1f",
        "list_bg": "#ffffff",
        "list_fg": "#4a0000",
        "list_select": "#ffd6d6",
    },
    "Blauw": {
        "mode": "Light",
        "bg_root": "#e6f0ff",
        "bg_sidebar": "#c7dcff",
        "bg_main": "#edf4ff",
        "bg_card": "#ffffff",
        "text": "#001a4d",
        "sidebar_text": "#001a4d",
        "button_text": "#001a4d",
        "button_fg": "#b3ccff",
        "button_hover": "#99bbff",
        "accent": "#0066ff",
        "list_bg": "#ffffff",
        "list_fg": "#001a4d",
        "list_select": "#d6e4ff",
    },
    "Geel": {
        "mode": "Light",
        "bg_root": "#fff9d9",
        "bg_sidebar": "#ffe999",
        "bg_main": "#fffbe6",
        "bg_card": "#ffffff",
        "text": "#4d3b00",
        "sidebar_text": "#4d3b00",
        "button_text": "#4d3b00",
        "button_fg": "#ffe08a",
        "button_hover": "#ffd76b",
        "accent": "#ffcc00",
        "list_bg": "#ffffff",
        "list_fg": "#4d3b00",
        "list_select": "#fff0b3",
    },
    "Groen": {
        "mode": "Light",
        "bg_root": "#e6ffef",
        "bg_sidebar": "#c4f5d4",
        "bg_main": "#f3fff7",
        "bg_card": "#ffffff",
        "text": "#003319",
        "sidebar_text": "#003319",
        "button_text": "#003319",
        "button_fg": "#bdeecb",
        "button_hover": "#a6e4b8",
        "accent": "#34c759",
        "list_bg": "#ffffff",
        "list_fg": "#003319",
        "list_select": "#d6f5df",
    },
    "Blauw-Groen": {
        "mode": "Dark",
        "bg_root": "#071821",
        "bg_sidebar": "#0b2430",
        "bg_main": "#071821",
        "bg_card": "#0f2f3b",
        "text": "#e6f9ff",
        "sidebar_text": "#e6f9ff",
        "button_text": "#e6f9ff",
        "button_fg": "#145c63",
        "button_hover": "#1a6f78",
        "accent": "#00e5ff",
        "list_bg": "#0b2430",
        "list_fg": "#e6f9ff",
        "list_select": "#145c63",
    },
}

# ============================================================
# PAD NAAR JSON & OPSLAAN/KIEZEN
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")

def opslaan(data):
    try:
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Fout", f"Kan data niet opslaan:\n{e}")

def kies_datum(entry_widget):
    top = ctk.CTkToplevel()
    top.title("Kies een datum")
    top.geometry("300x320")
    top.resizable(False, False)
    top.grab_set()  # Zorgt dat de focus op deze pop-up blijft
    
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=10, fill="both", expand=True)
    
    def selecteer():
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, cal.get_date())
        top.destroy()
        
    ctk.CTkButton(top, text="Selecteer", command=selecteer).pack(pady=10)

# ============================================================
# DATA OPSLAG
# ============================================================

def _standaard_vrijedagen():
    vandaag = dt.date.today()
    jaar = vandaag.year
    volgend = jaar + 1

    dagen = [
        {"naam": "Nieuwjaarsdag", "datum": f"{jaar}-01-01"},
        {"naam": "Goede Vrijdag", "datum": f"{jaar}-03-29"},
        {"naam": "1e Paasdag", "datum": f"{jaar}-03-31"},
        {"naam": "2e Paasdag", "datum": f"{jaar}-04-01"},
        {"naam": "Koningsdag", "datum": f"{jaar}-04-27"},
        {"naam": "Bevrijdingsdag", "datum": f"{jaar}-05-05"},
        {"naam": "Hemelvaartsdag", "datum": f"{jaar}-05-09"},
        {"naam": "1e Pinksterdag", "datum": f"{jaar}-05-19"},
        {"naam": "2e Pinksterdag", "datum": f"{jaar}-05-20"},
        {"naam": "Kerstmis (1e)", "datum": f"{jaar}-12-25"},
        {"naam": "Kerstmis (2e)", "datum": f"{jaar}-12-26"},
        {"naam": "Voorjaarsvakantie", "datum": f"{jaar}-02-17"},
        {"naam": "Meivakantie", "datum": f"{jaar}-05-01"},
        {"naam": "Zomervakantie", "datum": f"{jaar}-07-15"},
        {"naam": "Herfstvakantie", "datum": f"{jaar}-10-21"},
        {"naam": "Kerstvacantie", "datum": f"{jaar}-12-23"},
        {"naam": "Nieuwjaarsdag", "datum": f"{volgend}-01-01"},
        {"naam": "Voorjaarsvakantie", "datum": f"{volgend}-02-16"},
        {"naam": "Meivakantie", "datum": f"{volgend}-05-01"},
        {"naam": "Zomervakantie", "datum": f"{volgend}-07-14"},
        {"naam": "Herfstvakantie", "datum": f"{volgend}-10-20"},
        {"naam": "Kerstvakantie", "datum": f"{volgend}-12-23"},
    ]

    uniek = {}
    for d in dagen:
        uniek[(d["naam"], d["datum"])] = d
    return list(uniek.values())


def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": [],
            "settings": {"theme": "Wit"},
            "vrijedagen": [],
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)

    if "huiswerk" not in data:
        data["huiswerk"] = []
    if "notities" not in data:
        data["notities"] = []
    if "cijfers" not in data:
        data["cijfers"] = []
    if "rooster" not in data:
        data["rooster"] = []
    if "settings" not in data:
        data["settings"] = {"theme": "Wit"}
    if "theme" not in data["settings"]:
        data["settings"]["theme"] = "Wit"
    if "vrijedagen" not in data:
        data["vrijedagen"] = []

    for c in data.get("cijfers", []):
        if "periode" not in c:
            c["periode"] = "Periode 1"
        if "datum" not in c:
            c["datum"] = "2024-01-01"

    nieuwe_vrijedagen = []
    for v in data["vrijedagen"]:
        if isinstance(v, dict) and "naam" in v and "datum" in v:
            nieuwe_vrijedagen.append(v)
        elif isinstance(v, str):
            nieuwe_vrijedagen.append({"naam": "Vrije dag", "datum": v})
    data["vrijedagen"] = nieuwe_vrijedagen

    if not data["vrijedagen"]:
        data["vrijedagen"] = _standaard_vrijedagen()

    return data


# ============================================================
# UPDATE CHECKER
# ============================================================

HUIDIGE_VERSIE = "1.0.1"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_PAGE = "https://github.com/thijmenlangwerden1-hub/GC-OS"

def check_for_updates(silent=False):
    try:
        # User-Agent toevoegen voorkomt 403 Forbidden errors bij GitHub requests
        req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            nieuwste = response.read().decode("utf-8").strip()
    except Exception:
        if not silent:
            messagebox.showerror("Fout", "Kan geen verbinding maken met GitHub.")
        return

    if nieuwste == HUIDIGE_VERSIE:
        if not silent:
            messagebox.showinfo("Up‑to‑date", "Je gebruikt de nieuwste versie van GC‑OS.")
    else:
        messagebox.showinfo(
            "Update beschikbaar",
            f"Nieuwe versie gevonden!\n\n"
            f"Huidige versie: {HUIDIGE_VERSIE}\n"
            f"Nieuwste versie: {nieuwste}\n\n"
            f"Download de update via GitHub."
        )
        webbrowser.open(GITHUB_PAGE)

# ============================================================
# MAIN APPLICATIE CLASS
# ============================================================

class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Wit")
        if self.theme_name not in THEMES:
            self.theme_name = "Wit"

        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        ctk.set_default_color_theme("blue")

        self.title("GraafschapCollege‑OS")
        self.geometry("1100x650")
        self.minsize(950, 550)

        self.vakken_hw = [
            "Nederlands",
            "Engels",
            "Rekenen",
            "Hardware",
            "Netwerken",
            "Techlab",
            "Burgerschap",
            "Loopbaan",
        ]

        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.cijfer_rows = []

        self.theme_combo = None
        self.vrijedagen_listbox = None
        self.vrijedag_naam_entry = None
        self.vrijedag_datum_entry = None

        self.cijfer_vak_entry = None
        self.cijfer_waarde_entry = None
        self.cijfer_periode_entry = None
        self.cijfer_datum_entry = None

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()

        self.after(100, self.show_intro_screen)
        # Controleer na 2 seconden stil op de achtergrond op updates
        self.after(2000, lambda: check_for_updates(silent=True))

    # --------------------------------------------------------
    # INTRO-SCREEN
    # --------------------------------------------------------

    def show_intro_screen(self):
        t = THEMES[self.theme_name]

        intro = ctk.CTkToplevel(self)
        intro.overrideredirect(True)

        try:
            intro.attributes("-fullscreen", True)
        except Exception:
            intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])

        start_size = 10
        end_size = 60
        current_size = start_size

        label = ctk.CTkLabel(
            intro,
            text="GraafschapCollege‑OS",
            font=("Segoe UI", current_size, "bold"),
            text_color=t["accent"],
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        intro.attributes("-alpha", 0.0)

        def animate(alpha=0.0, size=current_size):
            if alpha < 1.0:
                intro.attributes("-alpha", alpha)
            if size < end_size:
                size += 2
                label.configure(font=("Segoe UI", size, "bold"))

            if alpha < 1.0 or size < end_size:
                self.after(15, lambda: animate(alpha + 0.03, size))
            else:
                self.after(600, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(15, lambda: fade_out(alpha - 0.04))
            else:
                try:
                    intro.destroy()
                except Exception:
                    pass
                try:
                    self.state("zoomed")
                except Exception:
                    pass

        animate()

    # --------------------------------------------------------
    # THEMA TOEPASSEN
    # --------------------------------------------------------

    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])

        self.configure(fg_color=t["bg_root"])

        if hasattr(self, "sidebar"):
            self.sidebar.configure(fg_color=t["bg_sidebar"])
        if hasattr(self, "main"):
            self.main.configure(fg_color=t["bg_main"])

        for btn in self.sidebar_buttons:
            try:
                btn.configure(
                    fg_color="transparent",
                    hover_color=t["button_hover"],
                    text_color=t["sidebar_text"],
                )
            except Exception:
                pass

        if self.hw_list is not None:
            self.hw_list.configure(
                bg=t["list_bg"],
                fg=t["list_fg"],
                selectbackground=t["list_select"],
                highlightthickness=0,
                borderwidth=0,
            )
            self._update_hw_list_colors()

        if self.note_list is not None:
            self.note_list.configure(
                bg=t["list_bg"],
                fg=t["list_fg"],
                selectbackground=t["list_select"],
                highlightthickness=0,
                borderwidth=0,
            )
        if self.cijfer_list is not None:
            self.cijfer_list.configure(
                bg=t["list_bg"],
                fg=t["list_fg"],
                selectbackground=t["list_select"],
                highlightthickness=0,
                borderwidth=0,
            )
        if self.vrijedagen_listbox is not None:
            self.vrijedagen_listbox.configure(
                bg=t["list_bg"],
                fg=t["list_fg"],
                selectbackground=t["list_select"],
                highlightthickness=0,
                borderwidth=0,
            )

        if self.theme_combo is not None:
            try:
                self.theme_combo.configure(
                    fg_color=t["button_fg"],
                    border_color=t["accent"],
                    button_color=t["accent"],
                    button_hover_color=t["button_hover"],
                    text_color=t["button_text"],
                )
            except Exception:
                pass

    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        title_label = ctk.CTkLabel(
            self.sidebar,
            text="GC‑OS",
            font=("Segoe UI", 26, "bold"),
        )
        title_label.pack(pady=25)

        buttons = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📝  Huiswerk", self.show_huiswerk),
            ("📅  Rooster", self.show_rooster),
            ("🗒  Notities", self.show_notities),
            ("📊  Cijfers", self.show_cijfers),
        ]

        self.sidebar_buttons.clear()
        for text, cmd in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                anchor="w",
                fg_color="transparent",
                command=cmd,
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.sidebar_buttons.append(btn)

        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="⚙  Instellingen",
            anchor="w",
            fg_color="transparent",
            command=self.show_settings,
        )
        settings_btn.pack(side="bottom", fill="x", padx=15, pady=15)
        self.sidebar_buttons.append(settings_btn)

        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()
        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.cijfer_rows = []
        self.vrijedagen_listbox = None
        self.vrijedag_naam_entry = None
        self.vrijedag_datum_entry = None
        self.cijfer_vak_entry = None
        self.cijfer_waarde_entry = None
        self.cijfer_periode_entry = None
        self.cijfer_datum_entry = None

    # --------------------------------------------------------
    # HULP: VRIJE DAGEN
    # --------------------------------------------------------

    def _get_upcoming_vrijedagen(self):
        vandaag = dt.date.today()
        upcoming = []
        for v in self.data.get("vrijedagen", []):
            datum_str = v.get("datum", "")
            naam = v.get("naam", "Vrije dag")
            try:
                jaar, maand, dag = map(int, datum_str.split("-"))
                d = dt.date(jaar, maand, dag)
                delta = (d - vandaag).days
                if delta >= 0:
                    upcoming.append((d, delta, naam))
            except Exception:
                continue
        upcoming.sort(key=lambda x: x[0])
        return upcoming

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)

        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        hw_total = len(self.data["huiswerk"])
        cijfers = self.data["cijfers"]
        gem = None
        if cijfers:
            gem = sum(c.get("cijfer", 0.0) for c in cijfers) / len(cijfers)

        ctk.CTkLabel(
            card,
            text=f"📚 Huiswerk open: {hw_open}/{hw_total}",
            font=("Segoe UI", 16),
            text_color=t["text"],
        ).pack(anchor="w", pady=5, padx=10)

        ctk.CTkLabel(
            card,
            text=f"📊 Gemiddelde cijfers: {gem:.2f}" if gem is not None else "📊 Geen cijfers",
            font=("Segoe UI", 16),
            text_color=t["text"],
        ).pack(anchor="w", pady=5, padx=10)

        card_vrij = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card_vrij.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            card_vrij,
            text="🎉 Vrije dagen & vakanties",
            font=("Segoe UI", 18, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=10, pady=(10, 5))

        upcoming = self._get_upcoming_vrijedagen()

        if not upcoming:
            ctk.CTkLabel(
                card_vrij,
                text="Geen vrije dagen of vakanties ingevoerd.",
                font=("Segoe UI", 14),
                text_color=t["text"],
            ).pack(anchor="w", padx=10, pady=5)
        else:
            eerst_datum, eerst_delta, eerst_naam = upcoming[0]
            if eerst_delta == 0:
                tekst = f"Vandaag ben je vrij: {eerst_naam} ({eerst_datum.strftime('%Y-%m-%d')})"
            elif eerst_delta == 1:
                tekst = f"Nog 1 dag tot: {eerst_naam} ({eerst_datum.strftime('%Y-%m-%d')})"
            else:
                tekst = f"Nog {eerst_delta} dagen tot: {eerst_naam} ({eerst_datum.strftime('%Y-%m-%d')})"

            ctk.CTkLabel(
                card_vrij,
                text=tekst,
                font=("Segoe UI", 14, "bold"),
                text_color=t["accent"],
            ).pack(anchor="w", padx=10, pady=(5, 10))

            ctk.CTkLabel(
                card_vrij,
                text="Komende vrije dagen:",
                font=("Segoe UI", 14),
                text_color=t["text"],
            ).pack(anchor="w", padx=10, pady=(0, 5))

            # Scrollbaar frame voor als er veel vrije dagen zijn
            scroll_vrij = ctk.CTkScrollableFrame(card_vrij, fg_color="transparent")
            scroll_vrij.pack(fill="both", expand=True, padx=10, pady=5)

            for d, delta, naam in upcoming[:15]:
                if delta == 0:
                    regel = f"• {d.strftime('%Y-%m-%d')} - {naam} (vandaag!)"
                elif delta == 1:
                    regel = f"• {d.strftime('%Y-%m-%d')} - {naam} (over 1 dag)"
                else:
                    regel = f"• {d.strftime('%Y-%m-%d')} - {naam} (over {delta} dagen)"
                ctk.CTkLabel(
                    scroll_vrij,
                    text=regel,
                    font=("Segoe UI", 12),
                    text_color=t["text"],
                ).pack(anchor="w", padx=10, pady=1)

        self.apply_theme()

    # --------------------------------------------------------
    # HUISWERK
    # --------------------------------------------------------

    def _update_hw_list_colors(self):
        if not self.hw_list:
            return
        t = THEMES[self.theme_name]
        vandaag = dt.date.today()

        for idx, h in enumerate(self.data.get("huiswerk", [])):
            datum_str = h.get("datum", "")
            kleur = t["list_fg"]
            try:
                jaar, maand, dag = map(int, datum_str.split("-"))
                d = dt.date(jaar, maand, dag)
                if d < vandaag:
                    kleur = "#ff0000"
            except Exception:
                kleur = t["list_fg"]
            try:
                self.hw_list.itemconfig(idx, fg=kleur)
            except Exception:
                pass

    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Huiswerk",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(
            left_frame,
            font=("Segoe UI", 11),
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
        )
        self.hw_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.hw_list.yview)
        sb.pack(side="right", fill="y")
        self.hw_list.config(yscrollcommand=sb.set)

        self.hw_list.delete(0, tk.END)
        for h in self.data["huiswerk"]:
            status = "✔" if h.get("afgerond", False) else "✘"
            datum = h.get("datum", "onbekend")
            vak = h.get("vak", "Onbekend")
            beschrijving = h.get("beschrijving", "")
            self.hw_list.insert(
                tk.END,
                f"{status} {datum} - {vak}: {beschrijving}"
            )

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(
            right_frame,
            text="Nieuw huiswerk",
            font=("Segoe UI", 16, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(right_frame, text="Vak:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 0))
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=10)

        ctk.CTkLabel(right_frame, text="Beschrijving:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 0))
        self.hw_beschrijving = ctk.CTkEntry(right_frame)
        self.hw_beschrijving.pack(fill="x", padx=10)

        ctk.CTkLabel(right_frame, text="Deadline (yyyy-mm-dd):", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 0))
        self.hw_datum = ctk.CTkEntry(right_frame)
        self.hw_datum.pack(fill="x", padx=10)

        ctk.CTkButton(
            right_frame,
            text="📅 Kies datum",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=lambda: kies_datum(self.hw_datum),
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            right_frame,
            text="Toevoegen",
            fg_color=t["accent"],
            hover_color=t["button_hover"],
            text_color="white",
            command=self.hw_toevoegen,
        ).pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(
            right_frame,
            text="Afronden",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=self.hw_afronden,
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            right_frame,
            text="Verwijderen",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=self.hw_verwijderen,
        ).pack(fill="x", padx=10, pady=5)

        self.apply_theme()
        self._update_hw_list_colors()

    def hw_toevoegen(self):
        vak = self.hw_vak.get().strip()
        beschrijving = self.hw_beschrijving.get().strip()
        datum = self.hw_datum.get().strip()

        if not vak or not beschrijving or not datum:
            messagebox.showerror("Fout", "Alle velden zijn verplicht.")
            return

        self.data["huiswerk"].append({
            "vak": vak,
            "beschrijving": beschrijving,
            "datum": datum,
            "afgerond": False,
        })

        opslaan(self.data)
        self.show_huiswerk()

    def hw_afronden(self):
        if not self.hw_list:
            return
        sel = self.hw_list.curselection()
        if not sel:
            return
        index = sel[0]
        if 0 <= index < len(self.data["huiswerk"]):
            self.data["huiswerk"][index]["afgerond"] = True
            opslaan(self.data)
            self.show_huiswerk()

    def hw_verwijderen(self):
        if not self.hw_list:
            return
        sel = self.hw_list.curselection()
        if not sel:
            return
        index = sel[0]
        if 0 <= index < len(self.data["huiswerk"]):
            self.data["huiswerk"].pop(index)
            opslaan(self.data)
            self.show_huiswerk()

    # --------------------------------------------------------
    # ROOSTER
    # --------------------------------------------------------

    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Rooster",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            card,
            text="(Hier kun je later een rooster toevoegen)",
            font=("Segoe UI", 14),
            text_color=t["text"],
        ).pack(anchor="w", padx=15, pady=15)

        self.apply_theme()

    # --------------------------------------------------------
    # NOTITIES
    # --------------------------------------------------------

    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Notities",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.note_list = tk.Listbox(
            left_frame,
            font=("Segoe UI", 11),
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
        )
        self.note_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.note_list.yview)
        sb.pack(side="right", fill="y")
        self.note_list.config(yscrollcommand=sb.set)

        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]:
            self.note_list.insert(tk.END, n)

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(
            right_frame,
            text="Nieuwe notitie",
            font=("Segoe UI", 16, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.note_input = ctk.CTkEntry(right_frame)
        self.note_input.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            right_frame,
            text="Toevoegen",
            fg_color=t["accent"],
            hover_color=t["button_hover"],
            text_color="white",
            command=self.note_toevoegen,
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            right_frame,
            text="Verwijderen",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=self.note_verwijderen,
        ).pack(fill="x", padx=10, pady=5)

        self.apply_theme()

    def note_toevoegen(self):
        text = self.note_input.get().strip()
        if not text:
            return
        self.data["notities"].append(text)
        opslaan(self.data)
        self.show_notities()

    def note_verwijderen(self):
        if not self.note_list:
            return
        sel = self.note_list.curselection()
        if not sel:
            return
        index = sel[0]
        if 0 <= index < len(self.data["notities"]):
            self.data["notities"].pop(index)
            opslaan(self.data)
            self.show_notities()

    # --------------------------------------------------------
    # CIJFERS (HERSTELD & AFGEMAAKT)
    # --------------------------------------------------------

    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Cijfers",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.cijfer_list = tk.Listbox(
            left_frame,
            font=("Consolas", 11),
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
        )
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.cijfer_list.yview)
        sb.pack(side="right", fill="y")
        self.cijfer_list.config(yscrollcommand=sb.set)

        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            vak = c.get("vak", "Onbekend")
            cijfer = c.get("cijfer", 0.0)
            periode = c.get("periode", "Periode 1")
            datum = c.get("datum", "2024-01-01")
            self.cijfer_list.insert(
                tk.END,
                f"{datum} | {vak:<15} | {periode:<10} | {cijfer:.1f}"
            )

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(
            right_frame,
            text="Nieuw Cijfer",
            font=("Segoe UI", 16, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(right_frame, text="Vak:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.cijfer_vak_entry = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.cijfer_vak_entry.set(self.vakken_hw[0])
        self.cijfer_vak_entry.pack(fill="x", padx=10)

        ctk.CTkLabel(right_frame, text="Cijfer:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.cijfer_waarde_entry = ctk.CTkEntry(right_frame)
        self.cijfer_waarde_entry.pack(fill="x", padx=10)

        ctk.CTkLabel(right_frame, text="Periode:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.cijfer_periode_entry = ctk.CTkComboBox(right_frame, values=["Periode 1", "Periode 2", "Periode 3", "Periode 4"], state="readonly")
        self.cijfer_periode_entry.set("Periode 1")
        self.cijfer_periode_entry.pack(fill="x", padx=10)

        ctk.CTkLabel(right_frame, text="Datum (yyyy-mm-dd):", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.cijfer_datum_entry = ctk.CTkEntry(right_frame)
        self.cijfer_datum_entry.pack(fill="x", padx=10)

        ctk.CTkButton(
            right_frame,
            text="📅 Kies datum",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=lambda: kies_datum(self.cijfer_datum_entry),
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            right_frame,
            text="Toevoegen",
            fg_color=t["accent"],
            hover_color=t["button_hover"],
            text_color="white",
            command=self.cijfer_toevoegen,
        ).pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(
            right_frame,
            text="Verwijderen",
            fg_color=t["button_fg"],
            hover_color=t["button_hover"],
            text_color=t["button_text"],
            command=self.cijfer_verwijderen,
        ).pack(fill="x", padx=10, pady=5)

        self.apply_theme()

    def cijfer_toevoegen(self):
        vak = self.cijfer_vak_entry.get().strip()
        waarde_str = self.cijfer_waarde_entry.get().strip()
        periode = self.cijfer_periode_entry.get().strip()
        datum = self.cijfer_datum_entry.get().strip()

        if not vak or not waarde_str or not periode or not datum:
            messagebox.showerror("Fout", "Alle velden zijn verplicht.")
            return

        try:
            waarde = float(waarde_str.replace(",", "."))
            if not (1.0 <= waarde <= 10.0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig cijfer in tussen 1.0 en 10.0.")
            return

        self.data["cijfers"].append({
            "vak": vak,
            "cijfer": waarde,
            "periode": periode,
            "datum": datum
        })
        opslaan(self.data)
        self.show_cijfers()

    def cijfer_verwijderen(self):
        if not self.cijfer_list:
            return
        sel = self.cijfer_list.curselection()
        if not sel:
            return
        index = sel[0]
        if 0 <= index < len(self.data["cijfers"]):
            self.data["cijfers"].pop(index)
            opslaan(self.data)
            self.show_cijfers()

    # --------------------------------------------------------
    # INSTELLINGEN & THEMA WISSELEN (NIEUW)
    # --------------------------------------------------------

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(
            self.main,
            text="Instellingen",
            font=("Segoe UI", 24, "bold"),
            text_color=t["text"],
        ).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_frame, text="Algemene Systeemopties", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=15)
        
        ctk.CTkLabel(left_frame, text="Kies Thema:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=15)
        self.theme_combo = ctk.CTkComboBox(left_frame, values=list(THEMES.keys()), state="readonly", command=self.wijzig_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=15, pady=5)

        # Update Checker sectie in UI
        ctk.CTkLabel(left_frame, text="Systeeminformatie", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(30, 5))
        ctk.CTkLabel(left_frame, text=f"Huidige softwareversie: {HUIDIGE_VERSIE}", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=15)
        
        ctk.CTkButton(
            left_frame,
            text="🔄 Controleer op Updates",
            fg_color=t["accent"],
            hover_color=t["button_hover"],
            text_color="white",
            command=lambda: check_for_updates(silent=False)
        ).pack(anchor="w", padx=15, pady=15)

        # Rechter frame: Vrije dagen beheer (zodat waardes in clear_main kloppen)
        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Beheer Vrije Dagen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=15)

        list_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.vrijedagen_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), borderwidth=0, highlightthickness=0, activestyle="none")
        self.vrijedagen_listbox.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_frame, command=self.vrijedagen_listbox.yview)
        sb.pack(side="right", fill="y")
        self.vrijedagen_listbox.config(yscrollcommand=sb.set)

        for v in self.data.get("vrijedagen", []):
            self.vrijedagen_listbox.insert(tk.END, f"{v.get('datum')} - {v.get('naam')}")

        ctk.CTkLabel(right_frame, text="Naam:", font=("Segoe UI", 11), text_color=t["text"]).pack(anchor="w", padx=15)
        self.vrijedag_naam_entry = ctk.CTkEntry(right_frame)
        self.vrijedag_naam_entry.pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(right_frame, text="Datum (yyyy-mm-dd):", font=("Segoe UI", 11), text_color=t["text"]).pack(anchor="w", padx=15)
        self.vrijedag_datum_entry = ctk.CTkEntry(right_frame)
        self.vrijedag_datum_entry.pack(fill="x", padx=15, pady=2)

        ctk.CTkButton(right_frame, text="📅 Kies datum", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: kies_datum(self.vrijedag_datum_entry)).pack(fill="x", padx=15, pady=3)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", hover_color=t["button_hover"], command=self.vrijedag_toevoegen).pack(fill="x", padx=15, pady=3)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self.vrijedag_verwijderen).pack(fill="x", padx=15, pady=(3, 15))

        self.apply_theme()

    def wijzig_thema(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

    def vrijedag_toevoegen(self):
        naam = self.vrijedag_naam_entry.get().strip()
        datum = self.vrijedag_datum_entry.get().strip()
        if not naam or not datum:
            messagebox.showerror("Fout", "Vul alle velden in.")
            return
        self.data["vrijedagen"].append({"naam": naam, "datum": datum})
        opslaan(self.data)
        self.show_settings()

    def vrijedag_verwijderen(self):
        if not self.vrijedagen_listbox:
            return
        sel = self.vrijedagen_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        if 0 <= index < len(self.data["vrijedagen"]):
            self.data["vrijedagen"].pop(index)
            opslaan(self.data)
            self.show_settings()


# ============================================================
# APPLICATIE STARTEN
# ============================================================

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
