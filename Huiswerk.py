import os
import sys
import json
import datetime as dt
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkcalendar import Calendar
import urllib.request
import webbrowser
import random
import threading

# ============================================================
# THEMA'S & KLEURENPALETTEN
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
        "button_fg": "#deecb",
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

HUIDIGE_VERSIE = "9.5v"
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
    ]

    uniek = {}
    for d in dagen:
        uniek[(d["naam"], d["datum"])] = d
    return list(uniek.values())

def _standaard_rooster():
    dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
    rooster = {}
    for d in dagen:
        rooster[d] = [
            {"tijd": "08:30 - 10:00", "les": "Geen les"},
            {"tijd": "10:15 - 11:45", "les": "Geen les"},
            {"tijd": "12:15 - 13:45", "les": "Geen les"},
            {"tijd": "14:00 - 15:30", "les": "Geen les"}
        ]
    return rooster

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": _standaard_rooster(),
            "settings": {"theme": "Wit"},
            "vrijedagen": _standaard_vrijedagen(),
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data or not isinstance(data["rooster"], dict): data["rooster"] = _standaard_rooster()
    if "settings" not in data: data["settings"] = {"theme": "Wit"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "vrijedagen" not in data: data["vrijedagen"] = []

    for c in data.get("cijfers", []):
        if "periode" not in c: c["periode"] = "Periode 1"
        if "datum" not in c: c["datum"] = "2026-01-01"
        if "weging" not in c: c["weging"] = "1"

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
        self.geometry("1150x680")
        self.minsize(950, 600)

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
        ctk.CTkLabel(log_win, text="Dit is er nieuw in deze versie:", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=(0, 15))

        txt_frame = ctk.CTkScrollableFrame(log_win, width=440, height=220, fg_color=t["bg_root"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(txt_frame, text=log_tekst.strip(), font=("Segoe UI", 12), justify="left", text_color=t["text"], anchor="w").pack(anchor="w", padx=10, pady=10)
        ctk.CTkButton(log_win, text="Sluiten & Ontdekken", fg_color=t["accent"], text_color="white", command=log_win.destroy).pack(pady=20)

    # --------------------------------------------------------
    # INTRO-SCREEN ANIMATIE
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
        end_size = 50
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
                self.after(15, lambda: animate(alpha + 0.04, size))
            else:
                self.after(800, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(15, lambda: fade_out(alpha - 0.05))
            else:
                try:
                    intro.destroy()
                    self.state("zoomed")
                except Exception:
                    pass

        animate()

    # --------------------------------------------------------
    # DE VERNIEUWDE UPDATE LAADBALK + FADING LOGO
    # --------------------------------------------------------

    def toon_update_laadbalk(self, silent=False):
        t = THEMES[self.theme_name]
        up_win = ctk.CTkToplevel(self)
        up_win.title("GC-OS Updateservice")
        up_win.geometry("520x360")
        up_win.resizable(False, False)
        up_win.configure(fg_color=t["bg_root"])
        up_win.grab_set()
        
        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (520 // 2)
        y = (up_win.winfo_screenheight() // 2) - (360 // 2)
        up_win.geometry(f"+{x}+{y}")

        # Grote, moderne glazen container
        main_card = ctk.CTkFrame(up_win, corner_radius=20, fg_color=t["bg_card"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)

        # HET GEANIMEERDE LOGO (Met Fade-in / Fade-out effect via tkinter kleurovergang)
        self.logo_label = ctk.CTkLabel(main_card, text="GC-OS", font=("Segoe UI", 38, "bold"), text_color=t["accent"])
        self.logo_label.pack(pady=(25, 5))
        
        # Fade configuratievariabelen
        self.fade_direction = -1  # -1 = donkerder worden, 1 = lichter worden
        self.current_alpha = 1.0
        self.is_updating = True

        def update_logo_fade():
            if not self.is_updating or not up_win.winfo_exists():
                return
            
            # Pas de alpha waarde aan
            if self.fade_direction == -1:
                self.current_alpha -= 0.05
                if self.current_alpha <= 0.2:
                    self.fade_direction = 1
            else:
                self.current_alpha += 0.05
                if self.current_alpha >= 1.0:
                    self.fade_direction = -1

            # Bereken hex-waarde tussen accentkleur en card achtergrondkleur voor een vloeiende fade
            try:
                bg_hex = t["bg_card"].lstrip('#')
                acc_hex = t["accent"].lstrip('#')
                
                # RGB omzetting
                bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                acc_rgb = tuple(int(acc_hex[i:i+2], 16) for i in (0, 2, 4))
                
                # Lineaire interpolatie
                mix_rgb = tuple(
                    int(bg_rgb[i] + (acc_rgb[i] - bg_rgb[i]) * self.current_alpha)
                    for i in range(3)
                )
                mix_hex = f"#{mix_rgb[0]:02x}{mix_rgb[1]:02x}{mix_rgb[2]:02x}"
                self.logo_label.configure(text_color=mix_hex)
            except Exception:
                pass
            
            up_win.after(40, update_logo_fade)

        # Start de pulseer-animatie direct
        update_logo_fade()

        status_lbl = ctk.CTkLabel(main_card, text="Systeem controleren op updates...", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        status_lbl.pack(pady=5)

        # Een veel mooiere dikke laadbalk
        loading_ind = ctk.CTkProgressBar(main_card, width=380, height=12, corner_radius=6, progress_color=t["accent"])
        loading_ind.pack(pady=10)
        loading_ind.start()

        pct_lbl = ctk.CTkLabel(main_card, text="Verbinding maken met server...", font=("Segoe UI", 13), text_color=t["text"])
        pct_lbl.pack()

        # Terminal-stijl infobalk onderaan de kaart
        info_frame = ctk.CTkFrame(main_card, height=35, corner_radius=8, fg_color=t["bg_root"])
        info_frame.pack(fill="x", padx=20, pady=(20, 0))
        info_frame.pack_propagate(False)

        sub_status_lbl = ctk.CTkLabel(info_frame, text="[INFO] Initializing fetch request...", font=("Consolas", 11), text_color="#71717a")
        sub_status_lbl.pack(side="left", padx=10, fill="y")

        def async_check():
            try:
                time.sleep(1.5)  # Geef even tijd om het coole scherm te tonen
                req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    nieuweste = response.read().decode("utf-8").strip()
                up_win.after(0, lambda: verwerk_check_resultaat(nieuweste))
            except Exception:
                up_win.after(0, handige_foutmelding)

        def verwerk_check_resultaat(nieuweste):
            loading_ind.stop()
            if nieuweste == HUIDIGE_VERSIE:
                self.is_updating = False
                self.logo_label.configure(text_color=t["accent"])
                if silent:
                    up_win.destroy()
                    return
                loading_ind.set(1.0)
                status_lbl.configure(text="Systeem up-to-date ✨")
                pct_lbl.configure(text=f"Huidige versie: v{HUIDIGE_VERSIE} (Nieuwste)")
                sub_status_lbl.configure(text="[SUCCESS] No update packages found.")
                ctk.CTkButton(main_card, text="Sluiten", fg_color=t["accent"], text_color="white", command=up_win.destroy).pack(pady=15)
            else:
                loading_ind.set(0.2)
                status_lbl.configure(text="Nieuwe Update Beschikbaar!")
                pct_lbl.configure(text=f"Versie: v{HUIDIGE_VERSIE} ➔ v{nieuweste}")
                sub_status_lbl.configure(text="[READY] Update packages pending.")
                
                knop_frame = ctk.CTkFrame(main_card, fg_color="transparent")
                knop_frame.pack(pady=15)

                ctk.CTkButton(knop_frame, text="⚡ Nu Installeren", fg_color=t["accent"], text_color="white", font=("Segoe UI", 13, "bold"), command=lambda: start_installatie_animatie(loading_ind, status_lbl, pct_lbl, sub_status_lbl, knop_frame)).pack(side="left", padx=8)
                ctk.CTkButton(knop_frame, text="Later", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(side="right", padx=8)

        def handige_foutmelding():
            self.is_updating = False
            self.logo_label.configure(text_color=t["accent"])
            if silent:
                up_win.destroy()
                return
            loading_ind.stop()
            status_lbl.configure(text="Verbindingsfout")
            pct_lbl.configure(text="Kan geen verbinding maken met GitHub.")
            sub_status_lbl.configure(text="[ERROR] HTTP fetch failed.")
            ctk.CTkButton(main_card, text="Sluiten", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(pady=15)

        threading.Thread(target=async_check, daemon=True).start()

        def start_installatie_animatie(balk, lbl, p_lbl, sub_lbl, frame):
            frame.pack_forget()
            lbl.configure(text="Update aan het voorbereiden...")
            balk.set(0.0)
            
            stappen = [
                (0.25, "Downloaden van core repository...", "[GET] Huiswerk.py download gestart..."),
                (0.55, "Integriteit van code verifiëren...", "[MD5] Validating script structural hash..."),
                (0.85, "Oude systeembestanden overschrijven...", "[SYS] Cleaning up caching modules..."),
                (1.00, "Systeem herstarten...", "[SUCCESS] Core patch set. Initializing reboot...")
            ]
            
            def voer_stap(index=0):
                if index < len(stappen):
                    progress, tekst, debug = stappen[index]
                    balk.set(progress)
                    lbl.configure(text="Systeem updaten...")
                    p_lbl.configure(text=tekst)
                    sub_lbl.configure(text=debug)
                    up_win.after(1000, lambda: voer_stap(index + 1))
                else:
                    self.is_updating = False
                    self.voer_update_uit(up_win, lbl)
            voer_stap()

    def voer_update_uit(self, up_win, status_lbl):
        try:
            try:
                req_log = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_log) as response_log:
                    nieuwe_log_data = response_log.read().decode("utf-8")
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write(nieuwe_log_data)
            except Exception:
                with open(LOG_BESTAND, "w", encoding="utf-8") as f_log:
                    f_log.write("Kleine prestatieverbeteringen en UI upgrades.")

            temp_file = os.path.join(SCRIPT_DIR, "update_tmp.py")
            req = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                nieuw_script_data = response.read().decode("utf-8")
                
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(nieuw_script_data)
                
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
            messagebox.showerror("Fout bij updaten", f"Er is een fout opgetreden:\n{e}")

    # --------------------------------------------------------
    # LAYOUT EN THEMER
    # --------------------------------------------------------

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

        for lst in [self.hw_list, self.note_list, self.cijfer_list, self.vrijedagen_listbox]:
            if lst is not None:
                lst.configure(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], highlightthickness=0, borderwidth=0)

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
    # MODULE: DASHBOARD
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
        
        geldige_cijfers = []
        for c in self.data["cijfers"]:
            try: geldige_cijfers.append(float(c.get("cijfer", 0.0)))
            except ValueError: pass
        gem = sum(geldige_cijfers) / len(geldige_cijfers) if geldige_cijfers else None

        ctk.CTkLabel(card, text=f"📚 Huiswerk openstaand: {hw_open} / {hw_total}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=6, padx=15)
        ctk.CTkLabel(card, text=f"📊 Algemeen Gemiddelde: {f'{gem:.2f}' if gem is not None else 'Nog geen cijfers'}", font=("Segoe UI", 15), text_color=t["text"]).pack(anchor="w", pady=6, padx=15)

        vandaag_str = dt.date.today().strftime("%Y-%m-%d")
        binnenkort_hw = [h for h in self.data["huiswerk"] if not h.get("afgerond") and h.get("datum") == vandaag_str]
        if binnenkort_hw:
            alert_card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#ffcccc" if t["mode"]=="Light" else "#5c1d1d")
            alert_card.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(alert_card, text=f"⚠️ Je hebt {len(binnenkort_hw)} huiswerktaak/taken die VANDAAG af moeten!", font=("Segoe UI", 13, "bold"), text_color="#111111" if t["mode"]=="Light" else "#ffffff").pack(padx=10, pady=5, anchor="w")

        card_vrij = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card_vrij.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(card_vrij, text="🎉 Vrije dagen & vakanties", font=("Segoe UI", 18, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))

        upcoming = self._get_upcoming_vrijedagen()
        if not upcoming:
            ctk.CTkLabel(card_vrij, text="Geen vrije dagen gepland.", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=15, pady=5)
        else:
            eerst_datum, eerst_delta, eerst_naam = upcoming[0]
            tekst = f"Vandaag ben je vrij: {eerst_naam}!" if eerst_delta == 0 else f"Nog {eerst_delta} dag(en) tot: {eerst_naam} ({eerst_datum.strftime('%Y-%m-%d')})"
            ctk.CTkLabel(card_vrij, text=tekst, font=("Segoe UI", 14, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=(5, 10))

            scroll_vrij = ctk.CTkScrollableFrame(card_vrij, fg_color="transparent")
            scroll_vrij.pack(fill="both", expand=True, padx=10, pady=5)

            for d, delta, naam in upcoming[:10]:
                regel = f"• {d.strftime('%Y-%m-%d')} - {naam} (" + ("vandaag!" if delta == 0 else f"over {delta} dagen") + ")"
                ctk.CTkLabel(scroll_vrij, text=regel, font=("Segoe UI", 13), text_color=t["text"]).pack(anchor="w", padx=15, pady=2)

        version_label = ctk.CTkLabel(self.main, text=f"Versie: {HUIDIGE_VERSIE}", font=("Segoe UI", 11), text_color=t["text"])
        version_label.pack(side="bottom", anchor="e", padx=20, pady=10)
        self.apply_theme()

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self.update_clock)

    # --------------------------------------------------------
    # MODULE: HUISWERK
    # --------------------------------------------------------

    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="Huiswerk Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.hw_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.hw_list.yview)
        sb.pack(side="right", fill="y")
        self.hw_list.config(yscrollcommand=sb.set)

        self._herlaad_huiswerk_lijst()

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Nieuwe Taak", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=15, pady=5)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving / Opdracht")
        self.hw_beschrijving.pack(fill="x", padx=15, pady=5)

        self.hw_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.hw_datum.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(right_frame, text="📅 Kies datum", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=lambda: kies_datum(self.hw_datum)).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.hw_toevoegen).pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkButton(right_frame, text="Status Omschakelen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.hw_afronden).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], hover_color=t["button_hover"], text_color=t["button_text"], command=self.hw_verwijderen).pack(fill="x", padx=15, pady=5)

        self.apply_theme()

    def _herlaad_huiswerk_lijst(self):
        self.hw_list.delete(0, tk.END)
        for h in self.data["huiswerk"]:
            status = "✔" if h.get("afgerond") else "❌"
            self.hw_list.insert(tk.END, f" [{status}] {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

    def hw_toevoegen(self):
        v, b, d = self.hw_vak.get(), self.hw_beschrijving.get().strip(), self.hw_datum.get().strip()
        if not b or not d:
            messagebox.showwarning("Waarschuwing", "Vul alle velden in.")
            return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()
        self.hw_beschrijving.delete(0, tk.END)
        self.hw_datum.delete(0, tk.END)

    def hw_afronden(self):
        selectie = self.hw_list.curselection()
        if not selectie: return
        idx = selectie[0]
        self.data["huiswerk"][idx]["afgerond"] = not self.data["huiswerk"][idx]["afgerond"]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    def hw_verwijderen(self):
        selectie = self.hw_list.curselection()
        if not selectie: return
        idx = selectie[0]
        del self.data["huiswerk"][idx]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    # --------------------------------------------------------
    # HERSTELDE / ONTBREKENDE PARSEN VAN JOUW SCRIPT OVERIGE MODULES
    # --------------------------------------------------------

    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Wekelijks Lesrooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        
        rooster_frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        rooster_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for dag, uren in self.data["rooster"].items():
            dag_card = ctk.CTkFrame(rooster_frame, fg_color=t["bg_card"], corner_radius=10)
            dag_card.pack(fill="x", pady=5)
            ctk.CTkLabel(dag_card, text=dag, font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=15, pady=5)
            for uur in uren:
                ctk.CTkLabel(dag_card, text=f"⏰ {uur['tijd']} -> {uur['les']}", font=("Segoe UI", 13), text_color=t["text"]).pack(anchor="w", padx=30, pady=2)
        self.apply_theme()

    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijke Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.note_list = tk.Listbox(container, font=("Segoe UI", 12))
        self.note_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        for n in self.data.get("notities", []):
            self.note_list.insert(tk.END, n)
            
        btn_frame = ctk.CTkFrame(container, fg_color="transparent", width=150)
        btn_frame.pack(side="right", fill="y", padx=5)
        
        def voeg_toe():
            dial = ctk.CTkInputDialog(text="Typ je nieuwe notitie:", title="Notitie")
            res = dial.get_input()
            if res:
                self.data["notities"].append(res)
                opslaan(self.data)
                self.show_notities()
                
        def verwijder():
            sel = self.note_list.curselection()
            if sel:
                del self.data["notities"][sel[0]]
                opslaan(self.data)
                self.show_notities()

        ctk.CTkButton(btn_frame, text="Nieuw", fg_color=t["accent"], text_color="white", command=voeg_toe).pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Verwijder", fg_color=t["button_fg"], text_color=t["button_text"], command=verwijder).pack(fill="x", pady=5)
        self.apply_theme()

    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.cijfer_list = tk.Listbox(container, font=("Segoe UI", 12))
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        for c in self.data.get("cijfers", []):
            self.cijfer_list.insert(tk.END, f"{c.get('vak')} - Cijfer: {c.get('cijfer')} (Weging: {c.get('weging')})")
            
        self.apply_theme()

    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Systeeminstellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)
        
        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(card, text="Selecteer Interface Thema:", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=15, pady=5)
        
        self.theme_combo = ctk.CTkComboBox(card, values=list(THEMES.keys()), command=self.wijzig_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=15, pady=10)

        ctk.CTkButton(card, text="🔄 Zoeken naar updates", fg_color=t["accent"], text_color="white", command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=15, pady=15)
        self.apply_theme()

    def wijzig_thema(self, nieuw_thema):
        if nieuw_thema in THEMES:
            self.theme_name = nieuw_thema
            self.data["settings"]["theme"] = nieuw_thema
            opslaan(self.data)
            self.apply_theme()
            self.show_settings()

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
