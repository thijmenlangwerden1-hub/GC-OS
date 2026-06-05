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
# SYSTEM CONFIGURATION & VERSIONING (v10.0.0v)
# ============================================================
HUIDIGE_VERSIE = "10.0.0v"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/changelog.txt"

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    print("[WAARSCHUWING] Matplotlib mist. Installeer via: pip install matplotlib")

# ============================================================
# NEW MAGISTER NEON THEME PALETTE
# ============================================================
THEMES = {
    "Magister Neon (Dark)": {
        "mode": "Dark",
        "bg_root": "#0d0722",         # Diep donkerpaars
        "bg_sidebar": "#160d33",      # Zijbalk paars
        "bg_main": "#0d0722",         # Hoofdscherm basis
        "bg_card": "#1c1242",         # Glassmorphism kaart look
        "border_color": "#332463",    # Subtiele paarse randen
        "text": "#ffffff",
        "sidebar_text": "#ffffff",
        "button_text": "#ffffff",
        "button_fg": "#ff3366",       # Magister roze/oranje accent
        "button_hover": "#cc244f",
        "accent": "#00f0ff",          # Neon cyaan voor tijden en koppen
        "badge_bg": "#291b54"         # Donkerpaars voor lesuur badges
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
        with open(BACKUP_BESTAND, "w", encoding="utf-8") as fb:
            json.dump(data, fb, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Systeemfout", f"Kan data niet wegschrijven:\n{e}")

def _standaard_rooster():
    rooster = {}
    dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
    for week in range(1, 5):
        w_key = f"Week {week}"
        rooster[w_key] = {}
        for d in dagen:
            if d == "Vrijdag":
                rooster[w_key][d] = [
                    {"tijd": "08:30 - 09:00", "les": "Netwerken (T311) - N. Schooneveldt (SHNV)"},
                    {"tijd": "09:00 - 09:30", "les": "Netwerken (T311) - N. Schooneveldt (SHNV)"},
                    {"tijd": "09:30 - 10:00", "les": "Netwerken (T311) - N. Schooneveldt (SHNV)"},
                    {"tijd": "10:30 - 11:00", "les": "Slbslab (T311) - A. Brolsma (BRM)"},
                    {"tijd": "11:00 - 11:30", "les": "Slbslab (T311) - A. Brolsma (BRM)"},
                    {"tijd": "11:30 - 12:00", "les": "Slbslab (T311) - A. Brolsma (BRM)"},
                    {"tijd": "12:30 - 13:00", "les": "Netwerken (T315) - N. Schooneveldt (SHNV)"},
                    {"tijd": "13:00 - 13:30", "les": "Netwerken (T315) - N. Schooneveldt (SHNV)"}
                ]
            else:
                rooster[w_key][d] = [
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
            "huiswerk": [{"vak": "Nederlands", "beschrijving": "We werken aan lezen en luisteren verkort in Taalblokken!", "datum": "2026-06-08", "afgerond": False}],
            "notities": ["Systeembestanden geladen in Magister-stijl."],
            "cijfers": [{"vak": "Nederlands 2F", "cijfer": "8.4", "weging": "1", "periode": "Periode 4"}],
            "rooster": _standaard_rooster(),
            "settings": {"theme": "Magister Neon (Dark)"}
        }
    
    with open(BESTAND, "r", encoding="utf-8") as f:
        try: data = json.load(f)
        except Exception: data = {}

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data: data["rooster"] = _standaard_rooster()
    if "settings" not in data: data["settings"] = {"theme": "Magister Neon (Dark)"}
    return data

def kies_datum(entry_widget):
    top = ctk.CTkToplevel()
    top.title("Kies Datum")
    top.geometry("320x360")
    top.resizable(False, False)
    top.grab_set()
    
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=15, fill="both", expand=True, padx=10)
    
    def selecteer():
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, cal.get_date())
        top.destroy()
        
    ctk.CTkButton(top, text="📅 Bevestigen", font=("Segoe UI", 12, "bold"), command=selecteer).pack(pady=10, padx=10, fill="x")

# ============================================================
# MAIN APPLICATION INTERFACE
# ============================================================
class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.data = laden()
        self.theme_name = "Magister Neon (Dark)"

        self.title(f"GraafschapCollege-OS Magister Engine [v{HUIDIGE_VERSIE}]")
        self.geometry("1300://780")
        self.minsize(1150, 720)

        self.vakken_hw = ["Nederlands", "Engels", "Rekenen", "Hardware", "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Project"]
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]
        self.sidebar_buttons = []
        self.hw_filter_var = "Alle"
        self.cijfer_filter_var = "Alle Periodes"
        self.huidige_rooster_week = "Week 1"
        self.geselecteerde_rooster_dag = "Vrijdag"

        self._build_layout()
        self.apply_theme()
        
        if "--post-update" in sys.argv:
            self.toon_post_update_loader()
        else:
            self.show_dashboard()
        
        threading.Thread(target=self._check_updates_background, daemon=True).start()

    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])
        self.sidebar.configure(fg_color=t["bg_sidebar"])
        self.main.configure(fg_color=t["bg_main"])

        for btn in self.sidebar_buttons:
            btn.configure(
                fg_color="transparent", 
                hover_color="#24194c", 
                text_color="#b3b0cb"
            )

    def _build_layout(self):
        # --- LINKER SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=(25, 20), padx=20, fill="x")
        
        logo_label = ctk.CTkLabel(brand_frame, text="Magister.", font=("Segoe UI", 26, "bold"), text_color="#ffffff")
        logo_label.pack(side="left")
        dot_label = ctk.CTkLabel(brand_frame, text="●", font=("Segoe UI", 10), text_color="#ff3366")
        dot_label.pack(side="left", anchor="n", pady=8, padx=2)

        buttons = [
            ("🏠    Start", self.show_dashboard),
            ("📝    Huiswerk", self.show_huiswerk),
            ("📅    Rooster Matrix", self.show_rooster),
            ("🗒    Kladblok", self.show_notities),
            ("📊    Cijfer Matrix", self.show_cijfers),
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w", 
                font=("Segoe UI", 14, "medium"), height=45, 
                corner_radius=8, command=cmd
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.sidebar_buttons.append(btn)

        settings_btn = ctk.CTkButton(
            self.sidebar, text="⚙    Instellingen", anchor="w", 
            font=("Segoe UI", 14, "medium"), height=45, 
            corner_radius=8, command=self.show_settings
        )
        settings_btn.pack(side="bottom", fill="x", padx=12, pady=20)
        self.sidebar_buttons.append(settings_btn)

        # --- HOOFD PANEL ---
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children(): 
            widget.destroy()

    # ============================================================
    # UPDATE ENGINE INTERFACES
    # ============================================================
    def toon_post_update_loader(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        self.sidebar.pack_forget()
        
        loader_container = ctk.CTkFrame(self.main, fg_color=t["bg_root"])
        loader_container.pack(fill="both", expand=True)
        
        ctk.CTkLabel(loader_container, text="Magister OS Engine", font=("Segoe UI", 36, "bold"), text_color=t["button_fg"]).pack(pady=(200, 10))
        status_lbl = ctk.CTkLabel(loader_container, text="Systeemregisters en componenten updaten...", font=("Segoe UI", 14, "italic"))
        status_lbl.pack()
        
        p_bar = ctk.CTkProgressBar(loader_container, width=400, height=12, progress_color=t["button_fg"], fg_color=t["bg_card"])
        p_bar.set(0)
        p_bar.pack(pady=20)

        def simuleer_installatie(stap=0):
            if stap <= 100:
                p_bar.set(stap / 100)
                if stap == 40: status_lbl.configure(text="Nieuwe UI shaders compileren...")
                elif stap == 80: status_lbl.configure(text="Data caches herstructureren...")
                self.after(15, lambda: simuleer_installatie(stap + 1))
            else:
                self.sidebar.pack(side="left", fill="y")
                if "--post-update" in sys.argv: sys.argv.remove("--post-update")
                self.show_dashboard()

        self.after(100, lambda: simuleer_installatie(0))

    def _check_updates_background(self):
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version != HUIDIGE_VERSIE:
                self.after(1000, lambda: self._toon_update_dialoog(remote_version))
        except Exception: pass

    def _handmatige_update_check(self):
        try:
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version == HUIDIGE_VERSIE:
                messagebox.showinfo("Update Info", "Je draait al de allernieuwste Magister Core! ✨")
            else:
                self._toon_update_dialoog(remote_version)
        except Exception as e:
            messagebox.showerror("Fout", f"Kan geen verbinding maken: {e}")

    def _toon_update_dialoog(self, nieuwe_versie):
        t = THEMES[self.theme_name]
        top = ctk.CTkToplevel()
        top.title("🚀 Update Center")
        top.geometry("500 rounded x 400")
        top.resizable(False, False)
        top.configure(fg_color=t["bg_root"])
        top.grab_set()

        ctk.CTkLabel(top, text="Systeem Update Beschikbaar", font=("Segoe UI", 20, "bold"), text_color=t["button_fg"]).pack(pady=15)
        
        txt = ctk.CTkTextbox(top, width=440, height=180, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        txt.insert("1.0", f"Huidige versie: v{HUIDIGE_VERSIE}\nNieuwe versie: v{nieuwe_versie}\n\nStabiliteitsfixes voor Windows file locking en geoptimaliseerde Magister UI visualisatie componenten.")
        txt.configure(state="disabled")
        txt.pack(pady=10)

        status_lbl = ctk.CTkLabel(top, text="Status: Gereed")
        p_bar = ctk.CTkProgressBar(top, width=440, progress_color=t["accent"])

        def voer_update_uit():
            top.unbind("<Destroy>")
            status_lbl.pack(pady=2)
            p_bar.pack(pady=5)
            p_bar.set(0)
            
            def download_async():
                try:
                    req_script = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_script) as response:
                        nieuw_script = response.read().decode('utf-8')
                    
                    huidig_script = os.path.abspath(sys.argv[0])
                    tijdelijk_script = huidig_script + ".tmp"
                    
                    with open(tijdelijk_script, "w", encoding="utf-8") as f:
                        f.write(nieuw_script)
                    
                    if os.name == 'nt':
                        cmd = f"timeout /t 1 /nobreak && move /y \"{tijdelijk_script}\" \"{huidig_script}\" && start python \"{huidig_script}\" --post-update"
                    else:
                        cmd = f"sleep 1 && mv -f \"{tijdelijk_script}\" \"{huidig_script}\" && python3 \"{huidig_script}\" --post-update &"
                    
                    subprocess.Popen(cmd, shell=True)
                    sys.exit()
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Fout", f"Update mislukt: {e}"))

            threading.Thread(target=download_async, daemon=True).start()

        ctk.CTkButton(top, text="Update Nu ⚡", fg_color="#2ed573", text_color="#000000", font=("Segoe UI", 12, "bold"), command=voer_update_uit).pack(pady=15)

    # ============================================================
    # MODULE 1: RE-IMAGINED MAGISTER START / DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        # Top Bar
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(20, 10))
        
        vandaag_str = dt.datetime.now().strftime("Vrijdag %d juni")
        ctk.CTkLabel(top_bar, text=vandaag_str, font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(side="left")
        
        nav_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        nav_frame.pack(side="right")
        ctk.CTkButton(nav_frame, text="‹", width=30, fg_color=t["bg_card"], text_color="#ffffff").pack(side="left", padx=2)
        ctk.CTkButton(nav_frame, text="›", width=30, fg_color=t["bg_card"], text_color="#ffffff").pack(side="left", padx=2)
        ctk.CTkButton(nav_frame, text="Dag ▼", width=70, fg_color=t["bg_card"], text_color="#ffffff").pack(side="left", padx=10)

        # Content Box Splitter
        content_box = ctk.CTkFrame(self.main, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=30, pady=10)

        # ROOSTER KOLOM (Midden)
        rooster_kolom = ctk.CTkFrame(content_box, fg_color="transparent")
        rooster_kolom.pack(side="left", fill="both", expand=True, padx=(0, 20))

        scroll_rooster = ctk.CTkScrollableFrame(rooster_kolom, fg_color="transparent")
        scroll_rooster.pack(fill="both", expand=True)

        vrijdag_lessen = self.data["rooster"].get(self.huidige_rooster_week, {}).get("Vrijdag", [])
        
        for i, les in enumerate(vrijdag_lessen):
            les_card = ctk.CTkFrame(scroll_rooster, fg_color=t["bg_card"], corner_radius=10, border_width=1, border_color=t["border_color"])
            les_card.pack(fill="x", pady=5, padx=2)

            badge = ctk.CTkFrame(les_card, width=35, height=35, corner_radius=6, fg_color=t["badge_bg"])
            badge.pack(side="left", padx=15, pady=10)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=str(i+2), font=("Segoe UI", 13, "bold"), text_color="#ffffff").pack(expand=True)

            details_frame = ctk.CTkFrame(les_card, fg_color="transparent")
            details_frame.pack(side="left", fill="both", expand=True, pady=8)
            
            ctk.CTkLabel(details_frame, text=les["les"], font=("Segoe UI", 14, "bold"), text_color="#ffffff").pack(anchor="w")
            ctk.CTkLabel(details_frame, text=les["tijd"], font=("Consolas", 11), text_color=t["accent"]).pack(anchor="w")

        # WIDGET KOLOM (Rechts)
        widget_kolom = ctk.CTkFrame(content_box, width=320, fg_color="transparent")
        widget_kolom.pack(side="right", fill="y")
        widget_kolom.pack_propagate(False)

        # Klok Widget
        clock_card = ctk.CTkFrame(widget_kolom, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border_color"])
        clock_card.pack(fill="x", pady=(0, 15))
        self.clock_label = ctk.CTkLabel(clock_card, text="", font=("Consolas", 32, "bold"), text_color="#ffffff")
        self.clock_label.pack(pady=15)
        self.update_clock()

        # Cijfer Widget
        cijfer_card = ctk.CTkFrame(widget_kolom, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border_color"])
        cijfer_card.pack(fill="x", pady=15)
        ctk.CTkLabel(cijfer_card, text="Nieuwe cijfers", font=("Segoe UI", 13), text_color="#b3b0cb").pack(pady=(12, 0))
        laatste_cijfer = self.data["cijfers"][-1] if self.data["cijfers"] else {"cijfer": "N/A", "vak": "Geen data"}
        ctk.CTkLabel(cijfer_card, text=laatste_cijfer["cijfer"], font=("Segoe UI", 46, "bold"), text_color="#ffffff").pack()
        ctk.CTkLabel(cijfer_card, text=laatste_cijfer["vak"], font=("Segoe UI", 13, "bold"), text_color="#ffffff").pack()
        ctk.CTkLabel(cijfer_card, text="Berekend engine resultaat", font=("Segoe UI", 11), text_color="#b3b0cb").pack(pady=(0, 12))

        # Huiswerk Widget
        hw_card = ctk.CTkFrame(widget_kolom, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border_color"])
        hw_card.pack(fill="both", expand=True, pady=(15, 0))
        ctk.CTkLabel(hw_card, text="Huiswerk Overzicht", font=("Segoe UI", 14, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=12)
        
        for hw in self.data["huiswerk"][:2]:
            item_box = ctk.CTkFrame(hw_card, fg_color="#241754", corner_radius=8)
            item_box.pack(fill="x", padx=12, pady=5)
            ctk.CTkLabel(item_box, text=hw["vak"], font=("Segoe UI", 13, "bold"), text_color="#ffffff").pack(anchor="w", padx=10, pady=(5, 0))
            ctk.CTkLabel(item_box, text=hw["beschrijving"], font=("Segoe UI", 11), text_color="#b3b0cb", wraplength=260, justify="left").pack(anchor="w", padx=10, pady=(0, 5))

    def update_clock(self):
        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%H:%M:%S"))
            self.after(1000, self.update_clock)

    # ============================================================
    # MODULE 2: HUISWERK PLANNER MATRIX
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(top_bar, text="📝 Huiswerk Matrix Planner", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(side="left")
        
        self.hw_filter = ctk.CTkComboBox(top_bar, values=["Alle", "Openstaand", "Afgerond"], width=130, state="readonly", command=self._set_hw_filter)
        self.hw_filter.set(self.hw_filter_var)
        self.hw_filter.pack(side="right")

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.hw_scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.hw_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._herlaad_huiswerk_lijst()

        right_frame = ctk.CTkFrame(container, corner_radius=12, fg_color=t["bg_card"], width=300, border_width=1, border_color=t["border_color"])
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Taak Toevoegen", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=20, pady=5)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving...")
        self.hw_beschrijving.pack(fill="x", padx=20, pady=5)

        d_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        d_frame.pack(fill="x", padx=20, pady=5)
        self.hw_datum = ctk.CTkEntry(d_frame, placeholder_text="YYYY-MM-DD")
        self.hw_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(d_frame, text="📅", width=35, fg_color="#241754", command=lambda: kies_datum(self.hw_datum)).pack(side="right")

        ctk.CTkButton(right_frame, text="Opslaan", fg_color=t["button_fg"], hover_color=t["button_hover"], command=self._voeg_huiswerk_toe).pack(fill="x", padx=20, pady=20)

    def _set_hw_filter(self, val):
        self.hw_filter_var = val
        self._herlaad_huiswerk_lijst()

    def _herlaad_huiswerk_lijst(self):
        for w in self.hw_scroll_frame.winfo_children(): w.destroy()
        t = THEMES[self.theme_name]

        for i, h in enumerate(self.data["huiswerk"]):
            is_af = h.get("afgerond", False)
            if self.hw_filter_var == "Openstaand" and is_af: continue
            if self.hw_filter_var == "Afgerond" and not is_af: continue

            row = ctk.CTkFrame(self.hw_scroll_frame, fg_color="#241754" if not is_af else "#1b4d3e", corner_radius=8)
            row.pack(fill="x", pady=4, padx=2)

            lbl_txt = f"{h.get('vak')} - {h.get('beschrijving')} \n📅 {h.get('datum')}"
            ctk.CTkLabel(row, text=lbl_txt, justify="left", font=("Segoe UI", 12)).pack(side="left", padx=15, pady=8)

            ctk.CTkButton(row, text="✓", width=30, fg_color="#2ed573", text_color="#000000", command=lambda idx=i: self._toggle_huiswerk(idx)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="🗑", width=30, fg_color="#ff4757", command=lambda idx=i: self._verwijder_huiswerk(idx)).pack(side="right", padx=5)

    def _voeg_huiswerk_toe(self):
        v, b, d = self.hw_vak.get(), self.hw_beschrijving.get(), self.hw_datum.get()
        if b and d:
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
    # MODULE 3: ROOSTER CONFIGURATION MATRIX
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(top_bar, text="📅 Rooster Editor Matrix", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(side="left")
        
        self.dag_selector = ctk.CTkComboBox(top_bar, values=["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"], state="readonly", width=120, command=self._wissel_rooster_dag)
        self.dag_selector.set(self.geselecteerde_rooster_dag)
        self.dag_selector.pack(side="right", padx=5)

        self.week_selector = ctk.CTkComboBox(top_bar, values=["Week 1", "Week 2", "Week 3", "Week 4"], state="readonly", width=100, command=self._wissel_rooster_week)
        self.week_selector.set(self.huidige_rooster_week)
        self.week_selector.pack(side="right", padx=5)

        scroll_rooster = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll_rooster.pack(fill="both", expand=True, padx=30)
        
        w_key = self.huidige_rooster_week
        d_key = self.geselecteerde_rooster_dag
        
        self.rooster_inputs = {w_key: {d_key: []}}
        lessen = self.data["rooster"].get(w_key, {}).get(d_key, [])

        for i, les in enumerate(lessen):
            row = ctk.CTkFrame(scroll_rooster, fg_color=t["bg_card"], corner_radius=8, border_width=1, border_color=t["border_color"])
            row.pack(fill="x", pady=4, padx=2)
            
            ctk.CTkLabel(row, text=f"Les {i+1}: ", width=50).pack(side="left", padx=10)
            
            tijd_ent = ctk.CTkEntry(row, width=120, fg_color=t["bg_root"])
            tijd_ent.insert(0, les.get("tijd", ""))
            tijd_ent.pack(side="left", padx=5, pady=8)
            
            les_ent = ctk.CTkEntry(row, fg_color=t["bg_root"])
            les_ent.insert(0, les.get("les", ""))
            les_ent.pack(side="left", fill="x", expand=True, padx=5, pady=8)
            
            self.rooster_inputs[w_key][d_key].append({"tijd": tijd_ent, "les": les_ent})

        ctk.CTkButton(self.main, text="💾 Rooster Opslaan", fg_color=t["button_fg"], hover_color=t["button_hover"], command=self._opslaan_rooster).pack(fill="x", padx=30, pady=20)

    def _wissel_rooster_week(self, gk):
        self.huidige_rooster_week = gk
        self.show_rooster()

    def _wissel_rooster_dag(self, gd):
        self.geselecteerde_rooster_dag = gd
        self.show_rooster()

    def _opslaan_rooster(self):
        w = self.huidige_rooster_week
        d = self.geselecteerde_rooster_dag
        self.data["rooster"][w][d] = [{"tijd": e["tijd"].get(), "les": e["les"].get()} for e in self.rooster_inputs[w][d]]
        opslaan(self.data)
        messagebox.showinfo("Matrix Link", "Systeemedities succesvol weggeschreven!")
        self.show_dashboard()

    # ============================================================
    # MODULE 4: NOTITIEBLOK SYSTEM
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="🗒 Systeem Kladblok", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(anchor="w", padx=30, pady=20)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        left_frame = ctk.CTkFrame(container, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, bg=t["bg_card"], fg="#ffffff", selectbackground=t["button_fg"])
        self.note_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.note_list.bind("<<ListboxSelect>>", self._laad_geselecteerde_notitie)
        self._herlaad_notitie_lijst()
        
        right_frame = ctk.CTkFrame(container, corner_radius=12, fg_color=t["bg_card"], width=320, border_width=1, border_color=t["border_color"])
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        self.note_txt = ctk.CTkTextbox(right_frame, font=("Segoe UI", 12), fg_color=t["bg_root"])
        self.note_txt.pack(fill="both", expand=True, padx=15, pady=15)
        
        b_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        b_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(b_frame, text="Opslaan", width=130, fg_color=t["button_fg"], command=self._voeg_notitie_toe).pack(side="left")
        ctk.CTkButton(b_frame, text="Verwijderen", width=130, fg_color="#ff4757", command=self._verwijder_notitie).pack(side="right")

    def _herlaad_notitie_lijst(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]:
            self.note_list.insert(tk.END, f"  📝  {n[:30]}...")

    def _laad_geselecteerde_notitie(self, event):
        sel = self.note_list.curselection()
        if sel:
            self.note_txt.delete("1.0", tk.END)
            self.note_txt.insert("1.0", self.data["notities"][sel[0]])

    def _voeg_notitie_toe(self):
        txt = self.note_txt.get("1.0", tk.END).strip()
        if txt:
            self.data["notities"].append(txt)
            opslaan(self.data)
            self._herlaad_notitie_lijst()
            self.note_txt.delete("1.0", tk.END)

    def _verwijder_notitie(self):
        sel = self.note_list.curselection()
        if sel:
            del self.data["notities"][sel[0]]
            opslaan(self.data)
            self._herlaad_notitie_lijst()
            self.note_txt.delete("1.0", tk.END)

    # ============================================================
    # MODULE 5: CIJFER ANALYSE MATRIX
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(top_bar, text="📊 Cijfer Analyse Matrix", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(side="left")
        
        self.cijfer_filter = ctk.CTkComboBox(top_bar, values=["Alle Periodes", "Periode 1", "Periode 2", "Periode 3", "Periode 4"], state="readonly", command=self._set_cijfer_filter)
        self.cijfer_filter.set(self.cijfer_filter_var)
        self.cijfer_filter.pack(side="right")

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        left_side = ctk.CTkFrame(container, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.graph_card = ctk.CTkFrame(left_side, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        self.graph_card.pack(fill="both", expand=True, pady=(0, 15))
        self._teken_gecombineerde_grafiek()
        
        list_card = ctk.CTkFrame(left_side, corner_radius=12, fg_color=t["bg_card"], height=180, border_width=1, border_color=t["border_color"])
        list_card.pack(fill="x")
        list_card.pack_propagate(False)
        
        self.cijfer_list = tk.Listbox(list_card, font=("Segoe UI", 11), borderwidth=0, bg=t["bg_card"], fg="#ffffff", selectbackground=t["button_fg"])
        self.cijfer_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(list_card, text="🗑 Wissen", fg_color="#ff4757", command=self._verwijder_cijfer).pack(side="right", padx=15, pady=15, anchor="s")
        
        self._herlaad_cijfer_matrix()

        right_side = ctk.CTkFrame(container, corner_radius=12, fg_color=t["bg_card"], width=280, border_width=1, border_color=t["border_color"])
        right_side.pack(side="right", fill="y")
        right_side.pack_propagate(False)

        ctk.CTkLabel(right_side, text="Cijfer Invoeren", font=("Segoe UI", 15, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        self.c_vak = ctk.CTkComboBox(right_side, values=self.vakken_hw, state="readonly")
        self.c_vak.set(self.vakken_hw[0])
        self.c_vak.pack(fill="x", padx=20, pady=5)
        
        self.c_cijfer = ctk.CTkEntry(right_side, placeholder_text="Cijfer...")
        self.c_cijfer.pack(fill="x", padx=20, pady=5)
        
        self.c_weging = ctk.CTkEntry(right_side, placeholder_text="Weging...")
        self.c_weging.insert(0, "1")
        self.c_weging.pack(fill="x", padx=20, pady=5)
        
        self.c_periode = ctk.CTkComboBox(right_side, values=self.periodes, state="readonly")
        self.c_periode.set(self.periodes[0])
        self.c_periode.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(right_side, text="Invoeren", fg_color=t["button_fg"], command=self._voeg_cijfer_toe).pack(fill="x", padx=20, pady=20)

    def _set_cijfer_filter(self, val):
        self.cijfer_filter_var = val
        self._herlaad_cijfer_matrix()
        self._teken_gecombineerde_grafiek()

    def _herlaad_cijfer_matrix(self):
        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            if self.cijfer_filter_var != "Alle Periodes" and c.get("periode") != self.cijfer_filter_var: continue
            self.cijfer_list.insert(tk.END, f"  [{c.get('periode')}] {c.get('vak')} ➔ {c.get('cijfer')} ({c.get('weging')}x)")

    def _voeg_cijfer_toe(self):
        v, c, w, p = self.c_vak.get(), self.c_cijfer.get(), self.c_weging.get(), self.c_periode.get()
        if c:
            self.data["cijfers"].append({"vak": v, "cijfer": c.replace(',', '.'), "weging": w, "periode": p})
            opslaan(self.data)
            self._herlaad_cijfer_matrix()
            self._teken_gecombineerde_grafiek()
            self.c_cijfer.delete(0, tk.END)

    def _verwijder_cijfer(self):
        sel = self.cijfer_list.curselection()
        if sel:
            del self.data["cijfers"][sel[0]]
            opslaan(self.data)
            self._herlaad_cijfer_matrix()
            self._teken_gecombineerde_grafiek()

    def _teken_gecombineerde_grafiek(self):
        for w in self.graph_card.winfo_children(): w.destroy()
        t = THEMES[self.theme_name]
        punten = [float(c["cijfer"]) for c in self.data["cijfers"] if self.cijfer_filter_var == "Alle Periodes" or c.get("periode") == self.cijfer_filter_var]

        fig = Figure(figsize=(5, 2), dpi=100)
        fig.patch.set_facecolor(t["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(t["bg_root"])
        
        if punten:
            ax.plot(punten, marker='o', color=t["accent"], linewidth=2)
        else:
            ax.text(0.5, 0.5, "Geen data", color="#ffffff", ha='center', va='center')
            
        ax.set_ylim(1, 10)
        ax.tick_params(colors="#ffffff", labelsize=8)
        ax.spines['bottom'].set_color(t["border_color"])
        ax.spines['left'].set_color(t["border_color"])
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # INSTELLINGEN INTERFACE
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="⚙ Instellingen", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(anchor="w", padx=30, pady=20)
        card = ctk.CTkFrame(self.main, corner_radius=12, fg_color=t["bg_card"], border_width=1, border_color=t["border_color"])
        card.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        ctk.CTkButton(card, text="🔄 Synchroniseer Updates", fg_color=t["button_fg"], hover_color=t["button_hover"], command=self._handmatige_update_check).pack(anchor="w", padx=30, pady=30)

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
