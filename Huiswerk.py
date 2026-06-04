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
        "button_fg": "#bideecb",
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

HUIDIGE_VERSIE = "1.0.11"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/version.txt"
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
            "settings": {"theme": "Wit"},
            "vrijedagen": [],
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data: data["rooster"] = []
    if "settings" not in data: data["settings"] = {"theme": "Wit"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
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
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan"
        ]
        
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]

        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None

        self.theme_combo = None
        self.vrijedagen_listbox = None
        self.clock_label = None

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()

        self.after(100, self.show_intro_screen)
        self.after(2500, lambda: self.toon_update_laadbalk(silent=True))
        
        # Controleer direct na opstarten of er een verse changelog klaarstaat
        self.after(3000, self.check_na_update_log)

    # --------------------------------------------------------
    # UPDATE LOG DETECTIE & POP-UP (ALLEEN NIEUWE VERSIE)
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
        log_win.title(f"✨ Update Succesvol!")
        log_win.geometry("500x400")
        log_win.resizable(False, False)
        log_win.configure(fg_color=t["bg_card"])
        log_win.grab_set()

        log_win.update_idletasks()
        x = (log_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (log_win.winfo_screenheight() // 2) - (400 // 2)
        log_win.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            log_win, 
            text="🎉 Update succesvol geïnstalleerd!", 
            font=("Segoe UI", 18, "bold"), 
            text_color=t["accent"]
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            log_win, 
            text="Dit is er nieuw in deze versie:", 
            font=("Segoe UI", 13), 
            text_color=t["text"]
        ).pack(pady=(0, 15))

        txt_frame = ctk.CTkScrollableFrame(log_win, width=440, height=220, fg_color=t["bg_root"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(
            txt_frame, 
            text=log_tekst.strip(), 
            font=("Segoe UI", 12), 
            justify="left", 
            text_color=t["text"],
            anchor="w"
        ).pack(anchor="w", padx=10, pady=10)

        ctk.CTkButton(
            log_win, 
            text="Sluiten & Ontdekken", 
            fg_color=t["accent"], 
            text_color="white", 
            command=log_win.destroy
        ).pack(pady=20)

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

        start_size = 10
        end_size = 60
        current_size = start_size

        label = ctk.CTkLabel(
            intro,
            text="GraafschapCollege‑OS",
            font=("Segoe UI", current_size, "bold"),
            text_color=t["accent"],
        )
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

    # --------------------------------------------------------
    # LAADBALKJE VOOR UPDATES
    # --------------------------------------------------------

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

        status_lbl = ctk.CTkLabel(
            up_win, 
            text="🔄 Controleren op beschikbare updates...", 
            font=("Segoe UI", 15, "bold"), 
            text_color=t["text"]
        )
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

                ctk.CTkButton(
                    knop_frame, 
                    text="📥 Download & Installeer", 
                    fg_color=t["accent"], 
                    text_color="white", 
                    command=lambda: self.voer_update_uit(up_win, status_lbl)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    knop_frame, 
                    text="Later", 
                    fg_color=t["button_fg"], 
                    text_color=t["button_text"], 
                    command=up_win.destroy
                ).pack(side="right", padx=5)

        laad_stap()

    # --------------------------------------------------------
    # DOWNLOAD SCRIPT & DOWNLOAD SPECIFIEKE CHANGELOG
    # --------------------------------------------------------

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
            
            if os.name == 'nt':  # Windows
                cmd = f'timeout /t 1 > nul && move /Y "{temp_file}" "{huidige_script}" && start "" "{sys.executable}" "{huidige_script}"'
                subprocess.Popen(cmd, shell=True)
            else:  # Mac / Linux
                cmd = f'sleep 1 && mv -f "{temp_file}" "{huidige_script}" && "{sys.executable}" "{huidige_script}" &'
                subprocess.Popen(cmd, shell=True)
                
            self.destroy()
            sys.exit()
            
        except Exception as e:
            status_lbl.configure(text="❌ Update mislukt!")
            messagebox.showerror("Fout bij updaten", f"Er is een fout opgetreden tijdens het updaten:\n{e}")

    # --------------------------------------------------------
    # THEMA TOEPASSEN
    # --------------------------------------------------------

    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])

        if hasattr(self, "sidebar"): self.sidebar.configure(fg_color=t["bg_sidebar"])
        if hasattr(self, "main"): self.main.configure(fg_color=t["bg_main"])

        for btn in self.sidebar_buttons:
            try:
                btn.configure(
                    fg_color="transparent",
                    hover_color=t["button_hover"],
                    text_color=t["sidebar_text"],
                )
            except Exception: pass

        for lst in [self.hw_list, self.note_list, self.cijfer_list, self.vrijedagen_listbox]:
            if lst is not None:
                lst.configure(
                    bg=t["list_bg"], fg=t["list_fg"],
                    selectbackground=t["list_select"],
                    highlightthickness=0, borderwidth=0,
                )

        if self.theme_combo is not None:
            try:
                self.theme_combo.configure(
                    fg_color=t["button_fg"], border_color=t["accent"],
                    button_color=t["accent"], button_hover_color=t["button_hover"],
                    text_color=t["button_text"],
                )
            except Exception: pass

    # --------------------------------------------------------
    # LAYOUT BOUWEN
    # --------------------------------------------------------

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
        self.vrijedagen_listbox = None
        self.theme_combo = None
        self.clock_label = None

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

    # --------------------------------------------------------
    # VIEWS: DASHBOARD
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
            self.after(1000, self.update_clock)

    # --------------------------------------------------------
    # VIEWS: HUISWERK
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # VIEWS: ROOSTER & NOTITIES
    # --------------------------------------------------------

    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Rooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(card, text="(Hier kun je later een rooster toevoegen)", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=15, pady=15)
        self.apply_theme()

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

        for n in self.data["notities"]: self.note_list.insert(tk.END, n)

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        self.note_input = ctk.CTkEntry(right_frame, placeholder_text="Nieuwe notitie")
        self.note_input.pack(fill="x", padx=10, pady=15)

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.note_toevoegen).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.note_verwijderen).pack(fill="x", padx=10, pady=5)
        self.apply_theme()

    def note_toevoegen(self):
        txt = self.note_input.get().strip()
        if not txt: return
        self.data["notities"].append(txt)
        opslaan(self.data)
        self.show_notities()

    def note_verwijderen(self):
        if not self.note_list or not self.note_list.curselection(): return
        self.data["notities"].pop(self.note_list.curselection()[0])
        opslaan(self.data)
        self.show_notities()

    # --------------------------------------------------------
    # VIEWS: CIJFERS & SETTINGS
    # --------------------------------------------------------

    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="Cijfers", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

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
            self.cijfer_list.insert(tk.END, f"{c.get('periode')} | {c.get('vak')}: {c.get('cijfer')} ({c.get('datum')})")

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Nieuw cijfer", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.cijfer_periode = ctk.CTkComboBox(right_frame, values=self.periodes, state="readonly")
        self.cijfer_periode.set(self.periodes[0])
        self.cijfer_periode.pack(fill="x", padx=10, pady=5)

        self.cijfer_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.cijfer_vak.set(self.vakken_hw[0])
        self.cijfer_vak.pack(fill="x", padx=10, pady=5)

        self.cijfer_waarde = ctk.CTkEntry(right_frame, placeholder_text="Cijfer (bv. 7.5)")
        self.cijfer_waarde.pack(fill="x", padx=10, pady=5)

        self.cijfer_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.cijfer_datum.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.cijfer_toevoegen).pack(fill="x", padx=10, pady=10)
        self.apply_theme()

    def cijfer_toevoegen(self):
        p, v, w, d = self.cijfer_periode.get(), self.cijfer_vak.get(), self.cijfer_waarde.get().strip(), self.cijfer_datum.get().strip()
        if not w or not d: return
        self.data["cijfers"].append({"periode": p, "vak": v, "cijfer": w, "datum": d})
        opslaan(self.data)
        self.show_cijfers()

    # --------------------------------------------------------
    # INSTELLEN & THEMA KIEZEN + HANDMATIG UPDATEN
    # --------------------------------------------------------

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        
        # 1. KAART VOOR THEMA SELECTIE
        theme_card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        theme_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(theme_card, text="🎨 Systeemthema aanpassen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.theme_combo = ctk.CTkComboBox(theme_card, values=list(THEMES.keys()), command=self.wijzig_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=15, pady=(5, 15))
        
        # 2. NIEUWE KAART VOOR HANDMATIGE UPDATES
        update_card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        update_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(update_card, text="🔄 GC-OS Systeemupdates", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            update_card, 
            text=f"Huidig geïnstalleerde versie: v{HUIDIGE_VERSIE}\nJe kunt hier handmatig controleren of er een nieuwere versie op GitHub staat.", 
            font=("Segoe UI", 13), 
            justify="left",
            text_color=t["text"]
        ).pack(anchor="w", padx=15, pady=5)
        
        # Knop die de update checker geforceerd/niet-silent start
        ctk.CTkButton(
            update_card, 
            text="🔄 Handmatig zoeken naar updates", 
            fg_color=t["accent"], 
            text_color="white", 
            command=lambda: self.toon_update_laadbalk(silent=False)
        ).pack(anchor="w", padx=15, pady=(10, 15))
        
        self.apply_theme()

    def wijzig_thema(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
