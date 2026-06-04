import os
import sys
import json
import datetime as dt
import time
import tkinter as tk
from tkinter import messagebox, ttk
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
    "Cyberpunk": {
        "mode": "Dark",
        "bg_root": "#1a0826",
        "bg_sidebar": "#2c0c42",
        "bg_main": "#1a0826",
        "bg_card": "#3d115c",
        "text": "#00ffcc",
        "sidebar_text": "#ff007f",
        "button_text": "#00ffcc",
        "button_fg": "#52167d",
        "button_hover": "#ff007f",
        "accent": "#00ffcc",
        "list_bg": "#2c0c42",
        "list_fg": "#00ffcc",
        "list_select": "#ff007f",
    }
}

MOTIVATIONAL_QUOTES = [
    "Succes is niet finaal, falen is niet fataal: het is de moed om door te gaan die telt.",
    "De beste manier om de toekomst te voorspellen is om hem zelf te creëren.",
    "Loop niet weg voor hardware errors, los ze op!",
    "Code is net als humor. Als je het moet uitleggen, is het slecht.",
    "Blijf gefocust, zet die telefoon op stil en knal die deadlines neer!"
]

# KLEUREN MATRIX VOOR DE VAKKEN GRAFIEK
GRAFIEK_KLEUREN = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#33FFF0", "#FFA500", "#8A2BE2"]

# ============================================================
# CONFIGURATIE & UPDATE INSTELLINGEN
# ============================================================

HUIDIGE_VERSIE = "2.4.14v"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")

# GITHUB URLS
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

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

def laden():
    if not os.path.exists(BESTAND):
        data = {
            "huiswerk": [],
            "notities": [],
            "cijfers": [],
            "rooster": [],
            "doelen": [],
            "settings": {"theme": "Wit", "naam": "Gebruiker"}
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
    if "rooster" not in data: data["rooster"] = []
    if "doelen" not in data: data["doelen"] = []
    if "settings" not in data: data["settings"] = {"theme": "Wit", "naam": "Gebruiker"}
    if "theme" not in data["settings"]: data["settings"]["theme"] = "Wit"
    if "naam" not in data["settings"]: data["settings"]["naam"] = "Gebruiker"

    return data

# ============================================================
# MAIN APPLICATIE
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
        self.geometry("1150x700")

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Vrije Afspraak"
        ]
        
        self.vakken_cijfers = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan"
        ]

        self.rooster_tijden = []
        for uur in range(8, 18):
            self.rooster_tijden.append(f"{uur:02d}:00")
            if uur != 17:
                self.rooster_tijden.append(f"{uur:02d}:30")
        
        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.clock_label = None
        self.rooster_stijl = "Week" 
        self.huidige_rooster_datum = dt.date.today()

        self._build_layout()
        self.apply_theme()

        self.after(100, self.show_intro_screen)

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="GC‑OS v" + HUIDIGE_VERSIE, font=("Segoe UI", 22, "bold")).pack(pady=25)

        buttons = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📝  Huiswerk", self.show_huiswerk),
            ("📅  Rooster", self.show_rooster),
            ("🗒  Notities", self.show_notities),
            ("📊  Cijfers", self.show_cijfers),
            ("🎯  Doelen & Motivatie", self.show_doelen),
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

    def apply_theme(self):
        t = THEMES[self.theme_name]
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg_root"])
        if hasattr(self, "sidebar"): self.sidebar.configure(fg_color=t["bg_sidebar"])
        if hasattr(self, "main"): self.main.configure(fg_color=t["bg_main"])

    def show_intro_screen(self):
        t = THEMES[self.theme_name]
        intro = ctk.CTkToplevel()
        intro.title("GC-OS Intro")
        intro.overrideredirect(True)
        intro.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        intro.lift()
        intro.attributes("-topmost", True)
        intro.configure(fg_color=t["bg_root"])

        label = ctk.CTkLabel(intro, text="GraafschapCollege‑OS", font=("Segoe UI", 50, "bold"), text_color=t["accent"])
        label.place(relx=0.5, rely=0.5, anchor="center")
        
        def sluit_intro():
            intro.destroy()
            self.deiconify()
            self.show_dashboard()

        self.after(1000, sluit_intro)

    # ============================================================
    # DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=20)

        naam = self.data["settings"].get("naam", "Gebruiker")
        ctk.CTkLabel(top_bar, text=f"Welkom terug, {naam}", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(side="left")

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

        ctk.CTkLabel(card, text=f"📚 Huiswerk taken open: {hw_open} van de {hw_total}", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(card, text=f"📊 Jouw algemeen gemiddelde: {gem:.2f}" if gem is not None else "📊 Nog geen cijfers ingevoerd", font=("Segoe UI", 16), text_color=t["text"]).pack(anchor="w", pady=5, padx=10)

        quote_card = ctk.CTkFrame(self.main, corner_radius=15, fg_color=t["bg_card"])
        quote_card.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(quote_card, text="💡 Motivatie voor vandaag:", font=("Segoe UI", 12, "italic"), text_color=t["accent"]).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(quote_card, text=f'"{random.choice(MOTIVATIONAL_QUOTES)}"', font=("Segoe UI", 14), text_color=t["text"], wrap=True).pack(anchor="w", padx=10, pady=5)

    def update_clock(self):
        if self.clock_label and self.clock_label.winfo_exists():
            nu = dt.datetime.now()
            self.clock_label.configure(text=nu.strftime("%d-%m-%Y | %H:%M:%S"))
            self.after(1000, self.update_clock)

    # ============================================================
    # HUISWERK
    # ============================================================
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Huiswerk Planner", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.hw_list = tk.Listbox(left_frame, font=("Segoe UI", 11), activestyle="none", bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"])
        self.hw_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(container, corner_radius=15, fg_color=t["bg_card"], width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly")
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=10, pady=10)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Beschrijving van taak")
        self.hw_beschrijving.pack(fill="x", padx=10, pady=5)

        self.hw_datum = ctk.CTkEntry(right_frame, placeholder_text="yyyy-mm-dd")
        self.hw_datum.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(right_frame, text="📅 Kies datum", command=lambda: kies_datum(self.hw_datum)).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right_frame, text="Toevoegen", fg_color=t["accent"], text_color="white", command=self.hw_toevoegen).pack(fill="x", padx=10, pady=15)
        ctk.CTkButton(right_frame, text="Markeer Afgerond", command=self.hw_afronden).pack(fill="x", padx=10, pady=5)
        
        self._herlaad_huiswerk_lijst()

    def _herlaad_huiswerk_lijst(self):
        self.hw_list.delete(0, tk.END)
        for h in self.data["huiswerk"]:
            status = "✔" if h.get("afgerond") else "❌"
            self.hw_list.insert(tk.END, f"[{status}] {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

    def hw_toevoegen(self):
        v = self.hw_vak.get()
        b = self.hw_beschrijving.get().strip()
        d = self.hw_datum.get().strip()
        if not b or not d: return
        self.data["huiswerk"].append({"vak": v, "beschrijving": b, "datum": d, "afgerond": False})
        opslaan(self.data)
        self._herlaad_huiswerk_lijst()

    def hw_afronden(self):
        try:
            index = self.hw_list.curselection()[0]
            self.data["huiswerk"][index]["afgerond"] = True
            opslaan(self.data)
            self._herlaad_huiswerk_lijst()
        except Exception: pass

    # ============================================================
    # ROOSTER (STRAKKER GRID DESIGN)
    # ============================================================
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        top_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(top_frame, text="Mijn Rooster", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(side="left")

        ctk.CTkButton(top_frame, text="Week", width=80, command=lambda: self.wissel_rooster_stijl("Week")).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="Maand", width=80, command=lambda: self.wissel_rooster_stijl("Maand")).pack(side="right", padx=5)

        nav_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(nav_frame, text="◀ Vorige", width=80, command=self.rooster_vorige).pack(side="left")
        self.rooster_datum_label = ctk.CTkLabel(nav_frame, text="", font=("Segoe UI", 16, "bold"), text_color=t["text"])
        self.rooster_datum_label.pack(side="left", expand=True)
        ctk.CTkButton(nav_frame, text="Volgende ▶", width=80, command=self.rooster_volgende).pack(side="right")

        # Hoofdcontainer voor het strakke grid
        self.rooster_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.rooster_container.pack(fill="both", expand=True, padx=20, pady=10)

        # De toevoegbalk onderaan het scherm
        add_frame = ctk.CTkFrame(self.main, fg_color=t["bg_card"], corner_radius=10)
        add_frame.pack(fill="x", padx=20, pady=10)

        self.rst_vak = ctk.CTkComboBox(add_frame, values=self.vakken_hw, width=150, state="readonly")
        self.rst_vak.set(self.vakken_hw[0])
        self.rst_vak.pack(side="left", padx=10, pady=10)

        self.rst_datum = ctk.CTkEntry(add_frame, placeholder_text="yyyy-mm-dd", width=110)
        self.rst_datum.insert(0, str(dt.date.today()))
        self.rst_datum.pack(side="left", padx=5, pady=10)

        self.rst_tijd_combo = ctk.CTkComboBox(add_frame, values=self.rooster_tijden, width=100, state="readonly")
        self.rst_tijd_combo.set("08:30")
        self.rst_tijd_combo.pack(side="left", padx=5, pady=10)

        ctk.CTkButton(add_frame, text="➕ Les Toevoegen", fg_color=t["accent"], text_color="white", command=self.rooster_toevoegen).pack(side="right", padx=10, pady=10)

        self.bouw_rooster_weergave()

    def wissel_rooster_stijl(self, stijl):
        self.rooster_stijl = stijl
        self.bouw_rooster_weergave()

    def rooster_vorige(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum -= dt.timedelta(days=7)
        else:
            self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=1) - dt.timedelta(days=1))
        self.bouw_rooster_weergave()

    def rooster_volgende(self):
        if self.rooster_stijl == "Week":
            self.huidige_rooster_datum += dt.timedelta(days=7)
        else:
            self.huidige_rooster_datum = (self.huidige_rooster_datum.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
        self.bouw_rooster_weergave()

    def bouw_rooster_weergave(self):
        for w in self.rooster_container.winfo_children(): w.destroy()
        t = THEMES[self.theme_name]

        if self.rooster_stijl == "Week":
            # Grid layout configureren voor strakke gelijke kolommen
            for col_idx in range(5):
                self.rooster_container.grid_columnconfigure(col_idx, weight=1, uniform="dag_kolom")
            self.rooster_container.grid_rowconfigure(0, weight=1)

            start_vd_week = self.huidige_rooster_datum - dt.timedelta(days=self.huidige_rooster_datum.weekday())
            eind_vd_week = start_vd_week + dt.timedelta(days=4)
            self.rooster_datum_label.configure(text=f"Week: {start_vd_week.strftime('%d %b')} t/m {eind_vd_week.strftime('%d %b %Y')}")

            dagen_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
            for i, naam in enumerate(dagen_namen):
                dag_datum = start_vd_week + dt.timedelta(days=i)
                dag_str = dag_datum.strftime("%Y-%m-%d")

                col = ctk.CTkFrame(self.rooster_container, fg_color=t["bg_card"], corner_radius=12)
                col.grid(row=0, column=i, sticky="nsew", padx=4, pady=5)

                header = ctk.CTkFrame(col, fg_color=t["accent"] if t["mode"] == "Dark" else t["button_fg"], corner_radius=8, height=45)
                header.pack(fill="x", padx=4, pady=4)
                header.pack_propagate(False)

                ctk.CTkLabel(header, text=f"{naam} ({dag_datum.strftime('%d-%m')})", font=("Segoe UI", 12, "bold"), text_color="#ffffff" if t["mode"] == "Dark" else t["text"]).pack(expand=True)

                scroll_col = ctk.CTkScrollableFrame(col, fg_color="transparent", corner_radius=0)
                scroll_col.pack(fill="both", expand=True, padx=2, pady=2)

                dag_lessen = [l for l in self.data["rooster"] if l.get("datum") == dag_str]
                dag_lessen.sort(key=lambda x: x.get("tijd", ""))

                for les in dag_lessen:
                    les_box = ctk.CTkFrame(scroll_col, fg_color=t["bg_root"], corner_radius=8, border_width=1, border_color=t["button_hover"])
                    les_box.pack(fill="x", padx=4, pady=4)
                    
                    lbl_tijd = ctk.CTkLabel(les_box, text=les.get('tijd'), font=("Segoe UI", 11, "bold"), text_color=t["accent"])
                    lbl_tijd.pack(anchor="w", padx=10, pady=(4, 0))
                    
                    lbl_vak = ctk.CTkLabel(les_box, text=les.get('vak'), font=("Segoe UI", 12), text_color=t["text"])
                    lbl_vak.pack(anchor="w", padx=10, pady=(0, 4))
        else:
            # Maand view via een Scrollable Frame
            scroll_maand = ctk.CTkScrollableFrame(self.rooster_container, fg_color=t["bg_card"], corner_radius=15)
            scroll_maand.pack(fill="both", expand=True)
            
            m_jaar = self.huidige_rooster_datum.year
            m_maand = self.huidige_rooster_datum.month
            self.rooster_datum_label.configure(text=self.huidige_rooster_datum.strftime("%B %Y"))

            maand_lessen = []
            for l in self.data["rooster"]:
                try:
                    ld = dt.datetime.strptime(l.get("datum"), "%Y-%m-%d").date()
                    if ld.year == m_jaar and ld.month == m_maand:
                        maand_lessen.append(l)
                except Exception: pass

            maand_lessen.sort(key=lambda x: (x.get("datum"), x.get("tijd")))
            if not maand_lessen:
                ctk.CTkLabel(scroll_maand, text="Geen geplande lessen deze maand.", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=20)
            else:
                for les in maand_lessen:
                    r_box = ctk.CTkFrame(scroll_maand, fg_color=t["bg_root"], corner_radius=8)
                    r_box.pack(fill="x", padx=15, pady=4)
                    ctk.CTkLabel(r_box, text=f"📅 {les.get('datum')} | ⏰ {les.get('tijd')} | 📘 {les.get('vak')}", font=("Segoe UI", 12), text_color=t["text"]).pack(side="left", padx=15, pady=8)

    def rooster_toevoegen(self):
        v = self.rst_vak.get()
        d = self.rst_datum.get().strip()
        t = self.rst_tijd_combo.get()
        if d and t:
            self.data["rooster"].append({"vak": v, "datum": d, "tijd": t})
            opslaan(self.data)
            self.bouw_rooster_weergave()

    # ============================================================
    # NOTITIES
    # ============================================================
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijke Notities", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.note_list = tk.Listbox(container, font=("Segoe UI", 11), bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"])
        self.note_list.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ctk.CTkFrame(container, fg_color=t["bg_card"], width=300, corner_radius=15)
        right.pack(side="right", fill="y")

        self.note_text = ctk.CTkTextbox(right, width=260, height=200)
        self.note_text.pack(padx=10, pady=10)

        ctk.CTkButton(right, text="Opslaan", fg_color=t["accent"], text_color="white", command=self.notitie_toevoegen).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(right, text="Verwijderen", command=self.notitie_verwijderen).pack(fill="x", padx=10, pady=5)

        self._herlaad_notities()

    def _herlaad_notities(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]:
            self.note_list.insert(tk.END, n)

    def notitie_toevoegen(self):
        txt = self.note_text.get("1.0", tk.END).strip()
        if txt:
            self.data["notities"].append(txt)
            opslaan(self.data)
            self._herlaad_notities()
            self.note_text.delete("1.0", tk.END)

    def notitie_verwijderen(self):
        try:
            idx = self.note_list.curselection()[0]
            self.data["notities"].pop(idx)
            opslaan(self.data)
            self._herlaad_notities()
        except Exception: pass

    # ============================================================
    # CIJFERS + MULTI-KLEUR GRAFIEK PER VAK
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie & Analyse", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)

        main_container = ctk.CTkFrame(self.main, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=5)

        vak_gemiddelden = {}
        for vak in self.vakken_cijfers:
            cijfers_voor_vak = [float(c["cijfer"]) for c in self.data["cijfers"] if c.get("vak") == vak]
            if cijfers_voor_vak:
                vak_gemiddelden[vak] = sum(cijfers_voor_vak) / len(cijfers_voor_vak)

        left_side = ctk.CTkFrame(main_container, fg_color=t["bg_card"], width=350, corner_radius=15)
        left_side.pack(side="left", fill="both", expand=False, padx=(0, 10))

        ctk.CTkLabel(left_side, text="Nieuw Cijfer", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=5)
        self.cijfer_vak = ctk.CTkComboBox(left_side, values=self.vakken_cijfers, state="readonly")
        self.cijfer_vak.set(self.vakken_cijfers[0])
        self.cijfer_vak.pack(fill="x", padx=15, pady=5)

        self.cijfer_val = ctk.CTkEntry(left_side, placeholder_text="bijv. 7.5")
        self.cijfer_val.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(left_side, text="Toevoegen", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(left_side, text="Gemiddelden per vak:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=(10, 2))
        scroll_gem = ctk.CTkScrollableFrame(left_side, height=200, fg_color="transparent")
        scroll_gem.pack(fill="both", expand=True, padx=10, pady=5)

        for i, vak in enumerate(self.vakken_cijfers):
            g = vak_gemiddelden.get(vak, None)
            g_txt = f"{g:.1f}" if g is not None else "--"
            bullet_kleur = GRAFIEK_KLEUREN[i % len(GRAFIEK_KLEUREN)]
            
            lbl_frame = ctk.CTkFrame(scroll_gem, fg_color="transparent")
            lbl_frame.pack(anchor="w", fill="x", padx=5, pady=2)
            
            # Gekleurde indicator voor de grafieklijn
            tk.Label(lbl_frame, text="■", fg=bullet_kleur, bg=t["bg_card"], font=("Segoe UI", 11)).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(lbl_frame, text=f"{vak}: {g_txt}", font=("Segoe UI", 12), text_color=t["text"]).pack(side="left")

        right_side = ctk.CTkFrame(main_container, fg_color=t["bg_card"], corner_radius=15)
        right_side.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.graph_canvas = tk.Canvas(right_side, height=200, bg=t["list_bg"], highlightthickness=0)
        self.graph_canvas.pack(fill="x", padx=15, pady=10)

        self.cijfer_list = tk.Listbox(right_side, font=("Segoe UI", 11), bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["list_select"])
        self.cijfer_list.pack(fill="both", expand=True, padx=15, pady=10)
        
        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f"{c.get('vak')}: {c.get('cijfer')}")

        self.teken_lijngrafiek()

    def cijfer_toevoegen(self):
        v = self.cijfer_vak.get()
        c = self.cijfer_val.get().replace(",", ".").strip()
        try:
            fl_c = float(c)
            if 1.0 <= fl_c <= 10.0:
                self.data["cijfers"].append({"vak": v, "cijfer": c})
                opslaan(self.data)
                self.show_cijfers()
        except ValueError: pass

    def teken_lijngrafiek(self):
        self.update_idletasks()
        w = self.graph_canvas.winfo_width()
        if w < 100: w = 450
        h = 200

        padding_x, padding_y = 50, 25
        graph_w = w - (padding_x * 2)
        graph_h = h - (padding_y * 2)

        # Teken basis statische hulplijnen (5.5 voldoende grens & 10 max)
        self.graph_canvas.create_line(padding_x, h - padding_y - (5.5/10.0 * graph_h), w - padding_x, h - padding_y - (5.5/10.0 * graph_h), fill="#555555", dash=(4,4))
        self.graph_canvas.create_text(25, h - padding_y - (5.5/10.0 * graph_h), text="5.5", fill="gray", font=("Segoe UI", 9))
        self.graph_canvas.create_text(25, padding_y, text="10", fill="gray", font=("Segoe UI", 9))

        heeft_grafiek = False

        # Loop door alle unieke vakken heen om per vak een lijn te trekken
        for vak_idx, vak in enumerate(self.vakken_cijfers):
            vak_cijfers = [float(c["cijfer"]) for c in self.data["cijfers"] if c.get("vak") == vak]
            
            if len(vak_cijfers) < 2:
                continue # Heeft minimaal 2 datapunten nodig per lijn
            
            heeft_grafiek = True
            lijn_kleur = GRAFIEK_KLEUREN[vak_idx % len(GRAFIEK_KLEUREN)]
            stap_x = graph_w / (len(vak_cijfers) - 1)
            
            punten = []
            for idx, cijfer in enumerate(vak_cijfers):
                x = padding_x + (idx * stap_x)
                y = h - padding_y - ((cijfer / 10.0) * graph_h)
                punten.append((x, y))

            # Teken de specifieke gekleurde lijn voor dit vak
            for i in range(len(punten) - 1):
                self.graph_canvas.create_line(punten[i][0], punten[i][1], punten[i+1][0], punten[i+1][1], fill=lijn_kleur, width=3)
                # Teken datapunten (bolletjes)
                self.graph_canvas.create_oval(punten[i][0]-3, punten[i][1]-3, punten[i][0]+3, punten[i][1]+3, fill=lijn_kleur, outline="white")
            self.graph_canvas.create_oval(punten[-1][0]-3, punten[-1][1]-3, punten[-1][0]+3, punten[-1][1]+3, fill=lijn_kleur, outline="white")

        if not heeft_grafiek:
            self.graph_canvas.create_text(w/2, h/2, text="Voer voor minimaal één vak 2 cijfers in voor lijngrafiek.", fill="gray", font=("Segoe UI", 11))

    # ============================================================
    # DOELEN & VOORTGANG
    # ============================================================
    def show_doelen(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Persoonlijke Leerdoelen & Voortgang", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_side = ctk.CTkScrollableFrame(container, fg_color=t["bg_card"], corner_radius=15)
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_side = ctk.CTkFrame(container, fg_color=t["bg_card"], width=300, corner_radius=15)
        right_side.pack(side="right", fill="y", padx=(10, 0))

        ctk.CTkLabel(right_side, text="Nieuw Doel", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=10)
        self.doel_entry = ctk.CTkEntry(right_side, placeholder_text="bijv. Netwerken hoofdstuk 4")
        self.doel_entry.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(right_side, text="Voortgang (%)", font=("Segoe UI", 12), text_color=t["text"]).pack(pady=5)
        self.doel_progress = ctk.CTkSlider(right_side, from_=0, to=100, number_of_steps=10)
        self.doel_progress.set(20)
        self.doel_progress.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(right_side, text="Doel Opslaan", fg_color=t["accent"], command=self.doel_toevoegen).pack(fill="x", padx=15, pady=20)

        self.bouw_doelen_lijst(left_side)

    def bouw_doelen_lijst(self, parent_frame):
        for w in parent_frame.winfo_children(): w.destroy()
        t = THEMES[self.theme_name]

        if not self.data["doelen"]:
            ctk.CTkLabel(parent_frame, text="Nog geen doelen gesteld. Tijd om te plannen!", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=20)
            return

        for idx, d in enumerate(self.data["doelen"]):
            item_frame = ctk.CTkFrame(parent_frame, fg_color=t["bg_root"])
            item_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(item_frame, text=d.get("titel"), font=("Segoe UI", 13, "bold"), text_color=t["text"]).pack(anchor="w", padx=10, pady=2)
            
            prog_val = d.get("progress", 0) / 100.0
            p_bar = ctk.CTkProgressBar(item_frame, progress_color=t["accent"])
            p_bar.set(prog_val)
            p_bar.pack(fill="x", padx=10, pady=5)

            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(btn_frame, text=f"Voortgang: {d.get('progress')}%", font=("Segoe UI", 11), text_color=t["text"]).pack(side="left")
            ctk.CTkButton(btn_frame, text="Verwijder", width=60, height=20, fg_color="#ff1f1f", command=lambda i=idx: self.doel_verwijderen(i)).pack(side="right")

    def doel_toevoegen(self):
        titel = self.doel_entry.get().strip()
        prog = int(self.doel_progress.get())
        if titel:
            self.data["doelen"].append({"titel": titel, "progress": prog})
            opslaan(self.data)
            self.show_doelen()

    def doel_verwijderen(self, idx):
        self.data["doelen"].pop(idx)
        opslaan(self.data)
        self.show_doelen()

    # ============================================================
    # INSTELLINGEN
    # ============================================================
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Systeem Instellingen", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=20)

        panel = ctk.CTkFrame(self.main, fg_color=t["bg_card"], corner_radius=15)
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(panel, text="📇 Gebruikersnaam Aanpassen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        self.name_entry = ctk.CTkEntry(panel, width=300)
        self.name_entry.insert(0, self.data["settings"].get("naam", "Gebruiker"))
        self.name_entry.pack(anchor="w", padx=20, pady=5)

        ctk.CTkButton(panel, text="💾 Naam Opslaan", command=self.naam_opslaan).pack(anchor="w", padx=20, pady=(5, 20))

        ctk.CTkLabel(panel, text="🎨 Systeemthema Kiezen", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(10, 5))
        self.theme_combo = ctk.CTkComboBox(panel, values=list(THEMES.keys()), state="readonly")
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(anchor="w", padx=20, pady=5)

        ctk.CTkButton(panel, text="Thema Toepassen", command=self.thema_wisselen).pack(anchor="w", padx=20, pady=(5, 20))

        ctk.CTkLabel(panel, text="🔄 Systeem Updates", font=("Segoe UI", 16, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkButton(panel, text="🚀 Zoeken naar updates", fg_color=t["accent"], text_color="white", command=self.toon_coole_update_loading_screen).pack(anchor="w", padx=20, pady=5)

    def naam_opslaan(self):
        nieuwe_naam = self.name_entry.get().strip()
        if nieuwe_naam:
            self.data["settings"]["naam"] = nieuwe_naam
            opslaan(self.data)
            messagebox.showinfo("Succes", "Je naam is succesvol bijgewerkt!")

    def thema_wisselen(self):
        gekozen = self.theme_combo.get()
        self.theme_name = gekozen
        self.data["settings"]["theme"] = gekozen
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

    # ============================================================
    # GC-OS UPDATER LAADBALK EN ENGINE
    # ============================================================
    def toon_coole_update_loading_screen(self):
        t = THEMES[self.theme_name]
        up_win = ctk.CTkToplevel(self)
        up_win.title("GC-OS Updater")
        up_win.geometry("500x350")
        up_win.resizable(False, False)
        up_win.configure(fg_color="#0d0214" if t["mode"] == "Dark" else t["bg_card"])
        up_win.grab_set()

        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (up_win.winfo_screenheight() // 2) - (350 // 2)
        up_win.geometry(f"+{x}+{y}")

        title_lbl = ctk.CTkLabel(up_win, text="🚀 GC-OS UPDATER PROTOCOL 🚀", font=("Courier New", 15, "bold"), text_color="#00ffcc")
        title_lbl.pack(pady=(25, 10))

        terminal_box = ctk.CTkTextbox(up_win, width=440, height=140, fg_color="#140526", text_color="#39ff14", font=("Courier New", 12))
        terminal_box.pack(pady=10)

        balk = ctk.CTkProgressBar(up_win, width=440, progress_color="#00e5ff")
        balk.set(0.0)
        balk.pack(pady=15)

        def log(bericht):
            terminal_box.insert(tk.END, bericht)
            terminal_box.see(tk.END)
            up_win.update()

        def start_update_check():
            try:
                balk.set(0.15)
                log(">> Initializing GC-OS Update Engine...\n")
                time.sleep(0.4)
                
                balk.set(0.35)
                log(">> Establishing secure handshake with GitHub Master Hub...\n")
                time.sleep(0.4)
                
                balk.set(0.60)
                log(">> Downloading central manifest file (version.txt)...\n")
                
                req = urllib.request.Request(GITHUB_VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    nieuwe_versie = response.read().decode('utf-8').strip()
                
                balk.set(0.85)
                log(f">> Remote manifest parsed. Latest release version: v{nieuwe_versie}\n")
                time.sleep(0.4)
                
                balk.set(1.0)
                log(">> Engine check successfully complete.\n")
                time.sleep(0.3)
                
                up_win.destroy()
                
                if nieuwe_versie != HUIDIGE_VERSIE:
                    changelog_text = "Geen changelog beschikbaar."
                    try:
                        cl_req = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(cl_req, timeout=5) as cl_res:
                            changelog_text = cl_res.read().decode('utf-8')
                    except Exception: pass

                    pop = ctk.CTkToplevel()
                    pop.title("Update Gevonden!")
                    pop.geometry("450x400")
                    pop.grab_set()

                    ctk.CTkLabel(pop, text=f"Nieuwe Update Beschikbaar: v{nieuwe_versie}", font=("Segoe UI", 16, "bold")).pack(pady=10)
                    
                    tb = ctk.CTkTextbox(pop, width=400, height=240)
                    tb.insert("1.0", f"Wat is er nieuw in deze release:\n---------------------\n{changelog_text}")
                    tb.configure(state="disabled")
                    tb.pack(pady=10)

                    btn_frame = ctk.CTkFrame(pop, fg_color="transparent")
                    btn_frame.pack(fill="x", padx=20, pady=10)

                    ctk.CTkButton(btn_frame, text="Nu Installeren", fg_color="#007aff", command=lambda: [pop.destroy(), voer_werkelijke_update_uit()]).pack(side="right", padx=5)
                    ctk.CTkButton(btn_frame, text="Later", command=pop.destroy).pack(side="right", padx=5)
                else:
                    messagebox.showinfo("GC-OS Updater", f"Je draait al op de meest actuele releaseversie! (v{HUIDIGE_VERSIE})")
                    
            except Exception as e:
                if up_win.winfo_exists(): up_win.destroy()
                messagebox.showerror("Update Error", f"Verbinding met update server mislukt:\n{e}")

        def voer_werkelijke_update_uit():
            try:
                req = urllib.request.Request(GITHUB_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    nieuwe_code = response.read().decode('utf-8')
                
                huidig_script_pad = os.path.abspath(sys.argv[0])
                
                with open(huidig_script_pad, "w", encoding="utf-8") as f:
                    f.write(nieuwe_code)
                
                messagebox.showinfo("Update Voltooid", "GC-OS is succesvol gepatcht! De applicatie start nu opnieuw op.")
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
            except Exception as e:
                messagebox.showerror("Patch Fout", f"Kritieke fout tijdens overschrijven scriptbestand:\n{e}")

        self.after(500, start_update_check)

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
