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
HUIDIGE_VERSIE = "6.1v"
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
            "Nederlands": "#ff3b30",   # Rood
            "Engels": "#007aff",       # Blauw
            "Rekenen": "#34c759",      # Groen
            "Hardware": "#ff9500",     # Oranje
            "Netwerken": "#af52de",    # Paars
            "Techlab": "#5ac8fa",      # Lichtblauw
            "Burgerschap": "#ffcc00",  # Geel
            "Loopbaan": "#4cd964"      # Lichtgroen
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
            if not intro.winfo_exists():
                return
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
            if not intro.winfo_exists():
                return
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

    # --------------------------------------------------------
    # UPDATE MANAGER (AANGEPAST: Laadtijd nu ongeveer 7 seconden)
    # --------------------------------------------------------
    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]
            
        # Stap 1: Controleer eerst volledig geruisloos op de achtergrond of er een update is
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                nieuweste = response.read().decode("utf-8").strip()
        except Exception:
            if silent:
                return
            messagebox.showerror("Fout", "Kon geen verbinding maken met GitHub repositories om op updates te controleren.")
            return

        # Als het systeem al up-to-date is
        if nieuweste == HUIDIGE_VERSIE:
            if silent:
                return
            # Toon direct een melding ZONDER het laadbalkscherm te openen
            messagebox.showinfo("GC-OS Update Engine", f"✨ Systeem is Volledig Up-to-Date\nHuidige versie ({HUIDIGE_VERSIE}) is de nieuwste stabiele build.")
            return

        # Stap 2: Er IS echt een update, dus NU pas maken we het visuele KB/s scherm aan
        up_win = ctk.CTkToplevel(self)
        up_win.title("🚀 GC-OS Update Engine")
        up_win.geometry("500x340")
        up_win.resizable(False, False)
        up_win.configure(fg_color=t["bg_card"])
        up_win.grab_set()
        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (up_win.winfo_screenheight() // 2) - (340 // 2)
        up_win.geometry(f"+{x}+{y}")
            
        # Header indicator
        ctk.CTkLabel(up_win, text="SYSTEM INTELLIGENCE UPDATE", font=("Courier New", 11, "bold"), text_color=t["accent"]).pack(pady=(25, 0))
            
        # Hoofd Status Label
        status_lbl = ctk.CTkLabel(up_win, text="Update gevonden! Voorbereiden...", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        status_lbl.pack(pady=(8, 5))
            
        # Live Detail Console Frame
        console_frame = ctk.CTkFrame(up_win, fg_color=t["bg_root"], height=55, width=420, corner_radius=8)
        console_frame.pack(pady=10, padx=40, fill="x")
        console_frame.pack_propagate(False)
            
        detail_lbl = ctk.CTkLabel(console_frame, text="[INFO] Initializing handshake protocols...", font=("Courier New", 11), text_color=t["text"], justify="left", anchor="w")
        detail_lbl.pack(padx=12, pady=6, fill="x", expand=True)
            
        # Progressie Balk
        balk = ctk.CTkProgressBar(up_win, width=420, height=14, progress_color=t["accent"], fg_color=t["button_fg"], corner_radius=7)
        balk.set(0.0)
        balk.pack(pady=(10, 5))
            
        # Percentage & Data teller label
        pct_lbl = ctk.CTkLabel(up_win, text="Downloaden starten...", font=("Segoe UI", 12, "bold"), text_color=t["text"])
        pct_lbl.pack(pady=(0, 15))
            
        def laad_stap(huidig_progress=0.0):
            if huidig_progress < 1.0:
                # 35 stappen van gemiddeld ~0.0285 met een pauze van 200ms geeft exact rond de 7 seconden (35 * 0.2s = 7s)
                stap = random.uniform(0.025, 0.032)
                nieuw_progress = min(huidig_progress + stap, 1.0)
                balk.set(nieuw_progress)
                
                kb_speed = random.randint(280, 520)
                pct_lbl.configure(text=f"Downloaden: {int(nieuw_progress * 100)}%  ({kb_speed} KB/s)")
                
                # Dynamische console logs per fase
                if nieuw_progress < 0.3:
                    status_lbl.configure(text="⚡ Handshaking protocols controleren...")
                    detail_lbl.configure(text=f"[CONNECT] GET /main/version.txt HTTP/1.1\n[STATUS] Bytes received: {int(nieuw_progress*140)}KB")
                elif 0.3 <= nieuw_progress < 0.6:
                    status_lbl.configure(text="📦 Manifest data uitpakken...")
                    detail_lbl.configure(text=f"[EXTRACT] Unpacking repository files...\n[FILE] Huiswerk.py.tmp -> target_buffer")
                elif 0.6 <= nieuw_progress < 0.9:
                    status_lbl.configure(text="🔍 Versies vergelijken...")
                    detail_lbl.configure(text=f"[PARSING] Checking local build against remote index...\n[COMPILING] Analyzing cryptographic hashes")
                elif nieuw_progress >= 0.9:
                    status_lbl.configure(text="⚙️ Afronden...")
                    detail_lbl.configure(text="[SUCCESS] Validating core assets...\n[READY] Requesting execution tree swap.")
                
                # Snelheid vastgezet op 200 milliseconden (0.2 seconde) per herhaling
                self.after(200, lambda: laad_stap(nieuw_progress))
            else:
                status_lbl.configure(text="🎉 NIEUWE BUILD BESCHIKBAAR!")
                detail_lbl.configure(text=f"[UPDATE FOUND] Remote node contains branch upgrade\n[MIGRATION] v{HUIDIGE_VERSIE} -> v{nieuweste}")
                pct_lbl.configure(text=f"Klaar om te upgraden naar v{nieuweste}")
                
                knop_frame = ctk.CTkFrame(up_win, fg_color="transparent")
                knop_frame.pack(pady=10)
                ctk.CTkButton(knop_frame, text="📥 Nu Installeren", fg_color=t["accent"], text_color="white", command=lambda: self.voer_update_uit(up_win, status_lbl)).pack(side="left", padx=6)
                ctk.CTkButton(knop_frame, text="Later", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(side="right", padx=6)

        # Start de visuele downloadbalk
        laad_stap()

    def voer_update_uit(self, up_win, status_lbl):
        status_lbl.configure(text="📥 Downloaden van update...")
        up_win.update()
        try:
            temp_file = os.path.join(SCRIPT_DIR, "update_tmp.py")
            req = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                nieuw_script_data = response.read().decode("utf-8")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(nieuw_script_data)
                
            try:
                req_log = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_log) as response_log:
                    changelog_data = response_log.read().decode("utf-8")
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write(changelog_data)
            except Exception:
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write("Systeem succesvol bijgewerkt naar de nieuwste versie!")
                    
            huidige_script = os.path.abspath(sys.argv[0])
            if os.name == 'nt':
                cmd = f'timeout /t 1 > nul && move /Y "{temp_file}" "{huidige_script}" && start "" "{sys.executable}" "{huidige_script}"'
            else:
                cmd = f'sleep 1 && mv -f "{temp_file}" "{huidige_script}" && "{sys.executable}" "{huidige_script}" &'
            subprocess.Popen(cmd, shell=True)
            self.destroy()
            sys.exit()
        except Exception as e:
            messagebox.showerror("Fout", f"Update mislukt:\n{e}")

    # --------------------------------------------------------
    # THEMA & LAYOUT MANAGEMENT
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

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text="GC‑OS", font=("Segoe UI", 26, "bold")).pack(pady=25)
            
        buttons = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📝  Huiswerk", self.show_huiswerk),
            ("📅  Maandrooster", self.show_rooster),
            ("🗒  Notities", self.show_notities),
            ("📊  Cijfers", self.show_cijfers),
        ]
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
        for widget in self.main.winfo_children():
            widget.destroy()
        self.clock_label = None

    # --------------------------------------------------------
    # GEPERSONALISEERD DASHBOARD
    # --------------------------------------------------------
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        nu_uur = dt.datetime.now().hour
        naam = self.data["settings"].get("gebruikersnaam", "Student")
            
        if nu_uur < 6:
            begroeting = f"Goedenacht, {naam}! 🌙"
        elif nu_uur < 12:
            begroeting = f"Goedemorgen, {naam}! ☀️"
        elif nu_uur < 18:
            begroeting = f"Goedemiddag, {naam}! 🌤️"
        else:
            begroeting = f"Goedenavond, {naam}! 🌆"
                
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=20)
            
        ctk.CTkLabel(top_bar, text=begroeting, font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(side="left")
        self.clock_label = ctk.CTkLabel(top_bar, text="", font=("Segoe UI", 14, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right", padx=10)
        self.update_clock()
            
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)
            
        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        gem = None
        if self.data["cijfers"]:
            try: gem = sum(float(c["cijfer"]) for c in self.data["cijfers"]) / len(self.data["cijfers"])
            except Exception: pass
                
        ctk.CTkLabel(card, text=f"📚 Openstaande huiswerktaken: {hw_open}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=5, padx=15)
        ctk.CTkLabel(card, text=f"📊 Gemiddeld cijfer: {f'{gem:.2f}' if gem else 'Nog geen cijfers'}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=5, padx=15)
        self.apply_theme()

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self.update_clock)

    # --------------------------------------------------------
    # HUISWERK
    # --------------------------------------------------------
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerkbeheer", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
            
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
        left_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
        self.hw_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none", bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], bd=0)
        self.hw_list.pack(fill="both", expand=True, padx=15, pady=15)
            
        for h in self.data["huiswerk"]:
            self.hw_list.insert(tk.END, f"{'✔' if h.get('afgerond') else '✘'} {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")
                
        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15, width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
            
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=15, pady=10)
            
        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving van de taak")
        self.hw_beschrijving.pack(fill="x", padx=15, pady=5)
            
        self.hw_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.hw_datum.pack(fill="x", padx=15, pady=5)
            
        ctk.CTkButton(right_frame, text="📅 Kies Datum", fg_color=t["button_fg"], text_color=t["button_text"], command=lambda: kies_datum(self.hw_datum)).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.hw_toevoegen).pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(right_frame, text="Vink af", fg_color=t["button_fg"], text_color=t["button_text"], command=self.hw_afronden).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.hw_verwijderen).pack(fill="x", padx=15, pady=5)
        self.apply_theme()

    def hw_toevoegen(self):
        v, b, d = self.hw_vak.get(), self.hw_beschrijving.get().strip(), self.hw_datum.get().strip()
        if b and d:
            self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
            opslaan(self.data)
            self.show_huiswerk()

    def hw_afronden(self):
        if self.hw_list.curselection():
            self.data["huiswerk"][self.hw_list.curselection()[0]]["afgerond"] = True
            opslaan(self.data)
            self.show_huiswerk()

    def hw_verwijderen(self):
        if self.hw_list.curselection():
            self.data["huiswerk"].pop(self.hw_list.curselection()[0])
            opslaan(self.data)
            self.show_huiswerk()

    # --------------------------------------------------------
    # ROOSTER
    # --------------------------------------------------------
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Interactieve Agenda & Maandrooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
            
        paned_container = ctk.CTkFrame(self.main, fg_color="transparent")
        paned_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
        left_side = ctk.CTkFrame(paned_container, fg_color=t["bg_card"], corner_radius=15, width=320)
        left_side.pack(side="left", fill="y", padx=(0, 10))
        left_side.pack_propagate(False)
            
        ctk.CTkLabel(left_side, text="1. Kies een datum", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=10)
        self.rooster_cal = Calendar(left_side, selectmode='day', date_pattern='yyyy-mm-dd')
        self.rooster_cal.pack(padx=10, pady=5, fill="x")
        self.rooster_cal.bind("<<CalendarSelected>>", lambda e: self.laad_dag_planner())
            
        info_box = ctk.CTkFrame(left_side, fg_color=t["bg_root"], corner_radius=10)
        info_box.pack(fill="both", expand=True, padx=15, pady=15)
            
        self.selected_date_lbl = ctk.CTkLabel(info_box, text="Geselecteerd:\nGeen dag gekozen", font=("Segoe UI", 13, "bold"), text_color=t["text"])
        self.selected_date_lbl.pack(pady=15, padx=10)
            
        self.right_side = ctk.CTkFrame(paned_container, fg_color=t["bg_card"], corner_radius=15)
        self.right_side.pack(side="right", fill="both", expand=True, padx=(10, 0))
            
        header_bar = ctk.CTkFrame(self.right_side, fg_color="transparent", height=25)
        header_bar.pack(fill="x", padx=25, pady=(10, 0))
            
        ctk.CTkLabel(header_bar, text="Tijdstip", font=("Segoe UI", 11, "bold"), text_color=t["text"], width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(header_bar, text="Vak", font=("Segoe UI", 11, "bold"), text_color=t["text"], width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_bar, text="Docent", font=("Segoe UI", 11, "bold"), text_color=t["text"], width=120, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_bar, text="Lokaal", font=("Segoe UI", 11, "bold"), text_color=t["text"], width=80, anchor="w").pack(side="left", padx=5)
            
        self.slots_scroll_frame = ctk.CTkScrollableFrame(self.right_side, fg_color="transparent")
        self.slots_scroll_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
            
        self.slot_inputs = {}
        self.laad_dag_planner()
        self.apply_theme()

    def laad_dag_planner(self):
        t = THEMES[self.theme_name]
        gekozen_datum = self.rooster_cal.get_date()
        self.selected_date_lbl.configure(text=f"🗓 Agenda voor:\n{gekozen_datum}")
            
        for widget in self.slots_scroll_frame.winfo_children():
            widget.destroy()
        self.slot_inputs.clear()
            
        bestaande_data = self.data["agenda_rooster"].get(gekozen_datum, {})
        for slot in self.tijd_slots:
            row = ctk.CTkFrame(self.slots_scroll_frame, fg_color=t["bg_root"], height=45, corner_radius=6)
            row.pack(fill="x", pady=3, padx=2)
                
            ctk.CTkLabel(row, text=slot, font=("Courier New", 11, "bold"), text_color=t["text"], width=100, anchor="w").pack(side="left", padx=10)
                
            vak_ent = ctk.CTkEntry(row, placeholder_text="bv. Hardware", fg_color=t["bg_card"], text_color=t["text"], border_width=1, border_color=t["button_hover"], width=150)
            vak_ent.pack(side="left", padx=5, pady=6)
                
            docent_ent = ctk.CTkEntry(row, placeholder_text="bv. JNS", fg_color=t["bg_card"], text_color=t["text"], border_width=1, border_color=t["button_hover"], width=120)
            docent_ent.pack(side="left", padx=5, pady=6)
                
            lokaal_ent = ctk.CTkEntry(row, placeholder_text="bv. D102", fg_color=t["bg_card"], text_color=t["text"], border_width=1, border_color=t["button_hover"], width=80)
            lokaal_ent.pack(side="left", padx=5, pady=6)
                
            if slot in bestaande_data and isinstance(bestaande_data[slot], dict):
                vak_ent.insert(0, bestaande_data[slot].get("vak", ""))
                docent_ent.insert(0, bestaande_data[slot].get("docent", ""))
                lokaal_ent.insert(0, bestaande_data[slot].get("lokaal", ""))
            elif slot in bestaande_data:
                vak_ent.insert(0, bestaande_data[slot])
                    
            self.slot_inputs[slot] = {
                "vak": vak_ent,
                "docent": docent_ent,
                "lokaal": lokaal_ent
            }
                
        action_bar = ctk.CTkFrame(self.slots_scroll_frame, fg_color="transparent")
        action_bar.pack(fill="x", pady=15)
            
        ctk.CTkButton(action_bar, text="💾 Wijzigingen Opslaan", fg_color=t["accent"], text_color="white", font=("Segoe UI", 12, "bold"), command=self.save_dag_planner).pack(side="right", padx=5)
        ctk.CTkButton(action_bar, text="🧹 Dag Leegmaken", fg_color=t["button_fg"], text_color=t["button_text"], command=self.clear_dag_planner).pack(side="left", padx=5)

    def save_dag_planner(self):
        gekozen_datum = self.rooster_cal.get_date()
        dag_data = {}
            
        for slot, inputs in self.slot_inputs.items():
            v = inputs["vak"].get().strip()
            d = inputs["docent"].get().strip()
            l = inputs["lokaal"].get().strip()
                
            if v or d or l:
                dag_data[slot] = {
                    "vak": v,
                    "docent": d,
                    "lokaal": l
                }
        if dag_data:
            self.data["agenda_rooster"][gekozen_datum] = dag_data
        else:
            if gekozen_datum in self.data["agenda_rooster"]:
                self.data["agenda_rooster"].pop(gekozen_datum)
        opslaan(self.data)
        messagebox.showinfo("Succes", f"Agenda voor {gekozen_datum} succesvol opgeslagen.")

    def clear_dag_planner(self):
        if messagebox.askyesno("Bevestigen", "Weet je zeker dat je alle invoervelden van deze dag leeg wilt maken?"):
            for slot, inputs in self.slot_inputs.items():
                inputs["vak"].delete(0, tk.END)
                inputs["docent"].delete(0, tk.END)
                inputs["lokaal"].delete(0, tk.END)

    # --------------------------------------------------------
    # NOTITIES
    # --------------------------------------------------------
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijke Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
            
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
        left_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none", bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], bd=0)
        self.note_list.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_list.bind("<<ListboxSelect>>", self.note_selecteren)
            
        for n in self.data["notities"]:
            titel = n.get("titel", "Geen titel")
            datum = n.get("datum", "")
            self.note_list.insert(tk.END, f"{datum} - {titel}")
                
        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15, width=400)
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        right_frame.pack_propagate(False)
            
        self.note_titel = ctk.CTkEntry(right_frame, placeholder_text="Titel van de notitie")
        self.note_titel.pack(fill="x", padx=15, pady=(15, 5))
            
        self.note_tekst = ctk.CTkTextbox(right_frame, font=("Segoe UI", 12))
        self.note_tekst.pack(fill="both", expand=True, padx=15, pady=5)
            
        btn_box = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=15)
            
        ctk.CTkButton(btn_box, text="Nieuw / Wis", fg_color=t["button_fg"], text_color=t["button_text"], command=self.note_wissen).pack(side="left", padx=(0, 5), fill="x", expand=True)
        ctk.CTkButton(btn_box, text="Opslaan", fg_color=t["accent"], text_color="white", command=self.note_opslaan).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(btn_box, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.note_verwijderen).pack(side="left", padx=(5, 0), fill="x", expand=True)
        self.apply_theme()

    def note_selecteren(self, event):
        if self.note_list.curselection():
            idx = self.note_list.curselection()[0]
            n = self.data["notities"][idx]
            self.note_titel.delete(0, tk.END)
            self.note_titel.insert(0, n.get("titel", ""))
            self.note_tekst.delete("1.0", tk.END)
            self.note_tekst.insert("1.0", n.get("tekst", ""))

    def note_wissen(self):
        self.note_titel.delete(0, tk.END)
        self.note_tekst.delete("1.0", tk.END)
        self.note_list.selection_clear(0, tk.END)

    def note_opslaan(self):
        titel = self.note_titel.get().strip()
        tekst = self.note_tekst.get("1.0", tk.END).strip()
        if not titel:
            messagebox.showwarning("Waarschuwing", "Geef de notitie tenminste een titel.")
            return
        datum_str = dt.date.today().strftime("%Y-%m-%d")
        if self.note_list.curselection():
            idx = self.note_list.curselection()[0]
            self.data["notities"][idx] = {"titel": titel, "tekst": tekst, "datum": datum_str}
        else:
            self.data["notities"].append({"titel": titel, "tekst": tekst, "datum": datum_str})
        opslaan(self.data)
        self.show_notities()

    def note_verwijderen(self):
        if self.note_list.curselection():
            idx = self.note_list.curselection()[0]
            self.data["notities"].pop(idx)
            opslaan(self.data)
            self.show_notities()

    # --------------------------------------------------------
    # CIJFERS & MATPLOTLIB INTEGRATIE
    # --------------------------------------------------------
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie & Voortgang", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)
            
        main_container = ctk.CTkFrame(self.main, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
        left_panel = ctk.CTkFrame(main_container, fg_color=t["bg_card"], corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
        self.cijfer_list = tk.Listbox(left_panel, font=("Segoe UI", 11), activestyle="none", bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], bd=0)
        self.cijfer_list.pack(fill="both", expand=True, padx=15, pady=15)
            
        gesorteerde_cijfers = sorted(self.data["cijfers"], key=lambda x: x.get("datum", ""))
        for c in gesorteerde_cijfers:
            self.cijfer_list.insert(tk.END, f"{c.get('datum')} - {c.get('vak')} ({c.get('periode', 'P1')}): {c.get('cijfer')} (Weging: {c.get('weging', '1x')})")
                
        right_panel = ctk.CTkFrame(main_container, fg_color=t["bg_card"], corner_radius=15, width=280)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
            
        self.c_vak = ctk.CTkComboBox(right_panel, values=self.vakken_hw, state="readonly")
        self.c_vak.set(self.vakken_hw[0])
        self.c_vak.pack(fill="x", padx=15, pady=8)
            
        self.c_periode = ctk.CTkComboBox(right_panel, values=self.periodes, state="readonly")
        self.c_periode.set(self.periodes[0])
        self.c_periode.pack(fill="x", padx=15, pady=5)
            
        self.c_val = ctk.CTkEntry(right_panel, placeholder_text="Cijfer (bv. 7.5)")
        self.c_val.pack(fill="x", padx=15, pady=5)
            
        self.c_weging = ctk.CTkComboBox(right_panel, values=["1x", "2x", "3x", "4x"], state="readonly")
        self.c_weging.set("1x")
        self.c_weging.pack(fill="x", padx=15, pady=5)
            
        self.c_datum = ctk.CTkEntry(right_panel, placeholder_text="yyyy-mm-dd")
        self.c_datum.pack(fill="x", padx=15, pady=5)
            
        ctk.CTkButton(right_panel, text="📅 Kies Datum", fg_color=t["button_fg"], text_color=t["button_text"], command=lambda: kies_datum(self.c_datum)).pack(fill="x", padx=15, pady=4)
        ctk.CTkButton(right_panel, text="Cijfer Opslaan", fg_color=t["accent"], text_color="white", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(right_panel, text="Verwijder Selectie", fg_color=t["button_fg"], text_color=t["button_text"], command=self.cijfer_verwijderen).pack(fill="x", padx=15, pady=4)
            
        self.graph_frame = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"], height=200)
        self.graph_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.graph_frame.pack_propagate(False)
            
        self.teken_cijfer_grafiek()
        self.apply_theme()

    def teken_cijfer_grafiek(self):
        t = THEMES[self.theme_name]
        for w in self.graph_frame.winfo_children():
            w.destroy()
        if not self.data["cijfers"]:
            ctk.CTkLabel(self.graph_frame, text="Voeg cijfers toe om de voortgangsgrafiek te genereren.", font=("Segoe UI", 13), text_color=t["text"]).pack(expand=True)
            return
                
        data_punten = sorted(self.data["cijfers"], key=lambda x: x.get("datum", ""))
        is_dark = (t["mode"] == "Dark")
        bg_color = "#1f1f23" if is_dark else "#ffffff"
        fg_color = "#f5f5f7" if is_dark else "#111111"
            
        fig, ax = plt.subplots(figsize=(10, 2.2), facecolor=bg_color)
        ax.set_facecolor(bg_color)
            
        vak_data = {}
        for p in data_punten:
            v = p.get("vak")
            if v not in vak_data:
                vak_data[v] = {"x": [], "y": []}
            vak_data[v]["x"].append(p.get("datum")[5:])
            try:
                vak_data[v]["y"].append(float(p.get("cijfer")))
            except ValueError:
                vak_data[v]["y"].append(0.0)
                    
        for vak, lijsten in vak_data.items():
            kleur = self.vak_kleuren.get(vak, t["accent"])
            ax.plot(lijsten["x"], lijsten["y"], marker='o', linewidth=2, markersize=6, label=vak, color=kleur)
                
        ax.set_title("Resultaten Verloop Per Vak", color=fg_color, fontsize=11, fontweight="bold", pad=8)
        ax.tick_params(colors=fg_color, labelsize=9)
        ax.set_ylim(1.0, 10.5)
        ax.grid(True, linestyle="--", alpha=0.15, color=fg_color)
            
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=8, facecolor=bg_color, edgecolor=fg_color, labelcolor=fg_color)
            
        fig.tight_layout()
        self.canvas_grafiek = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas_grafiek.draw()
        self.canvas_grafiek.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def cijfer_toevoegen(self):
        v = self.c_vak.get()
        p = self.c_periode.get()
        c = self.c_val.get().strip().replace(",", ".")
        w = self.c_weging.get()
        d = self.c_datum.get().strip()
        if c and d:
            try:
                float(c)
                self.data["cijfers"].append({"vak": v, "periode": p, "cijfer": c, "weging": w, "datum": d})
                opslaan(self.data)
                self.show_cijfers()
            except ValueError:
                messagebox.showerror("Fout", "Voer een geldig getal in voor het cijfer (bijv. 6.8).")

    def cijfer_verwijderen(self):
        if self.cijfer_list.curselection():
            gesorteerde_cijfers = sorted(self.data["cijfers"], key=lambda x: x.get("datum", ""))
            verwijder_item = gesorteerde_cijfers[self.cijfer_list.curselection()[0]]
            self.data["cijfers"].remove(verwijder_item)
            opslaan(self.data)
            self.show_cijfers()

    # --------------------------------------------------------
    # INSTELLINGEN & THEMA SELECTIE
    # --------------------------------------------------------
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Systeeminstellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
            
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
        ctk.CTkLabel(card, text="Gebruikersnaam aanpassen:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
            
        self.settings_name = ctk.CTkEntry(card, width=300)
        self.settings_name.insert(0, self.data["settings"].get("gebruikersnaam", "Student"))
        self.settings_name.pack(anchor="w", padx=20, pady=5)
            
        ctk.CTkLabel(card, text="Visueel Systeemthema Selecteren:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        themalijst = list(THEMES.keys())
        self.theme_combo = ctk.CTkComboBox(card, values=themalijst, state="readonly")
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=20, pady=5)
            
        ctk.CTkLabel(card, text="Systeem update & Onderhoud:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(25, 5))
        ctk.CTkButton(card, text="🔍 Zoeken naar Updates", fg_color=t["button_fg"], text_color=t["button_text"], command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=20, pady=5)
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
        self.apply_theme()
        messagebox.showinfo("Succes", "Instellingen succesvol bijgewerkt en opgeslagen.")

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
