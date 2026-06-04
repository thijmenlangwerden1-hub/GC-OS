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
        "button_fg": "#bdeecb",
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
# INSTELLINGEN & CONFIGURATIE (Versie 1.0.19)
# ============================================================

HUIDIGE_VERSIE = "1.0.19"
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
        {"naam": "Voorjaarsvakantie", "datum": f"{volgend}-02-16"},
        {"naam": "Meivakantie", "datum": f"{volgend}-05-01"},
        {"naam": "Zomervakantie", "datum": f"{volgend}-07-14"},
        {"naam": "Herfstvakantie", "datum": f"{volgend}-10-20"},
        {"naam": "Kerstvacantie", "datum": f"{volgend}-12-23"},
    ]

    uniek = {}
    for d in dagen:
        uniek[(d["naam"], d["datum"])] = d
    return list(uniek.values())

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": [],
            "settings": {"theme": "Wit", "naam": ""},
            "vrijedagen": [],
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data: data["rooster"] = []
    if "settings" not in data: data["settings"] = {"theme": "Wit", "naam": ""}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "naam" not in data["settings"]: data["settings"]["naam"] = ""
    if "vrijedagen" not in data: data["vrijedagen"] = []

    for c in data.get("cijfers", []):
        if "periode" not in c: c["periode"] = "Periode 1"
        if "datum" not in c: c["datum"] = "2026-01-01"

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

        # Verberg de hoofdapplicatie totdat de gebruiker succesvol is ingelogd
        self.withdraw()

        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Wit")
        if self.theme_name not in THEMES:
            self.theme_name = "Wit"

        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        ctk.set_default_color_theme("blue")

        self.title("GraafschapCollege‑OS")
        self.geometry("1100x650")
        self.minsize(950, 550)

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Vrije Afspraak"
        ]
        
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]
        self.weekdagen_volledig = ["Zondag", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag"]

        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.rooster_listbox = None

        self.theme_combo = None
        self.vrijedagen_listbox = None
        self.clock_label = None
        self.dashboard_title_label = None  

        self.rooster_stijl = "Week" 
        self.huidige_rooster_datum = dt.date.today()

        self._build_layout()
        self.apply_theme()

        # Start de opstart- en introanimatie
        self.after(100, self.show_intro_screen)

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
        ctk.CTkLabel(log_win, text="Dit is er nieuw in deze versie:", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=(0, 15))

        txt_frame = ctk.CTkScrollableFrame(log_win, width=440, height=220, fg_color=t["bg_root"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(txt_frame, text=log_tekst.strip(), font=("Segoe UI", 12), justify="left", text_color=t["text"], anchor="w").pack(anchor="w", padx=10, pady=10)

        ctk.CTkButton(log_win, text="Sluiten & Ontdekken", fg_color=t["accent"], text_color="white", command=log_win.destroy).pack(pady=20)

    def show_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("GC-OS Intro")
        intro.overrideredirect(True)

        try:
            intro.attributes("-fullscreen", True)
        except Exception:
            intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])

        start_size = 10
        end_size = 60
        current_size = start_size

        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", current_size, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.5, anchor="center")
        intro.attributes("-alpha", 0.0)

        def animate(alpha=0.0, size=current_size):
            if alpha < 1.0:
                intro.attributes("-alpha", alpha)
            if size < end_size:
                size += 2
                label.configure(font=("Segoe UI", size, "bold"))

            if alpha < 1.0 or size < end_size:
                self.after(15, lambda: animate(alpha + 0.03, size))
            else:
                self.after(600, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(15, lambda: fade_out(alpha - 0.04))
            else:
                try:
                    intro.destroy()
                except Exception:
                    pass
                self.show_login_screen()

        animate()

    # ============================================================
    # INLOGSCHERM SCRIPT
    # ============================================================
    def show_login_screen(self):
        t = THEMES[self.theme_name]
        self.login_win = ctk.CTkToplevel()
        self.login_win.title("Inloggen - GC-OS")
        self.login_win.geometry("400x350")
        self.login_win.resizable(False, False)
        self.login_win.configure(fg_color=t["bg_root"])
        
        self.login_win.update_idletasks()
        x = (self.login_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.login_win.winfo_screenheight() // 2) - (350 // 2)
        self.login_win.geometry(f"+{x}+{y}")
        self.login_win.grab_set()

        self.login_win.protocol("WM_DELETE_WINDOW", sys.exit)

        ctk.CTkLabel(self.login_win, text="Inloggen op GC-OS", font=("Segoe UI", 22, "bold"), text_color=t["accent"]).pack(pady=(30, 20))

        self.username_entry = ctk.CTkEntry(self.login_win, placeholder_text="Gebruikersnaam", width=260, height=35)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.login_win, placeholder_text="Wachtwoord", show="*", width=260, height=35)
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.login_win, text="Inloggen", fg_color=t["accent"], text_color="white", width=260, height=38, font=("Segoe UI", 13, "bold"), command=self.check_login).pack(pady=20)

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "admin" and password == "admin":
            self.login_win.destroy()
            self.deiconify()
            try:
                self.state("zoomed")
            except Exception:
                pass
            
            self.show_dashboard()

            # Controleer direct stil op de achtergrond op updates na inloggen
            self.after(500, lambda: self.toon_update_laadbalk(silent=True))
            self.after(1000, self.check_na_update_log)
        else:
            messagebox.showerror("Inloggen Mislukt", "Onjuiste gebruikersnaam of wachtwoord. Probeer het opnieuw.")

    # ============================================================
    # UPDATE MANAGER LOGICA
    # ============================================================
    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]
        up_win = ctk.CTkToplevel(self)
        up_win.title("GC-OS Update Manager")
        up_win.geometry("420x220")
        up_win.resizable(False, False)
        up_win.configure(fg_color=t["bg_card"])
        up_win.grab_set()

        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (420 // 2)
        y = (up_win.winfo_screenheight() // 2) - (220 // 2)
        up_win.geometry(f"+{x}+{y}")

        status_lbl = ctk.CTkLabel(up_win, text="🔄 Controleren op beschikbare updates...", font=("Segoe UI", 15, "bold"), text_color=t["text"])
        status_lbl.pack(pady=(35, 10))

        balk = ctk.CTkProgressBar(up_win, width=320, progress_color=t["accent"])
        balk.set(0.0)
        balk.pack(pady=10)

        pct_lbl = ctk.CTkLabel(up_win, text="0%", font=("Segoe UI", 12), text_color=t["text"])
        pct_lbl.pack()

        def laad_stap(huidig_progress=0.0):
            if huidig_progress < 1.0:
                stap = random.uniform(0.02, 0.07)
                nieuw_progress = min(huidig_progress + stap, 1.0)
                balk.set(nieuw_progress)
                pct_lbl.configure(text=f"{int(nieuw_progress * 100)}%")
                vertraging = int(random.uniform(40, 160))
                self.after(vertraging, lambda: laad_stap(nieuw_progress))
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
                status_lbl.configure(text="❌ Fout: Kan geen verbinding maken met GitHub.")
                ctk.CTkButton(up_win, text="Sluiten", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(pady=15)
                return

            if nieuweste == HUIDIGE_VERSIE:
                if silent:
                    up_win.destroy()
                    return
                status_lbl.configure(text=f"✨ Je bent helemaal up-to-date! (v{HUIDIGE_VERSIE})")
                ctk.CTkButton(up_win, text="Geweldig!", fg_color=t["accent"], text_color="white", command=up_win.destroy).pack(pady=15)
            else:
                status_lbl.configure(text=f"🎉 Update beschikbaar! v{HUIDIGE_VERSIE} ➔ v{nieuweste}")
                knop_frame = ctk.CTkFrame(up_win, fg_color="transparent")
                knop_frame.pack(pady=15)

                ctk.CTkButton(knop_frame, text="📥 Download & Installeer", fg_color=t["accent"], text_color="white", command=lambda: self.voer_update_uit(up_win, status_lbl)).pack(side="left", padx=5)
                ctk.CTkButton(knop_frame, text="Later", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(side="right", padx=5)

        laad_stap()

    def voer_update_uit(self, up_win, status_lbl):
        status_lbl.configure(text="📥 Downloaden van update...")
        up_win.update()
        try:
            try:
                req_log = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_log) as response_log:
                    nieuwe_log_data = response_log.read().decode("utf-8")
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write(nieuwe_log_data)
            except Exception:
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write("Kleine prestatieverbeteringen en bugfixes.")

            temp_file = os.path.join(SCRIPT_DIR, "update_tmp.py")
            req = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                nieuw_script_data = response.read().decode("utf-8")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(nieuw_script_data)

            status_lbl.configure(text="🔄 Installeren en herstarten...")
            up_win.update()
            time.sleep(1)

            huidige_script = os.path.abspath(sys.argv[0])
            if os.name == 'nt':
                cmd = f'timeout /t 1 > nul && move /Y "{temp_file}" "{huidige_script}" && start "" "{sys.executable}" "{huidige_script}"'
                subprocess.Popen(cmd, shell=True)
            else:
                cmd = f'sleep 1 && mv -f "{temp_file}" "{huidige_script}" && "{sys.executable}" "{huidige_script}" &'
                subprocess.Popen(cmd, shell=True)

            self.destroy()
            sys.exit()
        except Exception as e:
            status_lbl.configure(text="❌ Update mislukt!")
            messagebox.showerror("Fout bij updaten", f"Er is een fout opgetreden tijdens het updaten:\n{e}")

    # ============================================================
    # THEMA MANAGEMENT
    # ============================================================
    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])

        if hasattr(self, "sidebar"): self.sidebar.configure(fg_color=t["bg_sidebar"])
        if hasattr(self, "main"): self.main.configure(fg_color=t["bg_main"])

        for btn in self.sidebar_buttons:
            try:
                btn.configure(fg_color="transparent", hover_color=t["button_hover"], text_color=t["sidebar_text"])
            except Exception: pass

        for lst in [self.hw_list, self.note_list, self.cijfer_list, self.vrijedagen_listbox, self.rooster_listbox]:
            if lst is not None:
                lst.configure(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], highlightthickness=0, borderwidth=0)

        if self.theme_combo is not None:
            try:
                self.theme_combo.configure(fg_color=t["button_fg"], border_color=t["accent"], button_color=t["accent"], button_hover_color=t["button_hover"], text_color=t["button_text"])
            except Exception: pass

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
        for widget in self.main.winfo_children():
            widget.destroy()
        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.rooster_listbox = None
        self.vrijedagen_listbox = None
        self.theme_combo = None
        self.clock_label = None
        self.dashboard_title_label = None

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
                if delta >= 0:
                    upcoming.append((d, delta, naam))
            except Exception: continue
        upcoming.sort(key=lambda x: x[0])
        return upcoming

    # ============================================================
    # DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=20)

        self.dashboard_title_label = ctk.CTkLabel(top_bar, text="Dashboard", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        self.dashboard_title_label.pack(side="left")

        self.clock_label = ctk.CTkLabel(top_bar, text="", font=("Segoe UI", 14, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right", padx=10)
        self.update_clock()

        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)

        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        hw_total = len(self.data["huiswerk"])
        cijfers = self.data["cijfers"]
        
        geldige_cijfers = []
        for c in cijfers:
            try:
                geldige_cijfers.append(float(c.get("cijfer", 0.0)))
            except ValueError: pass
            
        gem = sum(geldige_cijfers) / len(geldige_cijfers) if geldige_cijfers else None

        ctk.CTkLabel(card, text=f"📚 Huiswerk open: {hw_open}/{hw_total}", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(card, text=f"📊 Gemiddelde cijfers: {gem:.2f}" if gem is not None else "📊 Geen cijfers", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)

        card_vrij = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card_vrij.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(card_vrij, text="🎉 Vrije dagen & vakanties", font=("Segoe UI", 18, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))

        upcoming = self._get_upcoming_vrijedagen()
        if not upcoming:
            ctk.CTkLabel(card_vrij, text="Geen vrije dagen of vakanties ingevoerd.", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=10, pady=5)
        else:
            eerst_datum, eerst_delta, eerst_naam = upcoming[0]
            tekst = f"Vandaag ben je vrij: {eerst_naam}" if eerst_delta == 0 else f"Nog {eerst_delta} dag(en) tot: {eerst_naam} ({eerst_datum.strftime('%Y-%m-%d')})"
            ctk.CTkLabel(card_vrij, text=tekst, font=("Segoe UI", 14, "bold"), text_color=t["accent"]).pack(anchor="w", padx=10, pady=(5, 10))

            scroll_vrij = ctk.CTkScrollableFrame(card_vrij, fg_color="transparent")
            scroll_vrij.pack(fill="both", expand=True, padx=10, pady=5)

            for d, delta, naam in upcoming[:15]:
                regel = f"• {d.strftime('%Y-%m-%d')} - {naam} (" + ("vandaag!" if delta == 0 else f"over {delta} dagen") + ")"
                ctk.CTkLabel(scroll_vrij, text=regel, font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=1)

        version_label = ctk.CTkLabel(self.main, text=f"Versie: {HUIDIGE_VERSIE}", font=("Segoe UI", 11), text_color=t["text"])
        version_label.pack(side="bottom", anchor="e", padx=20, pady=10)
        self.apply_theme()

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            nu = dt.datetime.now()
            tijd_str = nu.strftime("%d-%m-%Y | %H:%M:%S")
            self.clock_label.configure(text=tijd_str)
            
            if self.dashboard_title_label and self.dashboard_title_label.winfo_exists():
                naam = self.data["settings"].get("naam", "").strip()
                naam_str = f" {naam}" if naam else ""
                uur = nu.hour
                if 6 <= uur < 12: begroeting = f"Goedemorgen{naam_str}!"
                elif 12 <= uur < 18: begroeting = f"Hoi{naam_str}!"
                elif 18 <= uur < 24: begroeting = f"Goedenavond{naam_str}!"
                else: begroeting = f"Goedenacht{naam_str}!"
                self.dashboard_title_label.configure(text=begroeting)

            self.after(1000, self.update_clock)

    # ============================================================
    # HUISWERK BEHEER
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerk", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.hw_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.hw_list.yview)
        sb.pack(side="right", fill="y")
        self.hw_list.config(yscrollcommand=sb.set)

        for h in self.data["huiswerk"]:
            self.hw_list.insert(tk.END, f"{'✔' if h.get('afgerond') else '✘'} {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Nieuw huiswerk", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=10, pady=5)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving")
        self.hw_beschrijving.pack(fill="x", padx=10, pady=5)

        self.hw_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.hw_datum.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(right_frame, text="📅 Kies datum", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=lambda: kies_datum(self.hw_datum)).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.hw_toevoegen).pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkButton(right_frame, text="Afronden", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.hw_afronden).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.hw_verwijderen).pack(fill="x", padx=10, pady=5)
        self.apply_theme()

    def hw_toevoegen(self):
        v, b, d = self.hw_vak.get(), self.hw_beschrijving.get().strip(), self.hw_datum.get().strip()
        if not b or not d: return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self.show_huiswerk()

    def hw_afronden(self):
        if not self.hw_list or not self.hw_list.curselection(): return
        self.data["huiswerk"][self.hw_list.curselection()[0]]["afgerond"] = True
        opslaan(self.data)
        self.show_huiswerk()

    def hw_verwijderen(self):
        if not self.hw_list or not self.hw_list.curselection(): return
        self.data["huiswerk"].pop(self.hw_list.curselection()[0])
        opslaan(self.data)
        self.show_huiswerk()

    # ============================================================
    # ROOSTER LOGICA (Gerepareerd & Volledig)
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 5))

        title_lbl = ctk.CTkLabel(top_bar, text="School Rooster", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        title_lbl.pack(side="left")

        stijl_btn_text = "➔ Toon Maandrooster" if self.rooster_stijl == "Week" else "➔ Toon Weekrooster"
        self.stijl_wissel_btn = ctk.CTkButton(top_bar, text=stijl_btn_text, fg_color=t["accent"], text_color="white", command=self.wissel_rooster_stijl)
        self.stijl_wissel_btn.pack(side="right", padx=5)

        nav_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(nav_bar, text="◀ Vorige", width=80, fg_color=t["button_fg"], text_color=t["button_text"], command=self.rooster_vorige).pack(side="left", padx=2)
        
        if self.rooster_stijl == "Week":
            start_week = self.huidige_rooster_datum - dt.timedelta(days=(self.huidige_rooster_datum.weekday() + 1) % 7)
            eind_week = start_week + dt.timedelta(days=6)
            midden_text = f"Weekoverzicht: {start_week.strftime('%d %b')} t/m {eind_week.strftime('%d %b %Y')}"
        else:
            midden_text = f"Maandoverzicht: {self.huidige_rooster_datum.strftime('%B %Y')}"

        self.rooster_datum_lbl = ctk.CTkLabel(nav_bar, text=midden_text, font=("Segoe UI", 14, "bold"), text_color=t["text"])
        self.rooster_datum_lbl.pack(side="left", expand=True)

        ctk.CTkButton(nav_bar, text="Volgende ▶", width=80, fg_color=t["button_fg"], text_color=t["button_text"], command=self.rooster_volgende).pack(side="right", padx=2)

        self.rooster_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.rooster_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.render_rooster_data()
        self.apply_theme()

    def wissel_rooster_stijl(self):
        self.rooster_stijl = "Maand" if self.rooster_stijl == "Week" else "Week"
        self.show_rooster()

    def rooster_vorige(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum -= dt.timedelta(days=7)
        else:
            self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=1) - dt.timedelta(days=1))
        self.show_rooster()

    def rooster_volgende(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum += dt.timedelta(days=7)
        else:
            self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
        self.show_rooster()

    def render_rooster_data(self):
        t = THEMES[self.theme_name]
        self.rooster_listbox = tk.Listbox(self.rooster_container, font=("Segoe UI", 11), activestyle="none")
        self.rooster_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Invoer interface voor rooster items
        input_frame = ctk.CTkFrame(self.rooster_container, width=250, fg_color=t["bg_card"])
        input_frame.pack(side="right", fill="y", padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Afspraak Toevoegen", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=10, padx=10)
        
        self.rooster_vak_entry = ctk.CTkEntry(input_frame, placeholder_text="Activiteit / Vak")
        self.rooster_vak_entry.pack(fill="x", padx=10, pady=5)

        self.rooster_tijd_entry = ctk.CTkEntry(input_frame, placeholder_text="Tijd (bijv. 09:00 - 10:30)")
        self.rooster_tijd_entry.pack(fill="x", padx=10, pady=5)

        self.rooster_datum_entry = ctk.CTkEntry(input_frame, placeholder_text="yyyy-mm-dd")
        self.rooster_datum_entry.pack(fill="x", padx=10, pady=5)
        self.rooster_datum_entry.insert(0, self.huidige_rooster_datum.strftime("%Y-%m-%d"))

        ctk.CTkButton(input_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.rooster_toevoegen).pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(input_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.rooster_verwijderen).pack(fill="x", padx=10, pady=2)

        # Laad data in de lijst op basis van geselecteerde view
        self.herlaad_rooster_items()

    def herlaad_rooster_items(self):
        self.rooster_listbox.delete(0, tk.END)
        for r in self.data.get("rooster", []):
            self.rooster_listbox.insert(tk.END, f"{r.get('datum')} | {r.get('tijd')} - {r.get('vak')}")

    def rooster_toevoegen(self):
        v = self.rooster_vak_entry.get().strip()
        t = self.rooster_tijd_entry.get().strip()
        d = self.rooster_datum_entry.get().strip()
        if not v or not t or not d: return
        
        self.data["rooster"].append({"vak": v, "tijd": t, "datum": d})
        opslaan(self.data)
        self.herlaad_rooster_items()
        self.rooster_vak_entry.delete(0, tk.END)
        self.rooster_tijd_entry.delete(0, tk.END)

    def rooster_verwijderen(self):
        if not self.rooster_listbox.curselection(): return
        idx = self.rooster_listbox.curselection()[0]
        self.data["rooster"].pop(idx)
        opslaan(self.data)
        self.herlaad_rooster_items()

    # ============================================================
    # NOTITIES LOGICA
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="🗒 Mijn Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.note_list = tk.Listbox(container, font=("Segoe UI", 11), activestyle="none")
        self.note_list.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.note_list.bind("<<ListboxSelect>>", self.laad_notitie_tekst)

        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], corner_radius=15)
        right_frame.pack(side="right", fill="both", expand=True)

        self.note_title_entry = ctk.CTkEntry(right_frame, placeholder_text="Titel van de notitie")
        self.note_title_entry.pack(fill="x", padx=15, pady=(15, 5))

        self.note_text_area = ctk.CTkTextbox(right_frame, font=("Segoe UI", 12))
        self.note_text_area.pack(fill="both", expand=True, padx=15, pady=5)

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(btn_frame, text="Opslaan", fg_color=t["accent"], text_color="white", command=self.notitie_opslaan).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Nieuw", fg_color=t["button_fg"], text_color=t["button_text"], command=self.notitie_nieuw).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.notitie_verwijderen).pack(side="right", padx=2)

        self.herlaad_notities()
        self.apply_theme()

    def herlaad_notities(self):
        self.note_list.delete(0, tk.END)
        for n in self.data.get("notities", []):
            self.note_list.insert(tk.END, n.get("titel", "Naamloze notitie"))

    def laad_notitie_tekst(self, event):
        if not self.note_list.curselection(): return
        idx = self.note_list.curselection()[0]
        note = self.data["notities"][idx]
        self.note_title_entry.delete(0, tk.END)
        self.note_title_entry.insert(0, note.get("titel", ""))
        self.note_text_area.delete("1.0", tk.END)
        self.note_text_area.insert("1.0", note.get("tekst", ""))

    def notitie_opslaan(self):
        titel = self.note_title_entry.get().strip()
        tekst = self.note_text_area.get("1.0", tk.END).strip()
        if not titel: return

        if self.note_list.curselection():
            idx = self.note_list.curselection()[0]
            self.data["notities"][idx] = {"titel": titel, "tekst": tekst}
        else:
            self.data["notities"].append({"titel": titel, "tekst": tekst})

        opslaan(self.data)
        self.herlaad_notities()
        self.notitie_nieuw()

    def notitie_nieuw(self):
        self.note_title_entry.delete(0, tk.END)
        self.note_text_area.delete("1.0", tk.END)
        self.note_list.selection_clear(0, tk.END)

    def notitie_verwijderen(self):
        if not self.note_list.curselection(): return
        idx = self.note_list.curselection()[0]
        self.data["notities"].pop(idx)
        opslaan(self.data)
        self.herlaad_notities()
        self.notitie_nieuw()

    # ============================================================
    # CIJFERS REGISTRATIE
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="📊 Mijn Cijferlijst", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.cijfer_list = tk.Listbox(container, font=("Segoe UI", 11), activestyle="none")
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_frame = ctk.CTkFrame(container, fg_color=t["bg_card"], width=260, corner_radius=15)
        right_frame.pack(side="right", fill="y")

        ctk.CTkLabel(right_frame, text="Cijfer Toevoegen", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(pady=10)
        
        self.c_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.c_vak.pack(fill="x", padx=15, pady=5)

        self.c_cijfer = ctk.CTkEntry(right_frame, placeholder_text="Cijfer (bijv. 7.5)")
        self.c_cijfer.pack(fill="x", padx=15, pady=5)

        self.c_periode = ctk.CTkComboBox(right_frame, values=self.periodes, state="readonly")
        self.c_periode.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.cijfer_verwijderen).pack(fill="x", padx=15, pady=2)

        self.herlaad_cijfers()
        self.apply_theme()

    def herlaad_cijfers(self):
        self.cijfer_list.delete(0, tk.END)
        for c in self.data.get("cijfers", []):
            self.cijfer_list.insert(tk.END, f"{c.get('vak')} - {c.get('periode')}: {c.get('cijfer')}")

    def cijfer_toevoegen(self):
        v = self.c_vak.get()
        c = self.c_cijfer.get().strip().replace(",", ".")
        p = self.c_periode.get()
        if not c: return

        try:
            val = float(c)
            if not (1.0 <= val <= 10.0): raise ValueError
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig getal in tussen 1.0 en 10.0")
            return

        self.data["cijfers"].append({"vak": v, "cijfer": c, "periode": p, "datum": dt.date.today().strftime("%Y-%m-%d")})
        opslaan(self.data)
        self.herlaad_cijfers()
        self.c_cijfer.delete(0, tk.END)

    def cijfer_verwijderen(self):
        if not self.cijfer_list.curselection(): return
        idx = self.cijfer_list.curselection()[0]
        self.data["cijfers"].pop(idx)
        opslaan(self.data)
        self.herlaad_cijfers()

    # ============================================================
    # INSTELLINGEN
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="⚙ Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        card = ctk.CTkFrame(self.main, fg_color=t["bg_card"], corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(card, text="Gebruikersprofiel aanpassen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.settings_name_entry = ctk.CTkEntry(card, placeholder_text="Jouw naam", width=300)
        self.settings_name_entry.pack(anchor="w", padx=20, pady=5)
        self.settings_name_entry.insert(0, self.data["settings"].get("naam", ""))

        ctk.CTkLabel(card, text="Systeemthema selecteren", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.theme_combo = ctk.CTkComboBox(card, values=list(THEMES.keys()), state="readonly", command=self.wissel_thema_event)
        self.theme_combo.pack(anchor="w", padx=20, pady=5)
        self.theme_combo.set(self.theme_name)

        ctk.CTkButton(card, text="Instellingen Opslaan", fg_color=t["accent"], text_color="white", command=self.instellingen_opslaan).pack(anchor="w", padx=20, pady=30)
        ctk.CTkButton(card, text="🔄 Handmatig controleren op updates", fg_color=t["button_fg"], text_color=t["button_text"], command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=20, pady=5)

        self.apply_theme()

    def wissel_thema_event(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.apply_theme()

    def instellingen_opslaan(self):
        self.data["settings"]["naam"] = self.settings_name_entry.get().strip()
        self.data["settings"]["theme"] = self.theme_name
        opslaan(self.data)
        messagebox.showinfo("Succes", "Jouw instellingen zijn succesvol opgeslagen!")

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
