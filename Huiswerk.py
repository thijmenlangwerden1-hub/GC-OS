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

# ============================================================
# THEMA'S (Hersteld en geoptimaliseerd)
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

HUIDIGE_VERSIE = "5.2v"
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
    ]
    return dagen

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "agenda_rooster": {},
            "settings": {"theme": "Wit"},
            "vrijedagen": [],
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "agenda_rooster" not in data: data["agenda_rooster"] = {}
    if "settings" not in data: data["settings"] = {"theme": "Wit"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
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
        self.geometry("1150://680")
        self.geometry("1150x680")
        self.minsize(1000, 600)

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan"
        ]
        
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]

        # Genereren van de 30-minuten tijdsblokken (08:00 tot 17:00)
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

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()

        self.after(100, self.show_intro_screen)
        self.after(2500, lambda: self.toon_update_laadbalk(silent=True))
        self.after(3000, self.check_na_update_log)

    # --------------------------------------------------------
    # UPDATE LOG DETECTIE & POP-UP
    # --------------------------------------------------------

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

        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", 10, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.5, anchor="center")

        def animate(alpha=0.0, size=10):
            if alpha < 1.0:
                intro.attributes("-alpha", alpha)
            if size < 55:
                size += 2
                label.configure(font=("Segoe UI", size, "bold"))
            if alpha < 1.0 or size < 55:
                self.after(15, lambda: animate(alpha + 0.04, size))
            else:
                self.after(600, lambda: fade_out(1.0))

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(15, lambda: fade_out(alpha - 0.05))
            else:
                intro.destroy()
                try: self.state("zoomed")
                except Exception: pass

        animate()

    # --------------------------------------------------------
    # UPGRADED COOL UPDATE MANAGER
    # --------------------------------------------------------

    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]

        up_win = ctk.CTkToplevel(self)
        up_win.title("🚀 GC-OS Update Engine")
        up_win.geometry("460x280")
        up_win.resizable(False, False)
        up_win.configure(fg_color=t["bg_card"])
        up_win.grab_set()

        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (460 // 2)
        y = (up_win.winfo_screenheight() // 2) - (280 // 2)
        up_win.geometry(f"+{x}+{y}")

        # Coolere UI elementen
        ctk.CTkLabel(up_win, text="SYSTEM INTELLIGENCE UPDATE", font=("Courier New", 11, "bold"), text_color=t["accent"]).pack(pady=(20, 0))
        
        status_lbl = ctk.CTkLabel(up_win, text="Verbinding maken met server...", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        status_lbl.pack(pady=(10, 15))

        balk = ctk.CTkProgressBar(up_win, width=360, height=12, progress_color=t["accent"], corner_radius=6)
        balk.set(0.0)
        balk.pack(pady=5)

        pct_lbl = ctk.CTkLabel(up_win, text="INITIALIZING...", font=("Segoe UI", 12), text_color=t["text"])
        pct_lbl.pack(pady=(0, 10))

        def laad_stap(huidig_progress=0.0):
            if huidig_progress < 1.0:
                stap = random.uniform(0.03, 0.09)
                nieuw_progress = min(huidig_progress + stap, 1.0)
                balk.set(nieuw_progress)
                pct_lbl.configure(text=f"Dowloading packages... {int(nieuw_progress * 100)}%")
                
                # Dynamische statusteksten voor de 'cool-factor'
                if nieuw_progress > 0.3 and nieuw_progress < 0.6:
                    status_lbl.configure(text="⚡ Handshaking protocols controleren...")
                elif nieuw_progress >= 0.6 and nieuw_progress < 0.9:
                    status_lbl.configure(text="📦 Manifest data uitpakken...")
                elif nieuw_progress >= 0.9:
                    status_lbl.configure(text="🔍 Versies vergelijken...")

                self.after(int(random.uniform(50, 150)), lambda: laad_stap(nieuw_progress))
            else:
                voer_update_check_uit()

        def voer_update_check_uit():
            try:
                req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    nieuweste = response.read().decode("utf-8").strip()
            except Exception:
                if silent:
                    up_win.destroy()
                    return
                status_lbl.configure(text="❌ Connectie verbroken.")
                pct_lbl.configure(text="Kon geen verbinding maken met GitHub repositories.")
                ctk.CTkButton(up_win, text="Sluiten", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(pady=15)
                return

            if nieuweste == HUIDIGE_VERSIE:
                if silent:
                    up_win.destroy()
                    return
                status_lbl.configure(text="✨ Systeem is Volledig Up-to-Date")
                pct_lbl.configure(text=f"Huidige versie (v{HUIDIGE_VERSIE}) is de nieuwste stabiele build.")
                ctk.CTkButton(up_win, text="Sluiten", fg_color=t["accent"], text_color="white", command=up_win.destroy).pack(pady=15)
            else:
                status_lbl.configure(text="🎉 NIEUWE BUILD BESCHIKBAAR!")
                pct_lbl.configure(text=f"Upgrade van v{HUIDIGE_VERSIE} naar v{nieuweste}")
                knop_frame = ctk.CTkFrame(up_win, fg_color="transparent")
                knop_frame.pack(pady=15)
                ctk.CTkButton(knop_frame, text="📥 Nu Installeren", fg_color=t["accent"], text_color="white", command=lambda: self.voer_update_uit(up_win, status_lbl)).pack(side="left", padx=5)
                ctk.CTkButton(knop_frame, text="Later", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(side="right", padx=5)

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

    def _get_upcoming_vrijedagen(self):
        vandaag = dt.date.today()
        upcoming = []
        for v in self.data.get("vrijedagen", []):
            try:
                d = dt.datetime.strptime(v["datum"], "%Y-%m-%d").date()
                delta = (d - vandaag).days
                if delta >= 0: upcoming.append((d, delta, v["naam"]))
            except Exception: pass
        upcoming.sort(key=lambda x: x[0])
        return upcoming

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

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
    # UPGRADED: GEOPTIMALISEERD INTERACTIEF MAANDROOSTER
    # --------------------------------------------------------

    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        # Hoofdtitel van de module
        ctk.CTkLabel(self.main, text="Interactieve Agenda & Maandrooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)

        # Container opsplitsen in kalenderselectie (links) en urenplanner (rechts)
        paned_container = ctk.CTkFrame(self.main, fg_color="transparent")
        paned_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        left_side = ctk.CTkFrame(paned_container, fg_color=t["bg_card"], corner_radius=15, width=320)
        left_side.pack(side="left", fill="y", padx=(0, 10))
        left_side.pack_propagate(False)

        ctk.CTkLabel(left_side, text="1. Kies een datum", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=10)

        # Ingebouwde kalender voor maandoverzicht
        self.rooster_cal = Calendar(left_side, selectmode='day', date_pattern='yyyy-mm-dd')
        self.rooster_cal.pack(padx=10, pady=5, fill="x")
        self.rooster_cal.bind("<<CalendarSelected>>", lambda e: self.laad_dag_planner())

        # Snelkoppeling / Informatiebox links onderin
        info_box = ctk.CTkFrame(left_side, fg_color=t["bg_root"], corner_radius=10)
        info_box.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.selected_date_lbl = ctk.CTkLabel(info_box, text="Geselecteerd:\nGeen dag gekozen", font=("Segoe UI", 13, "bold"), text_color=t["text"])
        self.selected_date_lbl.pack(pady=15, padx=10)

        # Rechterzijde: De tijdsblokken (08:00 - 17:00 per 30 min)
        self.right_side = ctk.CTkFrame(paned_container, fg_color=t["bg_card"], corner_radius=15)
        self.right_side.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Dynamisch scroll-paneel voor alle tijdvakken
        self.slots_scroll_frame = ctk.CTkScrollableFrame(self.right_side, fg_color="transparent")
        self.slots_scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.slot_entries = {}
        self.laad_dag_planner()
        self.apply_theme()

    def laad_dag_planner(self):
        t = THEMES[self.theme_name]
        gekozen_datum = self.rooster_cal.get_date()
        self.selected_date_lbl.configure(text=f"🗓 Agenda voor:\n{gekozen_datum}")

        # Wis de oude invoervelden in de scrollbox
        for widget in self.slots_scroll_frame.winfo_children():
            widget.destroy()

        self.slot_entries.clear()
        bestaande_data = self.data["agenda_rooster"].get(gekozen_datum, {})

        # Bouw de 30-minuten gridrijen op
        for slot in self.tijd_slots:
            row = ctk.CTkFrame(self.slots_scroll_frame, fg_color=t["bg_root"], height=40, corner_radius=6)
            row.pack(fill="x", pady=3, padx=2)
            
            # Tijdlabel (bijv. 08:30 - 09:00)
            ctk.CTkLabel(row, text=slot, font=("Courier New", 12, "bold"), text_color=t["text"], width=110, anchor="w").pack(side="left", padx=10)
            
            # Invoerveld voor de activiteit
            ent = ctk.CTkEntry(row, placeholder_text="Vrij / Geen activiteit gepland...", fg_color=t["bg_card"], text_color=t["text"], border_width=1, border_color=t["button_hover"])
            ent.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=4)
            
            # Vul bestaande waarde in als die er is
            if slot in bestaande_data:
                ent.insert(0, bestaande_data[slot])
                
            self.slot_entries[slot] = ent

        # Centraal actiemenu onder de planner plakken
        action_bar = ctk.CTkFrame(self.slots_scroll_frame, fg_color="transparent")
        action_bar.pack(fill="x", pady=15)
        
        ctk.CTkButton(action_bar, text="💾 Wijzigingen Opslaan", fg_color=t["accent"], text_color="white", font=("Segoe UI", 12, "bold"), command=self.save_dag_planner).pack(side="right", padx=5)
        ctk.CTkButton(action_bar, text="🧹 Dag Leegmaken", fg_color=t["button_fg"], text_color=t["button_text"], command=self.clear_dag_planner).pack(side="left", padx=5)

    def save_dag_planner(self):
        gekozen_datum = self.rooster_cal.get_date()
        dag_data = {}
        
        for slot, entry in self.slot_entries.items():
            waarde = entry.get().strip()
            if waarde:  # Alleen opslaan als er daadwerkelijk iets is ingevuld
                dag_data[slot] = waarde

        if dag_data:
            self.data["agenda_rooster"][gekozen_datum] = dag_data
        elif gekozen_datum in self.data["agenda_rooster"]:
            del self.data["agenda_rooster"][gekozen_datum]

        opslaan(self.data)
        messagebox.showinfo("Succes", f"Je agenda voor {gekozen_datum} is succesvol bijgewerkt!")

    def clear_dag_planner(self):
        if messagebox.askyesno("Agenda Leegmaken", "Weet je zeker dat je alle invoer voor deze dag wilt wissen?"):
            for entry in self.slot_entries.values():
                entry.delete(0, tk.END)
            self.save_dag_planner()

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

        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), bd=0, bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"])
        self.note_list.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_list.bind("<<ListboxSelect>>", self.note_selecteren)

        for n in self.data["notities"]:
            self.note_list.insert(tk.END, n.get("titel", "Naamloze notitie"))

        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15, width=340)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        self.note_titel = ctk.CTkEntry(right_frame, placeholder_text="Titel van de notitie")
        self.note_titel.pack(fill="x", padx=15, pady=15)

        self.note_inhoud = ctk.CTkTextbox(right_frame, height=220)
        self.note_inhoud.pack(fill="both", expand=True, padx=15, pady=5)

        ctk.CTkButton(right_frame, text="Opslaan", fg_color=t["accent"], text_color="white", command=self.note_opslaan).pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.note_verwijderen).pack(fill="x", padx=15, pady=5)
        self.apply_theme()

    def note_selecteren(self, event):
        if self.note_list.curselection():
            note = self.data["notities"][self.note_list.curselection()[0]]
            self.note_titel.delete(0, tk.END)
            self.note_titel.insert(0, note.get("titel", ""))
            self.note_inhoud.delete("1.0", tk.END)
            self.note_inhoud.insert("1.0", note.get("inhoud", ""))

    def note_opslaan(self):
        tit, inh = self.note_titel.get().strip(), self.note_inhoud.get("1.0", tk.END).strip()
        if tit:
            if self.note_list.curselection():
                self.data["notities"][self.note_list.curselection()[0]] = {"titel": tit, "inhoud": inh}
            else:
                self.data["notities"].append({"titel": tit, "inhoud": inh})
            opslaan(self.data)
            self.show_notities()

    def note_verwijderen(self):
        if self.note_list.curselection():
            self.data["notities"].pop(self.note_list.curselection()[0])
            opslaan(self.data)
            self.show_notities()

    # --------------------------------------------------------
    # CIJFERS
    # --------------------------------------------------------

    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferlijst", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.cijfer_list = tk.Listbox(left_frame, font=("Segoe UI", 11), bd=0, bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"])
        self.cijfer_list.pack(fill="both", expand=True, padx=15, pady=15)

        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f"{c.get('vak')} - {c.get('periode')}: {c.get('cijfer')} (Weging: {c.get('weging')}x)")

        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15, width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        self.cijfer_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.cijfer_vak.set(self.vakken_hw[0])
        self.cijfer_vak.pack(fill="x", padx=15, pady=10)

        self.cijfer_periode = ctk.CTkComboBox(right_frame, values=self.periodes, state="readonly")
        self.cijfer_periode.set(self.periodes[0])
        self.cijfer_periode.pack(fill="x", padx=15, pady=5)

        self.cijfer_waarde = ctk.CTkEntry(right_frame, placeholder_text="Cijfer (bijv. 6.8)")
        self.cijfer_waarde.pack(fill="x", padx=15, pady=5)

        self.cijfer_weging = ctk.CTkEntry(right_frame, placeholder_text="Weging (bijv. 2)")
        self.cijfer_weging.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.cijfer_verwijderen).pack(fill="x", padx=15, pady=5)
        self.apply_theme()

    def cijfer_toevoegen(self):
        v, p, c, w = self.cijfer_vak.get(), self.cijfer_periode.get(), self.cijfer_waarde.get().strip().replace(',', '.'), self.cijfer_weging.get().strip()
        if c and w:
            self.data["cijfers"].append({"vak": v, "periode": p, "cijfer": c, "weging": w, "datum": dt.date.today().strftime('%Y-%m-%d')})
            opslaan(self.data)
            self.show_cijfers()

    def cijfer_verwijderen(self):
        if self.cijfer_list.curselection():
            self.data["cijfers"].pop(self.cijfer_list.curselection()[0])
            opslaan(self.data)
            self.show_cijfers()

    # --------------------------------------------------------
    # INSTELLINGEN
    # --------------------------------------------------------

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(card, text="🎨 Systeemthema wijzigen:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        self.theme_combo = ctk.CTkComboBox(card, values=list(THEMES.keys()), state="readonly", command=self.theme_wijzigen)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=20, pady=5)

        ctk.CTkLabel(card, text="🔄 Systeem Updates:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkButton(card, text="Handmatig zoeken naar updates", fg_color=t["accent"], text_color="white", command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=20, pady=5)
        self.apply_theme()

    def theme_wijzigen(self, nieuw_thema):
        if nieuw_thema in THEMES:
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
