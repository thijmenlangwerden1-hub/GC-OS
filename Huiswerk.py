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
# INSTELLINGEN & CONFIGURATIE (Versie 1.0.23)
# ============================================================

HUIDIGE_VERSIE = "1.0.23"
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
            "rooster": [],
            "settings": {"theme": "Wit", "naam": ""},
            "vrijedagen": [],
            "users": {"admin": "admin"}
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
    if "users" not in data: data["users"] = {"admin": "admin"}

    if not data["vrijedagen"]:
        data["vrijedagen"] = _standaard_vrijedagen()

    return data

# ============================================================
# MAIN APPLICATIE CLASS
# ============================================================

class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.withdraw()

        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Wit")
        if self.theme_name not in THEMES:
            self.theme_name = "Wit"

        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        ctk.set_default_color_theme("blue")

        self.title("GraafschapCollege‑OS")
        
        try:
            self.state("zoomed")
        except Exception:
            self.geometry("1100x650")

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Vrije Afspraak"
        ]
        
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]

        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.rooster_listbox = None
        self.theme_combo = None
        self.clock_label = None
        self.dashboard_title_label = None  

        self.rooster_stijl = "Week" 
        self.huidige_rooster_datum = dt.date.today()

        self._build_layout()
        self.apply_theme()

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
        ctk.CTkLabel(log_win, text="Dit is er nieuw:", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=(0, 15))

        txt_frame = ctk.CTkScrollableFrame(log_win, width=440, height=220, fg_color=t["bg_root"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(txt_frame, text=log_tekst.strip(), font=("Segoe UI", 12), justify="left", text_color=t["text"], anchor="w").pack(anchor="w", padx=10, pady=10)
        ctk.CTkButton(log_win, text="Sluiten", fg_color=t["accent"], text_color="white", command=log_win.destroy).pack(pady=20)

    def show_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("GC-OS Intro")
        intro.overridersdirect(True)

        try:
            intro.state("zoomed")
        except Exception:
            intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])

        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", 50, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.5, anchor="center")
        intro.attributes("-alpha", 0.0)

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                intro.attributes("-alpha", alpha)
                self.after(20, lambda: fade_in(alpha + 0.05))
            else:
                self.after(1000, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                intro.attributes("-alpha", alpha)
                self.after(20, lambda: fade_out(alpha - 0.05))
            else:
                intro.destroy()
                self.show_login_screen()

        fade_in()

    # ============================================================
    # INLOGSCHERM & REGISTRATIE
    # ============================================================
    def show_login_screen(self):
        t = THEMES[self.theme_name]
        self.login_win = ctk.CTkToplevel()
        self.login_win.title("Inloggen - GC-OS")
        
        try:
            self.login_win.state("zoomed")
        except Exception:
            self.login_win.geometry("900x600")

        self.login_win.configure(fg_color=t["bg_root"])
        self.login_win.protocol("WM_DELETE_WINDOW", sys.exit)

        login_panel = ctk.CTkFrame(self.login_win, fg_color=t["bg_card"], width=450, height=500, corner_radius=20)
        login_panel.place(relx=0.5, rely=0.5, anchor="center")
        login_panel.pack_propagate(False)

        ctk.CTkLabel(login_panel, text="Inloggen op GC-OS", font=("Segoe UI", 26, "bold"), text_color=t["accent"]).pack(pady=(40, 30))

        self.username_entry = ctk.CTkEntry(login_panel, placeholder_text="Gebruikersnaam", width=320, height=40, font=("Segoe UI", 13))
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(login_panel, placeholder_text="Wachtwoord", show="*", width=320, height=40, font=("Segoe UI", 13))
        self.password_entry.pack(pady=10)

        ctk.CTkButton(login_panel, text="Inloggen", fg_color=t["accent"], text_color="white", width=320, height=42, font=("Segoe UI", 14, "bold"), command=self.check_login).pack(pady=(25, 10))
        
        ctk.CTkLabel(login_panel, text="Nog geen account?", font=("Segoe UI", 12), text_color=t["text"]).pack(pady=(15, 0))
        ctk.CTkButton(login_panel, text="Account Registreren", fg_color="transparent", hover_color=t["button_hover"], text_color=t["accent"], width=320, font=("Segoe UI", 13, "underline"), command=self.show_register_screen).pack(pady=5)

    def show_register_screen(self):
        t = THEMES[self.theme_name]
        self.reg_win = ctk.CTkToplevel(self.login_win)
        self.reg_win.title("Registreren - GC-OS")
        
        try:
            self.reg_win.state("zoomed")
        except Exception:
            self.reg_win.geometry("900x600")
            
        self.reg_win.configure(fg_color=t["bg_root"])
        self.reg_win.grab_set()

        reg_panel = ctk.CTkFrame(self.reg_win, fg_color=t["bg_card"], width=450, height=520, corner_radius=20)
        reg_panel.place(relx=0.5, rely=0.5, anchor="center")
        reg_panel.pack_propagate(False)

        ctk.CTkLabel(reg_panel, text="Nieuw Account Aanmaken", font=("Segoe UI", 24, "bold"), text_color=t["accent"]).pack(pady=(35, 25))

        self.reg_user = ctk.CTkEntry(reg_panel, placeholder_text="Kies een gebruikersnaam", width=320, height=40)
        self.reg_user.pack(pady=10)

        self.reg_pass = ctk.CTkEntry(reg_panel, placeholder_text="Kies een wachtwoord", show="*", width=320, height=40)
        self.reg_pass.pack(pady=10)

        self.reg_pass_confirm = ctk.CTkEntry(reg_panel, placeholder_text="Herhaal het wachtwoord", show="*", width=320, height=40)
        self.reg_pass_confirm.pack(pady=10)

        ctk.CTkButton(reg_panel, text="Account Aanmaken", fg_color=t["accent"], text_color="white", width=320, height=42, font=("Segoe UI", 14, "bold"), command=self.register_user).pack(pady=(25, 10))
        ctk.CTkButton(reg_panel, text="Annuleren", fg_color="transparent", text_color=t["text"], width=320, command=self.reg_win.destroy).pack()

    def register_user(self):
        user = self.reg_user.get().strip()
        pwd = self.reg_pass.get().strip()
        pwd_conf = self.reg_pass_confirm.get().strip()

        if not user or not pwd:
            messagebox.showerror("Registratie Fout", "Vul alle velden in.")
            return
        if pwd != pwd_conf:
            messagebox.showerror("Registratie Fout", "Wachtwoorden komen niet overeen.")
            return
        if user in self.data["users"]:
            messagebox.showerror("Registratie Fout", "Deze gebruikersnaam bestaat al.")
            return

        self.data["users"][user] = pwd
        opslaan(self.data)
        
        messagebox.showinfo("Succes", "Je account is succesvol aangemaakt! Je kunt nu inloggen.")
        self.reg_win.destroy()

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username in self.data["users"] and self.data["users"][username] == password:
            self.login_win.destroy()
            self.deiconify()
            try:
                self.state("zoomed")
            except Exception:
                pass
            
            self.show_dashboard()

            self.after(500, lambda: self.toon_update_laadbalk(silent=True))
            self.after(1000, self.check_na_update_log)
        else:
            messagebox.showerror("Inloggen Mislukt", "Onjuiste gebruikersnaam of wachtwoord.")

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
                self.after(int(random.uniform(40, 120)), lambda: laad_stap(nieuw_progress))
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
                status_lbl.configure(text="❌ Fout: Geen internetverbinding.")
                ctk.CTkButton(up_win, text="Sluiten", fg_color=t["button_fg"], text_color=t["button_text"], command=up_win.destroy).pack(pady=15)
                return

            if nieuweste == HUIDIGE_VERSIE:
                if silent:
                    up_win.destroy()
                    return
                status_lbl.configure(text=f"✨ Je bent up-to-date! (v{HUIDIGE_VERSIE})")
                ctk.CTkButton(up_win, text="Sluiten", fg_color=t["accent"], text_color="white", command=up_win.destroy).pack(pady=15)
            else:
                status_lbl.configure(text=f"🎉 Update beschikbaar! v{HUIDIGE_VERSIE} ➔ v{nieuweste}")
                knop_frame = ctk.CTkFrame(up_win, fg_color="transparent")
                knop_frame.pack(pady=15)

                ctk.CTkButton(knop_frame, text="📥 Installeren", fg_color=t["accent"], text_color="white", command=lambda: self.voer_update_uit(up_win, status_lbl)).pack(side="left", padx=5)
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
                    f_log.write("Algemene updates en stabiliteitsverbeteringen.")

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
            messagebox.showerror("Fout bij updaten", f"Er is een fout opgetreden:\n{e}")

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

        for lst in [self.hw_list, self.note_list, self.cijfer_list, self.rooster_listbox]:
            if lst is not None:
                lst.configure(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"], highlightthickness=0, borderwidth=0)

        if self.theme_combo is not None:
            try:
                self.theme_combo.configure(fg_color=t["button_fg"], border_color=t["accent"], button_color=t["accent"], text_color=t["button_text"])
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
        
        geldige_cijfers = []
        for c in self.data["cijfers"]:
            try: geldige_cijfers.append(float(c.get("cijfer", 0.0)))
            except ValueError: pass
            
        gem = sum(geldige_cijfers) / len(geldige_cijfers) if geldige_cijfers else None

        ctk.CTkLabel(card, text=f"📚 Huiswerk open: {hw_open}/{hw_total}", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(card, text=f"📊 Gemiddelde cijfers: {gem:.2f}" if gem is not None else "📊 Geen cijfers", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)

        card_vrij = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card_vrij.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(card_vrij, text="🎉 Vrije dagen & vakanties", font=("Segoe UI", 18, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))

        upcoming = self._get_upcoming_vrijedagen()
        if not upcoming:
            ctk.CTkLabel(card_vrij, text="Geen vrije dagen ingevoerd.", font=("Segoe UI", 14), text_color=t["text"]).pack(anchor="w", padx=10, pady=5)
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
            self.clock_label.configure(text=nu.strftime("%d-%m-%Y | %H:%M:%S"))
            
            if self.dashboard_title_label and self.dashboard_title_label.winfo_exists():
                self.dashboard_title_label.configure(text="Dashboard")

            self.after(1000, self.update_clock)

    # ============================================================
    # HUISWERK LOGICA
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerk", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.hw_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        sb = tk.Scrollbar(left_frame, command=self.hw_list.yview)
        sb.pack(side="right", fill="y")
        self.hw_list.config(yscrollcommand=sb.set)

        self._herlaad_huiswerk_lijst()

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

    def _herlaad_huiswerk_lijst(self):
        if self.hw_list:
            self.hw_list.delete(0, tk.END)
            for h in self.data["huiswerk"]:
                status = "✔" if h.get("afgerond") else "✘"
                self.hw_list.insert(tk.END, f"{status} {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

    def hw_toevoegen(self):
        vak = self.hw_vak.get()
        desc = self.hw_beschrijving.get().strip()
        datum = self.hw_datum.get().strip()
        if not desc or not datum:
            messagebox.showerror("Fout", "Vul alle velden in.")
            return
        self.data["huiswerk"].append({"vak": vak, "beschrijving": desc, "datum": datum, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()
        self.hw_beschrijving.delete(0, tk.END)
        self.hw_datum.delete(0, tk.END)

    def hw_afronden(self):
        sel = self.hw_list.curselection()
        if not sel: return
        idx = sel[0]
        self.data["huiswerk"][idx]["afgerond"] = not self.data["huiswerk"][idx]["afgerond"]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    def hw_verwijderen(self):
        sel = self.hw_list.curselection()
        if not sel: return
        idx = sel[0]
        del self.data["huiswerk"][idx]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    # ============================================================
    # ROOSTER BEHEER
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Rooster Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        nav_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(nav_frame, text="◀ Vorige", width=80, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: self._navigeer_rooster(-1)).pack(side="left", padx=2)
        self.rooster_info_label = ctk.CTkLabel(nav_frame, text="", font=("Segoe UI", 14, "bold"), text_color=t["text"])
        self.rooster_info_label.pack(side="left", padx=15)
        ctk.CTkButton(nav_frame, text="Volgende ▶", width=80, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: self._navigeer_rooster(1)).pack(side="left", padx=2)

        self.stijl_btn = ctk.CTkButton(nav_frame, text=f"Weergave: {self.rooster_stijl}", fg_color=t["accent"], text_color="white", command=self._toggle_rooster_stijl)
        self.stijl_btn.pack(side="right", padx=5)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.rooster_listbox = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.rooster_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Les Toevoegen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        self.rst_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.rst_vak.set(self.vakken_hw[0])
        self.rst_vak.pack(fill="x", padx=10, pady=5)

        self.rst_tijd = ctk.CTkEntry(right_frame, placeholder_text="uu:mm - uu:mm (bijv. 08:30-10:00)")
        self.rst_tijd.pack(fill="x", padx=10, pady=5)

        self.rst_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.rst_datum.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(right_frame, text="📅 Kies datum", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: kies_datum(self.rst_datum)).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self._rooster_toevoegen).pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._rooster_verwijderen).pack(fill="x", padx=10, pady=5)

        self._herlaad_rooster()
        self.apply_theme()

    def _toggle_rooster_stijl(self):
        self.rooster_stijl = "Dag" if self.rooster_stijl == "Week" else "Week"
        self.stijl_btn.configure(text=f"Weergave: {self.rooster_stijl}")
        self._herlaad_rooster()

    def _navigeer_rooster(self, richting):
        delta = dt.timedelta(weeks=richting) if self.rooster_stijl == "Week" else dt.timedelta(days=richting)
        self.huidige_rooster_datum += delta
        self._herlaad_rooster()

    def _herlaad_rooster(self):
        if not self.rooster_listbox: return
        self.rooster_listbox.delete(0, tk.END)
        
        if self.rooster_stijl == "Week":
            start = self.huidige_rooster_datum - dt.timedelta(days=self.huidige_rooster_datum.weekday())
            eind = start + dt.timedelta(days=6)
            self.rooster_info_label.configure(text=f"Week: {start.strftime('%d %b')} t/m {eind.strftime('%d %b %Y')}")
            
            geldige_lessen = []
            for item in self.data["rooster"]:
                try:
                    d = dt.datetime.strptime(item["datum"], "%Y-%m-%d").date()
                    if start <= d <= eind:
                        geldige_lessen.append((d, item))
                except Exception: pass
            geldige_lessen.sort(key=lambda x: (x[0], x[1].get("tijd", "")))
            for d, item in geldige_lessen:
                self.rooster_listbox.insert(tk.END, f"[{d.strftime('%a %d-%m')}] {item['tijd']} -> {item['vak']}")
        else:
            self.rooster_info_label.configure(text=f"Dag: {self.huidige_rooster_datum.strftime('%A %d %B %Y')}")
            geldige_lessen = []
            for item in self.data["rooster"]:
                if item["datum"] == self.huidige_rooster_datum.strftime("%Y-%m-%d"):
                    geldige_lessen.append(item)
            geldige_lessen.sort(key=lambda x: x.get("tijd", ""))
            for item in geldige_lessen:
                self.rooster_listbox.insert(tk.END, f"{item['tijd']} -> {item['vak']}")

    def _rooster_toevoegen(self):
        vak = self.rst_vak.get()
        tijd = self.rst_tijd.get().strip()
        datum = self.rst_datum.get().strip()
        if not tijd or not datum:
            messagebox.showerror("Fout", "Vul alle velden in.")
            return
        self.data["rooster"].append({"vak": vak, "tijd": tijd, "datum": datum})
        opslaan(self.data)
        self._herlaad_rooster()
        self.rst_tijd.delete(0, tk.END)
        self.rst_datum.delete(0, tk.END)

    def _rooster_verwijderen(self):
        sel = self.rooster_listbox.curselection()
        if not sel: return
        idx = sel[0]
        
        # Bepaal welk echt item verwijderd moet worden op basis van de huidige filter weergave
        if self.rooster_stijl == "Week":
            start = self.huidige_rooster_datum - dt.timedelta(days=self.huidige_rooster_datum.weekday())
            eind = start + dt.timedelta(days=6)
            geldige_lessen = []
            for item in self.data["rooster"]:
                try:
                    d = dt.datetime.strptime(item["datum"], "%Y-%m-%d").date()
                    if start <= d <= eind: geldige_lessen.append(item)
                except Exception: pass
            geldige_lessen.sort(key=lambda x: (x["datum"], x.get("tijd", "")))
            target = geldige_lessen[idx]
            self.data["rooster"].remove(target)
        else:
            geldige_lessen = [i for i in self.data["rooster"] if i["datum"] == self.huidige_rooster_datum.strftime("%Y-%m-%d")]
            geldige_lessen.sort(key=lambda x: x.get("tijd", ""))
            target = geldige_lessen[idx]
            self.data["rooster"].remove(target)
            
        opslaan(self.data)
        self._herlaad_rooster()

    # ============================================================
    # NOTITIES BEHEER
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Notitieblok", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, width=250, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.note_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.note_list.bind("<<ListboxSelect>>", self._laad_geselecteerde_notitie)

        ctk.CTkButton(left_frame, text="+ Nieuwe Notitie", fg_color=t["accent"], text_color="white", command=self._notitie_nieuw).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(left_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._notitie_verwijderen).pack(fill="x", padx=10, pady=(0, 10))

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.note_text_area = tk.Text(right_frame, font=("Segoe UI", 12), bd=0, highlightthickness=0, wrap="word")
        self.note_text_area.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_text_area.bind("<KeyRelease>", self._automatisch_opslaan_notitie)

        self._herlaad_notitie_lijst()
        self.apply_theme()

    def _herlaad_notitie_lijst(self):
        if self.note_list:
            self.note_list.delete(0, tk.END)
            for n in self.data["notities"]:
                self.note_list.insert(tk.END, n.get("titel", "Lege notitie"))

    def _laad_geselecteerde_notitie(self, event=None):
        sel = self.note_list.curselection()
        if not sel: return
        idx = sel[0]
        self.note_text_area.delete("1.0", tk.END)
        self.note_text_area.insert("1.0", self.data["notities"][idx].get("inhoud", ""))

    def _notitie_nieuw(self):
        nieuwe_notitie = {"titel": "Nieuwe Notitie", "inhoud": ""}
        self.data["notities"].append(nieuwe_notitie)
        opslaan(self.data)
        self._herlaad_notitie_lijst()
        self.note_list.selection_clear(0, tk.END)
        self.note_list.selection_set(tk.END)
        self._laad_geselecteerde_notitie()

    def _automatisch_opslaan_notitie(self, event=None):
        sel = self.note_list.curselection()
        if not sel: return
        idx = sel[0]
        inhoud = self.note_text_area.get("1.0", "end-1c")
        
        regels = [r.strip() for r in inhoud.split("\n") if r.strip()]
        titel = regels[0][:25] if regels else "Lege notitie"
        
        self.data["notities"][idx]["inhoud"] = inhoud
        self.data["notities"][idx]["titel"] = titel
        opslaan(self.data)
        
        # Werk de titel live bij in de lijst zonder focus te verliezen
        self.note_list.delete(idx)
        self.note_list.insert(idx, titel)
        self.note_list.selection_set(idx)

    def _notitie_verwijderen(self):
        sel = self.note_list.curselection()
        if not sel: return
        idx = sel[0]
        del self.data["notities"][idx]
        opslaan(self.data)
        self.note_text_area.delete("1.0", tk.END)
        self._herlaad_notitie_lijst()

    # ============================================================
    # CIJFERS REGISTRATIE LOGICA
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.cijfer_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none")
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_frame, text="Cijfer Toevoegen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=(10, 5))
        self.cjf_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.cjf_vak.set(self.vakken_hw[0])
        self.cjf_vak.pack(fill="x", padx=10, pady=5)

        self.cjf_cijfer = ctk.CTkEntry(right_frame, placeholder_text="Cijfer (bijv. 7.5)")
        self.cjf_cijfer.pack(fill="x", padx=10, pady=5)

        self.cjf_periode = ctk.CTkComboBox(right_frame, values=self.periodes, state="readonly")
        self.cjf_periode.set(self.periodes[0])
        self.cjf_periode.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self._cijfer_toevoegen).pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkButton(right_frame, text="Verwijderen", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._cijfer_verwijderen).pack(fill="x", padx=10, pady=5)

        self.gemiddelden_box = ctk.CTkTextbox(right_frame, width=200, height=150, font=("Segoe UI", 12))
        self.gemiddelden_box.pack(fill="x", padx=10, pady=10)

        self._herlaad_cijfers()
        self.apply_theme()

    def _herlaad_cijfers(self):
        if not self.cijfer_list: return
        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f"{c['vak']} - {c['cijfer']} ({c['periode']})")
        
        # Bereken periodieke gemiddelden live
        stats = {p: [] for p in self.periodes}
        totaal_cijfers = []
        for c in self.data["cijfers"]:
            try:
                val = float(c["cijfer"])
                stats[c["periode"]].append(val)
                totaal_cijfers.append(val)
            except ValueError: pass

        self.gemiddelden_box.configure(state="normal")
        self.gemiddelden_box.delete("1.0", tk.END)
        self.gemiddelden_box.insert(tk.END, "📊 GEMIDDELDEN:\n\n")
        for p in self.periodes:
            cijfers = stats[p]
            gem = sum(cijfers) / len(cijfers) if cijfers else 0.0
            self.gemiddelden_box.insert(tk.END, f"{p}: {f'{gem:.1f}' if gem > 0 else 'N/A'}\n")
        
        alg_gem = sum(totaal_cijfers) / len(totaal_cijfers) if totaal_cijfers else 0.0
        self.gemiddelden_box.insert(tk.END, f"\nAlgemeen Totaal: {f'{alg_gem:.2f}' if alg_gem > 0 else 'N/A'}")
        self.gemiddelden_box.configure(state="disabled")

    def _cijfer_toevoegen(self):
        vak = self.cjf_vak.get()
        cijfer_str = self.cjf_cijfer.get().replace(",", ".")
        periode = self.cjf_periode.get()
        try:
            val = float(cijfer_str)
            if not (1.0 <= val <= 10.0): raise ValueError
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig cijfer in tussen 1.0 en 10.0")
            return
        
        self.data["cijfers"].append({"vak": vak, "cijfer": f"{val:.1f}", "periode": periode})
        opslaan(self.data)
        self._herlaad_cijfers()
        self.cjf_cijfer.delete(0, tk.END)

    def _cijfer_verwijderen(self):
        sel = self.cijfer_list.curselection()
        if not sel: return
        idx = sel[0]
        del self.data["cijfers"][idx]
        opslaan(self.data)
        self._herlaad_cijfers()

    # ============================================================
    # INSTELLINGEN BEHEER
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        card.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(card, text="Personaliseer interface", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=15, pady=10)

        ctk.CTkLabel(card, text="Gebruikersnaam:", text_color=t["text"]).pack(anchor="w", padx=15, pady=2)
        self.naam_entry = ctk.CTkEntry(card, width=300)
        self.naam_entry.insert(0, self.data["settings"].get("naam", ""))
        self.naam_entry.pack(anchor="w", padx=15, pady=5)

        ctk.CTkLabel(card, text="Kleurthema:", text_color=t["text"]).pack(anchor="w", padx=15, pady=2)
        self.theme_combo = ctk.CTkComboBox(card, values=list(THEMES.keys()), state="readonly")
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=15, pady=5)

        ctk.CTkButton(card, text="Opslaan & Toepassen", fg_color=t["accent"], text_color="white", command=self._instellingen_opslaan).pack(anchor="w", padx=15, pady=20)
        
        # Handmatige update knop voor de gebruiker
        ctk.CTkButton(card, text="🔄 Zoeken naar updates", fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: self.toon_update_laadbalk(silent=False)).pack(anchor="w", padx=15, pady=(0, 15))
        
        self.apply_theme()

    def _instellingen_opslaan(self):
        naam = self.naam_entry.get().strip()
        nieuw_thema = self.theme_combo.get()
        
        self.data["settings"]["naam"] = naam
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        
        self.theme_name = nieuw_thema
        self.apply_theme()
        messagebox.showinfo("Succes", "Instellingen succesvol bijgewerkt!")

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
