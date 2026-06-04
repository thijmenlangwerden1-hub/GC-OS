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

# ==============================================================================
# 2. PERSISTENT STORAGE ENGINE
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
        
        self.data = IO_SafeLoad()
        self.theme_name = self.data["settings"].get("theme", "Zwart")
        if self.theme_name not in THEMES:
            self.theme_name = "Zwart"

        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        self.title(f"GraafschapCollege-OS — Enterprise Edition Suite [v{HUIDIGE_VERSIE}]")
        self.geometry("1440x900")
        self.minsize(1200, 800)

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

        self._Core_Build_Layout()
        self.Core_Apply_Theme()
        
        self.after(100, self.Core_Bootloader_Sequence)

    def _Core_Build_Layout(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_header = ctk.CTkLabel(self.sidebar, text="GC-OS ULTIMATE", font=("Segoe UI", 22, "bold"))
        self.sidebar_header.pack(pady=(35, 5), padx=25, anchor="w")
        
        self.sidebar_sub = ctk.CTkLabel(self.sidebar, text=f"Kernel: {CODENAME} Build", font=("Segoe UI", 11), text_color="gray")
        self.sidebar_sub.pack(pady=(0, 25), padx=25, anchor="w")

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
        if actieve_sleutel == "settings":
            self.instellingen_knop.configure(fg_color=thema["button_fg"], text_color=thema["button_text"])
        else:
            self.instellingen_knop.configure(fg_color="transparent", text_color=thema["sidebar_text"])

    def Core_Bootloader_Sequence(self):
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

        tech_header = ctk.CTkFrame(boot_window, height=4, fg_color=thema["accent"])
        tech_header.pack(fill="x", side="top")

        center_container = ctk.CTkFrame(boot_window, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.45, anchor="center")

        logo_sub_label = ctk.CTkLabel(center_container, text="GRAAFSCHAP COLLEGE", font=("Segoe UI", 14, "tracking_widest"), text_color="gray")
        logo_sub_label.pack(pady=0)

        titel_label = ctk.CTkLabel(center_container, text="G C ‑ O S  P R O", font=("Segoe UI", 52, "bold"), text_color=thema["accent"])
        titel_label.pack(pady=(5, 10))
        
        ver_label = ctk.CTkLabel(center_container, text=f"SYSTEM VERSION {HUIDIGE_VERSIE} • ARCH: X64", font=("Consolas", 11), text_color="gray")
        ver_label.pack(pady=(0, 30))

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
                if stap % 15 == 0 and log_index < len(boot_logs):
                    huidige_log = boot_logs[log_index]
                    log_text.configure(text=f"{log_text.cget('text')}\n{huidige_log}")
                    log_index += 1
                vertraging = random.randint(15, 45) if 40 < stap < 70 else 15
                self.after(vertraging, lambda: SimuleerStappen(stap + 1, log_index))
            else:
                boot_window.destroy()
                self.deiconify()
                try: self.state("zoomed")
                except Exception: pass
                self.Module_Dashboard()

        SimuleerStappen(0, 0)

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
    # MODULE 2: HUISWERK PLANNER SYSTEM
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
    # MODULE 3: MATRIX LESROOSTER
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
                    ctk.CTkLabel(r_item, text=f"📅 {les.get('datum')}  |  ⏰ {les.get('tijd')}  |  📘 {les.get('vak')}  |  📍 Lokaal: {les.get('lokaal')}  |  👨‍🏫 Docent: {les.get('docent')}", font=("Segoe UI", 12), text_color=thema["text"]).pack(side="left", padx=15, pady=10)

    def _Rooster_Save_Lesson(self):
        self.data["rooster"].append({
            "vak": self.combo_rst_vak.get(), "datum": self.entry_rst_datum.get().strip(),
            "tijd": self.combo_rst_tijd.get(), "lokaal": self.entry_rst_lokaal.get().strip() or "N/A",
            "docent": self.entry_rst_docent.get().strip() or "N/A"
        })
        IO_SafeSave(self.data)
        self._Rooster_Render_Core()

    def _Rooster_Purge(self):
        if messagebox.askyesno("Systeemverificatie", "Weet u zeker dat u alle lesroosters wilt legen?"):
            self.data["rooster"] = []
            IO_SafeSave(self.data)
            self._Rooster_Render_Core()

    # ==============================================================================
    # MODULE 4: KENNISBANK & NOTITIES
    # ==============================================================================
    def Module_Notities(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("notities")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Kennisbank & Notities", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=300)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        self.note_listbox = tk.Listbox(links, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.note_listbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_listbox.bind("<<ListboxSelect>>", self._Note_Select)

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        rechts.pack(side="right", fill="both", expand=True)

        self.note_title = ctk.CTkEntry(rechts, placeholder_text="Titel van de notitie", font=("Segoe UI", 14, "bold"))
        self.note_title.pack(fill="x", padx=20, pady=(20, 10))

        self.note_text = tk.Text(rechts, font=("Segoe UI", 12), bg=thema["list_bg"], fg=thema["list_fg"], insertbackground=thema["text"], borderwidth=0, highlightthickness=0)
        self.note_text.pack(fill="both", expand=True, padx=20, pady=10)

        knoppen_balk = ctk.CTkFrame(rechts, fg_color="transparent")
        knoppen_balk.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(knoppen_balk, text="💾 Opslaan", fg_color=thema["accent"], text_color="white", command=self._Note_Save).pack(side="left", padx=5)
        ctk.CTkButton(knoppen_balk, text="➕ Nieuw", command=self._Note_New).pack(side="left", padx=5)
        ctk.CTkButton(knoppen_balk, text="🗑 Verwijderen", fg_color="#EF4444", text_color="white", command=self._Note_Delete).pack(side="right", padx=5)

        self._Note_Render_List()

    def _Note_Render_List(self):
        self.note_listbox.delete(0, tk.END)
        for n in self.data["notities"]:
            self.note_listbox.insert(tk.END, n.get("titel", "Naamloos"))

    def _Note_Select(self, event):
        try:
            idx = self.note_listbox.curselection()[0]
            note = self.data["notities"][idx]
            self.note_title.delete(0, tk.END)
            self.note_title.insert(0, note["titel"])
            self.note_text.delete("1.0", tk.END)
            self.note_text.insert("1.0", note["inhoud"])
        except IndexError: pass

    def _Note_New(self):
        self.note_title.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)

    def _Note_Save(self):
        t = self.note_title.get().strip() or "Naamloos"
        i = self.note_text.get("1.0", tk.END).strip()
        
        try:
            idx = self.note_listbox.curselection()[0]
            self.data["notities"][idx] = {"titel": t, "inhoud": i}
        except IndexError:
            self.data["notities"].append({"titel": t, "inhoud": i})

        IO_SafeSave(self.data)
        self._Note_Render_List()

    def _Note_Delete(self):
        try:
            idx = self.note_listbox.curselection()[0]
            self.data["notities"].pop(idx)
            IO_SafeSave(self.data)
            self._Note_New()
            self._Note_Render_List()
        except IndexError: pass

    # ==============================================================================
    # MODULE 5: CIJFER & KPI ANALYSE
    # ==============================================================================
    def Module_Cijfers(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("cijfers")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Cijfer & KPI Analyse Centrum", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkScrollableFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        links.pack(side="left", fill="both", expand=True, padx=(0, 15))

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Resultaat Registreren", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_fig_vak = ctk.CTkComboBox(rechts, values=self.vakken_lijst, state="readonly")
        self.entry_fig_vak.set(self.vakken_lijst[0])
        self.entry_fig_vak.pack(fill="x", padx=20, pady=8)

        self.entry_fig_grade = ctk.CTkEntry(rechts, placeholder_text="Cijfer (bijv. 7.5)")
        self.entry_fig_grade.pack(fill="x", padx=20, pady=8)

        self.entry_fig_weight = ctk.CTkEntry(rechts, placeholder_text="Weging (bijv. 2)")
        self.entry_fig_weight.insert(0, "1")
        self.entry_fig_weight.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="💾 Matrix Updaten", fg_color=thema["accent"], text_color="white", command=self._Grade_Save).pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(rechts, text="🗑 Alles Opschonen", fg_color="#EF4444", text_color="white", command=self._Grade_Purge).pack(fill="x", padx=20, pady=5)

        self.grade_scroll = links
        self._Grade_Render()

    def _Grade_Render(self):
        for w in self.grade_scroll.winfo_children(): w.destroy()
        thema = THEMES[self.theme_name]

        # Per vak berekenen
        for vak in self.vakken_lijst:
            vak_cijfers = [c for c in self.data["cijfers"] if c.get("vak") == vak]
            if not vak_cijfers: continue

            boven = sum(float(c["cijfer"]) * float(c["weging"]) for c in vak_cijfers)
            onder = sum(float(c["weging"]) for c in vak_cijfers)
            gemiddelde = boven / max(onder, 1)

            box = ctk.CTkFrame(self.grade_scroll, fg_color=thema["bg_root"], corner_radius=12)
            box.pack(fill="x", padx=15, pady=8)

            ctk.CTkLabel(box, text=vak, font=("Segoe UI", 14, "bold"), text_color=thema["text"]).pack(side="left", padx=15, pady=15)
            
            # Progress bar als visuele KPI meter
            pb = ctk.CTkProgressBar(box, width=200, progress_color="#10B981" if gemiddelde >= 5.5 else "#EF4444")
            pb.pack(side="left", padx=20)
            pb.set(gemiddelde / 10.0)

            ctk.CTkLabel(box, text=f"Gemiddelde: {gemiddelde:.2f} (Weging: {onder})", font=("Segoe UI", 12, "bold"), text_color=thema["accent"]).pack(side="right", padx=15)

    def _Grade_Save(self):
        try:
            cijfer = float(self.entry_fig_grade.get().replace(",", "."))
            weging = float(self.entry_fig_weight.get())
            if not (1.0 <= cijfer <= 10.0): raise ValueError
            
            self.data["cijfers"].append({"vak": self.entry_fig_vak.get(), "cijfer": cijfer, "weging": weging})
            IO_SafeSave(self.data)
            self._Grade_Render()
            self.entry_fig_grade.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Validatiefout", "Voer een geldig cijfer (1-10) en weging in.")

    def _Grade_Purge(self):
        if messagebox.askyesno("Systeemverificatie", "Alle cijfers permanent wissen?"):
            self.data["cijfers"] = []
            IO_SafeSave(self.data)
            self._Grade_Render()

    # ==============================================================================
    # MODULE 6: MIJLPalen & DOELEN
    # ==============================================================================
    def Module_Doelen(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("doelen")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Mijlpalen & Strategische Doelen", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        self.goal_scroll = ctk.CTkScrollableFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        self.goal_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15))

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Doel Toevoegen", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_goal = ctk.CTkEntry(rechts, placeholder_text="Wat is je mijlpaal?")
        self.entry_goal.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(rechts, text="🎯 Vastleggen", fg_color=thema["accent"], text_color="white", command=self._Goal_Save).pack(fill="x", padx=20, pady=10)

        self._Goal_Render()

    def _Goal_Render(self):
        for w in self.goal_scroll.winfo_children(): w.destroy()
        thema = THEMES[self.theme_name]

        for i, doel in enumerate(self.data["doelen"]):
            box = ctk.CTkFrame(self.goal_scroll, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", padx=15, pady=6)

            tekst_stijl = ("Segoe UI", 13, "overstrike" if doel.get("klaar") else "normal")
            ctk.CTkLabel(box, text=doel["doel"], font=tekst_stijl, text_color=thema["text"]).pack(side="left", padx=15, pady=12)

            btn_del = ctk.CTkButton(box, text="🗑", width=35, fg_color="#EF4444", text_color="white", command=lambda idx=i: self._Goal_Delete(idx))
            btn_del.pack(side="right", padx=10)

            btn_tog = ctk.CTkButton(box, text="✔" if not doel.get("klaar") else "🔄", width=35, command=lambda idx=i: self._Goal_Toggle(idx))
            btn_tog.pack(side="right", padx=5)

    def _Goal_Save(self):
        g = self.entry_goal.get().strip()
        if g:
            self.data["doelen"].append({"doel": g, "klaar": False})
            IO_SafeSave(self.data)
            self._Goal_Render()
            self.entry_goal.delete(0, tk.END)

    def _Goal_Toggle(self, idx):
        self.data["doelen"][idx]["klaar"] = not self.data["doelen"][idx]["klaar"]
        IO_SafeSave(self.data)
        self._Goal_Render()

    def _Goal_Delete(self, idx):
        self.data["doelen"].pop(idx)
        IO_SafeSave(self.data)
        self._Goal_Render()

    # ==============================================================================
    # MODULE 7: EXAMEN & TOETSING
    # ==============================================================================
    def Module_Examens(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("examens")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Examen & Toetsing Controlekamer", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        self.ex_scroll = ctk.CTkScrollableFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        self.ex_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15))

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Toets Inplannen", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_ex_vak = ctk.CTkComboBox(rechts, values=self.vakken_lijst, state="readonly")
        self.entry_ex_vak.set(self.vakken_lijst[0])
        self.entry_ex_vak.pack(fill="x", padx=20, pady=8)

        self.entry_ex_stof = ctk.CTkEntry(rechts, placeholder_text="Examenstof / Omschrijving")
        self.entry_ex_stof.pack(fill="x", padx=20, pady=8)

        self.entry_ex_datum = ctk.CTkEntry(rechts, placeholder_text="Datum (YYYY-MM-DD)")
        self.entry_ex_datum.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="📅 Datum Kiezen", command=lambda: UI_DateDialog(self.entry_ex_datum)).pack(fill="x", padx=20, pady=6)
        ctk.CTkButton(rechts, text="🎓 Vastleggen", fg_color=thema["accent"], text_color="white", command=self._Exam_Save).pack(fill="x", padx=20, pady=12)

        self._Exam_Render()

    def _Exam_Render(self):
        for w in self.ex_scroll.winfo_children(): w.destroy()
        thema = THEMES[self.theme_name]

        for i, ex in enumerate(self.data["examens"]):
            box = ctk.CTkFrame(self.ex_scroll, fg_color=thema["bg_root"], corner_radius=12)
            box.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(box, text=f"📅 {ex['datum']} | {ex['vak']} -> Stof: {ex['stof']}", font=("Segoe UI", 13), text_color=thema["text"]).pack(side="left", padx=15, pady=15)
            
            btn_del = ctk.CTkButton(box, text="🗑", width=40, fg_color="#EF4444", text_color="white", command=lambda idx=i: self._Exam_Delete(idx))
            btn_del.pack(side="right", padx=15)

    def _Exam_Save(self):
        v = self.entry_ex_vak.get()
        s = self.entry_ex_stof.get().strip()
        d = self.entry_ex_datum.get().strip()
        if v and s and d:
            self.data["examens"].append({"vak": v, "stof": s, "datum": d})
            IO_SafeSave(self.data)
            self._Exam_Render()
            self.entry_ex_stof.delete(0, tk.END)
            self.entry_ex_datum.delete(0, tk.END)

    def _Exam_Delete(self, idx):
        self.data["examens"].pop(idx)
        IO_SafeSave(self.data)
        self._Exam_Render()

    # ==============================================================================
    # MODULE 8: STUDIETOOLS (POMODORO & FLASHCARDS)
    # ==============================================================================
    def Module_Studietools(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("studietools")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Deep Work & Studietools Workspace", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        grid = ctk.CTkFrame(self.canvas, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        grid.columnconfigure((0, 1), weight=1, uniform="tools_grid")

        # Pomodoro Container
        pomo_card = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        pomo_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(pomo_card, text="⏱ Threaded Pomodoro Timer", font=("Segoe UI", 18, "bold"), text_color=thema["accent"]).pack(pady=20)
        self.pomo_label = ctk.CTkLabel(pomo_card, text="25:00", font=("Consolas", 48, "bold"), text_color=thema["text"])
        self.pomo_label.pack(pady=10)

        pomo_btns = ctk.CTkFrame(pomo_card, fg_color="transparent")
        pomo_btns.pack(pady=20)
        ctk.CTkButton(pomo_btns, text="▶ Start", width=90, fg_color="#10B981", text_color="white", command=self._Pomo_Start).pack(side="left", padx=5)
        ctk.CTkButton(pomo_btns, text="⏸ Pause", width=90, fg_color="#F59E0B", text_color="white", command=self._Pomo_Pause).pack(side="left", padx=5)
        ctk.CTkButton(pomo_btns, text="🔄 Reset", width=90, command=self._Pomo_Reset).pack(side="left", padx=5)

        # Flashcard Container
        fc_card = ctk.CTkFrame(grid, corner_radius=16, fg_color=thema["bg_card"])
        fc_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(fc_card, text="🧠 Flashcard Matrix Engine", font=("Segoe UI", 18, "bold"), text_color=thema["accent"]).pack(pady=15)
        
        self.fc_q = ctk.CTkEntry(fc_card, placeholder_text="Vraag / Concept")
        self.fc_q.pack(fill="x", padx=30, pady=5)
        self.fc_a = ctk.CTkEntry(fc_card, placeholder_text="Antwoord / Definitie")
        self.fc_a.pack(fill="x", padx=30, pady=5)
        ctk.CTkButton(fc_card, text="➕ Inladen in Geheugen", command=self._Fc_Save).pack(pady=10)

        ctk.CTkFrame(fc_card, height=2, fg_color=thema["bg_root"]).pack(fill="x", padx=30, pady=10)
        
        self.fc_display = ctk.CTkButton(fc_card, text="Klik hier om een Flashcard te trekken", font=("Segoe UI", 13, "italic"), height=60, fg_color=thema["bg_root"], text_color=thema["text"], command=self._Fc_Flip)
        self.fc_display.pack(fill="x", padx=30, pady=10)
        self.huidige_fc = None

    def _Pomo_Start(self):
        if not self.pomo_loopt:
            self.pomo_loopt = True
            if self.pomo_tijd_resterend == 0:
                minuten = self.data["settings"].get("pomodoro_werk", 25) if self.pomo_modus_is_werk else self.data["settings"].get("pomodoro_rust", 5)
                self.pomo_tijd_resterend = minuten * 60
            threading.Thread(target=self._Pomo_Thread_Loop, daemon=True).start()

    def _Pomo_Thread_Loop(self):
        while self.pomo_loopt and self.pomo_tijd_resterend > 0:
            mins, secs = divmod(self.pomo_tijd_resterend, 60)
            if hasattr(self, "pomo_label") and self.pomo_label.winfo_exists():
                self.pomo_label.configure(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            self.pomo_tijd_resterend -= 1
        
        if self.pomo_tijd_resterend == 0 and self.pomo_loopt:
            self.pomo_loopt = False
            self.pomo_modus_is_werk = not self.pomo_modus_is_werk
            messagebox.showinfo("Pomodoro Systeem", "Tijd is om! Schakelen naar de volgende modus.")
            self._Pomo_Reset()

    def _Pomo_Pause(self):
        self.pomo_loopt = False

    def _Pomo_Reset(self):
        self.pomo_loopt = False
        self.pomo_tijd_resterend = 0
        m = self.data["settings"].get("pomodoro_werk", 25) if self.pomo_modus_is_werk else self.data["settings"].get("pomodoro_rust", 5)
        self.pomo_label.configure(text=f"{m:02d}:00")

    def _Fc_Save(self):
        q = self.fc_q.get().strip()
        a = self.fc_a.get().strip()
        if q and a:
            self.data["flashcards"].append({"q": q, "a": a})
            IO_SafeSave(self.data)
            self.fc_q.delete(0, tk.END)
            self.fc_a.delete(0, tk.END)
            messagebox.showinfo("Matrix Engine", "Kaart succesvol opgeslagen.")

    def _Fc_Flip(self):
        if not self.data["flashcards"]:
            self.fc_display.configure(text="Geen kaarten beschikbaar. Voeg er eerst een toe.")
            return
        
        if self.huidige_fc is None:
            self.huidige_fc = random.choice(self.data["flashcards"])
            self.fc_display.configure(text=f"VRAAG: {self.huidige_fc['q']}\n(Klik voor antwoord)")
        else:
            self.fc_display.configure(text=f"ANTWOORD: {self.huidige_fc['a']}\n(Klik voor volgende kaart)")
            self.huidige_fc = None

    # ==============================================================================
    # MODULE 9: ABSENTIEREGISTRATIE
    # ==============================================================================
    def Module_Absentie(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("absentie")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Absentieregistratie & Logboek", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        self.abs_scroll = ctk.CTkScrollableFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        self.abs_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15))

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Absentie Melden", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_abs_type = ctk.CTkComboBox(rechts, values=["Ziek", "Dokter / Tandarts", "Verlof", "Te Laat"], state="readonly")
        self.entry_abs_type.set("Ziek")
        self.entry_abs_type.pack(fill="x", padx=20, pady=8)

        self.entry_abs_datum = ctk.CTkEntry(rechts, placeholder_text="Datum (YYYY-MM-DD)")
        self.entry_abs_datum.insert(0, str(dt.date.today()))
        self.entry_abs_datum.pack(fill="x", padx=20, pady=8)

        self.entry_abs_reden = ctk.CTkEntry(rechts, placeholder_text="Reden / Toelichting")
        self.entry_abs_reden.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="🛡 Logboek Updaten", fg_color=thema["accent"], text_color="white", command=self._Abs_Save).pack(fill="x", padx=20, pady=15)

        self._Abs_Render()

    def _Abs_Render(self):
        for w in self.abs_scroll.winfo_children(): w.destroy()
        thema = THEMES[self.theme_name]

        for i, ab in enumerate(self.data["absentie"]):
            box = ctk.CTkFrame(self.abs_scroll, fg_color=thema["bg_root"], corner_radius=12)
            box.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(box, text=f"⚠️ [{ab['type']}] {ab['datum']} - Reden: {ab['reden']}", font=("Segoe UI", 13), text_color=thema["text"]).pack(side="left", padx=15, pady=15)
            
            btn_del = ctk.CTkButton(box, text="🗑", width=40, fg_color="#EF4444", text_color="white", command=lambda idx=i: self._Abs_Delete(idx))
            btn_del.pack(side="right", padx=15)

    def _Abs_Save(self):
        t = self.entry_abs_type.get()
        d = self.entry_abs_datum.get().strip()
        r = self.entry_abs_reden.get().strip() or "Geen toelichting"
        if t and d:
            self.data["absentie"].append({"type": t, "datum": d, "reden": r})
            IO_SafeSave(self.data)
            self._Abs_Render()
            self.entry_abs_reden.delete(0, tk.END)

    def _Abs_Delete(self, idx):
        self.data["absentie"].pop(idx)
        IO_SafeSave(self.data)
        self._Abs_Render()

    # ==============================================================================
    # MODULE 10: STUDIEFINANCIERING & FINANCIËN
    # ==============================================================================
    def Module_Financien(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("financien")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Studiefinanciering & Budget Balans", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        self.fin_scroll = ctk.CTkScrollableFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        self.fin_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15))

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Mutatie Boeken", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)
        self.entry_fin_desc = ctk.CTkEntry(rechts, placeholder_text="Omschrijving (bijv. Duo, Boeken)")
        self.entry_fin_desc.pack(fill="x", padx=20, pady=8)

        self.entry_fin_val = ctk.CTkEntry(rechts, placeholder_text="Bedrag (bijv. 450.00 of -25.50)")
        self.entry_fin_val.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="💳 Mutatie Uitvoeren", fg_color=thema["accent"], text_color="white", command=self._Fin_Save).pack(fill="x", padx=20, pady=15)

        self._Fin_Render()

    def _Fin_Render(self):
        for w in self.fin_scroll.winfo_children(): w.destroy()
        thema = THEMES[self.theme_name]

        totaal_balans = sum(float(f["bedrag"]) for f in self.data["financien"])
        
        balans_kaart = ctk.CTkFrame(self.fin_scroll, fg_color=thema["button_fg"], corner_radius=12)
        balans_kaart.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(balans_kaart, text=f"Huidige Matrix Balans: € {totaal_balans:.2f}", font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=20)

        for i, fin in enumerate(self.data["financien"]):
            box = ctk.CTkFrame(self.fin_scroll, fg_color=thema["bg_root"], corner_radius=10)
            box.pack(fill="x", padx=15, pady=5)

            kleur = "#10B981" if float(fin["bedrag"]) >= 0 else "#EF4444"
            ctk.CTkLabel(box, text=fin["desc"], font=("Segoe UI", 13), text_color=thema["text"]).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(box, text=f"€ {float(fin['bedrag']):.2f}", font=("Segoe UI", 13, "bold"), text_color=kleur).pack(side="left", padx=20)

            btn_del = ctk.CTkButton(box, text="🗑", width=35, fg_color="#EF4444", text_color="white", command=lambda idx=i: self._Fin_Delete(idx))
            btn_del.pack(side="right", padx=10)

    def _Fin_Save(self):
        d = self.entry_fin_desc.get().strip()
        try:
            b = float(self.entry_fin_val.get().replace(",", "."))
            if d:
                self.data["financien"].append({"desc": d, "bedrag": b})
                IO_SafeSave(self.data)
                self._Fin_Render()
                self.entry_fin_desc.delete(0, tk.END)
                self.entry_fin_val.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Validatiefout", "Voer een geldig numeriek bedrag in.")

    def _Fin_Delete(self, idx):
        self.data["financien"].pop(idx)
        IO_SafeSave(self.data)
        self._Fin_Render()

    # ==============================================================================
    # CONFIGURATIE & CONFIG MODULE
    # ==============================================================================
    def Module_Settings(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("settings")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Systeem Configuraties & Kerninstellingen", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        box = ctk.CTkFrame(self.canvas, corner_radius=16, fg_color=thema["bg_card"])
        box.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        ctk.CTkLabel(box, text="Gebruikersprofiel Matrix", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=30, pady=(30, 10))
        
        self.cfg_naam = ctk.CTkEntry(box, width=300, placeholder_text="Gebruikersnaam")
        self.cfg_naam.insert(0, self.data["settings"].get("naam", "Student"))
        self.cfg_naam.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(box, text="Systeem Visuele Theme Matrix Map", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=30, pady=(20, 10))
        
        self.cfg_theme = ctk.CTkComboBox(box, values=list(THEMES.keys()), state="readonly", width=200)
        self.cfg_theme.set(self.theme_name)
        self.cfg_theme.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(box, text="Pomodoro Engine Parameters (Minuten)", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=30, pady=(20, 10))
        
        p_f = ctk.CTkFrame(box, fg_color="transparent")
        p_f.pack(anchor="w", padx=30, pady=5)
        
        self.cfg_p_werk = ctk.CTkEntry(p_f, width=80, placeholder_text="Werk")
        self.cfg_p_werk.insert(0, str(self.data["settings"].get("pomodoro_werk", 25)))
        self.cfg_p_werk.pack(side="left")
        
        self.cfg_p_rust = ctk.CTkEntry(p_f, width=80, placeholder_text="Rust")
        self.cfg_p_rust.insert(0, str(self.data["settings"].get("pomodoro_rust", 5)))
        self.cfg_p_rust.pack(side="left", padx=10)

        ctk.CTkButton(box, text="⚡ Wijzigingen Doorvoeren & Hete Herstart", fg_color=thema["accent"], text_color="white", command=self._Settings_Save).pack(anchor="w", padx=30, pady=40)

    def _Settings_Save(self):
        self.data["settings"]["naam"] = self.cfg_naam.get().strip() or "Student"
        self.data["settings"]["theme"] = self.cfg_theme.get()
        try:
            self.data["settings"]["pomodoro_werk"] = int(self.cfg_p_werk.get())
            self.data["settings"]["pomodoro_rust"] = int(self.cfg_p_rust.get())
        except ValueError: pass

        IO_SafeSave(self.data)
        self.System_Hard_Restart()

    def System_Hard_Restart(self):
        print("[GC-OS KERNEL]: Hot-reloading active instance...")
        try: self.destroy()
        except Exception: pass
        os.execv(sys.executable, ['python'] + sys.argv)

# ==============================================================================
# ENTRYPOINT EXECUTION HOOK
# ==============================================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
