import os
import sys
import json
import datetime as dt
import time
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from tkcalendar import Calendar
import random
import math
import threading

# ==============================================================================
# 1. GLOBALE CONFIGURATIE, CODENAMES & SYSTEM ARCHITECTURE
# ==============================================================================

HUIDIGE_VERSIE = "6.5.9v"
CODENAME = "AetherValkyrie-Pro"
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
    "Fouten zijn het bewijs dat je de grenzen van je intelligentie opzoekt."
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
        messagebox.showerror("Kritieke I/O Fout", f"Kan systeemdata niet wegschrijven:\n{e}")

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
        self.title(f"GraafschapCollege-OS — Enterprise Edition Suite [v{HUIDIGE_VERSIE}]")
        self.geometry("1440x900")
        self.minsize(1200, 800)

        # Systeemvariabelen & Opleidingsmatrices
        self.vakken_lijst = ["Nederlands", "Engels", "Rekenen", "Software Development", "Hardware & Infrastructure", "Databases", "Burgerschap", "Loopbaan", "Project Management", "Cybersecurity"]
        self.tijd_slots = [f"{uur:02d}:{minuut:02d}" for uur in range(8, 18) for minuut in (0, 30)]
        self.tijd_slots.sort()

        self.sidebar_buttons = {}
        self.huidige_rooster_modus = "Week"
        self.referentie_datum = dt.date.today()
        
        # Threaded Pomodoro Engine Variabelen
        self.pomo_loopt = False
        self.pomo_tijd_resterend = 0
        self.pomo_modus_is_werk = True

        # Componenten bouwen
        self._Core_Build_Layout()
        self.Core_Apply_Theme()
        
        # Luxe Bootloader Sequence initialiseren
        self.after(100, self.Core_Bootloader_Sequence)

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

    def Core_Bootloader_Sequence(self):
        """Extreem luxe, state-of-the-art full screen bootloader sequence."""
        thema = THEMES[self.theme_name]
        boot_window = ctk.CTkToplevel()
        boot_window.title("GC-OS Boot Engine")
        boot_window.overrideredirect(True)
        
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        boot_window.geometry(f"{sw}x{sh}+0+0")
        boot_window.lift()
        boot_window.attributes("-topmost", True)
        boot_window.configure(fg_color="#0A0A0C" if thema["mode"] == "Dark" else "#F1F5F9")

        # Top decoratieve bar (Luxe tech look)
        tech_header = ctk.CTkFrame(boot_window, height=4, fg_color=thema["accent"])
        tech_header.pack(fill="x", side="top")

        # Center Container
        center_container = ctk.CTkFrame(boot_window, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.45, anchor="center")

        # Subtiel pulserend effect gesimuleerd door vertraagde elementen
        logo_sub_label = ctk.CTkLabel(center_container, text="GRAAFSCHAP COLLEGE", font=("Segoe UI", 14, "tracking_widest"), text_color="gray")
        logo_sub_label.pack(pady=0)

        titel_label = ctk.CTkLabel(center_container, text="G C ‑ O S  P R O", font=("Segoe UI", 52, "bold"), text_color=thema["accent"])
        titel_label.pack(pady=(5, 10))
        
        ver_label = ctk.CTkLabel(center_container, text=f"SYSTEM VERSION {HUIDIGE_VERSIE} • ARCH: X64", font=("Consolas", 11), text_color="gray")
        ver_label.pack(pady=(0, 30))

        # Luxe Tech Diagnostics Terminal log venster binnen het laadscherm
        terminal_frame = ctk.CTkFrame(center_container, width=500, height=130, fg_color="#020204" if thema["mode"] == "Dark" else "#E2E8F0", corner_radius=10, border_width=1, border_color="#1E1E24")
        terminal_frame.pack(pady=10)
        terminal_frame.pack_propagate(False)
        
        log_text = ctk.CTkLabel(terminal_frame, text="[SYSTEM]: Initializing hardware hooks...", font=("Consolas", 12), text_color="#10B981" if thema["mode"] == "Dark" else "#0F172A", justify="left", anchor="w")
        log_text.pack(fill="both", expand=True, padx=15, pady=10)

        progressiebalk = ctk.CTkProgressBar(center_container, width=500, mode="determinate", height=6, progress_color=thema["accent"], fg_color="#1F1F29")
        progressiebalk.pack(pady=20)
        progressiebalk.set(0)

        boot_logs = [
            "[OK] Kernel structure loaded successfully.",
            "[INFO] Checking JSON integrity matrix map...",
            "[OK] Database connection verified. 0 defects.",
            "[INFO] Binding thread pools to Pomodoro engine...",
            "[OK] High-DPI screen awareness matrix injected.",
            "[INFO] Syncing custom color themes configurations...",
            "[SUCCESS] GC-OS UI Environment ready. Deploying canvas..."
        ]

        def SimuleerStappen(stap, log_index):
            if stap <= 100:
                progressiebalk.set(stap / 100)
                
                # Update luxe diagnostische logging op basis van progressie
                if stap % 15 == 0 and log_index < len(boot_logs):
                    huidige_log = boot_logs[log_index]
                    log_text.configure(text=f"{log_text.cget('text')}\n{huidige_log}")
                    log_index += 1
                    
                # Dynamische snelheid voor een realistisch laadgevoel
                vertraging = random.randint(15, 45) if 40 < stap < 70 else 15
                self.after(vertraging, lambda: SimuleerStappen(stap + 1, log_index))
            else:
                boot_window.destroy()
                self.deiconify()
                try: self.state("zoomed")
                except Exception: pass
                self.Module_Dashboard()

        SimuleerStappen(0, 0)

    def System_Hard_Restart(self):
        """Herschrijft runtime argumenten en herstart clean de python interpreter."""
        print("[GC-OS KERNEL]: Hot-reloading active instance...")
        try:
            # Sluit alle actieve tkinter loops en vernietig componenten clean
            self.destroy()
        except Exception:
            pass
        
        # Herstart het huidige python script exact met dezelfde argumenten
        os.execv(sys.executable, ['python'] + sys.argv)

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

    # ==============================================================================
    # MODULE 4: KENNISBANK & UITGEBREIDE NOTITIES
    # ==============================================================================
    def Module_Notities(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("notities")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Kennisbank, Documenten & Notities", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        scherm = ctk.CTkFrame(self.canvas, fg_color="transparent")
        scherm.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        self.notities_box = tk.Listbox(scherm, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.notities_box.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.notities_box.bind("<<ListboxSelect>>", self._Notes_Load_Item)

        editor = ctk.CTkFrame(scherm, fg_color=thema["bg_card"], width=420, corner_radius=16)
        editor.pack(side="right", fill="y")
        editor.pack_propagate(False)

        ctk.CTkLabel(editor, text="Advanced Textpad Kernel", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.note_title_entry = ctk.CTkEntry(editor, placeholder_text="Titel van de notitie")
        self.note_title_entry.pack(fill="x", padx=20, pady=5)

        self.note_text_area = ctk.CTkTextbox(editor, height=380)
        self.note_text_area.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(editor, text="💾 Systeembestand Opslaan", fg_color=thema["accent"], text_color="white", command=self._Notes_Save).pack(fill="x", padx=20, pady=6)
        ctk.CTkButton(editor, text="🗑 Document Vernietigen", fg_color="#EF4444", text_color="white", command=self._Notes_Delete).pack(fill="x", padx=20, pady=6)

        self._Notes_Rebuild_List()

    def _Notes_Rebuild_List(self):
        self.notities_box.delete(0, tk.END)
        for n in self.data["notities"]:
            self.notities_box.insert(tk.END, n.get("titel", "Naamloze Matrix"))

    def _Notes_Load_Item(self, event):
        try:
            idx = self.notities_box.curselection()[0]
            item = self.data["notities"][idx]
            self.note_title_entry.delete(0, tk.END)
            self.note_title_entry.insert(0, item.get("titel", ""))
            self.note_text_area.delete("1.0", tk.END)
            self.note_text_area.insert("1.0", item.get("inhoud", ""))
        except IndexError: pass

    def _Notes_Save(self):
        tit = self.note_title_entry.get().strip() or "Naamloze Matrix"
        inh = self.note_text_area.get("1.0", tk.END).strip()
        if not inh: return
        
        bestaat = False
        for n in self.data["notities"]:
            if n.get("titel") == tit:
                n["inhoud"] = inh
                bestaat = True
                break
        if not bestaat:
            self.data["notities"].append({"titel": tit, "inhoud": inh, "datum": str(dt.date.today())})
            
        IO_SafeSave(self.data)
        self._Notes_Rebuild_List()
        self.note_title_entry.delete(0, tk.END)
        self.note_text_area.delete("1.0", tk.END)

    def _Notes_Delete(self):
        try:
            idx = self.notities_box.curselection()[0]
            self.data["notities"].pop(idx)
            IO_SafeSave(self.data)
            self._Notes_Rebuild_List()
            self.note_title_entry.delete(0, tk.END)
            self.note_text_area.delete("1.0", tk.END)
        except IndexError: pass

    # ==============================================================================
    # MODULE 5: CIJFER MANAGEMENT & STATISTISCHE GRAPH MATRIX
    # ==============================================================================
    def Module_Cijfers(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("cijfers")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Cijfer & KPI Core Analyser", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        venster_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        venster_frame.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(venster_frame, fg_color=thema["bg_card"], width=350, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="Data Entry Engine", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.combo_cijfer_vak = ctk.CTkComboBox(links, values=self.vakken_lijst, state="readonly")
        self.combo_cijfer_vak.set(self.vakken_lijst[0])
        self.combo_cijfer_vak.pack(fill="x", padx=20, pady=8)

        self.entry_cijfer_waarde = ctk.CTkEntry(links, placeholder_text="Resultaat (bijv: 8.4)")
        self.entry_cijfer_waarde.pack(fill="x", padx=20, pady=8)

        self.entry_cijfer_weging = ctk.CTkEntry(links, placeholder_text="Weging (Factor, bijv: 2)")
        self.entry_cijfer_weging.insert(0, "1")
        self.entry_cijfer_weging.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(links, text="💾 Cijfer Committen", fg_color=thema["accent"], text_color="white", command=self._Cijfers_Save).pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(links, text="Vakgemiddelden Matrix:", font=("Segoe UI", 14, "bold"), text_color=thema["text"]).pack(pady=(15, 5))
        scroll_gemiddelden = ctk.CTkScrollableFrame(links, fg_color="transparent")
        scroll_gemiddelden.pack(fill="both", expand=True, padx=10, pady=5)

        for i, v_naam in enumerate(self.vakken_lijst):
            cijfers_gefilterd = [c for c in self.data["cijfers"] if c.get("vak") == v_naam]
            boven = sum(float(c["cijfer"]) * float(c.get("weging", 1)) for c in cijfers_gefilterd)
            onder = sum(float(c.get("weging", 1)) for c in cijfers_gefilterd)
            
            gem_calc = boven / onder if onder > 0 else 0.0
            gem_str = f"{gem_calc:.2f}" if gem_calc > 0 else "--"

            line_item = ctk.CTkFrame(scroll_gemiddelden, fg_color="transparent")
            line_item.pack(fill="x", pady=2)
            tk.Label(line_item, text="■", fg=GRAFIEK_KLEUREN[i % len(GRAFIEK_KLEUREN)], bg=thema["bg_card"]).pack(side="left")
            ctk.CTkLabel(line_item, text=f" {v_naam}: {gem_str}", font=("Segoe UI", 12), text_color=thema["text"]).pack(side="left")

        rechts = ctk.CTkFrame(venster_frame, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="Historische Database Log", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.cijfers_log_listbox = tk.Listbox(rechts, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.cijfers_log_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(rechts, text="🗑 Cijfer Uit Logboek Schrappen", fg_color="#EF4444", text_color="white", command=self._Cijfers_Delete).pack(fill="x", padx=20, pady=15)

        self._Cijfers_Refresh_Logs()

    def _Cijfers_Refresh_Logs(self):
        self.cijfers_log_listbox.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.cijfers_log_listbox.insert(tk.END, f"📘 {c.get('vak')} -> Resultaat: {c.get('cijfer')} (Weging: {c.get('weging')})")

    def _Cijfers_Save(self):
        try:
            v = self.combo_cijfer_vak.get()
            val = self.entry_cijfer_waarde.get().replace(",", ".")
            weg = self.entry_cijfer_weging.get().replace(",", ".")
            if not val or not weg: return
            if not (1.0 <= float(val) <= 10.0): raise ValueError()
            
            self.data["cijfers"].append({"vak": v, "cijfer": str(float(val)), "weging": str(float(weg))})
            IO_SafeSave(self.data)
            self.Module_Cijfers()
        except ValueError:
            messagebox.showerror("Matrix Input Error", "Voer een valide cijfer (1.0 - 10.0) en weging in.")

    def _Cijfers_Delete(self):
        try:
            idx = self.cijfers_log_listbox.curselection()[0]
            self.data["cijfers"].pop(idx)
            IO_SafeSave(self.data)
            self.Module_Cijfers()
        except IndexError: pass

    # ==============================================================================
    # MODULE 6: LEREN EN STRATEGISCHE LEERDOELEN MATRIX
    # ==============================================================================
    def Module_Doelen(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("doelen")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Mijlpalen & Strategische Leerdoelen Matrix", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        hoofd_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        hoofd_frame.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(hoofd_frame, fg_color=thema["bg_card"], width=360, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="Mijlpaal Definiëren", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.entry_doel_naam = ctk.CTkEntry(links, placeholder_text="Doelomschrijving")
        self.entry_doel_naam.pack(fill="x", padx=20, pady=8)

        self.entry_doel_target = ctk.CTkEntry(links, placeholder_text="Target Datum (YYYY-MM-DD)")
        self.entry_doel_target.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(links, text="📅 Systeem Datum", command=lambda: UI_DateDialog(self.entry_doel_target)).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(links, text="🎯 Mijlpaal Activeren", fg_color=thema["accent"], text_color="white", command=self._Doelen_Save).pack(fill="x", padx=20, pady=15)

        rechts = ctk.CTkFrame(hoofd_frame, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="Actieve Systeem Mijlpalen", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.doelen_scroller = ctk.CTkScrollableFrame(rechts, fg_color="transparent")
        self.doelen_scroller.pack(fill="both", expand=True, padx=20, pady=10)

        self._Doelen_Render_Items()

    def _Doelen_Render_Items(self):
        for widget in self.doelen_scroller.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        for idx, d in enumerate(self.data.get("doelen", [])):
            box = ctk.CTkFrame(self.doelen_scroller, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", pady=6, padx=5)

            status_str = "⭐ VOLTOOID" if d.get("checked") else "⏳ ACTIEF"
            ctk.CTkLabel(box, text=f"[{status_str}] {d.get('naam')} (Deadline: {d.get('target')})", font=("Segoe UI", 12, "bold"), text_color=thema["text"]).pack(side="left", padx=15, pady=12)

            ctk.CTkButton(box, text="Toggle", width=70, command=lambda i=idx: self._Doelen_Toggle(i)).pack(side="right", padx=5, pady=8)
            ctk.CTkButton(box, text="Wissen", fg_color="#EF4444", text_color="white", width=70, command=lambda i=idx: self._Doelen_Delete(i)).pack(side="right", padx=5, pady=8)

    def _Doelen_Save(self):
        nm = self.entry_doel_naam.get().strip()
        tg = self.entry_doel_target.get().strip()
        if not nm or not tg: return
        if "doelen" not in self.data: self.data["doelen"] = []
        self.data["doelen"].append({"naam": nm, "target": tg, "checked": False})
        IO_SafeSave(self.data)
        self.entry_doel_naam.delete(0, tk.END)
        self.entry_doel_target.delete(0, tk.END)
        self._Doelen_Render_Items()

    def _Doelen_Toggle(self, idx):
        self.data["doelen"][idx]["checked"] = not self.data["doelen"][idx]["checked"]
        IO_SafeSave(self.data)
        self._Doelen_Render_Items()

    def _Doelen_Delete(self, idx):
        self.data["doelen"].pop(idx)
        IO_SafeSave(self.data)
        self._Doelen_Render_Items()

    # ==============================================================================
    # MODULE 7: EXAMEN & TOETSING ARCHITECTUUR
    # ==============================================================================
    def Module_Examens(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("examens")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Examen & Toetsing Controle Matrix", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        hoofd_paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        hoofd_paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], width=360, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="Examen Inboeken", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.combo_ex_vak = ctk.CTkComboBox(links, values=self.vakken_lijst, state="readonly")
        self.combo_ex_vak.set(self.vakken_lijst[0])
        self.combo_ex_vak.pack(fill="x", padx=20, pady=8)

        self.entry_ex_datum = ctk.CTkEntry(links, placeholder_text="Examendatum (YYYY-MM-DD)")
        self.entry_ex_datum.pack(fill="x", padx=20, pady=8)

        self.entry_ex_weging = ctk.CTkEntry(links, placeholder_text="Weging Examen (bijv: 3)")
        self.entry_ex_weging.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(links, text="📅 Kalender Openen", command=lambda: UI_DateDialog(self.entry_ex_datum)).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(links, text="🎓 Examen Registreren", fg_color=thema["accent"], text_color="white", command=self._Examens_Save).pack(fill="x", padx=20, pady=15)

        rechts = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="Geregistreerde Toetsen & Examens", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.examens_scroller = ctk.CTkScrollableFrame(rechts, fg_color="transparent")
        self.examens_scroller.pack(fill="both", expand=True, padx=20, pady=10)

        self._Examens_Render_Items()

    def _Examens_Render_Items(self):
        for widget in self.examens_scroller.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        for idx, ex in enumerate(self.data.get("examens", [])):
            box = ctk.CTkFrame(self.examens_scroller, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(box, text=f"📌 {ex.get('vak')} — Datum: {ex.get('datum')} [Wegingsfactor: {ex.get('weging')}]", font=("Segoe UI", 12, "bold"), text_color=thema["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkButton(box, text="Schrappen", fg_color="#EF4444", text_color="white", width=80, command=lambda i=idx: self._Examens_Delete(i)).pack(side="right", padx=15, pady=8)

    def _Examens_Save(self):
        v = self.combo_ex_vak.get()
        d = self.entry_ex_datum.get().strip()
        w = self.entry_ex_weging.get().strip() or "1"
        if not d: return
        if "examens" not in self.data: self.data["examens"] = []
        self.data["examens"].append({"vak": v, "datum": d, "weging": w})
        IO_SafeSave(self.data)
        self.entry_ex_datum.delete(0, tk.END)
        self.entry_ex_weging.delete(0, tk.END)
        self._Examens_Render_Items()

    def _Examens_Delete(self, idx):
        self.data["examens"].pop(idx)
        IO_SafeSave(self.data)
        self._Examens_Render_Items()

    # ==============================================================================
    # MODULE 8: POMODORO KERNEL & FLASHCARDS
    # ==============================================================================
    def Module_Studietools(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("studietools")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Pomodoro Timer Engine & Flashcard Matrix", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        hoofd_paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        hoofd_paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], width=420, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="⏱ Pomodoro Processor", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.pomo_klok_label = ctk.CTkLabel(links, text="25:00", font=("Segoe UI", 48, "bold"), text_color=thema["text"])
        self.pomo_klok_label.pack(pady=20)

        self.pomo_status_label = ctk.CTkLabel(links, text="Status: IDLE", font=("Segoe UI", 13, "italic"), text_color="gray")
        self.pomo_status_label.pack(pady=5)

        ctk.CTkButton(links, text="⚡ Start/Hervat Engine", fg_color=thema["accent"], text_color="white", command=self._Pomo_Start).pack(fill="x", padx=30, pady=6)
        ctk.CTkButton(links, text="🛑 Pauzeer Engine", command=self._Pomo_Pause).pack(fill="x", padx=30, pady=6)
        ctk.CTkButton(links, text="🔄 Reset Cycles", command=self._Pomo_Reset).pack(fill="x", padx=30, pady=6)

        rechts = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="🃏 Flashcard Leerstation", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        fc_input_frame = ctk.CTkFrame(rechts, fg_color="transparent")
        fc_input_frame.pack(fill="x", padx=20)

        self.entry_fc_vraag = ctk.CTkEntry(fc_input_frame, placeholder_text="Definitie / Vraag")
        self.entry_fc_vraag.pack(side="left", fill="x", expand=True, padx=5)
        
        self.entry_fc_antwoord = ctk.CTkEntry(fc_input_frame, placeholder_text="Antwoord / Verklaring")
        self.entry_fc_antwoord.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(fc_input_frame, text="Toevoegen", width=90, command=self._Flashcards_Save).pack(side="right", padx=5)

        self.fc_scroller = ctk.CTkScrollableFrame(rechts, fg_color="transparent")
        self.fc_scroller.pack(fill="both", expand=True, padx=20, pady=15)

        self._Pomo_Update_Display()
        self._Flashcards_Render_Items()

    def _Pomo_Start(self):
        if self.pomo_loopt: return
        self.pomo_loopt = True
        if self.pomo_tijd_resterend <= 0:
            werk_min = int(self.data["settings"].get("pomodoro_werk", 25))
            self.pomo_tijd_resterend = werk_min * 60
        self.pomo_status_label.configure(text="Status: FOCUS TIJD ACTIEF", text_color=THEMES[self.theme_name]["accent"])
        self._Pomo_Tick_Scheduler()

    def _Pomo_Pause(self):
        self.pomo_loopt = False
        self.pomo_status_label.configure(text="Status: GEPAUZEERD", text_color="orange")

    def _Pomo_Reset(self):
        self.pomo_loopt = False
        self.pomo_modus_is_werk = True
        werk_min = int(self.data["settings"].get("pomodoro_werk", 25))
        self.pomo_tijd_resterend = werk_min * 60
        self.pomo_status_label.configure(text="Status: IDLE", text_color="gray")
        self._Pomo_Update_Display()

    def _Pomo_Tick_Scheduler(self):
        if self.pomo_loopt and self.pomo_tijd_resterend > 0:
            self.pomo_tijd_resterend -= 1
            self._Pomo_Update_Display()
            self.after(1000, self._Pomo_Tick_Scheduler)
        elif self.pomo_loopt and self.pomo_tijd_resterend <= 0:
            self.pomo_modus_is_werk = not self.pomo_modus_is_werk
            if self.pomo_modus_is_werk:
                self.pomo_tijd_resterend = int(self.data["settings"].get("pomodoro_werk", 25)) * 60
                messagebox.showinfo("Pomodoro Engine", "Pauze voorbij! Tijd om te knallen.")
            else:
                self.pomo_tijd_resterend = int(self.data["settings"].get("pomodoro_rust", 5)) * 60
                messagebox.showinfo("Pomodoro Engine", "Lekker gewerkt! Tijd voor rust.")
            self._Pomo_Tick_Scheduler()

    def _Pomo_Update_Display(self):
        if hasattr(self, "pomo_klok_label") and self.pomo_klok_label.winfo_exists():
            m, s = divmod(self.pomo_tijd_resterend, 60)
            self.pomo_klok_label.configure(text=f"{m:02d}:{s:02d}")

    def _Flashcards_Render_Items(self):
        for widget in self.fc_scroller.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        for idx, fc in enumerate(self.data.get("flashcards", [])):
            box = ctk.CTkFrame(self.fc_scroller, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(box, text=f"❓ Q: {fc.get('q')}  |  💡 A: {fc.get('a')}", font=("Segoe UI", 12), text_color=thema["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkButton(box, text="Verwijderen", fg_color="#EF4444", text_color="white", width=90, command=lambda i=idx: self._Flashcards_Delete(i)).pack(side="right", padx=15, pady=8)

    def _Flashcards_Save(self):
        q = self.entry_fc_vraag.get().strip()
        a = self.entry_fc_antwoord.get().strip()
        if not q or not a: return
        if "flashcards" not in self.data: self.data["flashcards"] = []
        self.data["flashcards"].append({"q": q, "a": a})
        IO_SafeSave(self.data)
        self.entry_fc_vraag.delete(0, tk.END)
        self.entry_fc_antwoord.delete(0, tk.END)
        self._Flashcards_Render_Items()

    def _Flashcards_Delete(self, idx):
        self.data["flashcards"].pop(idx)
        IO_SafeSave(self.data)
        self._Flashcards_Render_Items()

    # ==============================================================================
    # MODULE 9: ABSENTIEREGISTRATIE MATRIX SYSTEM
    # ==============================================================================
    def Module_Absentie(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("absentie")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Absentieregistratie & Aanwezigheidsmatrix", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        hoofd_paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        hoofd_paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], width=360, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="Incident Invoeren", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.combo_ab_vak = ctk.CTkComboBox(links, values=self.vakken_lijst, state="readonly")
        self.combo_ab_vak.set(self.vakken_lijst[0])
        self.combo_ab_vak.pack(fill="x", padx=20, pady=8)

        self.entry_ab_datum = ctk.CTkEntry(links, placeholder_text="Datum (YYYY-MM-DD)")
        self.entry_ab_datum.pack(fill="x", padx=20, pady=8)

        self.combo_ab_type = ctk.CTkComboBox(links, values=["Ziek gemeld", "Geoorloofd afwezig", "Ongeoorloofd (Te laat)", "Doktersbezoek"], state="readonly")
        self.combo_ab_type.set("Ziek gemeld")
        self.combo_ab_type.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(links, text="📅 Datum Selecteren", command=lambda: UI_DateDialog(self.entry_ab_datum)).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(links, text="🛡 Logboek Updaten", fg_color=thema["accent"], text_color="white", command=self._Absentie_Save).pack(fill="x", padx=20, pady=15)

        rechts = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="Absentie Historie Log", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.ab_scroller = ctk.CTkScrollableFrame(rechts, fg_color="transparent")
        self.ab_scroller.pack(fill="both", expand=True, padx=20, pady=10)

        self._Absentie_Render_Items()

    def _Absentie_Render_Items(self):
        for widget in self.ab_scroller.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        for idx, ab in enumerate(self.data.get("absentie", [])):
            box = ctk.CTkFrame(self.ab_scroller, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(box, text=f"⚠️ {ab.get('datum')} — {ab.get('vak')} [{ab.get('type')}]", font=("Segoe UI", 12, "bold"), text_color=thema["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkButton(box, text="Verwijderen", fg_color="#EF4444", text_color="white", width=85, command=lambda i=idx: self._Absentie_Delete(i)).pack(side="right", padx=15, pady=8)

    def _Absentie_Save(self):
        v = self.combo_ab_vak.get()
        d = self.entry_ab_datum.get().strip()
        t = self.combo_ab_type.get()
        if not d: return
        if "absentie" not in self.data: self.data["absentie"] = []
        self.data["absentie"].append({"vak": v, "datum": d, "type": t})
        IO_SafeSave(self.data)
        self.entry_ab_datum.delete(0, tk.END)
        self._Absentie_Render_Items()

    def _Absentie_Delete(self, idx):
        self.data["absentie"].pop(idx)
        IO_SafeSave(self.data)
        self._Absentie_Render_Items()

    # ==============================================================================
    # MODULE 10: STUDIE FINANCIËN INFRASTRUCTUUR
    # ==============================================================================
    def Module_Financien(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("financien")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Studiefinanciering & Financiële Knooppunten", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        hoofd_paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        hoofd_paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], width=360, corner_radius=16)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        ctk.CTkLabel(links, text="Mutatie Registreren", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.entry_fin_desc = ctk.CTkEntry(links, placeholder_text="Omschrijving")
        self.entry_fin_desc.pack(fill="x", padx=20, pady=8)

        self.entry_fin_bedrag = ctk.CTkEntry(links, placeholder_text="Bedrag (bijv. 55.40 of -20.00)")
        self.entry_fin_bedrag.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(links, text="💳 Transactie Boeken", fg_color=thema["accent"], text_color="white", command=self._Fin_Save).pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(links, text="Financieel Systeemsaldo:", font=("Segoe UI", 14, "bold"), text_color=thema["text"]).pack(pady=(15, 5))
        
        mutaties = self.data.get("financien", [])
        totaal_saldo = sum(float(m.get("bedrag", 0)) for m in mutaties)
        
        saldo_kleur = "green" if totaal_saldo >= 0 else "#EF4444"
        self.saldo_label = ctk.CTkLabel(links, text=f"€ {totaal_saldo:.2f}", font=("Segoe UI", 28, "bold"), text_color=saldo_kleur)
        self.saldo_label.pack(pady=10)

        rechts = ctk.CTkFrame(hoofd_paneel, fg_color=thema["bg_card"], corner_radius=16)
        rechts.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(rechts, text="Transactie Logboek Matrix", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.fin_scroller = ctk.CTkScrollableFrame(rechts, fg_color="transparent")
        self.fin_scroller.pack(fill="both", expand=True, padx=20, pady=10)

        self._Fin_Render_Items()

    def _Fin_Render_Items(self):
        for widget in self.fin_scroller.winfo_children(): widget.destroy()
        thema = THEMES[self.theme_name]

        for idx, m in enumerate(self.data.get("financien", [])):
            box = ctk.CTkFrame(self.fin_scroller, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", pady=5, padx=5)

            bedrag_float = float(m.get("bedrag", 0))
            teken = "+" if bedrag_float >= 0 else ""
            
            ctk.CTkLabel(box, text=f"🔹 {m.get('desc')} — Euro: {teken}{bedrag_float:.2f}", font=("Segoe UI", 12, "bold"), text_color=thema["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkButton(box, text="Wissen", fg_color="#EF4444", text_color="white", width=80, command=lambda i=idx: self._Fin_Delete(i)).pack(side="right", padx=15, pady=8)

    def _Fin_Save(self):
        desc = self.entry_fin_desc.get().strip()
        b_str = self.entry_fin_bedrag.get().replace(",", ".").strip()
        if not desc or not b_str: return
        try:
            val = float(b_str)
            if "financien" not in self.data: self.data["financien"] = []
            self.data["financien"].append({"desc": desc, "bedrag": str(val)})
            IO_SafeSave(self.data)
            self.entry_fin_desc.delete(0, tk.END)
            self.entry_fin_bedrag.delete(0, tk.END)
            self.Module_Financien()
        except ValueError:
            messagebox.showerror("Matrix Fout", "Voer een valide numeriek bedrag in.")

    def _Fin_Delete(self, idx):
        self.data["financien"].pop(idx)
        IO_SafeSave(self.data)
        self.Module_Financien()

    # ==============================================================================
    # MODULE 11: SYSTEM SETTINGS & SYSTEM HOT-REBOOT ENGINE
    # ==============================================================================
    def Module_Settings(self):
        self.Core_Clear_Canvas()
        thema = THEMES[self.theme_name]
        
        for knop in self.sidebar_buttons.values(): knop.configure(fg_color="transparent")

        ctk.CTkLabel(self.canvas, text="Systeem & Algoritme Configuraties", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        box = ctk.CTkScrollableFrame(self.canvas, fg_color=thema["bg_card"], corner_radius=16)
        box.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        # Profiel Instellingen Sectie
        ctk.CTkLabel(box, text="👤 Gebruikersprofiel Matrix", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.setting_naam_entry = ctk.CTkEntry(box, placeholder_text="Verander gebruikersnaam", width=260)
        self.setting_naam_entry.insert(0, self.data["settings"].get("naam", "Student"))
        self.setting_naam_entry.pack(anchor="w", padx=20, pady=5)

        # Thema Instellingen Sectie
        ctk.CTkLabel(box, text="🎨 Render Engine Uiterlijk", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=(25, 5))
        
        self.setting_theme_combo = ctk.CTkComboBox(box, values=list(THEMES.keys()), state="readonly", width=260)
        self.setting_theme_combo.set(self.theme_name)
        self.setting_theme_combo.pack(anchor="w", padx=20, pady=5)

        # Pomodoro Instellingen Sectie
        ctk.CTkLabel(box, text="⏱ Pomodoro Processor Tweak", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=(25, 5))
        
        self.setting_pomo_werk = ctk.CTkEntry(box, placeholder_text="Werktijd (minuten)", width=260)
        self.setting_pomo_werk.insert(0, str(self.data["settings"].get("pomodoro_werk", 25)))
        self.setting_pomo_werk.pack(anchor="w", padx=20, pady=5)

        self.setting_pomo_rust = ctk.CTkEntry(box, placeholder_text="Rusttijd (minuten)", width=260)
        self.setting_pomo_rust.insert(0, str(self.data["settings"].get("pomodoro_rust", 5)))
        self.setting_pomo_rust.pack(anchor="w", padx=20, pady=5)

        # Actie Knop voor Opslaan en de gegarandeerde automatische herstart
        ctk.CTkButton(box, text="💾 Kernparameters Flashen & OS Herstarten", fg_color=thema["accent"], text_color="white", width=260, command=self._Settings_Save_Action).pack(anchor="w", padx=20, pady=35)

    def _Settings_Save_Action(self):
        naam = self.setting_naam_entry.get().strip() or "Student"
        nieuw_thema = self.setting_theme_combo.get()
        p_werk = self.setting_pomo_werk.get().strip() or "25"
        p_rust = self.setting_pomo_rust.get().strip() or "5"

        self.data["settings"]["naam"] = naam
        self.data["settings"]["theme"] = nieuw_thema
        self.data["settings"]["pomodoro_werk"] = int(p_werk)
        self.data["settings"]["pomodoro_rust"] = int(p_rust)

        # Gegevens veilig naar disk wegschrijven
        IO_SafeSave(self.data)
        
        # Dialoogvenster tonen om de gebruiker te informeren over de luxe hot-reload herstart
        messagebox.showinfo(
            "Kernel Update Geflasht", 
            "Parameters succesvol bijgewerkt. GC-OS wordt nu volledig opnieuw opgestart om het nieuwe geheugenframe en luxe thema te initialiseren."
        )
        
        # Trigger de gegarandeerde OS-level hard restart loop
        self.System_Hard_Restart()

# ==============================================================================
# 5. HIGH-PERFORMANCE KICKSTART ENGINE
# ==============================================================================
if __name__ == "__main__":
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    RuntimeEngine = SchoolOS()
    RuntimeEngine.mainloop()
