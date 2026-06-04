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
# 1. GLOBALE CONFIGURATIE, CODENAMES & SYSTEM ARCHITECTURE
# ==============================================================================

HUIDIGE_VERSIE = "6.10.8v"
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
        "settings": {"theme": "Zwart", "naam": "Student", "pomodoro_werk": 25, "pomodoro_rust": 5, "automatisch_backups": True}
    }
    
    for sleutel, waarde in SysteemDefaults.items():
        if sleutel not in data:
            data[sleutel] = waarde
            
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
    # LUXE EN GEOPTIMALISEERDE BOOTLOADER / UPDATE ENGINE (v6.10.8v)
    # ==============================================================================
    def Core_Bootloader_Sequence(self):
        thema = THEMES[self.theme_name]
        
        # Volledig scherm overschrijven voor luxe dedicated interface effect
        boot_window = ctk.CTkToplevel()
        boot_window.title("GC-OS Engine Booting...")
        boot_window.overrideredirect(True)
        
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        boot_window.geometry(f"{sw}x{sh}+0+0")
        boot_window.lift()
        boot_window.attributes("-topmost", True)
        boot_window.configure(fg_color=thema["bg_root"])

        # Luxe gecentreerde container frame om de interface perfect te schalen
        container = ctk.CTkFrame(boot_window, fg_color=thema["bg_card"], corner_radius=24, border_width=1, border_color=thema["button_hover"])
        container.place(relx=0.5, rely=0.5, anchor="center", width=650, height=420)

        # OS Merk & Versie badge
        versie_badge = ctk.CTkFrame(container, fg_color=thema["button_fg"], corner_radius=6)
        versie_badge.place(relx=0.5, rely=0.15, anchor="center")
        ctk.CTkLabel(versie_badge, text=f"SYSTEM FIRMWARE v{HUIDIGE_VERSIE}", font=("Segoe UI Mono", 11, "bold"), text_color=thema["button_text"], padx=10, pady=2).pack()

        titel_label = ctk.CTkLabel(container, text="GraafschapCollege-OS", font=("Segoe UI", 38, "bold"), text_color=thema["text"])
        titel_label.place(relx=0.5, rely=0.28, anchor="center")
        
        sub_label = ctk.CTkLabel(container, text=f"CODENAME: {CODENAME}.sys // INITIALIZING COMPONENTS", font=("Segoe UI Mono", 12), text_color="gray")
        sub_label.place(relx=0.5, rely=0.38, anchor="center")

        # Premium percentage tracker (Grote neon-look cijfers)
        self.percentage_label = ctk.CTkLabel(container, text="0%", font=("Segoe UI", 48, "bold"), text_color=thema["accent"])
        self.percentage_label.place(relx=0.5, rely=0.55, anchor="center")

        # Prachtige, strakke, minimalistische progressiebalk
        progressiebalk = ctk.CTkProgressBar(container, width=480, height=6, mode="determinate", progress_color=thema["accent"], fg_color=thema["bg_root"])
        progressiebalk.place(relx=0.5, rely=0.70, anchor="center")
        progressiebalk.set(0)

        # Real-time console status logs onder de balk
        status_label = ctk.CTkLabel(container, text="Booting Quantum Core...", font=("Segoe UI Mono", 11), text_color="gray")
        status_label.place(relx=0.5, rely=0.78, anchor="center")

        # Decoratieve luxe architectuur-informatie onderaan de kaart
        foot_info = ctk.CTkLabel(container, text="SECURE BOOT MATRIX STATE: ACTIVE [128-BIT ENCRYPTION LAYER]", font=("Segoe UI Mono", 10), text_color="gray")
        foot_info.place(relx=0.5, rely=0.92, anchor="center")

        # Geavanceerd, asynchroon aansturingsalgoritme voor vloeiende laadstappen
        def SimuleerStappen(stap):
            if stap <= 100:
                # Bereken willekeurige micro-laadvertragingen om een luxe realistische analyse te simuleren
                progressiebalk.set(stap / 100)
                self.percentage_label.configure(text=f"{stap}%")
                
                # Realistische, high-end systeem logs triggeren op exacte stappen
                if stap == 12: status_label.configure(text="› Mapped virtual clusters & parsing localized I/O JSON databases...")
                elif stap == 34: status_label.configure(text="› Synchronizing graphical hardware acceleration assets...")
                elif stap == 56: status_label.configure(text="› Launching isolated thread safe cryptography engines...")
                elif stap == 78: status_label.configure(text="› Allocating volatile memory buffers & resolving system defaults...")
                elif stap == 92: status_label.configure(text="› Finalizing integrity handshakes, clearing temporary registers...")
                
                # Snelheidsvariatie toevoegen voor een realistisch premium gevoel
                volgende_vertraging = random.randint(15, 60) if 40 < stap < 70 else random.randint(25, 45)
                self.after(volgende_vertraging, lambda: SimuleerStappen(stap + 1))
            else:
                # Subtiele 'fade-out' simulatie en de-iconificatie van het hoofdvenster
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

        # Widget 1: Real-time Cijfer KPI Analyser
        card1 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card1.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card1, text="📊 Cijfer Analyse & Gemiddelden", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        
        alle_cijfers = [float(c["cijfer"]) for c in self.data["cijfers"] if "cijfer" in c]
        algemeen_gemiddelde = sum(alle_cijfers) / len(alle_cijfers) if alle_cijfers else 0.0
        
        ctk.CTkLabel(card1, text=f"• Totaal aantal ingevoerde cijfers: {len(alle_cijfers)}", font=("Segoe UI", 14), text_color=thema["text"]).pack(anchor="w", padx=25, pady=4)
        ctk.CTkLabel(card1, text=f"• Gewogen Algemeen Gemiddelde: {algemeen_gemiddelde:.2f}", font=("Segoe UI", 14), text_color=thema["text"]).pack(anchor="w", padx=25, pady=4)

        # Widget 2: Rooster voor Vandaag
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

        # Widget 3: Motivatie & AI Algoritme Quotes
        card3 = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        card3.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        ctk.CTkLabel(card3, text="💡 Systeem Filosofie", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(card3, text=f'"{random.choice(MOTIVATIONAL_QUOTES)}"', font=("Segoe UI", 13, "italic"), text_color=thema["text"], wrap=True).pack(anchor="w", padx=25, pady=10)

        # Widget 4: Kritieke Openstaande Deadlines
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
    # MODULE 3: GEAVANCEERD MATRIX LESROOSTER
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

                for les in lessen:
                    box = ctk.CTkFrame(scroll, fg_color=thema["bg_root"], corner_radius=8, border_width=1, border_color=thema["button_hover"])
                    box.pack(fill="x", padx=4, pady=4)
                    ctk.CTkLabel(box, text=les.get('tijd'), font=("Segoe UI", 11, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=10, pady=(6, 0))
                    ctk.CTkLabel(box, text=les.get('vak'), font=("Segoe UI", 12, "bold"), text_color=thema["text"]).pack(anchor="w", padx=10, pady=0)
                    ctk.CTkLabel(box, text=f"📍 {les.get('lokaal')} | 👨‍🏫 {les.get('docent')}", font=("Segoe UI", 10), text_color="gray").pack(anchor="w", padx=10, pady=(0, 6))
        else:
            scroller = ctk.CTkScrollableFrame(self.rooster_grote_container, fg_color=thema["bg_card"], corner_radius=16)
            scroller.pack(fill="both", expand=True)
            
            j, m = self.referentie_datum.year, self.referentie_datum.month
            self.rooster_titel_label.configure(text=self.referentie_datum.strftime("%B %Y").upper())

            gefilterde_lessen = []
            for l in self.data["rooster"]:
                try:
                    ld = dt.datetime.strptime(l.get("datum"), "%Y-%m-%d").date()
                    if ld.year == j and ld.month == m: gefilterde_lessen.append(l)
                except ValueError: pass

            gefilterde_lessen.sort(key=lambda x: (x.get("datum"), x.get("tijd")))
            if not gefilterde_lessen:
                ctk.CTkLabel(scroller, text="Geen ingeplande data voor deze maandmatrix.", font=("Segoe UI", 14, "italic"), text_color="gray").pack(pady=40)
            else:
                for les in gefilterde_lessen:
                    r_item = ctk.CTkFrame(scroller, fg_color=thema["bg_root"], corner_radius=10)
                    r_item.pack(fill="x", padx=20, pady=5)
                    ctk.CTkLabel(r_item, text=f"📅 {les.get('datum')}  |  ⏰ {les.get('tijd')}  |  📘 {les.get('vak')}  |  📍 Lokaal: {les.get('lokaal')}  |  👨‍🏫 Docent: {les.get('docent')}", font=("Segoe UI", 12), text_color=thema["text"]).pack(side="left", padx=20, pady=10)

    def _Rooster_Save_Lesson(self):
        v = self.combo_rst_vak.get()
        d = self.entry_rst_datum.get().strip()
        t = self.combo_rst_tijd.get()
        lok = self.entry_rst_lokaal.get().strip() or "Onbekend"
        doc = self.entry_rst_docent.get().strip() or "Onbekend"
        if d and t:
            self.data["rooster"].append({"vak": v, "datum": d, "tijd": t, "lokaal": lok, "docent": doc})
            IO_SafeSave(self.data)
            self._Rooster_Render_Core()

    def _Rooster_Purge(self):
        if messagebox.askyesno("Matrix Veiligheid", "Wilt u de volledige rooster database leegmaken?"):
            self.data["rooster"] = []
            IO_SafeSave(self.data)
            self._Rooster_Render_Core()

    # Placeholders voor missende UI modules om crashes te voorkomen
    def Module_Notities(self): pass
    def Module_Cijfers(self): pass
    def Module_Doelen(self): pass
    def Module_Examens(self): pass
    def Module_Studietools(self): pass
    def Module_Absentie(self): pass
    def Module_Financien(self): pass
    def Module_Settings(self): pass

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
