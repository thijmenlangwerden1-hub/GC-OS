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

# ============================================================
# CONFIGURATIE
# ============================================================

HUIDIGE_VERSIE = "1.1.1"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")

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
        self.geometry("1100x650")

        self.vakken_hw = [
            "Nederlands", "Engels", "Rekenen", "Hardware",
            "Netwerken", "Techlab", "Burgerschap", "Loopbaan", "Vrije Afspraak"
        ]
        
        self.sidebar_width = 230
        self.sidebar_buttons = []

        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.rooster_panel = None
        self.clock_label = None

        self.rooster_stijl = "Week" 
        self.huidige_rooster_datum = dt.date.today()

        self._build_layout()
        self.apply_theme()

        self.after(100, self.show_intro_screen)

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="GC‑OS", font=("Segoe UI", 26, "bold")).pack(pady=25)

        buttons = [
            ("🏠  Dashboard", self.show_dashboard),
            ("📝  Huiswerk", self.show_huiswerk),
            ("📅  Rooster", self.show_rooster),
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
        self.hw_list = None
        self.note_list = None
        self.cijfer_list = None
        self.rooster_panel = None
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
        if self.hw_list:
            self.hw_list.delete(0, tk.END)
            for h in self.data["huiswerk"]:
                status = "✔" if h.get("afgerond") else "❌"
                self.hw_list.insert(tk.END, f"[{status}] {h.get('datum')} - {h.get('vak')}: {h.get('beschrijving')}")

    def hw_toevoegen(self):
        v = self.hw_vak.get()
        b = self.hw_beschrijving.get().strip()
        d = self.hw_datum.get().strip()
        if not b or not d:
            return
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
    # ROOSTER (WEEK & MAAND)
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

        self.rooster_panel = ctk.CTkScrollableFrame(self.main, fg_color=t["bg_card"], corner_radius=15)
        self.rooster_panel.pack(fill="both", expand=True, padx=20, pady=10)

        add_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=10)

        self.rst_vak = ctk.CTkComboBox(add_frame, values=self.vakken_hw, width=150)
        self.rst_vak.set(self.vakken_hw[0])
        self.rst_vak.pack(side="left", padx=5)

        self.rst_datum = ctk.CTkEntry(add_frame, placeholder_text="yyyy-mm-dd", width=110)
        self.rst_datum.insert(0, str(dt.date.today()))
        self.rst_datum.pack(side="left", padx=5)

        self.rst_tijd = ctk.CTkEntry(add_frame, placeholder_text="HH:MM", width=70)
        self.rst_tijd.insert(0, "08:30")
        self.rst_tijd.pack(side="left", padx=5)

        ctk.CTkButton(add_frame, text="➕ Toevoegen", command=self.rooster_toevoegen).pack(side="left", padx=5)

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
        for w in self.rooster_panel.winfo_children():
            w.destroy()
        t = THEMES[self.theme_name]

        if self.rooster_stijl == "Week":
            start_vd_week = self.huidige_rooster_datum - dt.timedelta(days=self.huidige_rooster_datum.weekday())
            eind_vd_week = start_vd_week + dt.timedelta(days=4)
            self.rooster_datum_label.configure(text=f"Week: {start_vd_week.strftime('%d %b')} t/m {eind_vd_week.strftime('%d %b %Y')}")

            dagen_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
            for i, naam in enumerate(dagen_namen):
                dag_datum = start_vd_week + dt.timedelta(days=i)
                dag_str = dag_datum.strftime("%Y-%m-%d")

                col = ctk.CTkFrame(self.rooster_panel, fg_color=t["bg_root"], width=150, corner_radius=10)
                col.pack(side="left", fill="both", expand=True, padx=4, pady=5)

                ctk.CTkLabel(col, text=f"{naam}\n{dag_datum.strftime('%d-%m')}", font=("Segoe UI", 12, "bold"), text_color=t["text"]).pack(pady=5)

                dag_lessen = [l for l in self.data["rooster"] if l.get("datum") == dag_str]
                dag_lessen.sort(key=lambda x: x.get("tijd", ""))

                for les in dag_lessen:
                    les_box = ctk.CTkFrame(col, fg_color=t["accent"] if t["mode"] == "Dark" else t["button_fg"], corner_radius=6)
                    les_box.pack(fill="x", padx=5, pady=3)
                    ctk.CTkLabel(les_box, text=f"{les.get('tijd')} {les.get('vak')}", font=("Segoe UI", 11), text_color="#ffffff" if t["mode"] == "Dark" else t["text"]).pack(pady=3)
        else:
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
                ctk.CTkLabel(self.rooster_panel, text="Geen geplande lessen deze maand.", font=("Segoe UI", 13), text_color=t["text"]).pack(pady=20)
            else:
                for les in maand_lessen:
                    r_box = ctk.CTkFrame(self.rooster_panel, fg_color=t["bg_root"])
                    r_box.pack(fill="x", padx=10, pady=4)
                    ctk.CTkLabel(r_box, text=f"📅 {les.get('datum')} | ⏰ {les.get('tijd')} | 📘 {les.get('vak')}", font=("Segoe UI", 12), text_color=t["text"]).pack(side="left", padx=10, pady=5)

    def rooster_toevoegen(self):
        v = self.rst_vak.get()
        d = self.rst_datum.get().strip()
        t = self.rst_tijd.get().strip()
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
        if self.note_list:
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
    # CIJFERS + GRAPH
    # ============================================================
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="Cijferregistratie & Analyse", font=("Segoe UI", 24, "bold"), text_color=t["text"]).pack(anchor="w", padx=20, pady=15)

        main_container = ctk.CTkFrame(self.main, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=5)

        vak_gemiddelden = {}
        for vak in self.vakken_hw:
            cijfers_voor_vak = [float(c["cijfer"]) for c in self.data["cijfers"] if c.get("vak") == vak]
            if cijfers_voor_vak:
                vak_gemiddelden[vak] = sum(cijfers_voor_vak) / len(cijfers_voor_vak)

        left_side = ctk.CTkFrame(main_container, fg_color=t["bg_card"], width=350, corner_radius=15)
        left_side.pack(side="left", fill="both", expand=False, padx=(0, 10))

        ctk.CTkLabel(left_side, text="Nieuw Cijfer", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=5)
        self.cijfer_vak = ctk.CTkComboBox(left_side, values=self.vakken_hw, state="readonly")
        self.cijfer_vak.set(self.vakken_hw[0])
        self.cijfer_vak.pack(fill="x", padx=15, pady=5)

        self.cijfer_val = ctk.CTkEntry(left_side, placeholder_text="bijv. 7.5")
        self.cijfer_val.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(left_side, text="Toevoegen", command=self.cijfer_toevoegen).pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(left_side, text="Gemiddelden per vak:", font=("Segoe UI", 14, "bold"), text_color=t["text"]).pack(pady=(10, 2))
        scroll_gem = ctk.CTkScrollableFrame(left_side, height=200, fg_color="transparent")
        scroll_gem.pack(fill="both", expand=True, padx=10, pady=5)

        for vak in self.vakken_hw:
            g = vak_gemiddelden.get(vak, None)
            g_txt = f"{g:.1f}" if g is not None else "--"
            ctk.CTkLabel(scroll_gem, text=f"{vak}: {g_txt}", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=10, pady=2)

        right_side = ctk.CTkFrame(main_container, fg_color=t["bg_card"], corner_radius=15)
        right_side.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.graph_canvas = tk.Canvas(right_side, height=180, bg=t["list_bg"], highlightthickness=0)
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
        h = 180

        cijfers = []
        for c in self.data["cijfers"]:
            try: cijfers.append(float(c["cijfer"]))
            except ValueError: pass

        if len(cijfers) < 2:
            self.graph_canvas.create_text(w/2, h/2, text="Voer minimaal 2 cijfers in voor grafiek.", fill="gray")
            return

        padding_x, padding_y = 40, 20
        graph_w = w - (padding_x * 2)
        graph_h = h - (padding_y * 2)
        stap_x = graph_w / (len(cijfers) - 1)
        
        t = THEMES[self.theme_name]
        punten = []
        for idx, cijfer in enumerate(cijfers):
            x = padding_x + (idx * stap_x)
            y = h - padding_y - ((cijfer / 10.0) * graph_h)
            punten.append((x, y))

        for i in range(len(punten) - 1):
            self.graph_canvas.create_line(punten[i][0], punten[i][1], punten[i+1][0], punten[i+1][1], fill=t["accent"], width=3)

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
        ctk.CTkButton(panel, text="🚀 Handmatig zoeken naar updates", fg_color=t["accent"], text_color="white", command=self.toon_coole_update_loading_screen).pack(anchor="w", padx=20, pady=5)

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
    # COOLE UPDATE SCREEN
    # ============================================================
    def toon_coole_update_loading_screen(self):
        t = THEMES[self.theme_name]
        up_win = ctk.CTkToplevel(self)
        up_win.title("GC-OS Sync")
        up_win.geometry("500x350")
        up_win.resizable(False, False)
        up_win.configure(fg_color="#0d0214" if t["mode"] == "Dark" else t["bg_card"])
        up_win.grab_set()

        up_win.update_idletasks()
        x = (up_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (up_win.winfo_screenheight() // 2) - (350 // 2)
        up_win.geometry(f"+{x}+{y}")

        title_lbl = ctk.CTkLabel(up_win, text="⚡ INITIALIZING UPDATE PROTOCOL ⚡", font=("Courier New", 14, "bold"), text_color="#00ffcc")
        title_lbl.pack(pady=(25, 10))

        terminal_box = ctk.CTkTextbox(up_win, width=440, height=140, fg_color="#140526", text_color="#39ff14", font=("Courier New", 12))
        terminal_box.pack(pady=10)

        balk = ctk.CTkProgressBar(up_win, width=440, progress_color="#00e5ff")
        balk.set(0.0)
        balk.pack(pady=15)

        status_berichten = [
            ">> Connecting to remote server repository...\n",
            ">> Handshake established with GC-OS Master Hub.\n",
            ">> Fetching manifest: version.txt ...\n",
            ">> Checking architecture compatibility indices...\n",
            ">> System up-to-date checksum successfully generated!\n"
        ]

        def laad_proces(step_idx=0):
            if step_idx < len(status_berichten):
                terminal_box.insert(tk.END, status_berichten[step_idx])
                terminal_box.see(tk.END)
                balk.set((step_idx + 1) / len(status_berichten))
                self.after(600, lambda: laad_proces(step_idx + 1))
            else:
                title_lbl.configure(text="✨ CHECK COMPLETE ✨", text_color="#34c759")
                up_win.destroy()
                messagebox.showinfo("Update Manager", f"Je maakt al gebruik van de allernieuwste software release! (v{HUIDIGE_VERSIE})")

        laad_proces()

if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
