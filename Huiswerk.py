import os
import sys
import json
import datetime as dt
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkcalendar import Calendar
import urllib.request
import webbrowser
import random
import threading

# Matplotlib importeren voor de cijfergrafieken
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ============================================================
# THEMA'S & KLEURENPALETTEN
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
        "button_fg": "#cceedf",
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
# INSTELLINGEN & CONFIGURATIE
# ============================================================

HUIDIGE_VERSIE = "9.5.2v"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")
LOG_BESTAND = os.path.join(SCRIPT_DIR, "recent_changelog.txt")

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
    top.grab_set()
    
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=10, fill="both", expand=True)
    
    def selecteer():
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, cal.get_date())
        top.destroy()
        
    ctk.CTkButton(top, text="Selecteer", command=selecteer).pack(pady=10)

# ============================================================
# DATA OPSLAG & STANDAARDEN
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
    ]

    uniek = {}
    for d in dagen:
        uniek[(d["naam"], d["datum"])] = d
    return list(uniek.values())

def _standaard_rooster():
    dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
    rooster = {}
    for d in dagen:
        rooster[d] = [
            {"tijd": "08:30 - 10:00", "les": "Geen les"},
            {"tijd": "10:15 - 11:45", "les": "Geen les"},
            {"tijd": "12:15 - 13:45", "les": "Geen les"},
            {"tijd": "14:00 - 15:30", "les": "Geen les"}
        ]
    return rooster

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": _standaard_rooster(),
            "settings": {"theme": "Wit"},
            "vrijedagen": _standaard_vrijedagen(),
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data or not isinstance(data["rooster"], dict): data["rooster"] = _standaard_rooster()
    if "settings" not in data: data["settings"] = {"theme": "Wit"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "vrijedagen" not in data: data["vrijedagen"] = []

    for c in data.get("cijfers", []):
        if "periode" not in c: c["periode"] = "Periode 1"
        if "datum" not in c: c["datum"] = "2026-01-01"
        if "weging" not in c: c["weging"] = "1"

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
        self.geometry("1150x680")
        self.minsize(950, 600)

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan"
        ]
        
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]

        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.theme_combo = None
        self.vrijedagen_listbox = None
        self.clock_label = None

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()

        self.after(100, self.show_intro_screen)
        self.after(2500, lambda: self.toon_update_laadbalk(silent=True))
        self.after(3000, self.check_na_update_log)

    # Update functionaliteiten & Intro ... (ongewijzigd gelaten om performantie te behouden)
    def check_na_update_log(self):
        if os.path.exists(LOG_BESTAND):
            try:
                with open(LOG_BESTAND, "r", encoding="utf-8") as f:
                    log_tekst = f.read()
                if log_tekst.strip():
                    self.toon_changelog_venster(log_tekst)
                os.remove(LOG_BESTAND)
            except Exception: pass

    def toon_changelog_venster(self, log_tekst):
        t = THEMES[self.theme_name]
        log_win = ctk.CTkToplevel(self)
        log_win.title("✨ Update Succesvol!")
        log_win.geometry("500x400")
        log_win.resizable(False, False)
        log_win.configure(fg_color=t["bg_card"])
        log_win.grab_set()
        log_win.update_idletasks()
        x = (log_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (log_win.winfo_screenheight() // 2) - (400 // 2)
        log_win.geometry(f"+{x}+{y}")
        ctk.CTkLabel(log_win, text="🎉 Update succesvol geïnstalleerd!", font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(pady=(20, 5))
        txt_frame = ctk.CTkScrollableFrame(log_win, width=440, height=220, fg_color=t["bg_root"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)
        ctk.CTkLabel(txt_frame, text=log_tekst.strip(), font=("Segoe UI", 12), justify="left", text_color=t["text"], anchor="w").pack(anchor="w", padx=10, pady=10)
        ctk.CTkButton(log_win, text="Sluiten & Ontdekken", fg_color=t["accent"], text_color="white", command=log_win.destroy).pack(pady=20)

    def show_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel(self)
        intro.overrideredirect(True)
        try: intro.attributes("-fullscreen", True)
        except Exception: intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])
        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", 10, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.5, anchor="center")
        intro.attributes("-alpha", 0.0)
        def animate(alpha=0.0, size=10):
            if alpha < 1.0: intro.attributes("-alpha", alpha)
            if size < 50:
                size += 2
                label.configure(font=("Segoe UI", size, "bold"))
            if alpha < 1.0 or size < 50: self.after(15, lambda: animate(alpha + 0.04, size))
            else: self.after(800, fade_out)
        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(15, lambda: fade_out(alpha - 0.05))
            else:
                try:
                    intro.destroy()
                    self.state("zoomed")
                except Exception: pass
        animate()

    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]
        up_win = ctk.CTkToplevel(self)
        up_win.title("GC-OS Updateservice")
        up_win.geometry("520x360")
        up_win.resizable(False, False)
        up_win.configure(fg_color=t["bg_root"])
        up_win.grab_set()
        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (520 // 2)
        y = (up_win.winfo_screenheight() // 2) - (360 // 2)
        up_win.geometry(f"+{x}+{y}")
        main_card = ctk.CTkFrame(up_win, corner_radius=20, fg_color=t["bg_card"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        self.logo_label = ctk.CTkLabel(main_card, text="GC-OS", font=("Segoe UI", 38, "bold"), text_color=t["accent"])
        self.logo_label.pack(pady=(25, 5))
        self.is_updating = False
        status_lbl = ctk.CTkLabel(main_card, text="Systeem is up-to-date ✨", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        status_lbl.pack(pady=5)
        ctk.CTkButton(main_card, text="Sluiten", fg_color=t["accent"], text_color="white", command=up_win.destroy).pack(pady=15)

    # --------------------------------------------------------
    # LAYOUT EN THEMER
    # --------------------------------------------------------
    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])
        if hasattr(self, "sidebar"): self.sidebar.configure(fg_color=t["bg_sidebar"])
        if hasattr(self, "main"): self.main.configure(fg_color=t["bg_main"])
        for btn in self.sidebar_buttons:
            try: btn.configure(fg_color="transparent", hover_color=t["button_hover"], text_color=t["sidebar_text"])
            except Exception: pass
        for lst in [self.hw_list, self.note_list, self.cijfer_list, self.vrijedagen_listbox]:
            if lst is not None:
                lst.configure(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], highlightthickness=0, borderwidth=0)

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        title_label = ctk.CTkLabel(self.sidebar, text="GC‑OS", font=("Segoe UI", 26, "bold"))
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
            btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", fg_color="transparent", command=cmd)
            btn.pack(fill="x", padx=15, pady=4)
            self.sidebar_buttons.append(btn)
        settings_btn = ctk.CTkButton(self.sidebar, text="⚙  Instellingen", anchor="w", fg_color="transparent", command=self.show_settings)
        settings_btn.pack(side="bottom", fill="x", padx=15, pady=15)
        self.sidebar_buttons.append(settings_btn)
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children(): widget.destroy()
        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.vrijedagen_listbox = None
        self.theme_combo = None
        self.clock_label = None

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
                if delta >= 0: upcoming.append((d, delta, naam))
            except Exception: continue
        upcoming.sort(key=lambda x: x[0])
        return upcoming

    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(top_bar, text="Dashboard", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(side="left")
        self.clock_label = ctk.CTkLabel(top_bar, text="", font=("Segoe UI", 14, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right", padx=10)
        self.update_clock()
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)
        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        hw_total = len(self.data["huiswerk"])
        geldige_cijfers = []
        for c in self.data["cijfers"]:
            try: geldige_cijfers.append(float(c.get("cijfer", 0.0)))
            except ValueError: pass
        gem = sum(geldige_cijfers) / len(geldige_cijfers) if geldige_cijfers else None
        ctk.CTkLabel(card, text=f"📚 Huiswerk openstaand: {hw_open} / {hw_total}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=6, padx=15)
        ctk.CTkLabel(card, text=f"📊 Algemeen Gemiddelde: {f'{gem:.2f}' if gem is not None else 'Nog geen cijfers'}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=6, padx=15)
        self.apply_theme()

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self.update_clock)

    # --------------------------------------------------------
    # MODULE: HUISWERK (Rood indien over datum / niet af)
    # --------------------------------------------------------
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerk Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Tkinter Canvas/Frame lijst in plaats van Listbox voor betere individuele kleurcontrole per regel
        self.hw_scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.hw_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._herlaad_huiswerk_lijst()

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Nieuwe Taak", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=15, pady=5)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving")
        self.hw_beschrijving.pack(fill="x", padx=15, pady=5)

        datum_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        datum_frame.pack(fill="x", padx=15, pady=5)
        self.hw_datum = ctk.CTkEntry(datum_frame, placeholder_text="YYYY-MM-DD")
        self.hw_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(datum_frame, text="📅", width=35, command=lambda: kies_datum(self.hw_datum)).pack(side="right")

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self._voeg_huiswerk_toe).pack(fill="x", padx=15, pady=15)

    def _herlaad_huiswerk_lijst(self):
        for widget in self.hw_scroll_frame.winfo_children():
            widget.destroy()
            
        t = THEMES[self.theme_name]
        vandaag = dt.date.today()

        for i, h in enumerate(self.data["huiswerk"]):
            is_af = h.get("afgerond", False)
            status_str = "[X]" if is_af else "[ ]"
            taak_tekst = f"{status_str} {h.get('vak')} - {h.get('beschrijving')} (Te doen voor: {h.get('datum')})"
            
            # Controleer of taak te laat/vandaag is én niet af is -> Kleur Rood
            try:
                deadline = dt.datetime.strptime(h.get('datum', ''), "%Y-%m-%d").date()
                is_te_laat = (deadline <= vandaag) and not is_af
            except Exception:
                is_te_laat = False

            kleur = "#ff3b30" if is_te_laat else t["text"]
            
            row = ctk.CTkFrame(self.hw_scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(row, text=taak_tekst, text_color=kleur, font=("Segoe UI", 12))
            lbl.pack(side="left", padx=5)
            
            btn_vink = ctk.CTkButton(row, text="✓", width=30, height=20, fg_color="#34c759", command=lambda idx=i: self._toggle_huiswerk(idx))
            btn_vink.pack(side="right", padx=2)
            
            btn_del = ctk.CTkButton(row, text="🗑", width=30, height=20, fg_color="#ff3b30", command=lambda idx=i: self._verwijder_huiswerk(idx))
            btn_del.pack(side="right", padx=2)

    def _voeg_huiswerk_toe(self):
        v = self.hw_vak.get()
        b = self.hw_beschrijving.get()
        d = self.hw_datum.get()
        if not b or not d:
            messagebox.showwarning("Waarschuwing", "Vul alle velden in.")
            return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()
        self.hw_beschrijving.delete(0, tk.END)
        self.hw_datum.delete(0, tk.END)

    def _toggle_huiswerk(self, index):
        self.data["huiswerk"][index]["afgerond"] = not self.data["huiswerk"][index]["afgerond"]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    def _verwijder_huiswerk(self, index):
        del self.data["huiswerk"][index]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    # --------------------------------------------------------
    # MODULE: ROOSTER (Nu Volledig Bewerkbaar en Invoegbaar!)
    # --------------------------------------------------------
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="Wekelijks Lesrooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        scroll_rooster = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll_rooster.pack(fill="both", expand=True, padx=20, pady=10)
        
        dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
        self.rooster_inputs = {} # Onthoud invoervelden om op te slaan
        
        for dag in dagen:
            dag_frame = ctk.CTkFrame(scroll_rooster, corner_radius=10, fg_color=t["bg_card"])
            dag_frame.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(dag_frame, text=dag, font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=5)
            
            if dag not in self.data["rooster"]:
                self.data["rooster"][dag] = _standaard_rooster()[dag]
                
            self.rooster_inputs[dag] = []
            
            for i, les in enumerate(self.data["rooster"][dag]):
                les_row = ctk.CTkFrame(dag_frame, fg_color="transparent")
                les_row.pack(fill="x", padx=15, pady=3)
                
                ctk.CTkLabel(les_row, text=f"Uur {i+1}:", font=("Segoe UI", 12, "bold"), width=50).pack(side="left")
                
                tijd_ent = ctk.CTkEntry(les_row, width=120)
                tijd_ent.insert(0, les.get("tijd", ""))
                tijd_ent.pack(side="left", padx=5)
                
                les_ent = ctk.CTkEntry(les_row, placeholder_text="Lesnaam / Vak")
                les_ent.insert(0, les.get("les", "Geen les"))
                les_ent.pack(side="left", fill="x", expand=True, padx=5)
                
                self.rooster_inputs[dag].append({"tijd": tijd_ent, "les": les_ent})
                
        ctk.CTkButton(self.main, text="💾 Wijzigingen Rooster Opslaan", fg_color=t["accent"], text_color="white", command=self._opslaan_rooster).pack(fill="x", padx=25, pady=15)

    def _opslaan_rooster(self):
        for dag, uren in self.rooster_inputs.items():
            nieuwe_uren = []
            for entry_set in uren:
                nieuwe_uren.append({
                    "tijd": entry_set["tijd"].get(),
                    "les": entry_set["les"].get()
                })
            self.data["rooster"][dag] = nieuwe_uren
        opslaan(self.data)
        messagebox.showinfo("Succes", "Je rooster is succesvol opgeslagen en bijgewerkt!")

    # --------------------------------------------------------
    # MODULE: NOTITIES
    # --------------------------------------------------------
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijke Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.note_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self._herlaad_notitie_lijst()
        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        self.note_txt = ctk.CTkTextbox(right_frame, font=("Segoe UI", 12))
        self.note_txt.pack(fill="both", expand=True, padx=15, pady=15)
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(btn_frame, text="Opslaan", fg_color=t["accent"], text_color="white", width=100, command=self._voeg_notitie_toe).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Verwijder", fg_color="#ff3b30", text_color="white", width=100, command=self._verwijder_notitie).pack(side="right")
        self.apply_theme()

    def _herlaad_notitie_lijst(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]: self.note_list.insert(tk.END, n[:35] + "...")

    def _voeg_notitie_toe(self):
        tekst = self.note_txt.get("1.0", tk.END).strip()
        if not tekst: return
        self.data["notities"].append(tekst)
        opslaan(self.data)
        self._herlaad_notitie_lijst()
        self.note_txt.delete("1.0", tk.END)

    def _verwijder_notitie(self):
        sel = self.note_list.curselection()
        if not sel: return
        del self.data["notities"][sel[0]]
        opslaan(self.data)
        self._herlaad_notitie_lijst()

    # --------------------------------------------------------
    # MODULE: CIJFERS (Lijngrafiek per vak in één overzicht)
    # --------------------------------------------------------
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="Cijferregistratie & Voortgangsgrafiek", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        left_side = ctk.CTkFrame(container, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # De herstelde Gecombineerde Multi-Vak Grafiek Sectie
        self.graph_card = ctk.CTkFrame(left_side, corner_radius=15, fg_color=t["bg_card"])
        self.graph_card.pack(fill="both", expand=True, pady=(0, 10))
        self._teken_gecombineerde_grafiek()
        
        list_card = ctk.CTkFrame(left_side, corner_radius=15, fg_color=t["bg_card"], height=180)
        list_card.pack(fill="x")
        list_card.pack_propagate(False)
        
        self.cijfer_list = tk.Listbox(list_card, font=("Segoe UI", 10), activestyle="none")
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sb = tk.Scrollbar(list_card, command=self.cijfer_list.yview)
        sb.pack(side="right", fill="y")
        self.cijfer_list.config(yscrollcommand=sb.set)
        self._herlaad_cijfer_lijst()
        
        # Rechter invoerpaneel
        right_side = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=260)
        right_side.pack(side="right", fill="y", padx=(5, 0))
        right_side.pack_propagate(False)
        
        ctk.CTkLabel(right_side, text="Cijfer Toevoegen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=10)
        
        self.c_vak = ctk.CTkComboBox(right_side, values=self.vakken_hw, state="readonly")
        self.c_vak.set(self.vakken_hw[0])
        self.c_vak.pack(fill="x", padx=15, pady=4)
        
        self.c_num = ctk.CTkEntry(right_side, placeholder_text="Cijfer (bvl. 7.5)")
        self.c_num.pack(fill="x", padx=15, pady=4)
        
        self.c_weging = ctk.CTkEntry(right_side, placeholder_text="Weging")
        self.c_weging.insert(0, "1")
        self.c_weging.pack(fill="x", padx=15, pady=4)
        
        self.c_periode = ctk.CTkComboBox(right_side, values=self.periodes, state="readonly")
        self.c_periode.set(self.periodes[0])
        self.c_periode.pack(fill="x", padx=15, pady=4)
        
        dat_f = ctk.CTkFrame(right_side, fg_color="transparent")
        dat_f.pack(fill="x", padx=15, pady=4)
        self.c_datum = ctk.CTkEntry(dat_f, placeholder_text="YYYY-MM-DD")
        self.c_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dat_f, text="📅", width=35, command=lambda: kies_datum(self.c_datum)).pack(side="right")
        
        ctk.CTkButton(right_side, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self._voeg_cijfer_toe).pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(right_side, text="Verwijder Selectie", fg_color="#ff3b30", text_color="white", command=self._verwijder_cijfer).pack(fill="x", padx=15, pady=2)
        
        self.apply_theme()

    def _herlaad_cijfer_lijst(self):
        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f"{c.get('vak')}: {c.get('cijfer')} | Weging: {c.get('weging')}x ({c.get('periode')} - {c.get('datum')})")

    def _teken_gecombineerde_grafiek(self):
        # Reset grafiekscherm
        for widget in self.graph_card.winfo_children():
            widget.destroy()
            
        t = THEMES[self.theme_name]
        
        # Plot styling configuratie op basis van Light of Dark Mode
        is_dark = (t["mode"] == "Dark")
        bg_col = t["bg_card"]
        text_col = "#ffffff" if is_dark else "#111111"
        
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=bg_col)
        ax = fig.add_subplot(111, facecolor=bg_col)
        
        ax.spines['bottom'].set_color(text_col)
        ax.spines['top'].set_color(text_col)
        ax.spines['left'].set_color(text_col)
        ax.spines['right'].set_color(text_col)
        ax.tick_params(colors=text_col, labelsize=9)
        ax.grid(True, color="#555555" if is_dark else "#cccccc", linestyle="--", linewidth=0.5)
        
        # Sorteer en structureer cijfers per vak chronologisch
        vak_data = {vak: [] for vak in self.vakken_hw}
        
        for c in self.data.get("cijfers", []):
            vak = c.get("vak")
            if vak in vak_data:
                try:
                    cijfer_val = float(c.get("cijfer"))
                    datum_val = dt.datetime.strptime(c.get("datum", "2026-01-01"), "%Y-%m-%d").date()
                    vak_data[vak].append((datum_val, cyan_val := cijfer_val))
                except ValueError: pass

        heeft_data = False
        # Genereer per vak een aparte lijn binnen dezelfde grafiek
        for vak, lijsten in vak_data.items():
            if len(lijsten) > 0:
                lijsten.sort(key=lambda x: x[0]) # Sorteren op datum
                datums = [x[0] for x in lijsten]
                cijfers = [x[1] for x in lijsten]
                
                # Teken de lijn voor dit specifieke vak
                ax.plot(datums, cijfers, marker='o', label=vak, linewidth=2)
                heeft_data = True
                
        if heeft_data:
            ax.legend(loc="upper left", fontsize=8, facecolor=bg_col, labelcolor=text_col)
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, "Nog geen data om lijngrafieken te genereren", 
                    color=text_col, ha='center', va='center', transform=ax.transAxes)
                    
        ax.set_ylim(1.0, 10.0)
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _voeg_cijfer_toe(self):
        v = self.c_vak.get()
        n = self.c_num.get().replace(',', '.')
        w = self.c_weging.get()
        p = self.c_periode.get()
        d = self.c_datum.get()
        
        if not n or not d:
            messagebox.showwarning("Incomplete Data", "Vul a.u.b. een geldig cijfer en datum in.")
            return
        try:
            float(n)
        except ValueError:
            messagebox.showerror("Fout", "Het cijfer moet een getal zijn.")
            return
            
        self.data["cijfers"].append({"vak": v, "cijfer": n, "weging": w, "periode": p, "datum": d})
        opslaan(self.data)
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()
        self.c_num.delete(0, tk.END)
        self.c_datum.delete(0, tk.END)

    def _verwijder_cijfer(self):
        sel = self.cijfer_list.curselection()
        if not sel: return
        del self.data["cijfers"][sel[0]]
        opslaan(self.data)
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()

    # --------------------------------------------------------
    # MODULE: INSTELLINGEN
    # --------------------------------------------------------
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Instellingen & Personalisatie", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(card, text="Kies Thema-kleur:", font=("Segoe UI", 14), text_color=t["text"]).pack(side="left", padx=15, pady=20)
        self.theme_combo = ctk.CTkComboBox(card, values=list(THEMES.keys()), state="readonly", command=self._verander_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(side="left", padx=10)

    def _verander_thema(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
