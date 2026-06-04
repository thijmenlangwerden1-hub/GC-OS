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
import threading

# ==============================================================================
# 0. REPOSITORY CONFIGURATIE & DEPLOYMENT TARGETS (CRITIEK UPDATE SYSTEEM)
# ==============================================================================
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

# ==============================================================================
# 1. GLOBALE CONFIGURATIE, CODENAMES & SYSTEM ARCHITECTURE
# ==============================================================================
HUIDIGE_VERSIE = "8.9.9v"  # Handmatig opgewaardeerd naar de stabiele enterprise target
CODENAME = "QuantumValkyrie"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_matrix_data.json")

# UI Kleurenpaletten & Geavanceerde Thema Matrix (Getuned voor high-end monitors)
THEMES = {
    "Wit": {
        "mode": "Light", 
        "bg_root": "#F4F6F9", "bg_sidebar": "#FFFFFF", "bg_main": "#F4F6F9", "bg_card": "#FFFFFF",
        "text": "#1E293B", "sidebar_text": "#0F172A", "button_text": "#FFFFFF", "button_fg": "#4F46E5",
        "button_hover": "#4338CA", "accent": "#4F46E5", "list_bg": "#FFFFFF", "list_fg": "#1E293B", "list_select": "#E0E7FF"
    },
    "Zwart": {
        "mode": "Dark", 
        "bg_root": "#09090B", "bg_sidebar": "#18181B", "bg_main": "#09090B", "bg_card": "#27272A",
        "text": "#F4F4F5", "sidebar_text": "#F4F4F5", "button_text": "#F4F4F5", "button_fg": "#3F3F46",
        "button_hover": "#52525B", "accent": "#3B82F6", "list_bg": "#18181B", "list_fg": "#F4F4F5", "list_select": "#3F3F46"
    },
    "Rood": {
        "mode": "Dark", 
        "bg_root": "#1A0505", "bg_sidebar": "#2D0808", "bg_main": "#1A0505", "bg_card": "#3D0C0C",
        "text": "#FFEBEB", "sidebar_text": "#FFD6D6", "button_text": "#FFFFFF", "button_fg": "#DC2626",
        "button_hover": "#B91C1C", "accent": "#EF4444", "list_bg": "#2D0808", "list_fg": "#FFEBEB", "list_select": "#7F1D1D"
    },
    "Blauw": {
        "mode": "Dark", 
        "bg_root": "#020817", "bg_sidebar": "#0F172A", "bg_main": "#020817", "bg_card": "#1E293B",
        "text": "#F8FAFC", "sidebar_text": "#F1F5F9", "button_text": "#FFFFFF", "button_fg": "#2563EB",
        "button_hover": "#1D4ED8", "accent": "#3B82F6", "list_bg": "#0F172A", "list_fg": "#F8FAFC", "list_select": "#334155"
    },
    "Cyberpunk": {
        "mode": "Dark", 
        "bg_root": "#03000A", "bg_sidebar": "#0D001A", "bg_main": "#03000A", "bg_card": "#1A0033",
        "text": "#00FFCC", "sidebar_text": "#FF007F", "button_text": "#000000", "button_fg": "#00FFCC",
        "button_hover": "#FF007F", "accent": "#00FFCC", "list_bg": "#0D001A", "list_fg": "#00FFCC", "list_select": "#FF007F"
    },
    "Matrix": {
        "mode": "Dark", 
        "bg_root": "#000000", "bg_sidebar": "#050505", "bg_main": "#000000", "bg_card": "#0A0A0A",
        "text": "#33FF33", "sidebar_text": "#00FF00", "button_text": "#000000", "button_fg": "#00FF00",
        "button_hover": "#008800", "accent": "#00FF00", "list_bg": "#050505", "list_fg": "#33FF33", "list_select": "#004400"
    }
}

MOTIVATIONAL_QUOTES = [
    "Succes is niet finaal, falen is niet fataal: het is de moed om door te gaan.",
    "De beste manier om de toekomst te voorspellen is om hem zelf te bouwen.",
    "Blijf compilen, blijf pushen, geef nooit op.",
    "Code is net als humor. Als je het moet uitleggen, is het slecht.",
    "Focus op de progressie, niet op de perfectie.",
    "Fouten zijn het bewijs dat je de grenzen van je intelligentie opzoekt.",
    "De enige slechte code is de code die je morgen moet herschrijven."
]

GRAFIEK_KLEUREN = ["#6366F1", "#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#EC4899", "#8B5CF6", "#14B8A6"]

# ==============================================================================
# 2. PERSISTENT STORAGE & DATA ENCRYPTION ENGINE
# ==============================================================================
def IO_SafeSave(data):
    try:
        with open(BESTAND, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        messagebox.showerror("Kritieke I/O Fout", f"Kan systeemdata niet wegschrijven naar schijf:\n{e}")

def IO_SafeLoad():
    if not os.path.exists(BESTAND):
        data = {}
    else:
        with open(BESTAND, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    SysteemDefaults = {
        "huiswerk": [], "notities": [], "cijfers": [], "rooster": [], "doelen": [],
        "examens": [], "absentie": [], "financien": [], "flashcards": [],
        "settings": {
            "theme": "Zwart", 
            "naam": "Student", 
            "pomodoro_werk": 25, 
            "pomodoro_rust": 5, 
            "automatisch_backups": True,
            "geinstalleerde_versie": "0.0.0"
        }
    }
    
    for sleutel, waarde in SysteemDefaults.items():
        if sleutel not in data:
            data[sleutel] = waarde

    for k, v in SysteemDefaults["settings"].items():
        if k not in data["settings"]:
            data["settings"][k] = v
            
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Zwart"
    if "naam" not in data["settings"]: data["settings"]["naam"] = "Student"
    return data

def UI_DateDialog(target_entry):
    venster = ctk.CTkToplevel()
    venster.title("Selecteer Systeemdatum")
    venster.geometry("340x360")
    venster.resizable(False, False)
    venster.grab_set()
    
    kalender = Calendar(venster, selectmode='day', date_pattern='yyyy-mm-dd')
    kalender.pack(pady=15, fill="both", expand=True, padx=15)
    
    def BevestigDatum():
        target_entry.delete(0, tk.END)
        target_entry.insert(0, kalender.get_date())
        venster.destroy()
        
    ctk.CTkButton(venster, text="Datum Toepassen", command=BevestigDatum).pack(pady=15)

# ==============================================================================
# 3. CORE APPLICATION ENGINE & LAYOUT MANAGER
# ==============================================================================
class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        # Systeembestanden laden
        self.data = IO_SafeLoad()
        self.theme_name = self.data["settings"].get("theme", "Zwart")
        if self.theme_name not in THEMES:
            self.theme_name = "Zwart"

        # Basis UI initialisatie
        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        self.title(f"GraafschapCollege-OS Core — Enterprise Edition Suite [v{HUIDIGE_VERSIE}]")
        self.geometry("1440x900")
        self.minimum_width = 1200
        self.minimum_height = 800
        self.minsize(self.minimum_width, self.minimum_height)

        # Systeemvariabelen & Opleidingsmatrices
        self.vakken_lijst = ["Nederlands", "Engels", "Rekenen", "Software Development", "Hardware & Infrastructure", "Databases", "Burgerschap", "Loopbaan", "Project Management", "Cybersecurity"]
        self.tijd_slots = [f"{uur:02d}:{minuut:02d}" for uur in range(8, 18) for minuut in (0, 30)]
        self.tijd_slots.sort()

        self.sidebar_buttons = {}
        self.klok_thread_actief = True
        self.huidige_rooster_modus = "Week"
        self.referentie_datum = dt.date.today()
        
        # Threaded Pomodoro Engine Variabelen
        self.pomo_loopt = False
        self.pomo_tijd_resterend = 0
        self.pomo_modus_is_werk = True
        self.pomo_timer_thread = None

        # Componenten bouwen
        self._Core_Build_Layout()
        self.Core_Apply_Theme()
        
        # Boot sequence triggeren
        self.after(200, self.Core_Bootloader_Sequence)

    def _Core_Build_Layout(self):
        # Ultra-Smooth Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_header = ctk.CTkLabel(self.sidebar, text="GC-OS ULTIMATE", font=("Segoe UI", 22, "bold"))
        self.sidebar_header.pack(pady=(35, 5), padx=25, anchor="w")
        
        self.sidebar_sub = ctk.CTkLabel(self.sidebar, text=f"Kernel: {CODENAME} Build", font=("Segoe UI", 11), text_color="gray")
        self.sidebar_sub.pack(pady=(0, 25), padx=25, anchor="w")

        # Navigatie Systeem Matrix Map
        menu_configuratie = [
            ("dashboard", "🏠  Dashboard Overzicht", self.Module_Dashboard),
            ("huiswerk", "📝  Huiswerk Projecten", self.Module_Huiswerk),
            ("rooster", "📅  Matrix Lesrooster", self.Module_Rooster),
            ("notities", "🗒  Kennisbank & Notities", self.Module_Notities),
            ("cijfers", "📊  Cijfer & KPI Analyse", self.Module_Cijfers),
            ("doelen", "🎯  Mijlpalen & Doelen", self.Module_Doelen),
            ("examens", "🎓  Examen & Toetsing", self.Module_Examens),
            ("studietools", "⏱  Pomodoro & Flashcards", self.Module_Studietools),
            ("absentie", "🛡  Absentieregistratie", self.Module_Absentie),
            ("financien", "💳  Studiefinanciering", self.Module_Financien)
        ]

        for sleutel, tekst, methode in menu_configuratie:
            knop = ctk.CTkButton(
                self.sidebar, 
                text=tekst, 
                anchor="w", 
                height=42,
                corner_radius=10,
                font=("Segoe UI", 13, "medium"),
                fg_color="transparent", 
                command=methode
            )
            knop.pack(fill="x", padx=15, pady=4)
            self.sidebar_buttons[sleutel] = knop

        # Systeem Configuraties Knop onderaan verankeren
        self.instellingen_knop = ctk.CTkButton(
            self.sidebar, 
            text="⚙  Systeem Configuraties", 
            anchor="w", 
            height=42,
            corner_radius=10,
            font=("Segoe UI", 13, "medium"),
            fg_color="transparent", 
            command=self.Module_Settings
        )
        self.instellingen_knop.pack(side="bottom", fill="x", padx=15, pady=25)

        # Hoofd Render Window (Canvas)
        self.canvas = ctk.CTkFrame(self, corner_radius=0)
        self.canvas.pack(side="right", fill="both", expand=True)

    def Core_Clear_Canvas(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

    def Core_Apply_Theme(self):
        thema = THEMES[self.theme_name]
        ctk.set_appearance_mode(thema["mode"])
        self.configure(fg_color=thema["bg_root"])
        
        self.sidebar.configure(fg_color=thema["bg_sidebar"])
        self.sidebar_header.configure(text_color=thema["accent"])
        self.canvas.configure(fg_color=thema["bg_main"])

        for knop in self.sidebar_buttons.values():
            knop.configure(
                text_color=thema["sidebar_text"],
                hover_color=thema["button_hover"] if thema["mode"] == "Dark" else thema["list_select"]
            )
        self.instellingen_knop.configure(
            text_color=thema["sidebar_text"],
            hover_color=thema["button_hover"] if thema["mode"] == "Dark" else thema["list_select"]
        )

    def Core_Highlight_Menu(self, actieve_sleutel):
        thema = THEMES[self.theme_name]
        for sleutel, knop in self.sidebar_buttons.items():
            if sleutel == actieve_sleutel:
                knop.configure(fg_color=thema["button_fg"], text_color=thema["button_text"])
            else:
                knop.configure(fg_color="transparent", text_color=thema["sidebar_text"])

    # ==============================================================================
    # BOOTLOADER SEQUENCE MET INTELLIGENTE UPDATE-GUARD (v8.9.9v)
    # ==============================================================================
    def Core_Bootloader_Sequence(self):
        thema = THEMES[self.theme_name]
        geinstalleerde_v = self.data["settings"].get("geinstalleerde_versie", "0.0.0")
        is_nieuwe_update = (geinstalleerde_v != HUIDIGE_VERSIE)

        boot_window = ctk.CTkToplevel()
        boot_window.title("GC-OS Engine Booting...")
        boot_window.overrideredirect(True)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        boot_window.geometry(f"{sw}x{sh}+0+0")
        boot_window.lift()
        boot_window.attributes("-topmost", True)
        boot_window.configure(fg_color=thema["bg_root"])

        container = ctk.CTkFrame(boot_window, fg_color=thema["bg_card"], corner_radius=24, border_width=1, border_color=thema["button_hover"])
        container.place(relx=0.5, rely=0.5, anchor="center", width=650, height=420)

        badge_tekst = f"INSTALLING UPDATE v{HUIDIGE_VERSIE}" if is_nieuwe_update else f"FIRMWARE v{HUIDIGE_VERSIE} [STABLE]"
        versie_badge = ctk.CTkFrame(container, fg_color=thema["button_fg"] if is_nieuwe_update else "#10B981", corner_radius=6)
        versie_badge.place(relx=0.5, rely=0.15, anchor="center")
        ctk.CTkLabel(versie_badge, text=badge_tekst, font=("Segoe UI Mono", 11, "bold"), text_color="white", padx=10, pady=2).pack()

        titel_label = ctk.CTkLabel(container, text="GraafschapCollege-OS", font=("Segoe UI", 38, "bold"), text_color=thema["text"])
        titel_label.place(relx=0.5, rely=0.28, anchor="center")
        
        sub_label = ctk.CTkLabel(container, text="", font=("Segoe UI Mono", 12), text_color="gray")
        sub_label.place(relx=0.5, rely=0.38, anchor="center")

        self.percentage_label = ctk.CTkLabel(container, text="0%", font=("Segoe UI", 48, "bold"), text_color=thema["accent"])
        self.percentage_label.place(relx=0.5, rely=0.55, anchor="center")

        progressiebalk = ctk.CTkProgressBar(container, width=480, height=6, mode="determinate", progress_color=thema["accent"], fg_color=thema["bg_root"])
        progressiebalk.place(relx=0.5, rely=0.70, anchor="center")
        progressiebalk.set(0)

        status_label = ctk.CTkLabel(container, text="Initializing...", font=("Segoe UI Mono", 11), text_color="gray")
        status_label.place(relx=0.5, rely=0.78, anchor="center")

        foot_info = ctk.CTkLabel(container, text="SECURE BOOT MATRIX STATE: ACTIVE", font=("Segoe UI Mono", 10), text_color="gray")
        foot_info.place(relx=0.5, rely=0.92, anchor="center")

        def SimuleerStappen(stap):
            if stap <= 100:
                progressiebalk.set(stap / 100)
                self.percentage_label.configure(text=f"{stap}%")
                
                if is_nieuwe_update:
                    sub_label.configure(text=f"CODENAME: {CODENAME}.sys // WRITING NEW FIRMWARE")
                    if stap == 12: status_label.configure(text="› Unpacking matrix core update files & verifying hashes...")
                    elif stap == 35: status_label.configure(text="› Rewriting database keys & mapping virtual structural fields...")
                    elif stap == 58: status_label.configure(text="› Compiling UI assets & flushing old cache directories...")
                    elif stap == 82: status_label.configure(text="› Re-encrypting database profiles with 128-bit security layer...")
                    elif stap == 96: status_label.configure(text="› Installation complete. Updating system version registry...")
                    vertraging = random.randint(15, 45) if 30 < stap < 75 else random.randint(8, 20)
                else:
                    sub_label.configure(text=f"CODENAME: {CODENAME}.sys // VERIFYING INTEGRITY")
                    if stap == 5: status_label.configure(text="› Checking active kernel registration...")
                    elif stap == 50: status_label.configure(text="› System state matches target version. Skipping install pipeline.")
                    elif stap == 90: status_label.configure(text="› Hot-boot successfully authorized.")
                    vertraging = random.randint(1, 4)

                self.after(vertraging, lambda: SimuleerStappen(stap + 1))
            else:
                if is_nieuwe_update:
                    self.data["settings"]["geinstalleerde_versie"] = HUIDIGE_VERSIE
                    IO_SafeSave(self.data)

                boot_window.destroy()
                self.deiconify()
                try: self.state("zoomed")
                except Exception: pass
                self.Module_Dashboard()

        SimuleerStappen(0)

    # ==============================================================================
    # MODULE 1: INTERACTIEF CORE DASHBOARD
    # ==============================================================================
    def Module_Dashboard(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("dashboard")
        thema = THEMES[self.theme_name]

        kop_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        kop_frame.pack(fill="x", padx=35, pady=25)

        gebruikersnaam = self.data["settings"].get("naam", "Student")
        ctk.CTkLabel(kop_frame, text=f"Systeem Matrix — Welkom terug, {gebruikersnaam}", font=("Segoe UI", 28, "bold"), text_color=thema["text"]).pack(side="left")

        self.dashboard_klok = ctk.CTkLabel(kop_frame, text="", font=("Segoe UI", 15, "bold"), text_color=thema["accent"])
        self.dashboard_klok.pack(side="right", padx=15)
        self._Live_Klok_Loop()

        grid = ctk.CTkFrame(self.canvas, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=35, pady=5)
        grid.columnconfigure((0, 1), weight=1, uniform="dash_grid")
        grid.rowconfigure((0, 1), weight=1, uniform="dash_row")

        card1 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card1.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card1, text="📊 Cijfer Analyse & Gemiddelden", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        alle_cijfers = [float(c["cijfer"]) for c in self.data["cijfers"] if "cijfer" in c]
        algemeen_gemiddelde = sum(alle_cijfers) / len(alle_cijfers) if alle_cijfers else 0.0
        ctk.CTkLabel(card1, text=f"• Totaal aantal ingevoerde cijfers: {len(alle_cijfers)}", font=("Segoe UI", 14), text_color=thema["text"]).pack(anchor="w", padx=25, pady=4)
        ctk.CTkLabel(card1, text=f"• Gewogen Algemeen Gemiddelde: {algemeen_gemiddelde:.2f}", font=("Segoe UI", 14), text_color=thema["text"]).pack(anchor="w", padx=25, pady=4)

        card2 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card2.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card2, text="📅 Agenda & Lessen Vandaag", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        vandaag_iso = str(dt.date.today())
        lessen_vandaag = [l for l in self.data["rooster"] if l.get("datum") == vandaag_iso]
        if lessen_vandaag:
            for les in lessen_vandaag[:4]:
                ctk.CTkLabel(card2, text=f"⏰ {les.get('tijd')} | {les.get('vak')} [Lokaal: {les.get('lokaal')}]", font=("Segoe UI", 13), text_color=thema["text"]).pack(anchor="w", padx=25, pady=3)
        else:
            ctk.CTkLabel(card2, text="Geen lesactiviteiten gepland voor vandaag.", font=("Segoe UI", 13, "italic"), text_color="gray").pack(anchor="w", padx=25, pady=10)

        card3 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card3.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card3, text="💡 Systeem Filosofie", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(card3, text=f'"{random.choice(MOTIVATIONAL_QUOTES)}"', font=("Segoe UI", 13, "italic"), text_color=thema["text"], wrap=True).pack(anchor="w", padx=25, pady=10)

        card4 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card4.grid(row=1, column=1, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card4, text="🚨 Kritieke Openstaande Deadlines", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        open_taken = [h for h in self.data["huiswerk"] if not h.get("afgerond", False)]
        if open_taken:
            for taak in open_taken[:4]:
                ctk.CTkLabel(card4, text=f"⏳ {taak.get('datum')} - {taak.get('vak')}: {taak.get('beschrijving')[:35]}...", font=("Segoe UI", 13), text_color=thema["text"]).pack(anchor="w", padx=25, pady=3)
        else:
            ctk.CTkLabel(card4, text="Alle systemen operationeel. Geen openstaande taken!", font=("Segoe UI", 13, "italic"), text_color="gray").pack(anchor="w", padx=25, pady=10)

    def _Live_Klok_Loop(self):
        if hasattr(self, "dashboard_klok") and self.dashboard_klok.winfo_exists():
            self.dashboard_klok.configure(text=dt.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self._Live_Klok_Loop)

    # ==============================================================================
    # MODULE 2: ADVANCED HUISWERK PLANNER SYSTEM
    # ==============================================================================
    def Module_Huiswerk(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("huiswerk")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Huiswerk Projecten & Management", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        links.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.hw_listbox = tk.Listbox(links, font=("Segoe UI", 12), activestyle="none", bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.hw_listbox.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Nieuw Project Registreren", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_hw_vak = ctk.CTkComboBox(rechts, values=self.vakken_lijst, state="readonly")
        self.entry_hw_vak.set(self.vakken_lijst[0])
        self.entry_hw_vak.pack(fill="x", padx=20, pady=8)

        self.entry_hw_desc = ctk.CTkEntry(rechts, placeholder_text="Projectomschrijving")
        self.entry_hw_desc.pack(fill="x", padx=20, pady=8)

        self.entry_hw_datum = ctk.CTkEntry(rechts, placeholder_text="Inleverdatum (YYYY-MM-DD)")
        self.entry_hw_datum.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="📅 Systeemdatum Selecteren", command=lambda: UI_DateDialog(self.entry_hw_datum)).pack(fill="x", padx=20, pady=6)
        ctk.CTkButton(rechts, text="🚀 Project Toevoegen", fg_color=thema["accent"], text_color="white", command=self._Hw_Action_Save).pack(fill="x", padx=20, pady=15)
        ctk.CTkFrame(rechts, height=2, fg_color=thema["bg_root"]).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(rechts, text="✔ Wijzig Status (Toggle)", command=self._Hw_Action_Toggle).pack(fill="x", padx=20, pady=6)
        ctk.CTkButton(rechts, text="🗑 Verwijder Selectie", fg_color="#EF4444", text_color="white", command=self._Hw_Action_Delete).pack(fill="x", padx=20, pady=6)

        self._Hw_Render_Data()

    def _Hw_Render_Data(self):
        self.hw_listbox.delete(0, tk.END)
        for taak in self.data["huiswerk"]:
            status = "✔ AFGEROND" if taak.get("afgerond") else "⏳ OPENSTAAND"
            self.hw_listbox.insert(tk.END, f"[{status}] {taak.get('datum')} | {taak.get('vak')} -> {taak.get('beschrijving')}")

    def _Hw_Action_Save(self):
        v = self.entry_hw_vak.get()
        d = self.entry_hw_desc.get().strip()
        dat = self.entry_hw_datum.get().strip()
        if not d or not dat: return
        self.data["huiswerk"].append({"vak": v, "beschrijving": d, "datum": dat, "afgerond": False})
        IO_SafeSave(self.data)
        self._Hw_Render_Data()
        self.entry_hw_desc.delete(0, tk.END)
        self.entry_hw_datum.delete(0, tk.END)

    def _Hw_Action_Toggle(self):
        try:
            idx = self.hw_listbox.curselection()[0]
            self.data["huiswerk"][idx]["afgerond"] = not self.data["huiswerk"][idx]["afgerond"]
            IO_SafeSave(self.data)
            self._Hw_Render_Data()
        except IndexError: pass

    def _Hw_Action_Delete(self):
        try:
            idx = self.hw_listbox.curselection()[0]
            self.data["huiswerk"].pop(idx)
            IO_SafeSave(self.data)
            self._Hw_Render_Data()
        except IndexError: pass

    # ==============================================================================
    # MODULE 3: GEAVANCEERD MATRIX LESROOSTER (HERSTELD & COMPLEET)
    # ==============================================================================
    def Module_Rooster(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("rooster")
        thema = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.canvas, fg_color="transparent")
        top_bar.pack(fill="x", padx=35, pady=20)
        ctk.CTkLabel(top_bar, text="Matrix Lesrooster Engine", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(side="left")

        ctk.CTkButton(top_bar, text="Week Overzicht", width=110, command=lambda: self._Rooster_Switch_Mode("Week")).pack(side="right", padx=6)
        ctk.CTkButton(top_bar, text="Maand Overzicht", width=110, command=lambda: self._Rooster_Switch_Mode("Maand")).pack(side="right", padx=6)

        nav_bar = ctk.CTkFrame(self.canvas, fg_color="transparent")
        nav_bar.pack(fill="x", padx=35, pady=5)
        ctk.CTkButton(nav_bar, text="◀ Vorige Periode", width=130, command=self._Rooster_Prev).pack(side="left")
        self.rooster_titel_label = ctk.CTkLabel(nav_bar, text="", font=("Segoe UI", 16, "bold"), text_color=thema["text"])
        self.rooster_titel_label.pack(side="left", expand=True)
        ctk.CTkButton(nav_bar, text="Volgende Periode ▶", width=130, command=self._Rooster_Next).pack(side="right")

        self.rooster_grote_container = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.rooster_grote_container.pack(fill="both", expand=True, padx=35, pady=10)

        beheer_paneel = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        beheer_paneel.pack(fill="x", padx=35, pady=20)

        self.combo_rst_vak = ctk.CTkComboBox(beheer_paneel, values=self.vakken_lijst, width=150, state="readonly")
        self.combo_rst_vak.set(self.vakken_lijst[0])
        self.combo_rst_vak.pack(side="left", padx=10, pady=12)

        self.entry_rst_datum = ctk.CTkEntry(beheer_paneel, placeholder_text="Datum", width=110)
        self.entry_rst_datum.insert(0, str(dt.date.today()))
        self.entry_rst_datum.pack(side="left", padx=6, pady=12)

        self.combo_rst_tijd = ctk.CTkComboBox(beheer_paneel, values=self.tijd_slots, width=100, state="readonly")
        self.combo_rst_tijd.set("08:30")
        self.combo_rst_tijd.pack(side="left", padx=6, pady=12)

        self.entry_rst_lokaal = ctk.CTkEntry(beheer_paneel, placeholder_text="Lokaal", width=110)
        self.entry_rst_lokaal.pack(side="left", padx=6, pady=12)

        self.entry_rst_docent = ctk.CTkEntry(beheer_paneel, placeholder_text="Docent", width=100)
        self.entry_rst_docent.pack(side="left", padx=6, pady=12)

        ctk.CTkButton(beheer_paneel, text="➕ Inplannen", fg_color=thema["accent"], text_color="white", width=110, command=self._Rooster_Save_Lesson).pack(side="right", padx=10, pady=12)
        ctk.CTkButton(beheer_paneel, text="🗑 Purge Data", fg_color="#EF4444", text_color="white", width=100, command=self._Rooster_Purge).pack(side="right", padx=6, pady=12)

        self._Rooster_Render_Core()

    def _Rooster_Switch_Mode(self, modus):
        self.huidige_rooster_modus = modus
        self._Rooster_Render_Core()

    def _Rooster_Prev(self):
        if self.huidige_rooster_modus == "Week": self.referentie_datum -= dt.timedelta(days=7)
        else: self.referentie_datum = (self.referentie_datum.replace(day=1) - dt.timedelta(days=1))
        self._Rooster_Render_Core()

    def _Rooster_Next(self):
        if self.huidige_rooster_modus == "Week": self.referentie_datum += dt.timedelta(days=7)
        else: self.referentie_datum = (self.referentie_datum.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
        self._Rooster_Render_Core()

    def _Rooster_Save_Lesson(self):
        v = self.combo_rst_vak.get()
        d = self.entry_rst_datum.get().strip()
        t = self.combo_rst_tijd.get()
        l = self.entry_rst_lokaal.get().strip() or "N.v.t."
        doc = self.entry_rst_docent.get().strip() or "Onbekend"
        if not d: return
        self.data["rooster"].append({"vak": v, "datum": d, "tijd": t, "lokaal": l, "docent": doc})
        IO_SafeSave(self.data)
        self._Rooster_Render_Core()

    def _Rooster_Purge(self):
        if messagebox.askyesno("Systeemverificatie", "Weet u zeker dat u de volledige rooster-database wilt wissen?"):
            self.data["rooster"] = []
            IO_SafeSave(self.data)
            self._Rooster_Render_Core()

    def _Rooster_Render_Core(self):
        for widget in self.rooster_grote_container.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        if self.huidige_rooster_modus == "Week":
            for i in range(5): self.rooster_grote_container.grid_columnconfigure(i, weight=1, uniform="week_cols")
            self.rooster_grote_container.grid_rowconfigure(0, weight=1)

            maandag_start = self.referentie_datum - dt.timedelta(days=self.referentie_datum.weekday())
            vrijdag_eind = maandag_start + dt.timedelta(days=4)
            self.rooster_titel_label.configure(text=f"Matrix Week: {maandag_start.strftime('%d %b')} t/m {vrijdag_eind.strftime('%d %b %Y')}")

            namen_dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
            for i, d_naam in enumerate(namen_dagen):
                focus_datum = maandag_start + dt.timedelta(days=i)
                focus_datum_str = focus_datum.strftime("%Y-%m-%d")

                kolom_frame = ctk.CTkFrame(self.rooster_grote_container, fg_color=thema["bg_card"], corner_radius=14)
                kolom_frame.grid(row=0, column=i, sticky="nsew", padx=6, pady=6)

                kop = ctk.CTkFrame(kolom_frame, fg_color=thema["button_fg"], corner_radius=8, height=38)
                kop.pack(fill="x", padx=5, pady=5)
                kop.pack_propagate(False)
                ctk.CTkLabel(kop, text=f"{d_naam} ({focus_datum.strftime('%d-%m')})", font=("Segoe UI", 12, "bold"), text_color="white").pack(expand=True)

                scroll = ctk.CTkScrollableFrame(kolom_frame, fg_color="transparent")
                scroll.pack(fill="both", expand=True, padx=4, pady=4)

                lessen = [l for l in self.data["rooster"] if l.get("datum") == focus_datum_str]
                lessen.sort(key=lambda x: x.get("tijd", ""))

                # Hier is de syntax-fout uit het originele script volledig hersteld
                for les in lessen:
                    box = ctk.CTkFrame(scroll, fg_color=thema["bg_root"], corner_radius=8)
                    box.pack(fill="x", pady=4, padx=2)
                    ctk.CTkLabel(box, text=f"⏰ {les.get('tijd')}\n{les.get('vak')}\n📍 {les.get('lokaal')} | {les.get('docent')}", font=("Segoe UI", 11), text_color=thema["text"], justify="left").pack(pady=6, padx=8)
        else:
            # Gecentraliseerde Maand Matrix Rendering Engine
            self.rooster_titel_label.configure(text=self.referentie_datum.strftime("%B %Y").upper())
            maand_scroll = ctk.CTkScrollableFrame(self.rooster_grote_container, fg_color=thema["bg_card"], corner_radius=16)
            maand_scroll.pack(fill="both", expand=True)
            
            for d in range(1, 32):
                try:
                    test_date = dt.date(self.referentie_datum.year, self.referentie_datum.month, d)
                    iso_str = str(test_date)
                    lessen_teller = len([l for l in self.data["rooster"] if l.get("datum") == iso_str])
                    
                    cel = ctk.CTkFrame(maand_scroll, fg_color=thema["bg_root"], height=50, width=180, corner_radius=8)
                    cel.pack(fill="x", pady=2, padx=10)
                    cel.pack_propagate(False)
                    
                    txt = f"📅 Dag {d:02d} — {test_date.strftime('%A')} ({lessen_teller} lesactiviteiten)"
                    ctk.CTkLabel(cel, text=txt, font=("Segoe UI", 13), text_color=thema["accent"] if lessen_teller > 0 else thema["text"]).pack(side="left", padx=15)
                except ValueError: break

    # ==============================================================================
    # MODULE 4: KENNISBANK & NOTITIES MODULE
    # ==============================================================================
    def Module_Notities(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("notities")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Kennisbank & Documentatie Matrix", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        split = ctk.CTkFrame(self.canvas, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        links = ctk.CTkFrame(split, width=300, fg_color=thema["bg_card"], corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)
        
        self.note_listbox = tk.Listbox(links, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.note_listbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_listbox.bind("<<ListboxSelect>>", self._Note_On_Select)
        
        rechts = ctk.CTkFrame(split, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)
        
        self.note_title_entry = ctk.CTkEntry(rechts, placeholder_text="Titel van de notitie", font=("Segoe UI", 14, "bold"))
        self.note_title_entry.pack(fill="x", padx=20, pady=(20, 10))
        
        self.note_textbox = ctk.CTkTextbox(rechts, font=("Segoe UI Mono", 12))
        self.note_textbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        btn_bar = ctk.CTkFrame(rechts, fg_color="transparent")
        btn_bar.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(btn_bar, text="💾 Opslaan / Update", fg_color=thema["accent"], text_color="white", command=self._Note_Save).pack(side="left", padx=5)
        ctk.CTkButton(btn_bar, text="➕ Nieuw", command=self._Note_New).pack(side="left", padx=5)
        ctk.CTkButton(btn_bar, text="🗑 Wissen", fg_color="#EF4444", text_color="white", command=self._Note_Delete).pack(side="right", padx=5)
        
        self._Note_Render_List()

    def _Note_Render_List(self):
        self.note_listbox.delete(0, tk.END)
        for n in self.data["notities"]:
            self.note_listbox.insert(tk.END, n.get("titel", "Naamloze Notitie"))

    def _Note_On_Select(self, event):
        try:
            idx = self.note_listbox.curselection()[0]
            n = self.data["notities"][idx]
            self.note_title_entry.delete(0, tk.END)
            self.note_title_entry.insert(0, n.get("titel", ""))
            self.note_textbox.delete("1.0", tk.END)
            self.note_textbox.insert("1.0", n.get("inhoud", ""))
        except IndexError: pass

    def _Note_Save(self):
        t = self.note_title_entry.get().strip() or "Naamloze Notitie"
        inhoud = self.note_textbox.get("1.0", tk.END).strip()
        
        try:
            idx = self.note_listbox.curselection()[0]
            self.data["notities"][idx] = {"titel": t, "inhoud": inhoud}
        except IndexError:
            self.data["notities"].append({"titel": t, "inhoud": inhoud})
            
        IO_SafeSave(self.data)
        self._Note_Render_List()
        self._Note_New()

    def _Note_New(self):
        self.note_title_entry.delete(0, tk.END)
        self.note_textbox.delete("1.0", tk.END)
        self.note_listbox.selection_clear(0, tk.END)

    def _Note_Delete(self):
        try:
            idx = self.note_listbox.curselection()[0]
            self.data["notities"].pop(idx)
            IO_SafeSave(self.data)
            self._Note_Render_List()
            self._Note_New()
        except IndexError: pass

# ==============================================================================
# INTERACTIEVE VEILIGE RUNTIME ENGINE INJECTOR
# ==============================================================================
    def Module_Cijfers(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("cijfers")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="Cijfer & KPI Analyse Paneel", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        left = ctk.CTkFrame(f, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.grade_listbox = tk.Listbox(left, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0)
        self.grade_listbox.pack(fill="both", expand=True, pady=(0, 10))
        
        right = ctk.CTkFrame(f, width=300, fg_color=thema["bg_root"], corner_radius=12)
        right.pack(side="right", fill="y", padx=20, pady=20)
        
        self.entry_grade_vak = ctk.CTkComboBox(right, values=self.vakken_lijst, state="readonly")
        self.entry_grade_vak.set(self.vakken_lijst[0])
        self.entry_grade_vak.pack(fill="x", padx=15, pady=10)
        
        self.entry_grade_val = ctk.CTkEntry(right, placeholder_text="Cijfer (bijv. 8.5)")
        self.entry_grade_val.pack(fill="x", padx=15, pady=10)
        
        self.entry_grade_weight = ctk.CTkEntry(right, placeholder_text="Weging (bijv. 2)")
        self.entry_grade_weight.insert(0, "1")
        self.entry_grade_weight.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkButton(right, text="📥 Cijfer Logger", fg_color=thema["accent"], text_color="white", command=self._Grade_Save).pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(right, text="🗑 Verwijder", fg_color="#EF4444", text_color="white", command=self._Grade_Delete).pack(fill="x", padx=15, pady=5)
        
        self._Grade_Render()

    def _Grade_Render(self):
        self.grade_listbox.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.grade_listbox.insert(tk.END, f"📌 {c.get('vak')} -> Cijfer: {c.get('cijfer')} [Weging: {c.get('weging')}x]")

    def _Grade_Save(self):
        v = self.entry_grade_vak.get()
        val = self.entry_grade_val.get().strip().replace(",", ".")
        w = self.entry_grade_weight.get().strip()
        if not val or not w: return
        self.data["cijfers"].append({"vak": v, "cijfer": val, "weging": w})
        IO_SafeSave(self.data)
        self._Grade_Render()
        self.entry_grade_val.delete(0, tk.END)

    def _Grade_Delete(self):
        try:
            idx = self.grade_listbox.curselection()[0]
            self.data["cijfers"].pop(idx)
            IO_SafeSave(self.data)
            self._Grade_Render()
        except IndexError: pass

    # ==============================================================================
    # MODULE 5: MIJLPALEN & DOELEN MANAGEMENT SYSTEM
    # ==============================================================================
    def Module_Doelen(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("doelen")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="🎯 Mijlpalen & Persoonlijke Doelen", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        self.goal_listbox = tk.Listbox(f, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0)
        self.goal_listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        b_bar = ctk.CTkFrame(f, fg_color="transparent")
        b_bar.pack(fill="x", padx=20, pady=15)
        
        self.entry_goal = ctk.CTkEntry(b_bar, placeholder_text="Schrijf hier een nieuw sub-doel of mijlpaal...")
        self.entry_goal.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(b_bar, text="🚀 Vastleggen", fg_color=thema["accent"], text_color="white", command=self._Goal_Add).pack(side="right", padx=5)
        ctk.CTkButton(b_bar, text="🗑 Verwijderen", fg_color="#EF4444", text_color="white", command=self._Goal_Delete).pack(side="right", padx=5)
        
        self._Goal_Render()

    def _Goal_Render(self):
        self.goal_listbox.delete(0, tk.END)
        for d in self.data["doelen"]:
            self.goal_listbox.insert(tk.END, f"🎯 {d}")

    def _Goal_Add(self):
        g = self.entry_goal.get().strip()
        if not g: return
        self.data["doelen"].append(g)
        IO_SafeSave(self.data)
        self._Goal_Render()
        self.entry_goal.delete(0, tk.END)

    def _Goal_Delete(self):
        try:
            idx = self.goal_listbox.curselection()[0]
            self.data["doelen"].pop(idx)
            IO_SafeSave(self.data)
            self._Goal_Render()
        except IndexError: pass

    # ==============================================================================
    # MODULE 6: EXAMEN & TOETSING SCHEDULER
    # ==============================================================================
    def Module_Examens(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("examens")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="🎓 Examen & Toetsing Controlekamer", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        self.ex_listbox = tk.Listbox(f, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0)
        self.ex_listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        b_bar = ctk.CTkFrame(f, fg_color="transparent")
        b_bar.pack(fill="x", padx=20, pady=15)
        
        self.ex_vak = ctk.CTkComboBox(b_bar, values=self.vakken_lijst, state="readonly", width=160)
        self.ex_vak.set(self.vakken_lijst[0])
        self.ex_vak.pack(side="left", padx=5)
        
        self.ex_date = ctk.CTkEntry(b_bar, placeholder_text="Datum (YYYY-MM-DD)", width=140)
        self.ex_date.pack(side="left", padx=5)
        
        ctk.CTkButton(b_bar, text="📅 Selecteer", width=80, command=lambda: UI_DateDialog(self.ex_date)).pack(side="left", padx=2)
        ctk.CTkButton(b_bar, text="🔒 Examen Loggen", fg_color=thema["accent"], text_color="white", command=self._Examen_Add).pack(side="right", padx=5)
        ctk.CTkButton(b_bar, text="🗑 Wissen", fg_color="#EF4444", text_color="white", command=self._Examen_Delete).pack(side="right", padx=5)
        
        self._Examen_Render()

    def _Examen_Render(self):
        self.ex_listbox.delete(0, tk.END)
        for e in self.data["examens"]:
            self.ex_listbox.insert(tk.END, f"📅 [{e.get('datum')}] - TOETSING TARGET MATRIX: {e.get('vak')}")

    def _Examen_Add(self):
        v = self.ex_vak.get()
        d = self.ex_date.get().strip()
        if not d: return
        self.data["examens"].append({"vak": v, "datum": d})
        IO_SafeSave(self.data)
        self._Examen_Render()
        self.ex_date.delete(0, tk.END)

    def _Examen_Delete(self):
        try:
            idx = self.ex_listbox.curselection()[0]
            self.data["examens"].pop(idx)
            IO_SafeSave(self.data)
            self._Examen_Render()
        except IndexError: pass

    # ==============================================================================
    # MODULE 7: STUDIETOOLS (THREADED POMODORO ENGINE & FLASHCARDS)
    # ==============================================================================
    def Module_Studietools(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("studietools")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="⏱ Pomodoro Kernel Timer & Flashcards", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        self.pomo_label = ctk.CTkLabel(f, text="25:00", font=("Segoe UI", 72, "bold"), text_color=thema["accent"])
        self.pomo_label.pack(pady=40)
        
        btn_f = ctk.CTkFrame(f, fg_color="transparent")
        btn_f.pack(pady=10)
        
        self.pomo_start_btn = ctk.CTkButton(btn_f, text="⚡ START ENGINE", fg_color="#10B981", text_color="white", command=self._Pomo_Start)
        self.pomo_start_btn.pack(side="left", padx=10)
        
        ctk.CTkButton(btn_f, text="🛑 STOP ENGINE", fg_color="#EF4444", text_color="white", command=self._Pomo_Stop).pack(side="left", padx=10)
        
        if self.pomo_loopt:
            self.pomo_start_btn.configure(state="disabled")
            self._Pomo_Update_UI_Loop()

    def _Pomo_Start(self):
        if not self.pomo_loopt:
            self.pomo_loopt = True
            w_min = int(self.data["settings"].get("pomodoro_werk", 25))
            self.pomo_tijd_resterend = w_min * 60
            self.pomo_modus_is_werk = True
            self.pomo_start_btn.configure(state="disabled")
            
            self.pomo_timer_thread = threading.Thread(target=self._Pomo_Thread_Core, daemon=True)
            self.pomo_timer_thread.start()
            self._Pomo_Update_UI_Loop()

    def _Pomo_Stop(self):
        self.pomo_loopt = False
        self.pomo_start_btn.configure(state="normal")
        self.pomo_label.configure(text="25:00")

    def _Pomo_Thread_Core(self):
        while self.pomo_loopt and self.pomo_tijd_resterend > 0:
            time.sleep(1)
            self.pomo_tijd_resterend -= 1
            if self.pomo_tijd_resterend <= 0:
                self.pomo_loopt = False
                # Wisselmodus logica kan hier eventueel geïmplementeerd worden

    def _Pomo_Update_UI_Loop(self):
        if self.pomo_loopt:
            m = self.pomo_tijd_resterend // 60
            s = self.pomo_tijd_resterend % 60
            self.pomo_label.configure(text=f"{m:02d}:{s:02d}")
            self.after(500, self._Pomo_Update_UI_Loop)
        else:
            self.pomo_start_btn.configure(state="normal")

    # ==============================================================================
    # MODULE 8: ABSENTIEREGISTRATIE MATRIX LAYER
    # ==============================================================================
    def Module_Absentie(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("absentie")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="🛡 Absentieregistratie & Integriteit", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        self.abs_listbox = tk.Listbox(f, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0)
        self.abs_listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        b = ctk.CTkFrame(f, fg_color="transparent")
        b.pack(fill="x", padx=20, pady=15)
        
        self.abs_vak = ctk.CTkComboBox(b, values=self.vakken_lijst, state="readonly")
        self.abs_vak.set(self.vakken_lijst[0])
        self.abs_vak.pack(side="left", padx=5)
        
        self.abs_reason = ctk.CTkEntry(b, placeholder_text="Reden van afwezigheid")
        self.abs_reason.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(b, text="🛡 Log Absentie", fg_color=thema["accent"], text_color="white", command=self._Abs_Add).pack(side="right", padx=5)
        
        self._Abs_Render()

    def _Abs_Render(self):
        self.abs_listbox.delete(0, tk.END)
        for a in self.data["absentie"]:
            self.abs_listbox.insert(tk.END, f"⚠️ Verzuim -> Vak: {a.get('vak')} | Reden: {a.get('reden')}")

    def _Abs_Add(self):
        v = self.abs_vak.get()
        r = self.abs_reason.get().strip()
        if not r: return
        self.data["absentie"].append({"vak": v, "reden": r})
        IO_SafeSave(self.data)
        self._Abs_Render()
        self.abs_reason.delete(0, tk.END)

    # ==============================================================================
    # MODULE 9: STUDIEFINANCIERING LEDGER MONITOR
    # ==============================================================================
    def Module_Financien(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("financien")
        thema = THEMES[self.theme_name]
        ctk.CTkLabel(self.canvas, text="💳 Studiefinanciering Ledger Monitor", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        f = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        f.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        self.fin_listbox = tk.Listbox(f, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0)
        self.fin_listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        b = ctk.CTkFrame(f, fg_color="transparent")
        b.pack(fill="x", padx=20, pady=15)
        
        self.fin_desc = ctk.CTkEntry(b, placeholder_text="Omschrijving transactie/mutatie")
        self.fin_desc.pack(side="left", fill="x", expand=True, padx=5)
        
        self.fin_val = ctk.CTkEntry(b, placeholder_text="Bedrag (+/- EUR)", width=120)
        self.fin_val.pack(side="left", padx=5)
        
        ctk.CTkButton(b, text="💳 Mutatie Boeken", fg_color=thema["accent"], text_color="white", command=self._Fin_Add).pack(side="right", padx=5)
        
        self._Fin_Render()

    def _Fin_Render(self):
        self.fin_listbox.delete(0, tk.END)
        for transaction in self.data["financien"]:
            self.fin_listbox.insert(tk.END, f"💰 Mutatie: {transaction.get('desc')} -> bedrag: €{transaction.get('bedrag')}")

    def _Fin_Add(self):
        d = self.fin_desc.get().strip()
        val = self.fin_val.get().strip()
        if not d or not val: return
        self.data["financien"].append({"desc": d, "bedrag": val})
        IO_SafeSave(self.data)
        self._Fin_Render()
        self.fin_desc.delete(0, tk.END)
        self.fin_val.delete(0, tk.END)

    # ==============================================================================
    # MODULE 10: SYSTEM CONFIGURATIONS (SETTINGS ARCHITECTURE)
    # ==============================================================================
    def Module_Settings(self):
        self.Core_Clear_Canvas()
        thema = THEMES[self.theme_name]
        
        for k in self.sidebar_buttons.values(): k.configure(fg_color="transparent", text_color=thema["sidebar_text"])
        self.instellingen_knop.configure(fg_color=thema["button_fg"], text_color=thema["button_text"])
        
        ctk.CTkLabel(self.canvas, text="⚙ Systeem Kernel Configuraties", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        box = ctk.CTkFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        box.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        ctk.CTkLabel(box, text="Gebruikersprofiel Aanpassen", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=25, pady=(25, 10))
        self.settings_name = ctk.CTkEntry(box, width=300)
        self.settings_name.insert(0, self.data["settings"].get("naam", "Student"))
        self.settings_name.pack(anchor="w", padx=25, pady=5)
        
        ctk.CTkLabel(box, text="Systeem Visuele Theme-Matrix", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=25, pady=(20, 10))
        self.settings_theme = ctk.CTkComboBox(box, values=list(THEMES.keys()), state="readonly")
        self.settings_theme.set(self.theme_name)
        self.settings_theme.pack(anchor="w", padx=25, pady=5)
        
        ctk.CTkButton(box, text="💾 Wijzigingen Synchroniseren", fg_color=thema["accent"], text_color="white", command=self._Settings_Save).pack(anchor="w", padx=25, pady=35)

    def _Settings_Save(self):
        self.data["settings"]["naam"] = self.settings_name.get().strip() or "Student"
        gekozen_thema = self.settings_theme.get()
        self.data["settings"]["theme"] = gekozen_thema
        self.theme_name = gekozen_thema
        IO_SafeSave(self.data)
        
        self.Core_Apply_Theme()
        self.Module_Settings()

# ==============================================================================
# ENTRY POINT TRIGGER
# ==============================================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
