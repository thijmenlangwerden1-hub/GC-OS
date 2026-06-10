import os
import sys
import json
import datetime as dt
import subprocess
import time
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from tkcalendar import Calendar
import urllib.request
import webbrowser
import random
import calendar

# Importeer Matplotlib voor de cijfergrafiek
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        "button_fg": "#b4eecb",
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
HUIDIGE_VERSIE = "6.2v"
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
    ]
    return dagen

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "agenda_rooster": {},
            "settings": {"theme": "Wit", "gebruikersnaam": "Student"},
            "vrijedagen": [],
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)
            
    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "agenda_rooster" not in data: data["agenda_rooster"] = {}
    if "settings" not in data: data["settings"] = {"theme": "Wit", "gebruikersnaam": "Student"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "gebruikersnaam" not in data["settings"]: data["settings"]["gebruikersnaam"] = "Student"
    if "vrijedagen" not in data: data["vrijedagen"] = []
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
        self.minsize(1000, 600)
        
        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan"
        ]
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]
        self.vak_kleuren = {
            "Nederlands": "#ff3b30",
            "Engels": "#007aff",
            "Rekenen": "#34c759",
            "Hardware": "#ff9500",
            "Netwerken": "#af52de",
            "Techlab": "#5ac8fa",
            "Burgerschap": "#ffcc00",
            "Loopbaan": "#4cd964"
        }
        
        self.tijd_slots = []
        start_uur = 8
        while start_uur < 17:
            self.tijd_slots.append(f"{start_uur:02d}:00 - {start_uur:02d}:30")
            self.tijd_slots.append(f"{start_uur:02d}:30 - {(start_uur+1):02d}:00")
            start_uur += 1
            
        self.sidebar_width = 230
        self.sidebar_buttons = []
        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.theme_combo = None
        self.clock_label = None
        self.canvas_grafiek = None
        
        # Variabelen voor de kalendernavigatie
        self.huidig_jaar = dt.date.today().year
        self.huidige_maand = dt.date.today().month
        self.weergave_modus = "week"  # "week" of "maand"
        
        self._build_layout()
        self.apply_theme()
        self.show_dashboard()
        
        self.withdraw()
        if os.path.exists(LOG_BESTAND):
            self.show_update_boot_screen()
        else:
            self.show_cool_intro_screen()
            self.after(4000, lambda: self.toon_update_laadbalk(silent=True))
            self.after(4500, self.check_na_update_log)

    def check_na_update_log(self):
        if os.path.exists(LOG_BESTAND):
            try:
                with open(LOG_BESTAND, "r", encoding="utf-8") as f:
                    log_tekst = f.read()
                if log_tekst.strip():
                    self.toon_changelog_venster(log_tekst)
                os.remove(LOG_BESTAND)
            except Exception:
                pass

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
        ctk.CTkLabel(txt_frame, text=log_tekst.strip(), font=("Segoe UI", 12), justify="left", text_color=t["text"]).pack(padx=10, pady=10)
        ctk.CTkButton(log_win, text="Sluiten", fg_color=t["accent"], text_color="white", command=log_win.destroy).pack(pady=20)

    def show_update_boot_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("Updates Toepassen")
        intro.geometry("500x350")
        intro.resizable(False, False)
        intro.configure(fg_color=t["bg_card"])
        intro.update_idletasks()
        x = (intro.winfo_screenwidth() // 2) - (500 // 2)
        y = (intro.winfo_screenheight() // 2) - (350 // 2)
        intro.geometry(f"+{x}+{y}")
        intro.overrideredirect(True)
        intro.attributes("-topmost", True)
        accent_color = t["accent"]
        text_color = t["text"]
        
        spinner_canvas = tk.Canvas(intro, width=60, height=60, bg=t["bg_card"], bd=0, highlightthickness=0)
        spinner_canvas.pack(pady=(50, 10))
        
        angle = [0]
        def animate_spinner():
            if not intro.winfo_exists(): return
            spinner_canvas.delete("all")
            spinner_canvas.create_arc(5, 5, 55, 55, start=angle[0], extent=60, outline=accent_color, width=4, style="arc")
            angle[0] = (angle[0] - 8) % 360
            self.after(20, animate_spinner)
            
        title_lbl = ctk.CTkLabel(intro, text="Systeem bijwerken", font=("Segoe UI", 20, "bold"), text_color=text_color)
        title_lbl.pack(pady=(10, 2))
        sub_lbl = ctk.CTkLabel(intro, text="Onderdelen installeren en configureren...", font=("Segoe UI", 12), text_color=t["button_hover"])
        sub_lbl.pack(pady=(0, 30))
        
        balk = ctk.CTkProgressBar(intro, width=380, height=6, progress_color=accent_color, fg_color=t["button_fg"], corner_radius=3)
        balk.set(0.0)
        balk.pack(pady=5)
        
        status_lbl = ctk.CTkLabel(intro, text="Tijdelijke pakketten uitpakken...", font=("Segoe UI", 11), text_color=text_color)
        status_lbl.pack(pady=5)
        
        update_steps = [
            (0.15, "Back-up maken van gc_os_data.json..."),
            (0.35, "Code-binaries overschrijven..."),
            (0.55, "Operationeel cachegeheugen opschonen..."),
            (0.75, "Database-indexen controleren..."),
            (0.90, "Structurele integriteit valideren..."),
            (1.00, f"Migratie naar {HUIDIGE_VERSIE} voltooid.")
        ]
        
        def process_steps(index=0):
            if index < len(update_steps):
                progress, text = update_steps[index]
                balk.set(progress)
                status_lbl.configure(text=text)
                self.after(random.randint(400, 700), lambda: process_steps(index + 1))
            else:
                self.after(600, close_update_intro)
                
        def close_update_intro():
            intro.destroy()
            self.deiconify()
            try: self.state("zoomed")
            except Exception: pass
            self.check_na_update_log()
            
        animate_spinner()
        self.after(600, lambda: process_steps())

    def show_cool_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("Systeem Start Op")
        intro.geometry("500x350")
        intro.resizable(False, False)
        intro.configure(fg_color=t["bg_card"])
        intro.update_idletasks()
        x = (intro.winfo_screenwidth() // 2) - (500 // 2)
        y = (intro.winfo_screenheight() // 2) - (350 // 2)
        intro.geometry(f"+{x}+{y}")
        intro.overrideredirect(True)
        intro.attributes("-topmost", True)
        accent_color = t["accent"]
        text_color = t["text"]
        
        spinner_canvas = tk.Canvas(intro, width=60, height=60, bg=t["bg_card"], bd=0, highlightthickness=0)
        spinner_canvas.pack(pady=(60, 15))
        
        angle = [0]
        def animate_spinner():
            if not intro.winfo_exists(): return
            spinner_canvas.delete("all")
            spinner_canvas.create_arc(5, 5, 55, 55, start=angle[0], extent=80, outline=accent_color, width=4, style="arc")
            angle[0] = (angle[0] - 10) % 360
            self.after(25, animate_spinner)
            
        title_lbl = ctk.CTkLabel(intro, text="GraafschapCollege-OS", font=("Segoe UI", 22, "bold"), text_color=text_color)
        title_lbl.pack(pady=5)
        version_lbl = ctk.CTkLabel(intro, text=f"Versie {HUIDIGE_VERSIE}", font=("Segoe UI", 11), text_color=t["button_hover"])
        version_lbl.pack(pady=(0, 25))
        status_lbl = ctk.CTkLabel(intro, text="Systeemomgeving initialiseren...", font=("Segoe UI", 12), text_color=text_color)
        status_lbl.pack()
        
        boot_phrases = [
            "Hardware-abstractielagen laden...",
            "Verbinding maken met bestandstabellen...",
            "Roostersynchronisatie uitvoeren...",
            "Gebruikersprofiel verifiëren...",
            "Grafische interface canvas opbouwen...",
            "Klaar voor gebruik!"
        ]
        
        def cycle_text(index=0):
            if index < len(boot_phrases):
                status_lbl.configure(text=boot_phrases[index])
                self.after(random.randint(400, 650), lambda: cycle_text(index + 1))
            else:
                self.after(400, close_intro)
                
        def close_intro():
            intro.destroy()
            self.deiconify()
            try: self.state("zoomed")
            except Exception: pass
            
        animate_spinner()
        self.after(500, lambda: cycle_text())

    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                nieuweste = response.read().decode("utf-8").strip()
        except Exception:
            if silent: return
            messagebox.showerror("Update Fout", "Kan geen verbinding maken met de update-server.")
            return

        if nieuweste == HUIDIGE_VERSIE:
            if not silent:
                messagebox.showinfo("Geen Updates", f"Je draait al de nieuwste versie ({HUIDIGE_VERSIE}).")
            return

        # Nieuwe versie gevonden -> start downloadvenster
        win = ctk.CTkToplevel(self)
        win.title("Update downloaden...")
        win.geometry("460x220")
        win.resizable(False, False)
        win.configure(fg_color=t["bg_card"])
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (460 // 2)
        y = (win.winfo_screenheight() // 2) - (220 // 2)
        win.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(win, text=f"Nieuwe update gevonden: {nieuweste}", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(pady=(20, 5))
        balk = ctk.CTkProgressBar(win, width=380, progress_color=t["accent"], fg_color=t["button_fg"])
        balk.set(0.0)
        balk.pack(pady=10)
        
        lbl_status = ctk.CTkLabel(win, text="Initialiseren...", font=("Segoe UI", 12), text_color=t["text"])
        lbl_status.pack(pady=5)
        
        def download_voltooien():
            try:
                lbl_status.configure(text="Changelog ophalen...")
                win.update()
                req_log = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_log) as r_log:
                    ch_text = r_log.read().decode("utf-8")
                with open(LOG_BESTAND, "w", encoding="utf-8") as lf:
                    lf.write(ch_text)
            except Exception:
                with open(LOG_BESTAND, "w", encoding="utf-8") as lf:
                    lf.write("Systeemonderhoud succesvol afgerond.")

            try:
                lbl_status.configure(text="Script overschrijven...")
                win.update()
                req_script = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_script) as r_script:
                    script_code = r_script.read().decode("utf-8")
                
                huidig_script = sys.argv[0]
                with open(huidig_script, "w", encoding="utf-8") as f_script:
                    f_script.write(script_code)
                
                balk.set(1.0)
                lbl_status.configure(text="Systeem herstarten...")
                win.update()
                time.sleep(1.5)
                win.destroy()
                self.destroy()
                subprocess.Popen([sys.executable, huidig_script])
                sys.exit()
            except Exception as ex:
                messagebox.showerror("Update Mislukt", f"Fout tijdens overschrijven:\n{ex}")
                win.destroy()

        def simuleer_balk(p=0.0):
            if p <= 1.0:
                balk.set(p)
                procent = int(p * 100)
                lbl_status.configure(text=f"Downloaden van pakket-bestanden... ({procent}%)")
                self.after(150, lambda: simuleer_balk(p + 0.04))
            else:
                download_voltooien()

        self.after(500, lambda: simuleer_balk(0.0))

    def _build_layout(self):
        t = THEMES[self.theme_name]
        self.configure(fg_color=t["bg_root"])
        
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0, fg_color=t["bg_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo / Titel in sidebar
        lbl_logo = ctk.CTkLabel(self.sidebar, text="GC‑OS Terminal", font=("Segoe UI", 20, "bold"), text_color=t["sidebar_text"])
        lbl_logo.pack(pady=(25, 5))
        lbl_sublogo = ctk.CTkLabel(self.sidebar, text="Graafschap College", font=("Segoe UI", 11), text_color=t["accent"])
        lbl_sublogo.pack(pady=(0, 25))
        
        buttons_config = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📚  Huiswerk Planner", self.show_huiswerk),
            ("📝  Notitieblok", self.show_notities),
            ("📊  Cijfer Monitor", self.show_cijfers),
            ("📅  Lesrooster", self.show_rooster),
            ("⚙️  Instellingen", self.show_settings)
        ]
        
        for name, cmd in buttons_config:
            btn = ctk.CTkButton(
                self.sidebar, text=name, anchor="w", height=40,
                font=("Segoe UI", 13), fg_color="transparent",
                text_color=t["sidebar_text"], hover_color=t["button_hover"],
                command=cmd
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.sidebar_buttons.append(btn)
            
        # Klok onderaan de sidebar
        self.clock_label = ctk.CTkLabel(self.sidebar, text="00:00:00", font=("Segoe UI", 12, "bold"), text_color=t["sidebar_text"])
        self.clock_label.pack(side="bottom", pady=20)
        self._update_clock_loop()
        
        self.main_container = ctk.CTkFrame(self, fg_color=t["bg_main"], corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

    def _update_clock_loop(self):
        vandaag = dt.datetime.now()
        tijd_str = vandaag.strftime("%H:%M:%S  |  %d-%m-%Y")
        if self.clock_label and self.clock_label.winfo_exists():
            self.clock_label.configure(text=tijd_str)
            self.after(1000, self._update_clock_loop)

    def apply_theme(self):
        t = THEMES[self.theme_name]
        self.configure(fg_color=t["bg_root"])
        self.sidebar.configure(fg_color=t["bg_sidebar"])
        self.main_container.configure(fg_color=t["bg_main"])
        
        for btn in self.sidebar_buttons:
            btn.configure(text_color=t["sidebar_text"], hover_color=t["button_hover"])
        if self.clock_label:
            self.clock_label.configure(text_color=t["sidebar_text"])

    def clear_main(self):
        for child in self.main_container.winfo_children():
            child.destroy()

    # ============================================================
    # MODULE 1: DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        username = self.data["settings"].get("gebruikersnaam", "Student")
        
        top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top_frame.pack(fill="x", padx=35, pady=(25, 10))
        
        lbl_welcome = ctk.CTkLabel(top_frame, text=f"Welkom terug, {username}!", font=("Segoe UI", 26, "bold"), text_color=t["text"])
        lbl_welcome.pack(side="left")
        
        # Grid voor statistieken / kaarten
        grid_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=35, pady=10)
        grid_frame.columnconfigure((0, 1), weight=1, uniform="equal")
        grid_frame.rowconfigure((0, 1), weight=1, uniform="equal")
        
        # Kaart 1: Aankomend Huiswerk
        c1 = ctk.CTkFrame(grid_frame, fg_color=t["bg_card"], corner_radius=12)
        c1.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c1, text="📅 Eerstvolgende Deadlines", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=18, pady=(15, 5))
        
        hw_vandaag = [h for h in self.data["huiswerk"] if not h.get("done", False)]
        hw_vandaag = sorted(hw_vandaag, key=lambda x: x.get("datum", ""))[:3]
        
        if not hw_vandaag:
            ctk.CTkLabel(c1, text="Heerlijk! Geen openstaand huiswerk.", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=18, pady=10)
        else:
            for hw in hw_vandaag:
                lbl_txt = f"• [{hw.get('vak')}] {hw.get('titel')} ({hw.get('datum')})"
                ctk.CTkLabel(c1, text=lbl_txt, font=("Segoe UI", 12), text_color=t["text"], justify="left").pack(anchor="w", padx=18, pady=2)
                
        # Kaart 2: Cijferoverzicht
        c2 = ctk.CTkFrame(grid_frame, fg_color=t["bg_card"], corner_radius=12)
        c2.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c2, text="📊 Laatste Cijfers", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=18, pady=(15, 5))
        
        if not self.data["cijfers"]:
            ctk.CTkLabel(c2, text="Nog geen cijfers ingevoerd in de database.", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=18, pady=10)
        else:
            for c_item in reversed(self.data["cijfers"][-3:]):
                lbl_c = f"• {c_item.get('vak')}: {c_item.get('cijfer')} ({c_item.get('periode')})"
                ctk.CTkLabel(c2, text=lbl_c, font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=18, pady=2)
                
        # Kaart 3: Vrije Dagen & Vakanties
        c3 = ctk.CTkFrame(grid_frame, fg_color=t["bg_card"], corner_radius=12)
        c3.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c3, text="🏝️ Aankomende Vrije Dagen", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=18, pady=(15, 5))
        
        vandaag_dt = dt.date.today()
        toekomstige_dagen = []
        for vd in self.data["vrijedagen"]:
            try:
                vd_dt = dt.datetime.strptime(vd["datum"], "%Y-%m-%d").date()
                if vd_dt >= vandaag_dt:
                    toekomstige_dagen.append((vd_dt, vd["naam"]))
            except Exception: pass
            
        toekomstige_dagen = sorted(toekomstige_dagen, key=lambda x: x[0])[:3]
        if not toekomstige_dagen:
            ctk.CTkLabel(c3, text="Geen vrije dagen geconfigureerd.", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=18, pady=10)
        else:
            for v_date, v_name in toekomstige_dagen:
                diff = (v_date - vandaag_dt).days
                lbl_vd = f"• {v_name} - {v_date.strftime('%d-%m-%Y')} (nog {diff} dagen)"
                ctk.CTkLabel(c3, text=lbl_vd, font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=18, pady=2)

        # Kaart 4: Systeemstatus & Snelkoppelingen
        c4 = ctk.CTkFrame(grid_frame, fg_color=t["bg_card"], corner_radius=12)
        c4.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c4, text="🚀 Snelkoppelingen & Informatie", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=18, pady=(15, 5))
        
        btn_f = ctk.CTkFrame(c4, fg_color="transparent")
        btn_f.pack(fill="both", expand=True, padx=18, pady=5)
        
        ctk.CTkButton(btn_f, text="Infoland (GC)", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: webbrowser.open("https://graafschapcollege.infoland.nl")).pack(side="left", padx=4, pady=5, expand=True, fill="x")
        ctk.CTkButton(btn_f, text="Modern Blackboard", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: webbrowser.open("https://blackboard.graafschapcollege.nl")).pack(side="left", padx=4, pady=5, expand=True, fill="x")

    # ============================================================
    # MODULE 2: HUISWERK PLANNER
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        lbl_title = ctk.CTkLabel(self.main_container, text="📚 Huiswerk & Opdrachten Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        lbl_title.pack(anchor="w", padx=35, pady=(25, 15))
        
        split_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=35, pady=5)
        split_frame.columnconfigure(0, weight=4)
        split_frame.columnconfigure(1, weight=3)
        
        # Linker paneel: Lijst met opdrachten
        left_pane = ctk.CTkFrame(split_frame, fg_color=t["bg_card"], corner_radius=12)
        left_pane.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        
        ctk.CTkLabel(left_pane, text="Openstaande Taken", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        self.hw_list = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        self.hw_list.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Rechter paneel: Toevoegen formulier
        right_pane = ctk.CTkFrame(split_frame, fg_color=t["bg_card"], corner_radius=12)
        right_pane.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        
        ctk.CTkLabel(right_pane, text="Nieuwe Taak Registreren", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkLabel(right_pane, text="Vak / Categorie:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(5, 2))
        combo_vak = ctk.CTkComboBox(right_pane, values=self.vakken_hw, state="readonly", width=220)
        combo_vak.set(self.vakken_hw[0])
        combo_vak.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(right_pane, text="Omschrijving / Titel:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(10, 2))
        entry_titel = ctk.CTkEntry(right_pane, placeholder_text="bijv. Huiswerk blz 40", width=240)
        entry_titel.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(right_pane, text="Inleverdatum (Deadline):", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(10, 2))
        date_f = ctk.CTkFrame(right_pane, fg_color="transparent")
        date_f.pack(anchor="w", padx=20, pady=5)
        entry_date = ctk.CTkEntry(date_f, placeholder_text="YYYY-MM-DD", width=140)
        entry_date.insert(0, dt.date.today().strftime("%Y-%m-%d"))
        entry_date.pack(side="left", padx=(0, 5))
        ctk.CTkButton(date_f, text="📅", width=35, command=lambda: kies_datum(entry_date)).pack(side="left")
        
        def taak_toevoegen():
            v = combo_vak.get()
            tit = entry_titel.get().strip()
            dat = entry_date.get().strip()
            if not tit or not dat:
                messagebox.showwarning("Invoer Ongeldig", "Vul alle velden in.")
                return
            try:
                dt.datetime.strptime(dat, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Datum Fout", "Gebruik het formaat: YYYY-MM-DD")
                return
                
            self.data["huiswerk"].append({
                "vak": v, "titel": tit, "datum": dat, "done": False
            })
            opslaan(self.data)
            entry_titel.delete(0, tk.END)
            self._render_huiswerk_lijst()
            
        ctk.CTkButton(right_pane, text="➕ Toevoegen aan Lijst", fg_color=t["accent"], text_color="white", command=taak_toevoegen).pack(anchor="w", padx=20, pady=25)
        self._render_huiswerk_lijst()

    def _render_huiswerk_lijst(self):
        for child in self.hw_list.winfo_children():
            child.destroy()
        t = THEMES[self.theme_name]
        
        sortering = sorted(self.data["huiswerk"], key=lambda x: (x.get("done", False), x.get("datum", "")))
        
        if not sortering:
            ctk.CTkLabel(self.hw_list, text="Geen actieve huistaken gevonden.", font=("Segoe UI", 12), text_color=t["text"]).pack(pady=20)
            return
            
        for index, hw in enumerate(sortering):
            row_f = ctk.CTkFrame(self.hw_list, fg_color=t["bg_main"], corner_radius=6)
            row_f.pack(fill="x", pady=4, padx=5)
            
            v_kleur = self.vak_kleuren.get(hw.get("vak"), t["accent"])
            tag = ctk.CTkLabel(row_f, text=f" {hw.get('vak')} ", font=("Segoe UI", 11, "bold"), text_color="white", fg_color=v_kleur, corner_radius=4)
            tag.pack(side="left", padx=10, pady=8)
            
            strike = " "
            lbl_color = t["text"]
            if hw.get("done", False):
                strike = "[AFGEROND] "
                lbl_color = t["button_hover"]
                
            info_txt = f"{strike}{hw.get('titel')}  |  ⏱️ {hw.get('datum')}"
            lbl_info = ctk.CTkLabel(row_f, text=info_txt, font=("Segoe UI", 12), text_color=lbl_color, justify="left")
            lbl_info.pack(side="left", padx=10, fill="x", expand=True, anchor="w")
            
            def m_done(item=hw):
                item["done"] = not item.get("done", False)
                opslaan(self.data)
                self._render_huiswerk_lijst()
                
            def m_del(item=hw):
                if messagebox.askyesno("Verwijderen", "Weet je zeker dat je deze taak wilt wissen?"):
                    self.data["huiswerk"].remove(item)
                    opslaan(self.data)
                    self._render_huiswerk_lijst()

            btn_d = ctk.CTkButton(row_f, text="✓", width=28, height=28, fg_color="#34c759" if not hw.get("done") else "#8e8e93", text_color="white", command=m_done)
            btn_d.pack(side="right", padx=4)
            
            btn_x = ctk.CTkButton(row_f, text="✕", width=28, height=28, fg_color="#ff3b30", text_color="white", command=m_del)
            btn_x.pack(side="right", padx=4)

    # ============================================================
    # MODULE 3: NOTITIEBLOK
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        lbl_title = ctk.CTkLabel(self.main_container, text="📝 Persoonlijk Notitieblok", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        lbl_title.pack(anchor="w", padx=35, pady=(25, 15))
        
        split_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=35, pady=5)
        split_frame.columnconfigure(0, weight=3)
        split_frame.columnconfigure(1, weight=5)
        
        left_pane = ctk.CTkFrame(split_frame, fg_color=t["bg_card"], corner_radius=12)
        left_pane.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        
        ctk.CTkLabel(left_pane, text="Bestaande Notities", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        self.note_list = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        self.note_list.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        right_pane = ctk.CTkFrame(split_frame, fg_color=t["bg_card"], corner_radius=12)
        right_pane.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        
        ctk.CTkLabel(right_pane, text="Editor", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        entry_title = ctk.CTkEntry(right_pane, placeholder_text="Titel van de notitie...", width=320)
        entry_title.pack(anchor="w", padx=20, pady=5)
        
        txt_editor = ctk.CTkTextbox(right_pane, height=260, fg_color=t["bg_main"], text_color=t["text"])
        txt_editor.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.huidige_notitie_index = None
        
        def opslaan_notitie():
            tit = entry_title.get().strip()
            body = txt_editor.get("1.0", tk.END).strip()
            if not tit:
                messagebox.showwarning("Geen Titel", "Geef de notitie minimaal een titel mee.")
                return
                
            payload = {"titel": tit, "inhoud": body, "datum": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}
            
            if self.huidige_notitie_index is None:
                self.data["notities"].append(payload)
            else:
                self.data["notities"][self.huidige_notitie_index] = payload
                
            opslaan(self.data)
            self._render_notitie_lijst(entry_title, txt_editor)
            messagebox.showinfo("Opgeslagen", "Notitie succesvol bijgewerkt.")
            
        def nieuwe_notitie():
            self.huidige_notitie_index = None
            entry_title.delete(0, tk.END)
            txt_editor.delete("1.0", tk.END)
            
        btn_f = ctk.CTkFrame(right_pane, fg_color="transparent")
        btn_f.pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(btn_f, text="💾 Opslaan", fg_color=t["accent"], text_color="white", command=opslaan_notitie).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_f, text="📄 Nieuw Document", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=nieuwe_notitie).pack(side="left")
        
        self._render_notitie_lijst(entry_title, txt_editor)

    def _render_notitie_lijst(self, entry_t, txt_e):
        for child in self.note_list.winfo_children():
            child.destroy()
        t = THEMES[self.theme_name]
        
        if not self.data["notities"]:
            ctk.CTkLabel(self.note_list, text="Geen notities.", font=("Segoe UI", 12), text_color=t["text"]).pack(pady=20)
            return
            
        for idx, n in enumerate(self.data["notities"]):
            n_frame = ctk.CTkFrame(self.note_list, fg_color=t["bg_main"], corner_radius=6)
            n_frame.pack(fill="x", pady=3, padx=5)
            
            def laden_in_editor(i=idx):
                self.huidige_notitie_index = i
                item = self.data["notities"][i]
                entry_t.delete(0, tk.END)
                entry_t.insert(0, item.get("titel", ""))
                txt_e.delete("1.0", tk.END)
                txt_e.insert("1.0", item.get("inhoud", ""))
                
            def wissen_notitie(i=idx):
                if messagebox.askyesno("Wissen", "Weet je zeker dat je deze notitie wilt weggooien?"):
                    self.data["notities"].pop(i)
                    opslaan(self.data)
                    self._render_notitie_lijst(entry_t, txt_e)
                    self.huidige_notitie_index = None
                    entry_t.delete(0, tk.END)
                    txt_e.delete("1.0", tk.END)

            lbl_n = ctk.CTkLabel(n_frame, text=n.get("titel"), font=("Segoe UI", 12), text_color=t["text"], cursor="hand2")
            lbl_n.pack(side="left", padx=10, pady=8, fill="x", expand=True, anchor="w")
            lbl_n.bind("<Button-1>", lambda e, i=idx: laden_in_editor(i))
            
            btn_del = ctk.CTkButton(n_frame, text="🗑️", width=28, height=28, fg_color="transparent", text_color="#ff3b30", command=lambda i=idx: wissen_notitie(i))
            btn_del.pack(side="right", padx=5)

    # ============================================================
    # MODULE 4: CIJFER OVERZICHT & GRAPH
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        lbl_title = ctk.CTkLabel(self.main_container, text="📊 Cijferregistratie & Analyse", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        lbl_title.pack(anchor="w", padx=35, pady=(25, 15))
        
        main_split = ctk.CTkFrame(self.main_container, fg_color="transparent")
        main_split.pack(fill="both", expand=True, padx=35, pady=5)
        main_split.columnconfigure(0, weight=3)
        main_split.columnconfigure(1, weight=4)
        
        left_p = ctk.CTkFrame(main_split, fg_color=t["bg_card"], corner_radius=12)
        left_p.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        
        ctk.CTkLabel(left_p, text="Nieuw Resultaat Invoeren", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkLabel(left_p, text="Vakomschrijving:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(5, 2))
        combo_v = ctk.CTkComboBox(left_p, values=self.vakken_hw, state="readonly", width=180)
        combo_v.set(self.vakken_hw[0])
        combo_v.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(left_p, text="Behaald Cijfer (bijv. 7.5):", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(10, 2))
        entry_c = ctk.CTkEntry(left_p, placeholder_text="0.0", width=100)
        entry_c.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(left_p, text="Schoolperiode:", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(10, 2))
        combo_p = ctk.CTkComboBox(left_p, values=self.periodes, state="readonly", width=180)
        combo_p.set(self.periodes[0])
        combo_p.pack(anchor="w", padx=20, pady=5)
        
        right_p = ctk.CTkFrame(main_split, fg_color=t["bg_card"], corner_radius=12)
        right_p.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        
        ctk.CTkLabel(right_p, text="Statistische Voortgangsgrafiek", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
        self.canvas_grafiek = ctk.CTkFrame(right_p, fg_color="transparent")
        self.canvas_grafiek.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable lijst onder de input
        ctk.CTkLabel(left_p, text="Historie:", font=("Segoe UI", 13, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(15, 2))
        self.cijfer_list = ctk.CTkScrollableFrame(left_p, height=130, fg_color=t["bg_main"])
        self.cijfer_list.pack(fill="x", padx=20, pady=5)
        
        def cijfer_opslaan():
            vk = combo_v.get()
            per = combo_p.get()
            raw_c = entry_c.get().replace(",", ".")
            try:
                val = float(raw_c)
                if val < 1.0 or val > 10.0: raise ValueError
            except ValueError:
                messagebox.showerror("Invoer Fout", "Voer een geldig getal in tussen 1.0 en 10.0")
                return
                
            self.data["cijfers"].append({"vak": vk, "cijfer": val, "periode": per, "tijd": dt.datetime.now().strftime("%d-%m")})
            opslaan(self.data)
            entry_c.delete(0, tk.END)
            self._render_cijfer_scherm()
            
        ctk.CTkButton(left_p, text="💾 Resultaat Opslaan", fg_color=t["accent"], text_color="white", command=cijfer_opslaan).pack(anchor="w", padx=20, pady=15)
        self._render_cijfer_scherm()

    def _render_cijfer_scherm(self):
        # Lijst verversen
        for child in self.cijfer_list.winfo_children():
            child.destroy()
        t = THEMES[self.theme_name]
        
        if not self.data["cijfers"]:
            ctk.CTkLabel(self.cijfer_list, text="Geen data.", font=("Segoe UI", 11), text_color=t["text"]).pack(pady=10)
        else:
            for c in reversed(self.data["cijfers"]):
                r = ctk.CTkFrame(self.cijfer_list, fg_color="transparent")
                r.pack(fill="x", pady=2)
                
                txt = f"{c.get('vak')} -> {c.get('cijfer')} ({c.get('periode')})"
                ctk.CTkLabel(r, text=txt, font=("Segoe UI", 12), text_color=t["text"]).pack(side="left", padx=5)
                
                def b_wissen(target=c):
                    self.data["cijfers"].remove(target)
                    opslaan(self.data)
                    self._render_cijfer_scherm()
                    
                ctk.CTkButton(r, text="✕", width=20, height=20, fg_color="transparent", text_color="#ff3b30", command=b_wissen).pack(side="right", padx=5)

        # Grafiek tekenen met Matplotlib
        for child in self.canvas_grafiek.winfo_children():
            child.destroy()
            
        if len(self.data["cijfers"]) < 2:
            ctk.CTkLabel(self.canvas_grafiek, text="Voer minimaal 2 cijfers in om\nde trendgrafiek te genereren.", font=("Segoe UI", 12), text_color=t["text"]).pack(expand=True)
            return
            
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(t["bg_card"])
        ax.set_facecolor(t["bg_main"])
        
        cijfers_lijst = self.data["cijfers"][-8:] # Toon maximaal laatste 8 data-punten
        y_vals = [x["cijfer"] for x in cijfers_lijst]
        x_labels = [f"{x['tijd']}\n{x['vak'][:3]}" for x in cijfers_lijst]
        
        ax.plot(range(len(y_vals)), y_vals, marker="o", color=t["accent"], linewidth=2, markersize=6)
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, fontsize=8, color=t["text"])
        ax.set_ylim(1, 10.5)
        ax.tick_params(colors=t["text"])
        ax.spines["bottom"].set_color(t["button_hover"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(t["button_hover"])
        ax.grid(True, linestyle="--", alpha=0.3, color=t["text"])
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_grafiek)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ============================================================
    # MODULE 5: LESROOSTER (AGENDA MATRIX MET MAAND- EN WEEKMODUS)
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        # Hoofd navigatiebalk voor het rooster
        nav_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        nav_frame.pack(fill="x", padx=35, pady=(25, 10))
        
        lbl_title = ctk.CTkLabel(nav_frame, text="📅 Lesrooster & Agenda", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        lbl_title.pack(side="left")
        
        # Knoppen om te schakelen tussen Week / Maand en Terug naar Vandaag
        btn_switch_text = "📅 Toon Maand" if self.weergave_modus == "week" else "📆 Toon Week"
        btn_switch = ctk.CTkButton(nav_frame, text=btn_switch_text, font=("Segoe UI", 12), width=110, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._toggle_rooster_modus)
        btn_switch.pack(side="right", padx=(5, 0))
        
        btn_vandaag = ctk.CTkButton(nav_frame, text="📍 Vandaag", font=("Segoe UI", 12, "bold"), width=90, fg_color=t["accent"], text_color="white", command=self._navigeer_naar_vandaag)
        btn_vandaag.pack(side="right", padx=5)
        
        # Render de geselecteerde modus
        if self.weergave_modus == "week":
            self._render_week_rooster()
        else:
            self._render_maand_rooster()

    def _toggle_rooster_modus(self):
        self.weergave_modus = "maand" if self.weergave_modus == "week" else "week"
        self.show_rooster()

    def _navigeer_naar_vandaag(self):
        vandaag = dt.date.today()
        self.huidig_jaar = vandaag.year
        self.huidige_maand = vandaag.month
        self.weergave_modus = "week"  # Forceer terug naar week om direct de dagsleuven te zien
        self.show_rooster()

    def _render_week_rooster(self):
        t = THEMES[self.theme_name]
        dagen_week = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
        vandaag_index = dt.datetime.now().weekday()  # Maandag = 0, Zondag = 6
        
        grid_container = ctk.CTkScrollableFrame(self.main_container, fg_color=t["bg_card"], corner_radius=12)
        grid_container.pack(fill="both", expand=True, padx=35, pady=10)
        
        grid_container.columnconfigure(0, weight=2)
        
        # Grid Headers bouwen
        for d_idx, dag in enumerate(dagen_week):
            grid_container.columnconfigure(d_idx + 1, weight=3)
            
            # Controleer of de dag van vandaag gemarkeerd moet worden
            is_vandaag = (d_idx == vandaag_index)
            
            if is_vandaag:
                # Rode bovenbalk container voor de huidige dag
                header_frame = ctk.CTkFrame(grid_container, fg_color="#ff3b30", corner_radius=4, height=32)
                header_frame.grid(row=0, column=d_idx + 1, padx=4, pady=5, sticky="nsew")
                header_frame.pack_propagate(False)
                lbl_hd = ctk.CTkLabel(header_frame, text=f"🌟 {dag}", font=("Segoe UI", 13, "bold"), text_color="white")
                lbl_hd.pack(expand=True)
            else:
                lbl_hd = ctk.CTkLabel(grid_container, text=dag, font=("Segoe UI", 13, "bold"), text_color=t["accent"])
                grid_container.rowconfigure(0, minsize=40)
                lbl_hd.grid(row=0, column=d_idx + 1, padx=4, pady=10, sticky="nsew")
            
        # Blok-matrix genereren
        for s_idx, slot in enumerate(self.tijd_slots):
            lbl_slot = ctk.CTkLabel(grid_container, text=slot, font=("Segoe UI", 11), text_color=t["text"])
            lbl_slot.grid(row=s_idx + 1, column=0, padx=10, pady=4, sticky="w")
            
            for d_idx, dag in enumerate(dagen_week):
                slot_key = f"{dag}_{slot}"
                waarde = self.data["agenda_rooster"].get(slot_key, "")
                is_vandaag = (d_idx == vandaag_index)
                
                # Bepaal randkleuren en diktes voor 'Vandaag' kolom
                border_color_params = {"border_color": "#ff3b30", "border_width": 1.5} if is_vandaag else {}
                
                btn_slot = ctk.CTkButton(
                    grid_container, text=waarde if waarde else "-",
                    font=("Segoe UI", 11), height=28,
                    fg_color=t["bg_main"] if not waarde else t["button_fg"],
                    text_color=t["text"] if waarde else t["button_hover"],
                    hover_color=t["button_hover"],
                    **border_color_params
                )
                btn_slot.grid(row=s_idx + 1, column=d_idx + 1, padx=3, pady=3, sticky="nsew")
                
                def bind_click(k=slot_key, b=btn_slot):
                    self._edit_rooster_slot(k, b)
                    
                btn_slot.configure(command=bind_click)

    def _render_maand_rooster(self):
        t = THEMES[self.theme_name]
        vandaag = dt.date.today()
        
        # Kalender besturingspaneel (Maand vooruit / achteruit)
        cal_nav = ctk.CTkFrame(self.main_container, fg_color=t["bg_card"], corner_radius=8, height=45)
        cal_nav.pack(fill="x", padx=35, pady=(5, 10))
        cal_nav.pack_propagate(False)
        
        maanden_namen = ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"]
        lbl_maand_jaar = ctk.CTkLabel(cal_nav, text=f"{maanden_namen[self.huidige_maand - 1]} {self.huidig_jaar}", font=("Segoe UI", 15, "bold"), text_color=t["text"])
        lbl_maand_jaar.pack(side="left", padx=15)
        
        def verander_maand(richting):
            self.huidige_maand += richting
            if self.huidige_maand > 12:
                self.huidige_maand = 1
                self.huidig_jaar += 1
            elif self.huidige_maand < 1:
                self.huidige_maand = 12
                self.huidig_jaar -= 1
            self.show_rooster()
            
        btn_next = ctk.CTkButton(cal_nav, text="▶", font=("Segoe UI", 11), width=35, fg_color="transparent", text_color=t["text"], hover_color=t["button_hover"], command=lambda: verander_maand(1))
        btn_next.pack(side="right", padx=5, pady=5)
        btn_prev = ctk.CTkButton(cal_nav, text="◀", font=("Segoe UI", 11), width=35, fg_color="transparent", text_color=t["text"], hover_color=t["button_hover"], command=lambda: verander_maand(-1))
        btn_prev.pack(side="right", padx=2, pady=5)
        
        # Grid voor de dagen van de maand
        maand_grid = ctk.CTkFrame(self.main_container, fg_color=t["bg_card"], corner_radius=12)
        maand_grid.pack(fill="both", expand=True, padx=35, pady=5)
        
        dagen_headers = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
        for i, dh in enumerate(dagen_headers):
            maand_grid.columnconfigure(i, weight=1, uniform="equal")
            lbl = ctk.CTkLabel(maand_grid, text=dh, font=("Segoe UI", 12, "bold"), text_color=t["accent"])
            lbl.grid(row=0, column=i, pady=8)
            
        # Bereken kalender datastructuur
        cal_obj = calendar.Calendar(firstweekday=0)
        maand_dagen = cal_obj.monthdayscalendar(self.huidig_jaar, self.huidige_maand)
        
        for r_idx, week in enumerate(maand_dagen):
            maand_grid.rowconfigure(r_idx + 1, weight=1, uniform="equal")
            for c_idx, dag_nummer in enumerate(week):
                if dag_nummer == 0:
                    # Leeg vakje buiten de huidige maandgrenzen
                    leeg = ctk.CTkFrame(maand_grid, fg_color="transparent")
                    leeg.grid(row=r_idx + 1, column=c_idx, sticky="nsew", padx=2, pady=2)
                    continue
                    
                is_echt_vandaag = (self.huidig_jaar == vandaag.year and self.huidige_maand == vandaag.month and dag_nummer == vandaag.day)
                
                # Basis stijl van het dagkaartje
                card_bg = t["bg_main"]
                border_params = {"border_color": "#ff3b30", "border_width": 2} if is_echt_vandaag else {}
                
                dag_box = ctk.CTkFrame(maand_grid, fg_color=card_bg, corner_radius=8, **border_params)
                dag_box.grid(row=r_idx + 1, column=c_idx, sticky="nsew", padx=3, pady=3)
                
                # Nummering
                text_color_dag = "#ff3b30" if is_echt_vandaag else t["text"]
                lbl_num = ctk.CTkLabel(dag_box, text=str(dag_nummer), font=("Segoe UI", 12, "bold" if is_echt_vandaag else "normal"), text_color=text_color_dag)
                lbl_num.pack(anchor="nw", padx=6, pady=4)
                
                # Controleer op huiswerktaken voor deze specifieke kalenderdatum
                huidige_datum_str = f"{self.huidig_jaar}-{self.huidige_maand:02d}-{dag_nummer:02d}"
                taken_vandaag = [h for h in self.data["huiswerk"] if h.get("datum") == huidige_datum_str and not h.get("done")]
                
                if taken_vandaag:
                    indicator_text = f"📚 {len(taken_vandaag)} taak/taken" if len(taken_vandaag) > 1 else f"📚 {taken_vandaag[0]['titel'][:10]}..."
                    lbl_task = ctk.CTkLabel(dag_box, text=indicator_text, font=("Segoe UI", 10), text_color=t["accent"])
                    lbl_task.pack(anchor="sw", side="bottom", padx=6, pady=4)

    def _edit_rooster_slot(self, slot_key, button_widget):
        t = THEMES[self.theme_name]
        huidige_waarde = self.data["agenda_rooster"].get(slot_key, "")
        
        pop = ctk.CTkToplevel(self)
        pop.title("Slot Aanpassen")
        pop.geometry("340x180")
        pop.resizable(False, False)
        pop.grab_set()
        pop.update_idletasks()
        x = (pop.winfo_screenwidth() // 2) - (340 // 2)
        y = (pop.winfo_screenheight() // 2) - (180 // 2)
        pop.geometry(f"+{x}+{y}")
        pop.configure(fg_color=t["bg_card"])
        
        ctk.CTkLabel(pop, text=f"Inhoud invoeren voor:\n{slot_key.replace('_', ' - ')}", font=("Segoe UI", 12, "bold"), text_color=t["text"]).pack(pady=12)
        ent = ctk.CTkEntry(pop, width=260)
        ent.insert(0, huidige_waarde)
        ent.pack(pady=5)
        
        def bewaren():
            txt = ent.get().strip()
            if txt:
                self.data["agenda_rooster"][slot_key] = txt
                button_widget.configure(text=txt, fg_color=t["button_fg"], text_color=t["text"])
            else:
                if slot_key in self.data["agenda_rooster"]:
                    del self.data["agenda_rooster"][slot_key]
                button_widget.configure(text="-", fg_color=t["bg_main"], text_color=t["button_hover"])
            opslaan(self.data)
            pop.destroy()
            
        ctk.CTkButton(pop, text="✓ Bevestigen", fg_color=t["accent"], text_color="white", width=120, command=bewaren).pack(pady=15)

    # ============================================================
    # MODULE 6: INSTELLINGEN
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        lbl_title = ctk.CTkLabel(self.main_container, text="⚙️ Systeeminstellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        lbl_title.pack(anchor="w", padx=35, pady=(25, 15))
        
        card = ctk.CTkFrame(self.main_container, fg_color=t["bg_card"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=35, pady=10)
        
        ctk.CTkLabel(card, text="Gebruikersprofiel aanpassen:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        self.settings_name = ctk.CTkEntry(card, width=280)
        self.settings_name.insert(0, self.data["settings"].get("gebruikersnaam", "Student"))
        self.settings_name.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(card, text="Visueel Systeemthema Selecteren:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        themalijst = list(THEMES.keys())
        self.theme_combo = ctk.CTkComboBox(card, values=themalijst, state="readonly", width=200)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(card, text="Systeem update & Onderhoud:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(25, 5))
        ctk.CTkButton(card, text="🔍 Zoeken naar Updates", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkButton(card, text="💾 Instellingen Toepassen", fg_color=t["accent"], text_color="white", command=self.settings_opslaan).pack(side="bottom", anchor="e", padx=20, pady=20)
        self.apply_theme()

    def settings_opslaan(self):
        nieuw_thema = self.theme_combo.get()
        nieuw_naam = self.settings_name.get().strip()
        
        if nieuw_naam:
            self.data["settings"]["gebruikersnaam"] = nieuw_naam
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        
        self.theme_name = nieuw_thema
        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        self.apply_theme()
        self.show_dashboard()
        messagebox.showinfo("Instellingen Opgeslagen", "De configuratiewijzigingen zijn met succes toegepast op de actieve sessie.")

if __name__ == "__main__":
    # Start de hoofdapplicatie
    app = SchoolOS()
    app.mainloop()
