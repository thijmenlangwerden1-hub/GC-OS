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
# 1. GLOBALE CONFIGURATIE, LUXE THEMES & SYSTEM ARCHITECTURE
# ==============================================================================

HUIDIGE_VERSIE = "7.5.1v"
CODENAME = "AetherValkyrie-Pro-Luxe"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_matrix_data.json")

THEMES = {
    "Luxe Slate (Light)": {
        "mode": "Light", 
        "bg_root": "#F8FAFC", "bg_sidebar": "#FFFFFF", "bg_main": "#F8FAFC", "bg_card": "#FFFFFF",
        "text": "#0F172A", "sidebar_text": "#334155", "button_text": "#FFFFFF", "button_fg": "#6366F1",
        "button_hover": "#4F46E5", "accent": "#6366F1", "list_bg": "#FFFFFF", "list_fg": "#0F172A", "list_select": "#EEF2F6"
    },
    "Premium Obsidian (Dark)": {
        "mode": "Dark", 
        "bg_root": "#0B0F19", "bg_sidebar": "#111827", "bg_main": "#0B0F19", "bg_card": "#1F2937",
        "text": "#F9FAFB", "sidebar_text": "#9CA3AF", "button_text": "#FFFFFF", "button_fg": "#3B82F6",
        "button_hover": "#2563EB", "accent": "#60A5FA", "list_bg": "#1F2937", "list_fg": "#F9FAFB", "list_select": "#374151"
    },
    "Crimson Velvet": {
        "mode": "Dark", 
        "bg_root": "#110404", "bg_sidebar": "#1A0909", "bg_main": "#110404", "bg_card": "#261010",
        "text": "#FCA5A5", "sidebar_text": "#F87171", "button_text": "#FFFFFF", "button_fg": "#EF4444",
        "button_hover": "#DC2626", "accent": "#F87171", "list_bg": "#1A0909", "list_fg": "#FCA5A5", "list_select": "#451A1A"
    },
    "Cyberpunk Neon": {
        "mode": "Dark", 
        "bg_root": "#03000A", "bg_sidebar": "#0D001A", "bg_main": "#03000A", "bg_card": "#1A0033",
        "text": "#00FFCC", "sidebar_text": "#FF007F", "button_text": "#000000", "button_fg": "#00FFCC",
        "button_hover": "#FF007F", "accent": "#00FFCC", "list_bg": "#0D001A", "list_fg": "#00FFCC", "list_select": "#FF007F"
    },
    "Matrix Core": {
        "mode": "Dark", 
        "bg_root": "#000000", "bg_sidebar": "#050505", "bg_main": "#000000", "bg_card": "#0A0A0A",
        "text": "#33FF33", "sidebar_text": "#00FF00", "button_text": "#000000", "button_fg": "#00FF00",
        "button_hover": "#008800", "accent": "#00FF00", "list_bg": "#050505", "list_fg": "#33FF33", "list_select": "#004400"
    }
}

MOTIVATIONAL_QUOTES = [
    "Succes is de som van kleine inspanningen, dag in dag uit herhaald.",
    "De beste manier om de toekomst te voorspellen is om hem zelf te bouwen.",
    "Blijf compilen, blijf pushen, geef nooit op.",
    "Code is net als kunst. Elegantie ontstaat door het weglaten van de ruis.",
    "Focus op de progressie, niet op de perfectie."
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
        "settings": {"theme": "Premium Obsidian (Dark)", "naam": "Student Pro", "pomodoro_werk": 25, "pomodoro_rust": 5, "automatisch_backups": True}
    }
    
    for sleutel, waarde in SysteemDefaults.items():
        if sleutel not in data:
            data[sleutel] = waarde
            
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Premium Obsidian (Dark)"
    if "naam" not in data["settings"]: data["settings"]["naam"] = "Student Pro"
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
        self.theme_name = self.data["settings"].get("theme", "Premium Obsidian (Dark)")
        if self.theme_name not in THEMES:
            self.theme_name = "Premium Obsidian (Dark)"

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

        self.sidebar_header = ctk.CTkLabel(self.sidebar, text="GC-OS PRESTIGE", font=("Segoe UI", 22, "bold"))
        self.sidebar_header.pack(pady=(35, 5), padx=25, anchor="w")
        
        self.sidebar_sub = ctk.CTkLabel(self.sidebar, text=f"Kernel: {CODENAME}", font=("Segoe UI", 11), text_color="gray")
        self.sidebar_sub.pack(pady=(0, 25), padx=25, anchor="w")

        menu_configuratie = [
            ("dashboard", "🏠  Dashboard Overzicht", self.Module_Dashboard),
            ("huiswerk", "📝  Huiswerk Projecten", self.Module_Huiswerk),
            ("rooster", "📅  Matrix Lesrooster", self.Module_Rooster),
            ("notities", "🗒  Kennisbank & Notities", self.Module_Notities),
            ("cijfers", "📊  Cijfer & KPI Analyse", self.Module_Cijfers)
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
        
        ver_label = ctk.CTkLabel(center_container, text=f"SYSTEM VERSION {HUIDIGE_VERSIE} • LUXE BUILD", font=("Consolas", 11), text_color="gray")
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
            "[INFO] Rendering luxury UI component schemas...",
            "[SUCCESS] GC-OS UI Environment ready. Deploying canvas..."
        ]

        def SimuleerStappen(stap, log_index):
            if stap <= 100:
                progressiebalk.set(stap / 100)
                if stap % 20 == 0 and log_index < len(boot_logs):
                    huidige_log = boot_logs[log_index]
                    log_text.configure(text=f"{log_text.cget('text')}\n{huidige_log}")
                    log_index += 1
                vertraging = random.randint(10, 30)
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
        ctk.CTkLabel(kop_frame, text=f"Prestige Suite — Welkom, {gebruikersnaam}", font=("Segoe UI", 28, "bold"), text_color=thema["text"]).pack(side="left")

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
        ctk.CTkLabel(card4, text="🚨 Openstaande Deadlines", font=("Segoe UI", 16, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=20, pady=15)
        
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
    # MODULE 4: KENNISBANK & NOTITIES (Volledig Uitgeschreven v7.5.1v)
    # ==============================================================================
    def Module_Notities(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("notities")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Kennisbank & Persoonlijke Notities", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)
        
        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=300)
        links.pack(side="left", fill="y", padx=(0, 15))
        links.pack_propagate(False)

        self.notes_listbox = tk.Listbox(links, font=("Segoe UI", 12), activestyle="none", bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.notes_listbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.notes_listbox.bind("<<ListboxSelect>>", self._Notes_Load_Selected)

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        rechts.pack(side="right", fill="both", expand=True)

        self.entry_note_titel = ctk.CTkEntry(rechts, placeholder_text="Titel van de notitie", font=("Segoe UI", 14, "bold"))
        self.entry_note_titel.pack(fill="x", padx=20, pady=(20, 10))

        self.txt_note_inhoud = tk.Text(rechts, font=("Consolas", 12), bg=thema["list_bg"], fg=thema["list_fg"], insertbackground=thema["text"], borderwidth=0, highlightthickness=0)
        self.txt_note_inhoud.pack(fill="both", expand=True, padx=20, pady=10)

        knop_balk = ctk.CTkFrame(rechts, fg_color="transparent")
        knop_balk.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(knop_balk, text="📝 Nieuwe Notitie", command=self._Notes_Clear_Fields).pack(side="left", padx=5)
        ctk.CTkButton(knop_balk, text="💾 Opslaan", fg_color=thema["accent"], text_color="white", command=self._Notes_Save).pack(side="left", padx=5)
        ctk.CTkButton(knop_balk, text="🗑 Verwijderen", fg_color="#EF4444", text_color="white", command=self._Notes_Delete).pack(side="right", padx=5)

        self._Notes_Render_List()

    def _Notes_Render_List(self):
        self.notes_listbox.delete(0, tk.END)
        for n in self.data["notities"]:
            self.notes_listbox.insert(tk.END, n.get("titel", "Naamloos"))

    def _Notes_Load_Selected(self, event):
        try:
            idx = self.notes_listbox.curselection()[0]
            note = self.data["notities"][idx]
            self.entry_note_titel.delete(0, tk.END)
            self.entry_note_titel.insert(0, note.get("titel", ""))
            self.txt_note_inhoud.delete("1.0", tk.END)
            self.txt_note_inhoud.insert("1.0", note.get("inhoud", ""))
        except IndexError: pass

    def _Notes_Clear_Fields(self):
        self.entry_note_titel.delete(0, tk.END)
        self.txt_note_inhoud.delete("1.0", tk.END)

    def _Notes_Save(self):
        titel = self.entry_note_titel.get().strip()
        inhoud = self.txt_note_inhoud.get("1.0", tk.END).strip()
        if not titel: return

        selectie = self.notes_listbox.curselection()
        if selectie:
            idx = selectie[0]
            self.data["notities"][idx] = {"titel": titel, "inhoud": inhoud}
        else:
            self.data["notities"].append({"titel": titel, "inhoud": inhoud})

        IO_SafeSave(self.data)
        self._Notes_Render_List()
        self._Notes_Clear_Fields()

    def _Notes_Delete(self):
        try:
            idx = self.notes_listbox.curselection()[0]
            self.data["notities"].pop(idx)
            IO_SafeSave(self.data)
            self._Notes_Render_List()
            self._Notes_Clear_Fields()
        except IndexError: pass

    # ==============================================================================
    # MODULE 5: CIJFER & KPI ANALYSE (Volledig Uitgeschreven v7.5.1v)
    # ==============================================================================
    def Module_Cijfers(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("cijfers")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Cijferregistratie & Voortgangsindicator", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        paneel = ctk.CTkFrame(self.canvas, fg_color="transparent")
        paneel.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        links = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"])
        links.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.cijfer_listbox = tk.Listbox(links, font=("Segoe UI", 12), activestyle="none", bg=thema["list_bg"], fg=thema["list_fg"], selectbackground=thema["list_select"], borderwidth=0, highlightthickness=0)
        self.cijfer_listbox.pack(fill="both", expand=True, padx=20, pady=20)

        rechts = ctk.CTkFrame(paneel, corner_radius=16, fg_color=thema["bg_card"], width=340)
        rechts.pack(side="right", fill="y")
        rechts.pack_propagate(False)

        ctk.CTkLabel(rechts, text="Resultaat Toevoegen", font=("Segoe UI", 15, "bold"), text_color=thema["accent"]).pack(pady=15)

        self.combo_cijfer_vak = ctk.CTkComboBox(rechts, values=self.vakken_lijst, state="readonly")
        self.combo_cijfer_vak.set(self.vakken_lijst[0])
        self.combo_cijfer_vak.pack(fill="x", padx=20, pady=8)

        self.entry_cijfer_waarde = ctk.CTkEntry(rechts, placeholder_text="Cijfer (bijv. 7.5)")
        self.entry_cijfer_waarde.pack(fill="x", padx=20, pady=8)

        self.entry_cijfer_weging = ctk.CTkEntry(rechts, placeholder_text="Weging (bijv. 2)")
        self.entry_cijfer_weging.insert(0, "1")
        self.entry_cijfer_weging.pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(rechts, text="💾 Resultaat Inboeken", fg_color=thema["accent"], text_color="white", command=self._Cijfer_Save).pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(rechts, text="🗑 Verwijder Selectie", fg_color="#EF4444", text_color="white", command=self._Cijfer_Delete).pack(fill="x", padx=20, pady=5)

        self._Cijfer_Render_Data()

    def _Cijfer_Render_Data(self):
        self.cijfer_listbox.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.cijfer_listbox.insert(tk.END, f"📘 {c.get('vak')}  |  Resultaat: {c.get('cijfer')}  (Weging: {c.get('weging')}x)")

    def _Cijfer_Save(self):
        v = self.combo_cijfer_vak.get()
        c_w = self.entry_cijfer_waarde.get().replace(",", ".").strip()
        w_w = self.entry_cijfer_weging.get().strip()

        try:
            float(c_w)
            int(w_w)
        except ValueError:
            messagebox.showwarning("Invoerfout", "Zorg voor een numeriek cijfer en weging.")
            return

        self.data["cijfers"].append({"vak": v, "cijfer": c_w, "weging": w_w})
        IO_SafeSave(self.data)
        self._Cijfer_Render_Data()
        self.entry_cijfer_waarde.delete(0, tk.END)

    def _Cijfer_Delete(self):
        try:
            idx = self.cijfer_listbox.curselection()[0]
            self.data["cijfers"].pop(idx)
            IO_SafeSave(self.data)
            self._Cijfer_Render_Data()
        except IndexError: pass

    # ==============================================================================
    # SYSTEM SETTINGS CONFIGURATOR MODULE
    # ==============================================================================
    def Module_Settings(self):
        self.Core_Clear_Canvas()
        self.Core_Highlight_Menu("settings")
        thema = THEMES[self.theme_name]

        ctk.CTkLabel(self.canvas, text="Systeem Configuraties & Architectuur", font=("Segoe UI", 24, "bold"), text_color=thema["text"]).pack(anchor="w", padx=35, pady=20)

        box = ctk.CTkFrame(self.canvas, corner_radius=16, fg_color=thema["bg_card"])
        box.pack(fill="both", expand=True, padx=35, pady=(0, 35))

        ctk.CTkLabel(box, text="Gebruikersprofiel Naam", font=("Segoe UI", 14, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=30, pady=(30, 5))
        self.entry_set_naam = ctk.CTkEntry(box, width=300)
        self.entry_set_naam.insert(0, self.data["settings"].get("naam", "Student"))
        self.entry_set_naam.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(box, text="Systeem Visualisatie Theme Designer", font=("Segoe UI", 14, "bold"), text_color=thema["accent"]).pack(anchor="w", padx=30, pady=(20, 5))
        self.combo_set_theme = ctk.CTkComboBox(box, values=list(THEMES.keys()), width=300, state="readonly")
        self.combo_set_theme.set(self.theme_name)
        self.combo_set_theme.pack(anchor="w", padx=30, pady=5)

        def SlaInstellingenOp():
            self.data["settings"]["naam"] = self.entry_set_naam.get().strip() or "Student"
            gekozen_thema = self.combo_set_theme.get()
            self.data["settings"]["theme"] = gekozen_thema
            self.theme_name = gekozen_thema
            IO_SafeSave(self.data)
            self.Core_Apply_Theme()
            self.Module_Settings()
            messagebox.showinfo("Systeemwijziging", "Luxe interface-instellingen succesvol doorgevoerd.")

        ctk.CTkButton(box, text="⚙️ Wijzigingen Toepassen", fg_color=thema["button_fg"], text_color=thema["button_text"], command=SlaInstellingenOp).pack(anchor="w", padx=30, pady=40)

# ==============================================================================
# 4. RUNTIME INITIALIZATION ENTRYPOINT
# ==============================================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
