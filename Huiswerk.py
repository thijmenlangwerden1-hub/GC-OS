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
# INSTELLINGEN & CONFIGURATIE
# ============================================================

HUIDIGE_VERSIE = "1.0.14"
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
        
        # Stijl 1 dagen: Zondag tot Zaterdag
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

        # Rooster navigatie variabelen
        self.rooster_stijl = "Week" # "Week" of "Maand"
        self.huidige_rooster_datum = dt.date.today()

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()

        self.after(100, self.show_intro_screen)
        self.after(2500, lambda: self.toon_update_laadbalk(silent=True))
        self.after(3000, self.check_na_update_log)

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
        intro = ctk.CTkToplevel(self)
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
                try:
                    self.state("zoomed")
                except Exception:
                    pass

        animate()

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
    # REVOLUTIONAIRE TWEE-STIJLEN ROOSTER SECTIE
    # ============================================================

    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        # Bovenste besturingsbalk
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 5))

        title_lbl = ctk.CTkLabel(top_bar, text="School Rooster", font=("Segoe UI", 24, "bold"), text_color=t["text"])
        title_lbl.pack(side="left")

        # Wisselknop tussen de twee stijlen
        stijl_btn_text = "➔ Toon Maandrooster" if self.rooster_stijl == "Week" else "➔ Toon Zondag-Zaterdag"
        self.stijl_wissel_btn = ctk.CTkButton(top_bar, text=stijl_btn_text, fg_color=t["accent"], text_color="white", command=self.wissel_rooster_stijl)
        self.stijl_wissel_btn.pack(side="right", padx=5)

        # Navigatiebalk voor weken/maanden
        nav_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(nav_bar, text="◀ Vorige", width=80, fg_color=t["button_fg"], text_color=t["button_text"], command=self.rooster_vorige).pack(side="left", padx=2)
        
        # Bereken huidige weergave titel string
        if self.rooster_stijl == "Week":
            start_week = self.huidige_rooster_datum - dt.timedelta(days=(self.huidige_rooster_datum.weekday() + 1) % 7) # Zondag
            eind_week = start_week + dt.timedelta(days=6) # Zaterdag
            midden_text = f"Weekoverzicht: {start_week.strftime('%d %b')} t/m {eind_week.strftime('%d %b %Y')}"
        else:
            midden_text = f"Maandoverzicht: {self.huidige_rooster_datum.strftime('%B %Y')}"

        self.rooster_datum_lbl = ctk.CTkLabel(nav_bar, text=midden_text, font=("Segoe UI", 14, "bold"), text_color=t["text"])
        self.rooster_datum_lbl.pack(side="left", expand=True)

        ctk.CTkButton(nav_bar, text="Volgende ▶", width=80, fg_color=t["button_fg"], text_color=t["button_text"], command=self.rooster_volgende).pack(side="right", padx=2)

        # Hoofdcontainer voor de weergave en invoer
        self.rooster_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.rooster_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Render de geselecteerde weergave stijl
        if self.rooster_stijl == "Week":
            self.render_week_rooster()
        else:
            self.render_maand_rooster()

        self.apply_theme()

    def wissel_rooster_stijl(self):
        self.rooster_stijl = "Maand" if self.rooster_stijl == "Week" else "Week"
        self.show_rooster()

    def rooster_vorige(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum -= dt.timedelta(days=7)
        else:
            # Terug naar vorige maand
            eerste_dag = self.huidige_rooster_datum.replace(day=1)
            self.huidige_rooster_datum = eerste_dag - dt.timedelta(days=1)
        self.show_rooster()

    def rooster_volgende(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum += dt.timedelta(days=7)
        else:
            # Naar volgende maand
            volgende_maand = self.huidige_rooster_datum.replace(day=28) + dt.timedelta(days=4)
            self.huidige_rooster_datum = volgende_maand.replace(day=1)
        self.show_rooster()

    # --------------------------------------------------------
    # STIJL 1: ZONDAG TOT ZATERDAG WEEK ROOSTER
    # --------------------------------------------------------
    def render_week_rooster(self):
        t = THEMES[self.theme_name]
        
        # Bereken de startdatum (Zondag) van deze week
        # In Python is .weekday() 0=Maandag...6=Zondag. We willen dat Zondag de start is.
        d_idx = (self.huidige_rooster_datum.weekday() + 1) % 7
        zondag_start = self.huidige_rooster_datum - dt.timedelta(days=d_idx)

        # Agenda grid frame
        grid_scroll = ctk.CTkScrollableFrame(self.rooster_container, fg_color="transparent")
        grid_scroll.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Bouw 7 kolommen voor Zondag t/m Zaterdag
        for i, dag_naam in enumerate(self.weekdagen_volledig):
            lus_datum = zondag_start + dt.timedelta(days=i)
            datum_str = lus_datum.strftime("%Y-%m-%d")

            # Kolom container
            kolom = ctk.CTkFrame(grid_scroll, fg_color=t["bg_card"], corner_radius=10)
            kolom.pack(fill="x", pady=4, padx=2)

            # Koptekst per dag
            is_vandaag = (lus_datum == dt.date.today())
            kop_kleur = t["accent"] if is_vandaag else t["text"]
            ctk.CTkLabel(kolom, text=f"{dag_naam} ({lus_datum.strftime('%d-%m')})", font=("Segoe UI", 13, "bold"), text_color=kop_kleur).pack(anchor="w", padx=10, pady=5)

            # Zoek afspraken voor deze dag
            dag_items = [r for r in self.data["rooster"] if r.get("datum") == datum_str]
            dag_items.sort(key=lambda x: x.get("tijd", ""))

            if not dag_items:
                ctk.CTkLabel(kolom, text="Geen lessen of afspraken", font=("Segoe UI", 11), text_color="gray").pack(anchor="w", padx=20, pady=2)
            else:
                for item in dag_items:
                    item_str = f"🕒 {item.get('tijd')} | {item.get('vak')} [{item.get('lokaal')}]"
                    lbl = ctk.CTkLabel(kolom, text=item_str, font=("Segoe UI", 12), text_color=t["text"])
                    lbl.pack(anchor="w", padx=20, pady=2)

        # Rechter paneel voor beheer/handmatige invoer
        self.render_rooster_beheer_paneel(self.rooster_container, t)

    # --------------------------------------------------------
    # STIJL 2: MAANDROOSTER MET GROTE BLOKKEN EN AFSPRAKEN
    # --------------------------------------------------------
    def render_maand_rooster(self):
        t = THEMES[self.theme_name]

        # Hoofdframe voor kalender grid
        kalender_frame = ctk.CTkFrame(self.rooster_container, fg_color=t["bg_card"], corner_radius=15)
        kalender_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=2)

        # Dagen van de week koppen boven het maandrooster
        for col, dag_naam in enumerate(self.weekdagen_volledig):
            kalender_frame.grid_columnconfigure(col, weight=1, uniform="equal")
            ctk.CTkLabel(kalender_frame, text=dag_naam[:2], font=("Segoe UI", 12, "bold"), text_color=t["accent"]).grid(row=0, column=col, pady=5)

        # Bereken kalender datums van de geselecteerde maand
        eerste_dag_maand = self.huidige_rooster_datum.replace(day=1)
        # Bepaal hoeveel dagen we terug moeten om op de start-zondag te komen
        start_afwijking = (eerste_dag_maand.weekday() + 1) % 7
        start_kalender_datum = eerste_dag_maand - dt.timedelta(days=start_afwijking)

        # Genereer 6 rijen aan data (standaard matrix grootte voor kalenders)
        for row in range(1, 7):
            kalender_frame.grid_rowconfigure(row, weight=1, uniform="equal")
            for col in range(7):
                cel_datum = start_kalender_datum + dt.timedelta(days=((row - 1) * 7) + col)
                cel_datum_str = cel_datum.strftime("%Y-%m-%d")

                # Is deze cel van de huidige maand of aangrenzend?
                in_maand = (cel_datum.month == self.huidige_rooster_datum.month)
                
                # Frame voor de dag-cel
                cel_bg = t["bg_root"] if in_maand else t["bg_card"]
                if cel_datum == dt.date.today():
                    cel_border = t["accent"]
                    border_w = 2
                else:
                    cel_border = t["button_hover"]
                    border_w = 1

                cel = ctk.CTkFrame(kalender_frame, fg_color=cel_bg, border_color=cel_border, border_width=border_w, corner_radius=6)
                cel.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

                # Dagcijfer label
                tekst_kleur = t["text"] if in_maand else "gray"
                ctk.CTkLabel(cel, text=str(cel_datum.day), font=("Segoe UI", 11, "bold"), text_color=tekst_kleur).pack(anchor="nw", padx=5, pady=2)

                # Haal afspraken/rooster op voor deze specifieke dag
                items = [r for r in self.data["rooster"] if r.get("datum") == cel_datum_str]
                
                if items:
                    # Scrollable container binnen de cel zodat alles past en leesbaar blijft
                    cel_scroll = ctk.CTkScrollableFrame(cel, fg_color="transparent", header_name="", corner_radius=0)
                    cel_scroll.pack(fill="both", expand=True, padx=2, pady=2)
                    
                    for item in items[:4]: # Maximaal 4 compacte weergaven tonen direct in overzicht
                        item_tekst = f"{item.get('tijd')} {item.get('vak')}"
                        lbl = ctk.CTkLabel(cel_scroll, text=item_tekst, font=("Segoe UI", 9), text_color=t["text"], anchor="w", height=14)
                        lbl.pack(fill="x", anchor="w")

        # Rechter paneel voor beheer/handmatige invoer
        self.render_rooster_beheer_paneel(self.rooster_container, t)

    def render_rooster_beheer_paneel(self, container, t):
        right_frame = ctk.CTkFrame(container, width=240, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Afspraak Toevoegen", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.rst_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.rst_vak.set(self.vakken_hw[0])
        self.rst_vak.pack(fill="x", padx=10, pady=4)

        self.rst_lokaal = ctk.CTkEntry(right_frame, placeholder_text="Lokaal (bijv. B204)")
        self.rst_lokaal.pack(fill="x", padx=10, pady=4)

        self.rst_tijd = ctk.CTkEntry(right_frame, placeholder_text="Tijd (bijv. 09:15)")
        self.rst_tijd.pack(fill="x", padx=10, pady=4)

        self.rst_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.rst_datum.pack(fill="x", padx=10, pady=4)
        self.rst_datum.insert(0, self.huidige_rooster_datum.strftime("%Y-%m-%d"))

        ctk.CTkButton(right_frame, text="📅 Kies Datum", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=lambda: kies_datum(self.rst_datum)).pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(right_frame, text="Opslaan in Rooster", fg_color=t["accent"], text_color="white", command=self.rooster_item_toevoegen).pack(fill="x", padx=10, pady=(10, 15))

        # Lijst om huidige items te bekijken en te deleten
        ctk.CTkLabel(right_frame, text="Alle Afspraken", font=("Segoe UI", 13, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=2)
        
        self.rooster_listbox = tk.Listbox(right_frame, font=("Segoe UI", 10), activestyle="none")
        self.rooster_listbox.pack(fill="both", expand=True, padx=10, pady=4)

        # Sorteer en laad alle afspraken in listbox
        rooster_gesorteerd = sorted(self.data["rooster"], key=lambda x: (x.get("datum", ""), x.get("tijd", "")))
        for r in rooster_gesorteerd:
            self.rooster_listbox.insert(tk.END, f"{r.get('datum')} {r.get('tijd')} - {r.get('vak')}")

        ctk.CTkButton(right_frame, text="Geselecteerde Wissen", fg_color="#ff3b30" if "Dark" in t["mode"] else "#ff3b30", text_color="white", command=lambda: self.rooster_item_verwijderen(rooster_gesorteerd)).pack(fill="x", padx=10, pady=10)

    def rooster_item_toevoegen(self):
        v, l, tj, dt_str = self.rst_vak.get(), self.rst_lokaal.get().strip(), self.rst_tijd.get().strip(), self.rst_datum.get().strip()
        if not l or not tj or not dt_str:
            messagebox.showwarning("Invoer incompleet", "Vul alstublieft alle velden in.")
            return
        
        self.data["rooster"].append({
            "vak": v,
            "lokaal": l,
            "tijd": tj,
            "datum": dt_str
        })
        opslaan(self.data)
        self.show_rooster()

    def rooster_item_verwijderen(self, gesorteerde_lijst):
        if not self.rooster_listbox or not self.rooster_listbox.curselection(): return
        geselecteerd_item = gesorteerde_lijst[self.rooster_listbox.curselection()[0]]
        
        # Verwijder uit de originele database list
        self.data["rooster"].remove(geselecteerd_item)
        opslaan(self.data)
        self.show_rooster()

    # --------------------------------------------------------
    # VIEWS: NOTITIES
    # --------------------------------------------------------

    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.note_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.note_list.bind("<<ListboxSelect>>", self.note_selecteren)

        sb = tk.Scrollbar(left_frame, command=self.note_list.yview)
        sb.pack(side="right", fill="y")
        self.note_list.config(yscrollcommand=sb.set)

        for n in self.data["notities"]:
            self.note_list.insert(tk.END, n.get("titel", "Naamloos"))

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.note_title = ctk.CTkEntry(right_frame, placeholder_text="Titel van de notitie", font=("Segoe UI", 14, "bold"))
        self.note_title.pack(fill="x", padx=15, pady=(15, 5))

        self.note_text = ctk.CTkTextbox(right_frame, font=("Segoe UI", 12))
        self.note_text.pack(fill="both", expand=True, padx=15, pady=5)

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(btn_frame, text="Opslaan", fg_color=t["accent"], text_color="white", command=self.note_opslaan).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Nieuw", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.note_nieuw).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Verwijderen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.note_verwijderen).pack(side="right", padx=5)

        self.apply_theme()

    def note_selecteren(self, event):
        if not self.note_list or not self.note_list.curselection(): return
        idx = self.note_list.curselection()[0]
        n = self.data["notities"][idx]
        self.note_title.delete(0, tk.END)
        self.note_title.insert(0, n.get("titel", ""))
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", n.get("inhoud", ""))

    def note_opslaan(self):
        titel = self.note_title.get().strip()
        inhoud = self.note_text.get("1.0", tk.END).strip()
        if not titel: return

        if self.note_list and self.note_list.curselection():
            idx = self.note_list.curselection()[0]
            self.data["notities"][idx] = {"titel": titel, "inhoud": inhoud}
        else:
            self.data["notities"].append({"titel": titel, "inhoud": inhoud})

        opslaan(self.data)
        self.show_notities()

    def note_nieuw(self):
        self.note_title.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)
        if self.note_list: self.note_list.selection_clear(0, tk.END)

    def note_verwijderen(self):
        if not self.note_list or not self.note_list.curselection(): return
        self.data["notities"].pop(self.note_list.curselection()[0])
        opslaan(self.data)
        self.show_notities()

    # --------------------------------------------------------
    # VIEWS: CIJFERS
    # --------------------------------------------------------

    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="Cijferregistratie", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.cijfer_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.cijfer_list.yview)
        sb.pack(side="right", fill="y")
        self.cijfer_list.config(yscrollcommand=sb.set)

        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f"[{c.get('periode', 'Periode 1')}] {c.get('vak')} - Cijfer: {c.get('cijfer')} (Weging: {c.get('weging')}x)")

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Nieuw cijfer", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.cijfer_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.cijfer_vak.set(self.vakken_hw[0])
        self.cijfer_vak.pack(fill="x", padx=10, pady=5)

        self.cijfer_val = ctk.CTkEntry(right_frame, placeholder_text="Cijfer (bijv. 7.5)")
        self.cijfer_val.pack(fill="x", padx=10, pady=5)

        self.cijfer_weging = ctk.CTkEntry(right_frame, placeholder_text="Weging (bijv. 1)")
        self.cijfer_weging.pack(fill="x", padx=10, pady=5)

        self.cijfer_periode = ctk.CTkComboBox(right_frame, values=self.periodes, state="readonly")
        self.cijfer_periode.set(self.periodes[0])
        self.cijfer_periode.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.cijfer_toevoegen).pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.cijfer_verwijderen).pack(fill="x", padx=10, pady=5)

        self.apply_theme()

    def cijfer_toevoegen(self):
        v, c, w, p = self.cijfer_vak.get(), self.cijfer_val.get().strip(), self.cijfer_weging.get().strip(), self.cijfer_periode.get()
        if not c or not w: return
        self.data["cijfers"].append({"vak": v, "cijfer": c, "weging": w, "periode": p, "datum": dt.date.today().strftime("%Y-%m-%d")})
        opslaan(self.data)
        self.show_cijfers()

    def cijfer_verwijderen(self):
        if not self.cijfer_list or not self.cijfer_list.curselection(): return
        self.data["cijfers"].pop(self.cijfer_list.curselection()[0])
        opslaan(self.data)
        self.show_cijfers()

    # --------------------------------------------------------
    # VIEWS: INSTELLINGEN
    # --------------------------------------------------------

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Card: Profiel
        card_p = ctk.CTkFrame(scroll, corner_radius=15, fg_color=t["bg_card"])
        card_p.pack(fill="x", pady=10)
        ctk.CTkLabel(card_p, text="Persoonlijke instellingen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.settings_name = ctk.CTkEntry(card_p, placeholder_text="Jouw naam voor de begroeting")
        self.settings_name.pack(fill="x", padx=15, pady=5)
        self.settings_name.insert(0, self.data["settings"].get("naam", ""))

        ctk.CTkButton(card_p, text="Naam Opslaan", fg_color=t["accent"], text_color="white", command=self.save_name_setting).pack(anchor="w", padx=15, pady=(5, 15))

        # Card: Thema
        card_t = ctk.CTkFrame(scroll, corner_radius=15, fg_color=t["bg_card"])
        card_t.pack(fill="x", pady=10)
        ctk.CTkLabel(card_t, text="Systeemthema selecteren", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))

        self.theme_combo = ctk.CTkComboBox(card_t, values=list(THEMES.keys()), command=self.change_theme_setting)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=15, pady=(5, 15))

        # Card: Vrije Dagen Beheer
        card_v = ctk.CTkFrame(scroll, corner_radius=15, fg_color=t["bg_card"])
        card_v.pack(fill="x", pady=10)
        ctk.CTkLabel(card_v, text="Vrije dagen & Vakanties aanpassen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))

        v_container = ctk.CTkFrame(card_v, fg_color="transparent")
        v_container.pack(fill="x", padx=15, pady=5)

        self.vrijedagen_listbox = tk.Listbox(v_container, font=("Segoe UI", 10), height=6, activestyle="none")
        self.vrijedagen_listbox.pack(side="left", fill="both", expand=True)

        v_sb = tk.Scrollbar(v_container, command=self.vrijedagen_listbox.yview)
        v_sb.pack(side="right", fill="y")
        self.vrijedagen_listbox.config(yscrollcommand=v_sb.set)

        self._herlaad_vrijedagen_listbox()

        f_invoer = ctk.CTkFrame(card_v, fg_color="transparent")
        f_invoer.pack(fill="x", padx=15, pady=5)

        self.vrij_naam = ctk.CTkEntry(f_invoer, placeholder_text="Naam (bijv. Kerstmis)")
        self.vrij_naam.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.vrij_datum = ctk.CTkEntry(f_invoer, placeholder_text="yyyy-mm-dd")
        self.vrij_datum.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(f_invoer, text="📅", width=35, fg_color=t["button_fg"], text_color=t["button_text"], command=lambda: kies_datum(self.vrij_datum)).pack(side="left", padx=5)

        btn_v_frame = ctk.CTkFrame(card_v, fg_color="transparent")
        btn_v_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(btn_v_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.vrijedag_toevoegen).pack(side="left", padx=5)
        ctk.CTkButton(btn_v_frame, text="Geselecteerde Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], command=self.vrijedag_verwijderen).pack(side="right", padx=5)

        # Card: Info & Update Handmatig
        card_i = ctk.CTkFrame(scroll, corner_radius=15, fg_color=t["bg_card"])
        card_i.pack(fill="x", pady=10)
        ctk.CTkLabel(card_i, text="Over GraafschapCollege-OS", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(card_i, text=f"Huidige softwareversie: v{HUIDIGE_VERSIE}\nOntwikkeld voor studenten van het Graafschap College.", justify="left", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(card_i, text="🔄 Nu Controleren Op Updates", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=15, pady=(5, 15))

        self.apply_theme()

    def _herlaad_vrijedagen_listbox(self):
        if not self.vrijedagen_listbox: return
        self.vrijedagen_listbox.delete(0, tk.END)
        gesorteerd = sorted(self.data["vrijedagen"], key=lambda x: x.get("datum", ""))
        for v in gesorteerd:
            self.vrijedagen_listbox.insert(tk.END, f"{v.get('datum')} - {v.get('naam')}")

    def vrijedag_toevoegen(self):
        n, d = self.vrij_naam.get().strip(), self.vrij_datum.get().strip()
        if not n or not d: return
        self.data["vrijedagen"].append({"naam": n, "datum": d})
        opslaan(self.data)
        self._herlaad_vrijedagen_listbox()
        self.vrij_naam.delete(0, tk.END)
        self.vrij_datum.delete(0, tk.END)

    def vrijedag_verwijderen(self):
        if not self.vrijedagen_listbox or not self.vrijedagen_listbox.curselection(): return
        idx = self.vrijedagen_listbox.curselection()[0]
        gesorteerd = sorted(self.data["vrijedagen"], key=lambda x: x.get("datum", ""))
        verwijderd_item = gesorteerd[idx]
        
        self.data["vrijedagen"].remove(verwijderd_item)
        opslaan(self.data)
        self._herlaad_vrijedagen_listbox()

    def save_name_setting(self):
        naam = self.settings_name.get().strip()
        self.data["settings"]["naam"] = naam
        opslaan(self.data)
        messagebox.showinfo("Opgeslagen", "Je naam is succesvol bijgewerkt op het dashboard!")

    def change_theme_setting(self, gekozen_thema):
        if gekozen_thema in THEMES:
            self.theme_name = gekozen_thema
            self.data["settings"]["theme"] = gekozen_thema
            opslaan(self.data)
            self.apply_theme()
            self.show_settings()

# ============================================================
# APPLICATIE STARTEN
# ============================================================

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
