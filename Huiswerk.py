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
import threading

# ============================================================
# SYSTEM CONFIGURATION & VERSIONING (v9.8.2v)
# ============================================================
HUIDIGE_VERSIE = "9.8.2v"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    print("[WAARSCHUWING] Matplotlib mist. Installeer via: pip install matplotlib")

# ============================================================
# AVANCEERDE THEMA ENGINE & PALETTEN
# ============================================================
THEMES = {
    "Cyberpunk (Dark)": {
        "mode": "Dark",
        "bg_root": "#0b0c10",
        "bg_sidebar": "#1f2833",
        "bg_main": "#0b0c10",
        "bg_card": "#151a22",
        "border_color": "#232d38",
        "text": "#c5c6c7",
        "sidebar_text": "#66fcf1",
        "button_text": "#0b0c10",
        "button_fg": "#66fcf1",
        "button_hover": "#45a29e",
        "accent": "#66fcf1",
    },
    "Neon Purple": {
        "mode": "Dark",
        "bg_root": "#120024",
        "bg_sidebar": "#1a0033",
        "bg_main": "#120024",
        "bg_card": "#26004d",
        "border_color": "#3d007a",
        "text": "#ffffff",
        "sidebar_text": "#ff007f",
        "button_text": "#ffffff",
        "button_fg": "#ff007f",
        "button_hover": "#b30059",
        "accent": "#ff007f",
    },
    "Minimal Light": {
        "mode": "Light",
        "bg_root": "#f8fafc",
        "bg_sidebar": "#ffffff",
        "bg_main": "#f8fafc",
        "bg_card": "#ffffff",
        "border_color": "#e2e8f0",
        "text": "#0f172a",
        "sidebar_text": "#4f46e5",
        "button_text": "#ffffff",
        "button_fg": "#4f46e5",
        "button_hover": "#4338ca",
        "accent": "#4f46e5",
    },
    "Matrix Green": {
        "mode": "Dark",
        "bg_root": "#000000",
        "bg_sidebar": "#0d0d0d",
        "bg_main": "#000000",
        "bg_card": "#111111",
        "border_color": "#00ff41",
        "text": "#00ff41",
        "sidebar_text": "#00ff41",
        "button_text": "#000000",
        "button_fg": "#00ff41",
        "button_hover": "#00b32d",
        "accent": "#00ff41",
    }
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")
BACKUP_BESTAND = os.path.join(SCRIPT_DIR, "gc_os_backup.json")

# ============================================================
# DATA MANAGEMENT CORING
# ============================================================
def opslaan(data):
    try:
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Maak direct een veilige back-up
        with open(BACKUP_BESTAND, "w", encoding="utf-8") as fb:
            json.dump(data, fb, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Systeemfout", f"Kan data niet wegschrijven:\n{e}")

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
        if os.path.exists(BACKUP_BESTAND):
            try:
                with open(BACKUP_BESTAND, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception: pass
        return {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": _standaard_rooster(),
            "settings": {"theme": "Cyberpunk (Dark)"}
        }
    
    with open(BESTAND, "r", encoding="utf-8") as f:
        try: data = json.load(f)
        except Exception: data = {}

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data: data["rooster"] = _standaard_rooster()
    if "settings" not in data: data["settings"] = {"theme": "Cyberpunk (Dark)"}
    return data

def kies_datum(entry_widget):
    top = ctk.CTkToplevel()
    top.title("Kies Datum")
    top.geometry("320x360")
    top.resizable(False, False)
    top.after(200, lambda: top.iconify()) # Forceer hertekening bugfix windows
    top.after(250, lambda: top.deiconify())
    top.grab_set()
    
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=15, fill="both", expand=True, padx=10)
    
    def selecteer():
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, cal.get_date())
        top.destroy()
        
    ctk.CTkButton(top, text="📅 Datum Bevestigen", font=("Segoe UI", 12, "bold"), corner_radius=8, command=selecteer).pack(pady=10, padx=10, fill="x")

# ============================================================
# MAIN APPLICATION INTERFACE CODE
# ============================================================
class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Cyberpunk (Dark)")
        if self.theme_name not in THEMES: self.theme_name = "Cyberpunk (Dark)"

        self.title(f"GraafschapCollege-OS Engine [v{HUIDIGE_VERSIE}]")
        self.geometry("1280x760")
        self.minsize(1080, 700)

        # Core app variabelen
        self.vakken_hw = ["Nederlands", "Engels", "Rekenen", "Hardware", "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Project"]
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]
        self.sidebar_buttons = []
        self.hw_filter_var = "Alle"
        self.cijfer_filter_var = "Alle Periodes"

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()
        
        # Async Update Check Engine
        threading.Thread(target=self._check_updates_background, daemon=True).start()

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
                    hover_color=t["bg_card"], 
                    text_color=t["text"] if t["mode"]=="Light" else "#ffffff"
                )
            except Exception: pass

    def _build_layout(self):
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=30, padx=25, fill="x")
        
        title_label = ctk.CTkLabel(brand_frame, text="GC‑OS SYSTEM", font=("Segoe UI", 24, "bold"))
        title_label.pack(anchor="w")
        
        ver_label = ctk.CTkLabel(brand_frame, text=f"Build Engine: v{HUIDIGE_VERSIE}", font=("Consolas", 12), text_color="#71717a")
        ver_label.pack(anchor="w")

        # Navigatie Knoppen
        buttons = [
            ("🏠   Dashboard", self.show_dashboard),
            ("📝   Huiswerk Planner", self.show_huiswerk),
            ("📅   Interactief Rooster", self.show_rooster),
            ("🗒   Notitie Blok", self.show_notities),
            ("📊   Cijfer Matrix", self.show_cijfers),
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w", 
                font=("Segoe UI", 14, "bold"), height=48, 
                corner_radius=10, command=cmd
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.sidebar_buttons.append(btn)

        settings_btn = ctk.CTkButton(
            self.sidebar, text="⚙   Instellingen", anchor="w", 
            font=("Segoe UI", 14, "bold"), height=48, 
            corner_radius=10, command=self.show_settings
        )
        settings_btn.pack(side="bottom", fill="x", padx=15, pady=25)
        self.sidebar_buttons.append(settings_btn)

        # Hoofdscherm Frame
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children(): 
            widget.destroy()

    # ============================================================
    # UPGRADE & LIVE SYNC OVERVIEW INTERFACE
    # ============================================================
    def _check_updates_background(self):
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version != HUIDIGE_VERSIE:
                self.after(1500, lambda: self._toon_update_dialoog(remote_version))
        except Exception:
            pass

    def _handmatige_update_check(self):
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version == HUIDIGE_VERSIE:
                messagebox.showinfo("GC-OS Update Sync", f"Je draait de allernieuwste Core: v{HUIDIGE_VERSIE} 😎")
            else:
                self._toon_update_dialoog(remote_version)
        except Exception as e:
            messagebox.showerror("Update Fout", f"Verbinding met GitHub Core geweigerd:\n{e}")

    def _toon_update_dialoog(self, nieuwe_versie):
        changelog = "Geen live changelog data gevonden op GitHub repository."
        try:
            req = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                changelog = response.read().decode('utf-8')
        except Exception: pass

        t = THEMES[self.theme_name]
        top = ctk.CTkToplevel()
        top.title("🚀 Update Center - GC-OS")
        top.geometry("560x460")
        top.resizable(False, False)
        top.configure(fg_color=t["bg_root"])
        top.grab_set()

        ctk.CTkLabel(top, text="Systeem Update Beschikbaar!", font=("Segoe UI", 22, "bold"), text_color=t["accent"]).pack(pady=15)
        ctk.CTkLabel(top, text=f"Huidige Core: v{HUIDIGE_VERSIE} ➔ Nieuwe Core: v{nieuwe_versie}", font=("Segoe UI", 13)).pack(pady=2)
        
        txt = ctk.CTkTextbox(top, width=500, height=220, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        txt.insert("1.0", f"Changelog Wijzigingen:\n\n{changelog}")
        txt.configure(state="disabled")
        txt.pack(pady=15)

        # Voortgangsbalk voor UI herkenning
        progress = ctk.CTkProgressBar(top, width=500, mode="indeterminate")

        def voer_update_uit():
            progress.pack(pady=5)
            progress.start()
            
            def download_async():
                try:
                    time.sleep(1) # Visual padding
                    req_script = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_script) as response:
                        nieuw_script = response.read().decode('utf-8')
                    
                    huidig_script = sys.argv[0]
                    with open(huidig_script, "w", encoding="utf-8") as f:
                        f.write(nieuw_script)
                        
                    self.after(0, lambda: succes_update())
                except Exception as e:
                    self.after(0, lambda: fout_update(e))

            def succes_update():
                progress.stop()
                messagebox.showinfo("Update Succes", "GC-OS Update succesvol geïnstalleerd. Het systeem herstart nu.")
                top.destroy()
                os.execv(sys.executable, ['python'] + sys.argv)

            def fout_update(err):
                progress.stop()
                progress.pack_forget()
                messagebox.showerror("Update Mislukt", f"Fout tijdens overschrijven script:\n{err}")

            threading.Thread(target=download_async, daemon=True).start()

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkButton(btn_frame, text="Update Uitvoeren ⚡", fg_color="#2ed573", text_color="#000000", font=("Segoe UI", 13, "bold"), corner_radius=10, height=40, command=voer_update_uit).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Uitstellen", fg_color="#ff4757", text_color="#ffffff", corner_radius=10, height=40, command=top.destroy).pack(side="right", fill="x", expand=True, padx=(10, 0))

    # ============================================================
    # ENGINE CORE MODULES: 1. DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=30)
        
        ctk.CTkLabel(header, text="Overzicht Dashboard", font=("Segoe UI", 28, "bold"), text_color=t["text"]).pack(side="left")
        
        self.clock_label = ctk.CTkLabel(header, text="", font=("Consolas", 15, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right")
        self.update_clock()

        grid = ctk.CTkFrame(self.main, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=35, pady=10)

        # Kaart 1: Huiswerk stats
        card_hw = ctk.CTkFrame(grid, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card_hw.place(relx=0.0, rely=0.0, relwidth=0.48, relheight=0.42)
        
        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        ctk.CTkLabel(card_hw, text="📚 Openstaand Huiswerk", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=25, pady=20)
        ctk.CTkLabel(card_hw, text=f"{hw_open} Taken open", font=("Segoe UI", 36, "bold")).pack(anchor="w", padx=25)

        # Kaart 2: Cijfer gemiddelde
        card_cijfer = ctk.CTkFrame(grid, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card_cijfer.place(relx=0.52, rely=0.0, relwidth=0.48, relheight=0.42)
        
        g_cijfers = []
        for c in self.data["cijfers"]:
            try: g_cijfers.append(float(c["cijfer"]))
            except Exception: pass
            
        gem = sum(g_cijfers) / len(g_cijfers) if g_cijfers else 0.0
        
        ctk.CTkLabel(card_cijfer, text="📊 Gewogen Gemiddelde", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=25, pady=20)
        color_g = "#2ed573" if gem >= 5.5 else ("#ff4757" if gem > 0 else t["text"])
        ctk.CTkLabel(card_cijfer, text=f"{gem:.2f}" if gem > 0 else "N/A", font=("Segoe UI", 42, "bold"), text_color=color_g).pack(anchor="w", padx=25)

        # Kaart 3: Snelnotitie Widget (Onderkant)
        card_quick = ctk.CTkFrame(grid, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card_quick.place(relx=0.0, rely=0.48, relwidth=1.0, relheight=0.46)
        ctk.CTkLabel(card_quick, text="📌 Systeem Notities Quick-View", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=25, pady=15)
        
        quick_txt = ctk.CTkTextbox(card_quick, fg_color="transparent", font=("Segoe UI", 12))
        quick_txt.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        if self.data["notities"]:
            for n in self.data["notities"]: quick_txt.insert("end", f"• {n}\n")
        else:
            quick_txt.insert("1.0", "Geen notities aanwezig in database config.")
        quick_txt.configure(state="disabled")

    def update_clock(self):
        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%H:%M:%S | %d-%m-%Y"))
            self.after(1000, self.update_clock)

    # ============================================================
    # ENGINE CORE MODULES: 2. HUISWERK PLANNER (ZOEKEN + FILTERS)
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=35, pady=25)
        ctk.CTkLabel(top_bar, text="📝 Huiswerk Planner Matrix", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(side="left")
        
        # Snel Zoekbalk
        self.hw_search = ctk.CTkEntry(top_bar, placeholder_text="Zoek op taak/vak...", width=200, corner_radius=8)
        self.hw_search.pack(side="right", padx=(10, 0))
        self.hw_search.bind("<KeyRelease>", lambda e: self._herlaad_huiswerk_lijst())

        # Filter functionaliteit
        self.hw_filter = ctk.CTkComboBox(top_bar, values=["Alle", "Openstaand", "Afgerond"], width=130, state="readonly", command=self._set_hw_filter)
        self.hw_filter.set(self.hw_filter_var)
        self.hw_filter.pack(side="right", padx=10)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.hw_scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.hw_scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._herlaad_huiswerk_lijst()

        # Invoerscherm Rechts
        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=310, border_width=1, border_color=t["border_color"])
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Nieuwe Taak Invoeren", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=20)
        
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly", corner_radius=8)
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=20, pady=6)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Taak omschrijving...", corner_radius=8)
        self.hw_beschrijving.pack(fill="x", padx=20, pady=6)

        datum_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        datum_frame.pack(fill="x", padx=20, pady=6)
        self.hw_datum = ctk.CTkEntry(datum_frame, placeholder_text="YYYY-MM-DD", corner_radius=8)
        self.hw_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(datum_frame, text="📅", width=40, corner_radius=8, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: kies_datum(self.hw_datum)).pack(side="right")

        ctk.CTkButton(
            right_frame, text="🚀 Opslaan in Engine", font=("Segoe UI", 13, "bold"), 
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=10, height=40, command=self._voeg_huiswerk_toe
        ).pack(fill="x", padx=20, pady=25)

    def _set_hw_filter(self, val):
        self.hw_filter_var = val
        self._herlaad_huiswerk_lijst()

    def _herlaad_huiswerk_lijst(self):
        for widget in self.hw_scroll_frame.winfo_children(): widget.destroy()
        t = THEMES[self.theme_name]
        vandaag = dt.date.today()
        zoekterm = self.hw_search.get().lower() if hasattr(self, 'hw_search') else ""

        for i, h in enumerate(self.data["huiswerk"]):
            is_af = h.get("afgerond", False)
            
            # Filters controleren
            if self.hw_filter_var == "Openstaand" and is_af: continue
            if self.hw_filter_var == "Afgerond" and not is_af: continue
            
            # Zoekbalk filteren
            if zoekterm and (zoekterm not in h.get('vak', '').lower() and zoekterm not in h.get('beschrijving', '').lower()):
                continue

            try:
                deadline = dt.datetime.strptime(h.get('datum', ''), "%Y-%m-%d").date()
                te_laat = (deadline <= vandaag) and not is_af
            except Exception: te_laat = False

            row_bg = "#ff4757" if te_laat else (t["bg_root"] if not is_af else "#2ed573")
            txt_color = "#ffffff" if (te_laat or is_af) else t["text"]

            row = ctk.CTkFrame(self.hw_scroll_frame, fg_color=row_bg, corner_radius=10)
            row.pack(fill="x", pady=4, padx=5)

            status_symboon = "✅" if is_af else "⏳"
            taak_tekst = f"{status_symboon} {h.get('vak')} — {h.get('beschrijving')} \n📅 Deadline: {h.get('datum')}"
            
            lbl = ctk.CTkLabel(row, text=taak_tekst, text_color=txt_color, font=("Segoe UI", 12, "bold"), justify="left")
            lbl.pack(side="left", padx=15, pady=8)

            btn_vink = ctk.CTkButton(row, text="✓", width=35, height=30, corner_radius=6, fg_color="#ffffff" if is_af else "#2ed573", text_color="#000000", font=("Segoe UI", 12, "bold"), command=lambda idx=i: self._toggle_huiswerk(idx))
            btn_vink.pack(side="right", padx=5)

            btn_del = ctk.CTkButton(row, text="🗑", width=35, height=30, corner_radius=6, fg_color="#ff6b81", text_color="#ffffff", command=lambda idx=i: self._verwijder_huiswerk(idx))
            btn_del.pack(side="right", padx=10)

    def _voeg_huiswerk_toe(self):
        v, b, d = self.hw_vak.get(), self.hw_beschrijving.get(), self.hw_datum.get()
        if not b or not d: return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()
        self.hw_beschrijving.delete(0, tk.END)
        self.hw_datum.delete(0, tk.END)

    def _toggle_huiswerk(self, index):
        self.data["huiswerk"][index]["afgerond"] = not self.data["huiswerk"][index]["afgerond"]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    def _verwijder_huiswerk(self, index):
        del self.data["huiswerk"][index]
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    # ============================================================
    # ENGINE CORE MODULES: 3. ROOSTER MANAGEMENT SYSTEM
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="📅 Wekelijks Lesrooster Control", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=35, pady=25)
        
        scroll_rooster = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll_rooster.pack(fill="both", expand=True, padx=35, pady=5)
        
        dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
        self.rooster_inputs = {}
        
        for dag in dagen:
            dag_frame = ctk.CTkFrame(scroll_rooster, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
            dag_frame.pack(fill="x", pady=6, padx=5)
            
            ctk.CTkLabel(dag_frame, text=dag, font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=10)
            
            if dag not in self.data["rooster"]: self.data["rooster"][dag] = _standaard_rooster()[dag]
            self.rooster_inputs[dag] = []
            
            for i, les in enumerate(self.data["rooster"][dag]):
                les_row = ctk.CTkFrame(dag_frame, fg_color="transparent")
                les_row.pack(fill="x", padx=20, pady=4)
                
                ctk.CTkLabel(les_row, text=f"{i+1}e Uur:", font=("Segoe UI", 12, "bold"), width=60, text_color=t["text"]).pack(side="left")
                
                tijd_ent = ctk.CTkEntry(les_row, width=120, corner_radius=6)
                tijd_ent.insert(0, les.get("tijd", ""))
                tijd_ent.pack(side="left", padx=5)
                
                les_ent = ctk.CTkEntry(les_row, placeholder_text="Vak / Docent / Lokaal", corner_radius=6)
                les_ent.insert(0, les.get("les", "Geen les"))
                les_ent.pack(side="left", fill="x", expand=True, padx=5)
                
                self.rooster_inputs[dag].append({"tijd": tijd_ent, "les": les_ent})
                
        ctk.CTkButton(
            self.main, text="💾 Rooster Wijzigingen Synchroniseren", font=("Segoe UI", 14, "bold"),
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=12, height=45, command=self._opslaan_rooster
        ).pack(fill="x", padx=40, pady=20)

    def _opslaan_rooster(self):
        for dag, uren in self.rooster_inputs.items():
            self.data["rooster"][dag] = [{"tijd": e["tijd"].get(), "les": e["les"].get()} for e in uren]
        opslaan(self.data)
        messagebox.showinfo("Matrix Synchronisatie", "Rooster succesvol opgeslagen en geback-upt! 🔥")

    # ============================================================
    # ENGINE CORE MODULES: 4. NOTITIEBLOK MANAGEMENT
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="🗒 Systeem Kladblok", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=35, pady=25)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, bg=t["bg_card"], fg=t["text"], selectbackground=t["accent"], selectforeground=t["bg_root"])
        self.note_list.pack(fill="both", expand=True, padx=15, pady=15)
        self.note_list.bind("<<ListboxSelect>>", self._laad_geselecteerde_notitie)
        self._herlaad_notitie_lijst()
        
        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=360, border_width=1, border_color=t["border_color"])
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        self.note_txt = ctk.CTkTextbox(right_frame, font=("Segoe UI", 13), corner_radius=10, fg_color=t["bg_root"], border_width=1, border_color=t["border_color"])
        self.note_txt.pack(fill="both", expand=True, padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Opslaan", corner_radius=8, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._voeg_notitie_toe).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Verwijder", corner_radius=8, fg_color="#ff4757", text_color="#ffffff", command=self._verwijder_notitie).pack(side="right", expand=True, fill="x", padx=(5, 0))

    def _herlaad_notitie_lijst(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]: 
            kort = n.replace('\n', ' ')
            self.note_list.insert(tk.END, f"  📝  {kort[:35]}...")

    def _laad_geselecteerde_notitie(self, event):
        sel = self.note_list.curselection()
        if sel:
            self.note_txt.delete("1.0", tk.END)
            self.note_txt.insert("1.0", self.data["notities"][sel[0]])

    def _voeg_notitie_toe(self):
        tekst = self.note_txt.get("1.0", tk.END).strip()
        if not tekst: return
        self.data["notities"].append(tekst)
        opslaan(self.data)
        self._herlaad_notitie_lijst()
        self.note_txt.delete("1.0", tk.END)

    def _verwijder_notitie(self):
        sel = self.note_list.curselection()
        if not sel: return
        del self.data["notities"][sel[0]]
        opslaan(self.data)
        self._herlaad_notitie_lijst()
        self.note_txt.delete("1.0", tk.END)

    # ============================================================
    # ENGINE CORE MODULES: 5. CIJFEROVERZICHT MATRIX & GRAPHING
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=35, pady=20)
        ctk.CTkLabel(top_bar, text="📊 Cijfer Analyse Center", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(side="left")
        
        self.cijfer_filter = ctk.CTkComboBox(top_bar, values=["Alle Periodes", "Periode 1", "Periode 2", "Periode 3", "Periode 4"], state="readonly", width=140, command=self._set_cijfer_filter)
        self.cijfer_filter.set(self.cijfer_filter_var)
        self.cijfer_filter.pack(side="right", padx=10)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        left_side = ctk.CTkFrame(container, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.graph_card = ctk.CTkFrame(left_side, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        self.graph_card.pack(fill="both", expand=True, pady=(0, 15))
        self._teken_gecombineerde_grafiek()
        
        list_card = ctk.CTkFrame(left_side, corner_radius=15, fg_color=t["bg_card"], height=200, border_width=1, border_color=t["border_color"])
        list_card.pack(fill="x")
        list_card.pack_propagate(False)
        
        self.cijfer_list = tk.Listbox(list_card, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, bg=t["bg_card"], fg=t["text"], selectbackground=t["accent"], selectforeground=t["bg_root"])
        self.cijfer_list.pack(fill="both", expand=True, padx=15, pady=15)
        self._herlaad_cijfer_lijst()
        
        # Invoer Rechter Paneel
        right_side = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=300, border_width=1, border_color=t["border_color"])
        right_side.pack(side="right", fill="y")
        right_side.pack_propagate(False)
        
        ctk.CTkLabel(right_side, text="Cijfer Invoeren", font=("Segoe UI", 16, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        
        self.c_vak = ctk.CTkComboBox(right_side, values=self.vakken_hw, state="readonly", corner_radius=8)
        self.c_vak.set(self.vakken_hw[0])
        self.c_vak.pack(fill="x", padx=20, pady=5)
        
        self.c_num = ctk.CTkEntry(right_side, placeholder_text="Cijfer (bvb 7.5)", corner_radius=8)
        self.c_num.pack(fill="x", padx=20, pady=5)
        
        self.c_weging = ctk.CTkEntry(right_side, placeholder_text="Weging (bvb 1 of 2)", corner_radius=8)
        self.c_weging.insert(0, "1")
        self.c_weging.pack(fill="x", padx=20, pady=5)
        
        self.c_periode = ctk.CTkComboBox(right_side, values=self.periodes, state="readonly", corner_radius=8)
        self.c_periode.set(self.periodes[0])
        self.c_periode.pack(fill="x", padx=20, pady=5)
        
        dat_f = ctk.CTkFrame(right_side, fg_color="transparent")
        dat_f.pack(fill="x", padx=20, pady=5)
        self.c_datum = ctk.CTkEntry(dat_f, placeholder_text="YYYY-MM-DD", corner_radius=8)
        self.c_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dat_f, text="📅", width=40, corner_radius=8, command=lambda: kies_datum(self.c_datum)).pack(side="right")
        
        ctk.CTkButton(right_side, text="✨ Cijfer Opslaan", corner_radius=10, height=38, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._voeg_cijfer_toe).pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(right_side, text="🗑 Verwijder Cijfer", corner_radius=10, height=38, fg_color="#ff4757", text_color="#ffffff", command=self._verwijder_cijfer).pack(fill="x", padx=20, pady=2)

    def _set_cijfer_filter(self, val):
        self.cijfer_filter_var = val
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()

    def _herlaad_cijfer_lijst(self):
        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            if self.cijfer_filter_var != "Alle Periodes" and c.get("periode") != self.cijfer_filter_var:
                continue
            self.cijfer_list.insert(tk.END, f"  📈  {c.get('vak')} ➔ {c.get('cijfer')}  (Weging: {c.get('weging')}x | {c.get('periode')} | {c.get('datum')})")

    def _teken_gecombineerde_grafiek(self):
        for widget in self.graph_card.winfo_children(): widget.destroy()
        
        if 'Figure' not in globals():
            ctk.CTkLabel(self.graph_card, text="Matplotlib visualisatie bibliotheek mist.").pack(expand=True)
            return

        t = THEMES[self.theme_name]
        is_dark = (t["mode"] == "Dark")
        bg_col = t["bg_card"]
        text_col = "#ffffff" if is_dark else "#0f172a"
        
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=bg_col)
        ax = fig.add_subplot(111, facecolor=bg_col)
        
        ax.spines['bottom'].set_color(text_col)
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_color(text_col)
        ax.spines['right'].set_none()
        ax.tick_params(colors=text_col, labelsize=9)
        ax.grid(True, color="#334155" if is_dark else "#cbd5e1", linestyle="--", linewidth=0.5)
        
        vak_data = {vak: [] for vak in self.vakken_hw}
        for c in self.data.get("cijfers", []):
            if self.cijfer_filter_var != "Alle Periodes" and c.get("periode") != self.cijfer_filter_var:
                continue
            vak = c.get("vak")
            if vak in vak_data:
                try:
                    cijfer_val = float(c.get("cijfer"))
                    datum_val = dt.datetime.strptime(c.get("datum", "2026-01-01"), "%Y-%m-%d").date()
                    vak_data[vak].append((datum_val, cijfer_val))
                except ValueError: pass

        heeft_data = False
        for vak, lijsten in vak_data.items():
            if len(lijsten) > 0:
                lijsten.sort(key=lambda x: x[0])
                datums = [x[0] for x in lijsten]
                cijfers = [x[1] for x in lijsten]
                ax.plot(datums, cijfers, marker='o', label=vak, linewidth=2.5, antialiased=True)
                heeft_data = True
                
        if heeft_data:
            ax.legend(loc="upper left", fontsize=8, facecolor=bg_col, labelcolor=text_col, framealpha=0.6)
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, "Geen cijfer data gevonden voor deze selectie.", color=text_col, ha='center', va='center', transform=ax.transAxes, fontname="Segoe UI", fontsize=12)
                    
        ax.set_ylim(1.0, 10.5)
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

    def _voeg_cijfer_toe(self):
        v, n, w, p, d = self.c_vak.get(), self.c_num.get().replace(',', '.'), self.c_weging.get(), self.c_periode.get(), self.c_datum.get()
        if not n or not d: return
        try: float(n)
        except ValueError: return
            
        self.data["cijfers"].append({"vak": v, "cijfer": n, "weging": w, "periode": p, "datum": d})
        opslaan(self.data)
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()
        self.c_num.delete(0, tk.END)
        self.c_datum.delete(0, tk.END)

    def _verwijder_cijfer(self):
        sel = self.cijfer_list.curselection()
        if not sel: return
        
        # Match geselecteerde filter index terug naar hoofd data model
        gefilterde_lijst = []
        for idx, c in enumerate(self.data["cijfers"]):
            if self.cijfer_filter_var == "Alle Periodes" or c.get("periode") == self.cijfer_filter_var:
                gefilterde_lijst.append(idx)
                
        doel_index = gefilterde_lijst[sel[0]]
        del self.data["cijfers"][doel_index]
        
        opslaan(self.data)
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()

    # ============================================================
    # ENGINE CORE MODULES: 6. INSTELLINGSBEHEER
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="⚙ Instellingen & Systeem Engine", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=35, pady=25)
        
        card_theme = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card_theme.pack(fill="x", padx=35, pady=10)
        
        ctk.CTkLabel(card_theme, text="Kies Core UI Skin Versie:", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(side="left", padx=25, pady=25)
        
        self.theme_combo = ctk.CTkComboBox(card_theme, values=list(THEMES.keys()), state="readonly", corner_radius=8, command=self._verander_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(side="left", padx=10)

        card_update = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card_update.pack(fill="x", padx=35, pady=10)

        ctk.CTkLabel(card_update, text="GitHub Update Sync Engine Protocol:", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(side="left", padx=25, pady=25)
        
        ctk.CTkButton(
            card_update, text="🔄 Handmatige Sync Starten", font=("Segoe UI", 13, "bold"),
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=8, command=self._handmatige_update_check
        ).pack(side="right", padx=25, pady=20)

    def _verander_thema(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

# ============================================================
# START OS REVOLUTION ENGINE EXECUTION
# ============================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
