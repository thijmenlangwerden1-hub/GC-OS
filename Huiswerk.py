import os
import sys
import json
import datetime as dt
import time
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from tkcalendar import Calendar
import urllib.request
import webbrowser
import random
import math

# ============================================================
# GLOBAL CONFIGURATION & THEMES (VERSION 4.5.9v)
# ============================================================

HUIDIGE_VERSIE = "4.5.9v"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

# Geoptimaliseerde UI-Thema's met perfecte contrasten voor de Sidebar en Cards
THEMES = {
    "Wit": {
        "mode": "Light", 
        "bg_root": "#F2F3F7", "bg_sidebar": "#FFFFFF", "bg_main": "#F2F3F7", "bg_card": "#FFFFFF",
        "text": "#111111", "sidebar_text": "#1C1C1E", "button_text": "#FFFFFF", "button_fg": "#007AFF",
        "button_hover": "#0056B3", "accent": "#007AFF", "list_bg": "#FFFFFF", "list_fg": "#111111", "list_select": "#CFE3FF"
    },
    "Zwart": {
        "mode": "Dark", 
        "bg_root": "#0B0B0C", "bg_sidebar": "#16161A", "bg_main": "#0B0B0C", "bg_card": "#1F1F24",
        "text": "#F5F5F7", "sidebar_text": "#F5F5F7", "button_text": "#F5F5F7", "button_fg": "#2C2C31",
        "button_hover": "#3E3E45", "accent": "#0A84FF", "list_bg": "#16161A", "list_fg": "#F5F5F7", "list_select": "#2F2F35"
    },
    "Rood": {
        "mode": "Light", 
        "bg_root": "#FFF5F5", "bg_sidebar": "#2D0808", "bg_main": "#FFF5F5", "bg_card": "#FFFFFF",
        "text": "#4A0000", "sidebar_text": "#FFD6D6", "button_text": "#FFFFFF", "button_fg": "#E63946",
        "button_hover": "#B81D24", "accent": "#E63946", "list_bg": "#FFFFFF", "list_fg": "#4A0000", "list_select": "#FFD6D6"
    },
    "Blauw": {
        "mode": "Light", 
        "bg_root": "#F0F4F8", "bg_sidebar": "#0A192F", "bg_main": "#F0F4F8", "bg_card": "#FFFFFF",
        "text": "#0F2042", "sidebar_text": "#E6F0FF", "button_text": "#FFFFFF", "button_fg": "#172A45",
        "button_hover": "#3066BE", "accent": "#3066BE", "list_bg": "#FFFFFF", "list_fg": "#0F2042", "list_select": "#D6E4FF"
    },
    "Cyberpunk": {
        "mode": "Dark", 
        "bg_root": "#0C0214", "bg_sidebar": "#1A0033", "bg_main": "#0C0214", "bg_card": "#26004C",
        "text": "#00FFCC", "sidebar_text": "#FF007F", "button_text": "#000000", "button_fg": "#00FFCC",
        "button_hover": "#FF007F", "accent": "#00FFCC", "list_bg": "#1A0033", "list_fg": "#00FFCC", "list_select": "#FF007F"
    }
}

MOTIVATIONAL_QUOTES = [
    "Succes is niet finaal, falen is niet fataal: het is de moed om door te gaan die telt.",
    "De beste manier om de toekomst te voorspellen is om hem zelf te creëren.",
    "Loop niet weg voor hardware errors, los ze op!",
    "Code is net als humor. Als je het moet uitleggen, is het slecht.",
    "Blijf gefocust, zet die telefoon op stil en knal die deadlines neer!",
    "Fouten zijn het bewijs dat je probeert.",
    "Het geheim van vooruitkomen is beginnen."
]

GRAFIEK_KLEUREN = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#33FFF0", "#FFA500", "#8A2BE2"]

# ============================================================
# DATA HANDLING PROCEDURES
# ============================================================

def opslaan(data):
    try:
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Fout", f"Kan data niet opslaan:\n{e}")

def laden():
    if not os.path.exists(BESTAND):
        data = {}
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}

    default_keys = {
        "huiswerk": [], "notities": [], "cijfers": [], "rooster": [], "doelen": [],
        "examens": [], "absentie": [], "financien": [], "flashcards": [],
        "settings": {"theme": "Wit", "naam": "Gebruiker", "pomodoro_werk": 25, "pomodoro_rust": 5}
    }
    for k, v in default_keys.items():
        if k not in data:
            data[k] = v
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "naam" not in data["settings"]: data["settings"]["naam"] = "Gebruiker"
    return data

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
# APPLICATION CORE ENGINE
# ============================================================

class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Wit")
        if self.theme_name not in THEMES:
            self.theme_name = "Wit"

        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        ctk.set_default_color_theme("blue")
        self.title("GraafschapCollege‑OS Ultimate Suite")
        self.geometry("1280x800")

        self.vakken_hw = ["Nederlands", "Engels", "Rekenen", "Hardware", "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Vrije Afspraak"]
        self.vakken_cijfers = ["Nederlands", "Engels", "Rekenen", "Hardware", "Netwerken", "Techlab", "Burgerschap", "Loopbaan"]
        
        self.rooster_tijden = [f"{u:02d}:00" for u in range(8, 18)] + [f"{u:02d}:30" for u in range(8, 17)]
        self.rooster_tijden.sort()

        self.sidebar_buttons = []
        self.clock_label = None
        self.rooster_stijl = "Week"
        self.huidige_rooster_datum = dt.date.today()
        
        # Pomodoro status variabelen
        self.pomo_running = False
        self.pomo_tijd_over = 0
        self.pomo_is_werk = True

        self._build_layout()
        self.apply_theme()
        self.after(100, self.show_intro_screen)

    def _build_layout(self):
        # Sidebar Base Frame
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Title
        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="GC‑OS Pro v" + HUIDIGE_VERSIE, font=("Segoe UI", 20, "bold"))
        self.sidebar_title.pack(pady=(30, 20), padx=20)

        # Navigatie Items
        menu_items = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📝  Huiswerk Planner", self.show_huiswerk),
            ("📅  Lesrooster Matrix", self.show_rooster),
            ("🗒  Uitgebreide Notities", self.show_notities),
            ("📊  Cijfer Analyse Centrum", self.show_cijfers),
            ("🎯  Leerdoelen & KPIs", self.show_doelen),
            ("🎓  Examen & Toets Planner", self.show_examens),
            ("⏱  Pomodoro & Flashcards", self.show_studietools),
            ("🛡  Absentie & Aanwezigheid", self.show_absentie),
            ("💳  Studie Financiën", self.show_financien)
        ]

        # Knoppen genereren en opslaan in beheerde lijst voor dynamische uiterlijk-switches
        for text, cmd in menu_items:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                anchor="w", 
                height=40,
                corner_radius=8,
                font=("Segoe UI", 13, "medium"),
                fg_color="transparent", 
                command=cmd
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.sidebar_buttons.append(btn)

        # Systeem Instellingen Knop (Onderaan geankerd)
        self.settings_btn = ctk.CTkButton(
            self.sidebar, 
            text="⚙  Systeem Instellingen", 
            anchor="w", 
            height=40,
            corner_radius=8,
            font=("Segoe UI", 13, "medium"),
            fg_color="transparent", 
            command=self.show_settings
        )
        self.settings_btn.pack(side="bottom", fill="x", padx=15, pady=20)

        # Hoofdscherm Frame
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()
        self.clock_label = None

    def apply_theme(self):
        """
        Zorgt voor een extreem soepele overgang van kleuren over de gehele UI.
        Elke pixel van de sidebar en actieve elementen wordt hier gematcht.
        """
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])
        
        # Sidebar styling updates
        if hasattr(self, "sidebar"): 
            self.sidebar.configure(fg_color=t["bg_sidebar"])
            if hasattr(self, "sidebar_title"):
                self.sidebar_title.configure(text_color=t["sidebar_text"])
            
            # Alle menu-knoppen updaten naar de nieuwe thema-standaard
            for btn in self.sidebar_buttons:
                btn.configure(
                    text_color=t["sidebar_text"],
                    hover_color=t["button_hover"] if t["mode"] == "Dark" else t["list_select"]
                )
            
            # Losse instellingenknop handmatig meenemen
            if hasattr(self, "settings_btn"):
                self.settings_btn.configure(
                    text_color=t["sidebar_text"],
                    hover_color=t["button_hover"] if t["mode"] == "Dark" else t["list_select"]
                )
                
        if hasattr(self, "main"): 
            self.main.configure(fg_color=t["bg_main"])

    def show_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("GC-OS Bootloader")
        intro.overrideredirect(True)
        intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        try: intro.state("zoomed")
        except Exception: pass
        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])

        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", 55, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.45, anchor="center")
        sub_label = ctk.CTkLabel(intro, text="Beveiligde kernel wordt geïnitialiseerd...", font=("Segoe UI", 16), text_color=t["text"])
        sub_label.place(relx=0.5, rely=0.55, anchor="center")
        
        def sluit_intro():
            intro.destroy()
            self.deiconify()
            try: self.state("zoomed")
            except Exception: pass
            self.show_dashboard()
        self.after(1500, sluit_intro)

    # ============================================================
    # MODULE 1: INTERACTIEF DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=20)

        naam = self.data["settings"].get("naam", "Gebruiker")
        ctk.CTkLabel(top_bar, text=f"Systeemonderkant - Welkom, {naam}", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(side="left")

        self.clock_label = ctk.CTkLabel(top_bar, text="", font=("Segoe UI", 14, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right", padx=10)
        self.update_clock()

        # Grid Container voor Widgets
        grid_container = ctk.CTkFrame(self.main, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=25, pady=5)
        grid_container.columnconfigure((0,1), weight=1, uniform="dash_grid")
        grid_container.rowconfigure((0,1), weight=1, uniform="dash_row")

        # Widget 1: Huiswerk & Cijfer KPI Status
        w1 = ctk.CTkFrame(grid_container, corner_radius=15, fg_color=t["bg_card"])
        w1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(w1, text="📊 Algemene Kerngetallen", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=10)
        
        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        ctk.CTkLabel(w1, text=f"• Openstaande Huiswerktaken: {hw_open}", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=20, pady=5)
        
        c_list = [float(c["cijfer"]) for c in self.data["cijfers"] if "cijfer" in c]
        gem = sum(c_list) / len(c_list) if c_list else 0.0
        ctk.CTkLabel(w1, text=f"• Algemeen Gewogen Gemiddelde: {gem:.2f}" if gem > 0 else "• Nog geen cijfers geregistreerd", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=20, pady=5)

        # Widget 2: Rooster Vandaag
        w2 = ctk.CTkFrame(grid_container, corner_radius=15, fg_color=t["bg_card"])
        w2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(w2, text="📅 Rooster Vandaag", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=10)
        
        vandaag_str = str(dt.date.today())
        lessen_vandaag = [l for l in self.data["rooster"] if l.get("datum") == vandaag_str]
        if lessen_vandaag:
            for les in lessen_vandaag[:3]:
                ctk.CTkLabel(w2, text=f"• {les.get('tijd')} - {les.get('vak')} (Lokaal: {les.get('lokaal','NVT')})", font=("Segoe UI", 13), text_color=t["text"]).pack(anchor="w", padx=20, pady=2)
        else:
            ctk.CTkLabel(w2, text="Geen geplande activiteiten voor vandaag.", font=("Segoe UI", 13, "italic"), text_color="gray").pack(anchor="w", padx=20, pady=5)

        # Widget 3: Motivatie & Quotes
        w3 = ctk.CTkFrame(grid_container, corner_radius=15, fg_color=t["bg_card"])
        w3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(w3, text="💡 Dagelijkse Filosofie", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=10)
        ctk.CTkLabel(w3, text=f'"{random.choice(MOTIVATIONAL_QUOTES)}"', font=("Segoe UI", 13, "italic"), text_color=t["text"], wrap=True).pack(anchor="w", padx=20, pady=10)

        # Widget 4: Deadlines & Examens
        w4 = ctk.CTkFrame(grid_container, corner_radius=15, fg_color=t["bg_card"])
        w4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(w4, text="🚨 Kritieke Deadlines", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=10)
        if self.data["examens"]:
            for ex in self.data["examens"][:3]:
                ctk.CTkLabel(w4, text=f"• Toets {ex.get('vak')} op {ex.get('datum')}", font=("Segoe UI", 13), text_color=t["text"]).pack(anchor="w", padx=20, pady=2)
        else:
            ctk.CTkLabel(w4, text="Geen naderende examens of toetsen gepland.", font=("Segoe UI", 13, "italic"), text_color="gray").pack(anchor="w", padx=20, pady=5)

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self.update_clock)

    # ============================================================
    # MODULE 2: HUISWERK PLANNER SYSTEM
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerk Matrix & Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=25, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        left = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(left, font=("Segoe UI", 11), activestyle="none", bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], borderwidth=0, highlightthickness=0)
        self.hw_list.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        right = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=300)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Nieuwe Taak", font=("Segoe UI", 14, "bold"), text_color=t["accent"]).pack(pady=10)
        self.hw_vak = ctk.CTkComboBox(right, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=15, pady=5)

        self.hw_beschrijving = ctk.CTkEntry(right, placeholder_text="Omschrijving of taakomschrijving")
        self.hw_beschrijving.pack(fill="x", padx=15, pady=5)

        self.hw_datum = ctk.CTkEntry(right, placeholder_text="Inleverdatum (yyyy-mm-dd)")
        self.hw_datum.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(right, text="📅 Datum Kiezen", command=lambda: kies_datum(self.hw_datum)).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right, text="Taak Toevoegen", fg_color=t["accent"], text_color="white", command=self.hw_toevoegen).pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(right, text="Vink Af / Status Switchen", command=self.hw_afronden).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right, text="Verwijder Geselecteerde", fg_color="#ff3b30", text_color="white", command=self.hw_verwijderen).pack(fill="x", padx=15, pady=5)

        self._herlaad_huiswerk_lijst()

    def _herlaad_huiswerk_lijst(self):
        self.hw_list.delete(0, tk.END)
        for h in self.data["huiswerk"]:
            status = "✔ Voltooid" if h.get("afgerond") else "❌ Openstaand"
            self.hw_list.insert(tk.END, f"[{status}] {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

    def hw_toevoegen(self):
        v = self.hw_vak.get()
        b = self.hw_beschrijving.get().strip()
        d = self.hw_datum.get().strip()
        if not b or not d: return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()
        self.hw_beschrijving.delete(0, tk.END)

    def hw_afronden(self):
        try:
            idx = self.hw_list.curselection()[0]
            self.data["huiswerk"][idx]["afgerond"] = not self.data["huiswerk"][idx]["afgerond"]
            opslaan(self.data)
            self._herlaad_huiswerk_lijst()
        except Exception: pass

    def hw_verwijderen(self):
        try:
            idx = self.hw_list.curselection()[0]
            self.data["huiswerk"].pop(idx)
            opslaan(self.data)
            self._herlaad_huiswerk_lijst()
        except Exception: pass

    # ============================================================
    # MODULE 3: GEAVANCEERD ROOSTER MATRIX SYSTEM
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(top, text="Geavanceerd Lesrooster Matrix", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(side="left")

        ctk.CTkButton(top, text="Weekoverzicht", width=100, command=lambda: self.wissel_rooster_stijl("Week")).pack(side="right", padx=5)
        ctk.CTkButton(top, text="Maandoverzicht", width=100, command=lambda: self.wissel_rooster_stijl("Maand")).pack(side="right", padx=5)

        nav = ctk.CTkFrame(self.main, fg_color="transparent")
        nav.pack(fill="x", padx=25, pady=5)
        ctk.CTkButton(nav, text="◀ Vorige Periode", width=120, command=self.rooster_vorige).pack(side="left")
        self.rooster_datum_label = ctk.CTkLabel(nav, text="", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        self.rooster_datum_label.pack(side="left", expand=True)
        ctk.CTkButton(nav, text="Volgende Periode ▶", width=120, command=self.rooster_volgende).pack(side="right")

        self.rooster_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.rooster_container.pack(fill="both", expand=True, padx=25, pady=10)

        add = ctk.CTkFrame(self.main, fg_color=t["bg_card"], corner_radius=12)
        add.pack(fill="x", padx=25, pady=15)

        self.rst_vak = ctk.CTkComboBox(add, values=self.vakken_hw, width=140, state="readonly")
        self.rst_vak.set(self.vakken_hw[0])
        self.rst_vak.pack(side="left", padx=10, pady=10)

        self.rst_datum = ctk.CTkEntry(add, placeholder_text="Datum", width=100)
        self.rst_datum.insert(0, str(dt.date.today()))
        self.rst_datum.pack(side="left", padx=5, pady=10)

        self.rst_tijd_combo = ctk.CTkComboBox(add, values=self.rooster_tijden, width=90, state="readonly")
        self.rst_tijd_combo.set("08:30")
        self.rst_tijd_combo.pack(side="left", padx=5, pady=10)

        self.rst_lokaal = ctk.CTkEntry(add, placeholder_text="Lokaal (bijv. D102)", width=100)
        self.rst_lokaal.pack(side="left", padx=5, pady=10)

        self.rst_docent = ctk.CTkEntry(add, placeholder_text="Docent Code", width=90)
        self.rst_docent.pack(side="left", padx=5, pady=10)

        ctk.CTkButton(add, text="➕ Toevoegen", fg_color=t["accent"], text_color="white", width=90, command=self.rooster_toevoegen).pack(side="right", padx=10, pady=10)
        ctk.CTkButton(add, text="🗑 Wissen", fg_color="#ff3b30", text_color="white", width=80, command=self.rooster_wissen).pack(side="right", padx=5, pady=10)

        self.bouw_rooster_weergave()

    def wissel_rooster_stijl(self, stijl):
        self.rooster_stijl = stijl
        self.bouw_rooster_weergave()

    def rooster_vorige(self):
        if self.rooster_stijl == "Week": self.huidige_rooster_datum -= dt.timedelta(days=7)
        else: self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=1) - dt.timedelta(days=1))
        self.bouw_rooster_weergave()

    def rooster_volgende(self):
        if self.rooster_stijl == "Week": self.huidige_rooster_datum += dt.timedelta(days=7)
        else: self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
        self.bouw_rooster_weergave()

    def bouw_rooster_weergave(self):
        for w in self.rooster_container.winfo_children(): w.destroy()
        t = THEMES[self.theme_name]

        if self.rooster_stijl == "Week":
            for col_idx in range(5):
                self.rooster_container.grid_columnconfigure(col_idx, weight=1, uniform="dag_kolom")
            self.rooster_container.grid_rowconfigure(0, weight=1)

            start_vd_week = self.huidige_rooster_datum - dt.timedelta(days=self.huidige_rooster_datum.weekday())
            eind_vd_week = start_vd_week + dt.timedelta(days=4)
            self.rooster_datum_label.configure(text=f"Week Matrix: {start_vd_week.strftime('%d %b')} t/m {eind_vd_week.strftime('%d %b %Y')}")

            dagen_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
            for i, naam in enumerate(dagen_namen):
                dag_datum = start_vd_week + dt.timedelta(days=i)
                dag_str = dag_datum.strftime("%Y-%m-%d")

                col = ctk.CTkFrame(self.rooster_container, fg_color=t["bg_card"], corner_radius=12)
                col.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)

                header = ctk.CTkFrame(col, fg_color=t["accent"] if t["mode"] == "Dark" else t["button_fg"], corner_radius=8, height=40)
                header.pack(fill="x", padx=4, pady=4)
                header.pack_propagate(False)
                ctk.CTkLabel(header, text=f"{naam} ({dag_datum.strftime('%d-%m')})", font=("Segoe UI", 12, "bold"), text_color="#ffffff" if t["mode"] == "Dark" else t["text"]).pack(expand=True)

                scroll = ctk.CTkScrollableFrame(col, fg_color="transparent", corner_radius=0)
                scroll.pack(fill="both", expand=True, padx=2, pady=2)

                dag_lessen = [l for l in self.data["rooster"] if l.get("datum") == dag_str]
                dag_lessen.sort(key=lambda x: x.get("tijd", ""))

                for les in dag_lessen:
                    les_box = ctk.CTkFrame(scroll, fg_color=t["bg_root"], corner_radius=8, border_width=1, border_color=t["button_hover"])
                    les_box.pack(fill="x", padx=4, pady=4)
                    ctk.CTkLabel(les_box, text=les.get('tijd'), font=("Segoe UI", 11, "bold"), text_color=t["accent"]).pack(anchor="w", padx=8, pady=(4, 0))
                    ctk.CTkLabel(les_box, text=les.get('vak'), font=("Segoe UI", 12, "bold"), text_color=t["text"]).pack(anchor="w", padx=8, pady=0)
                    ctk.CTkLabel(les_box, text=f"📍 {les.get('lokaal','--')} | 👨‍🏫 {les.get('docent','--')}", font=("Segoe UI", 10), text_color="gray").pack(anchor="w", padx=8, pady=(0, 4))
        else:
            scroll_maand = ctk.CTkScrollableFrame(self.rooster_container, fg_color=t["bg_card"], corner_radius=15)
            scroll_maand.pack(fill="both", expand=True)
            
            m_jaar, m_maand = self.huidige_rooster_datum.year, self.huidige_rooster_datum.month
            self.rooster_datum_label.configure(text=self.huidige_rooster_datum.strftime("%B %Y"))

            maand_lessen = []
            for l in self.data["rooster"]:
                try:
                    ld = dt.datetime.strptime(l.get("datum"), "%Y-%m-%d").date()
                    if ld.year == m_jaar and ld.month == m_maand: maand_lessen.append(l)
                except Exception: pass

            maand_lessen.sort(key=lambda x: (x.get("datum"), x.get("tijd")))
            if not maand_lessen:
                ctk.CTkLabel(scroll_maand, text="Geen lesrooster data voor deze maand.", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=25)
            else:
                for les in maand_lessen:
                    r_box = ctk.CTkFrame(scroll_maand, fg_color=t["bg_root"], corner_radius=8)
                    r_box.pack(fill="x", padx=15, pady=4)
                    ctk.CTkLabel(r_box, text=f"📅 {les.get('datum')}  |  ⏰ {les.get('tijd')}  |  📘 {les.get('vak')}  |  📍 Lokaal: {les.get('lokaal','--')}  |  Docent: {les.get('docent','--')}", font=("Segoe UI", 12), text_color=t["text"]).pack(side="left", padx=15, pady=8)

    def rooster_toevoegen(self):
        v = self.rst_vak.get()
        d = self.rst_datum.get().strip()
        t = self.rst_tijd_combo.get()
        lok = self.rst_lokaal.get().strip() or "NVT"
        doc = self.rst_docent.get().strip() or "NVT"
        if d and t:
            for les in self.data["rooster"]:
                if les.get("datum") == d and les.get("tijd") == t:
                    messagebox.showwarning("Roosterconflict", "Er staat al een les gepland op dit tijdstip!")
                    return
            self.data["rooster"].append({"vak": v, "datum": d, "tijd": t, "lokaal": lok, "docent": doc})
            opslaan(self.data)
            self.bouw_rooster_weergave()

    def rooster_wissen(self):
        if messagebox.askyesno("Synchronisatie", "Wilt u alle lesrooster data definitief wissen?"):
            self.data["rooster"] = []
            opslaan(self.data)
            self.bouw_rooster_weergave()

    # ============================================================
    # MODULE 4: UITGEBREIDE NOTITIES & TEXTPAD
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijk Kenniscentrum & Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=25, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.note_list = tk.Listbox(container, font=("Segoe UI", 11), bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], borderwidth=0, highlightthickness=0)
        self.note_list.pack(side="left", fill="both", expand=True, padx=(0, 15))
        self.note_list.bind("<<ListboxSelect>>", self._laad_notitie_in_pad)

        right = ctk.CTkFrame(container, fg_color=t["bg_card"], width=350, corner_radius=15)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Kladblok Editor", font=("Segoe UI", 14, "bold"), text_color=t["accent"]).pack(pady=10)
        self.note_text = ctk.CTkTextbox(right, width=310, height=350)
        self.note_text.pack(padx=15, pady=5)

        ctk.CTkButton(right, text="💾 Document Opslaan", fg_color=t["accent"], text_color="white", command=self.notitie_toevoegen).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right, text="🗑 Notitie Verwijderen", fg_color="#ff3b30", text_color="white", command=self.notitie_verwijderen).pack(fill="x", padx=15, pady=5)

        self._herlaad_notities()

    def _herlaad_notities(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]:
            kort = n.get("inhoud", "").split('\n')[0][:30] if isinstance(n, dict) else str(n)[:30]
            self.note_list.insert(tk.END, kort or "Lege notitie")

    def _laad_notitie_in_pad(self, event):
        try:
            idx = self.note_list.curselection()[0]
            item = self.data["notities"][idx]
            self.note_text.delete("1.0", tk.END)
            if isinstance(item, dict): self.note_text.insert("1.0", item.get("inhoud", ""))
            else: self.note_text.insert("1.0", str(item))
        except Exception: pass

    def notitie_toevoegen(self):
        txt = self.note_text.get("1.0", tk.END).strip()
        if not txt: return
        self.data["notities"].append({"inhoud": txt, "datum": str(dt.date.today())})
        opslaan(self.data)
        self._herlaad_notities()
        self.note_text.delete("1.0", tk.END)

    def notitie_verwijderen(self):
        try:
            idx = self.note_list.curselection()[0]
            self.data["notities"].pop(idx)
            opslaan(self.data)
            self._herlaad_notities()
            self.note_text.delete("1.0", tk.END)
        except Exception: pass

    # ============================================================
    # MODULE 5: CIJFER ANALYSE CENTRUM (GRAFIEKEN)
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie & Prestatie Analyse", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=25, pady=15)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=5)

        left = ctk.CTkFrame(container, fg_color=t["bg_card"], width=320, corner_radius=15)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="Nieuw Cijfer Boeken", font=("Segoe UI", 14, "bold"), text_color=t["accent"]).pack(pady=10)
        self.cijfer_vak = ctk.CTkComboBox(left, values=self.vakken_cijfers, state="readonly")
        self.cijfer_vak.set(self.vakken_cijfers[0])
        self.cijfer_vak.pack(fill="x", padx=15, pady=5)

        self.cijfer_val = ctk.CTkEntry(left, placeholder_text="Resultaat (bijv. 7.3)")
        self.cijfer_val.pack(fill="x", padx=15, pady=5)

        self.cijfer_weging = ctk.CTkEntry(left, placeholder_text="Weging (bijv. 1, 2 of 3)")
        self.cijfer_weging.insert(0, "1")
        self.cijfer_weging.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(left, text="Cijfer Vastleggen", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(left, text="Vakgemiddelden:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=(15, 2))
        scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for i, vak in enumerate(self.vakken_cijfers):
            c_voor_vak = [c for c in self.data["cijfers"] if c.get("vak") == vak]
            totaal_punten = sum(float(c["cijfer"]) * float(c.get("weging", 1)) for c in c_voor_vak)
            totaal_weging = sum(float(c.get("weging", 1)) for c in c_voor_vak)
            
            g = totaal_punten / totaal_weging if totaal_weging > 0 else None
            g_txt = f"{g:.2f}" if g is not None else "--"
            
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(anchor="w", fill="x", pady=2)
            tk.Label(f, text="■", fg=GRAFIEK_KLEUREN[i % len(GRAFIEK_KLEUREN)], bg=t["bg_card"]).pack(side="left")
            ctk.CTkLabel(f, text=f" {vak}: {g_txt}", font=("Segoe UI", 12), text_color=t["text"]).pack(side="left")

    def cijfer_toevoegen(self):
        try:
            v = self.cijfer_vak.get()
            val = self.cijfer_val.get().replace(",", ".")
            weg = self.cijfer_weging.get()
            if not val: return
            float(val) # validatie
            self.data["cijfers"].append({"vak": v, "cijfer": val, "weging": weg})
            opslaan(self.data)
            self.show_cijfers()
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig getal in voor het cijfer.")

    # ============================================================
    # TIJDELIJKE FALLBACKS VOOR ONBREKENDE SCHERMEN (POLISH)
    # ============================================================
    def show_doelen(self): 
        self.clear_main()
        ctk.CTkLabel(self.main, text="🎯 Leerdoelen & KPIs Dashboard", font=("Segoe UI", 24, "bold"), text_color=THEMES[self.theme_name]["text"]).pack(padx=25, pady=20)

    def show_examens(self): 
        self.clear_main()
        ctk.CTkLabel(self.main, text="🎓 Examen & Toets Matrix", font=("Segoe UI", 24, "bold"), text_color=THEMES[self.theme_name]["text"]).pack(padx=25, pady=20)

    def show_studietools(self): 
        self.clear_main()
        ctk.CTkLabel(self.main, text="⏱ Pomodoro Kernel & Flashcards", font=("Segoe UI", 24, "bold"), text_color=THEMES[self.theme_name]["text"]).pack(padx=25, pady=20)

    def show_absentie(self): 
        self.clear_main()
        ctk.CTkLabel(self.main, text="🛡 Absentieregistratie Matrix", font=("Segoe UI", 24, "bold"), text_color=THEMES[self.theme_name]["text"]).pack(padx=25, pady=20)

    def show_financien(self): 
        self.clear_main()
        ctk.CTkLabel(self.main, text="💳 Financiële Knooppunten & Subsidies", font=("Segoe UI", 24, "bold"), text_color=THEMES[self.theme_name]["text"]).pack(padx=25, pady=20)

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="⚙ Systeem Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=25, pady=20)
        
        box = ctk.CTkFrame(self.main, fg_color=t["bg_card"], corner_radius=15)
        box.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        ctk.CTkLabel(box, text="Kies Systeemthema:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        theme_selector = ctk.CTkComboBox(box, values=list(THEMES.keys()), state="readonly")
        theme_selector.set(self.theme_name)
        theme_selector.pack(anchor="w", padx=20, pady=5)
        
        def verander_thema():
            self.theme_name = theme_selector.get()
            self.data["settings"]["theme"] = self.theme_name
            opslaan(self.data)
            self.apply_theme()
            self.show_settings()
            
        ctk.CTkButton(box, text="Thema Toepassen", fg_color=t["accent"], text_color=t["button_text"], command=verander_thema).pack(anchor="w", padx=20, pady=15)

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
