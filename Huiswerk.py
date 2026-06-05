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
# VERSIONING & GITHUB LINKS
# ============================================================
HUIDIGE_VERSIE = "1.1.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"

# Matplotlib importeren voor de cijfergrafieken
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ============================================================
# THEMA'S & COOLE KLEURENPALETTEN
# ============================================================
THEMES = {
    "Cyberpunk (Dark)": {
        "mode": "Dark",
        "bg_root": "#0b0c10",
        "bg_sidebar": "#1f2833",
        "bg_main": "#0b0c10",
        "bg_card": "#151a22",
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
        "text": "#ffffff",
        "sidebar_text": "#ff007f",
        "button_text": "#ffffff",
        "button_fg": "#ff007f",
        "button_hover": "#b30059",
        "accent": "#ff007f",
    },
    "Minimal Wit": {
        "mode": "Light",
        "bg_root": "#f4f6f9",
        "bg_sidebar": "#ffffff",
        "bg_main": "#f4f6f9",
        "bg_card": "#ffffff",
        "text": "#1e293b",
        "sidebar_text": "#0f172a",
        "button_text": "#ffffff",
        "button_fg": "#4f46e5",
        "button_hover": "#4338ca",
        "accent": "#4f46e5",
    },
    "Matrix Groen": {
        "mode": "Dark",
        "bg_root": "#000000",
        "bg_sidebar": "#0d0d0d",
        "bg_main": "#000000",
        "bg_card": "#1a1a1a",
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

def opslaan(data):
    try:
        with open(BESTAND, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Fout", f"Kan data niet opslaan:\n{e}")

def kies_datum(entry_widget):
    top = ctk.CTkToplevel()
    top.title("Kies een datum")
    top.geometry("300x340")
    top.resizable(False, False)
    top.grab_set()
    
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=10, fill="both", expand=True)
    
    def selecteer():
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, cal.get_date())
        top.destroy()
        
    ctk.CTkButton(top, text="📅 Selecteer", corner_radius=10, command=selecteer).pack(pady=10)

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
            "settings": {"theme": "Cyberpunk (Dark)"}
        }
    else:
        with open(BESTAND, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except Exception: data = {}

    if "huiswerk" not in data: data["huiswerk"] = []
    if "notities" not in data: data["notities"] = []
    if "cijfers" not in data: data["cijfers"] = []
    if "rooster" not in data: data["rooster"] = _standaard_rooster()
    if "settings" not in data: data["settings"] = {"theme": "Cyberpunk (Dark)"}
    return data

# ============================================================
# MAIN APPLICATIE CLASS
# ============================================================
class SchoolOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Cyberpunk (Dark)")
        if self.theme_name not in THEMES: self.theme_name = "Cyberpunk (Dark)"

        self.title(f"GraafschapCollege‑OS v{HUIDIGE_VERSIE}")
        self.geometry("1200x720")
        self.minsize(1000, 650)

        self.vakken_hw = ["Nederlands", "Engels", "Rekenen", "Hardware", "Netwerken", "Techlab", "Burgerschap", "Loopbaan"]
        self.periodes = ["Periode 1", "Periode 2", "Periode 3", "Periode 4"]
        self.sidebar_buttons = []

        self._build_layout()
        self.apply_theme()
        self.show_dashboard()
        
        # Start automatische achtergrond update-check bij opstarten
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
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=35, padx=20, fill="x")
        
        title_label = ctk.CTkLabel(brand_frame, text="GC‑OS", font=("Segoe UI", 28, "bold"))
        title_label.pack(anchor="w")
        
        ver_label = ctk.CTkLabel(brand_frame, text=f"Version {HUIDIGE_VERSIE}", font=("Consolas", 11), text_color="#71717a")
        ver_label.pack(anchor="w")

        buttons = [
            ("🏠   Dashboard", self.show_dashboard),
            ("📝   Huiswerk", self.show_huiswerk),
            ("📅   Rooster", self.show_rooster),
            ("🗒   Notities", self.show_notities),
            ("📊   Cijfers", self.show_cijfers),
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w", 
                font=("Segoe UI", 14, "bold"), height=45, 
                corner_radius=12, command=cmd
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.sidebar_buttons.append(btn)

        settings_btn = ctk.CTkButton(
            self.sidebar, text="⚙   Instellingen", anchor="w", 
            font=("Segoe UI", 14, "bold"), height=45, 
            corner_radius=12, command=self.show_settings
        )
        settings_btn.pack(side="bottom", fill="x", padx=15, pady=20)
        self.sidebar_buttons.append(settings_btn)

        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children(): widget.destroy()

    # --------------------------------------------------------
    # UPDATE SYSTEM LOGIC
    # --------------------------------------------------------
    def _check_updates_background(self):
        try:
            with urllib.request.urlopen(GITHUB_VERSION_URL, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version != HUIDIGE_VERSIE:
                self.after(2000, lambda: self._toon_update_dialoog(remote_version))
        except Exception:
            pass

    def _handmatige_update_check(self):
        try:
            with urllib.request.urlopen(GITHUB_VERSION_URL, timeout=5) as response:
                remote_version = response.read().decode('utf-8').strip()
            if remote_version == HUIDIGE_VERSIE:
                messagebox.showinfo("GC-OS Update", "Je draait al de nieuwste versie! 😎")
            else:
                self._toon_update_dialoog(remote_version)
        except Exception as e:
            messagebox.showerror("Update Fout", f"Kan geen verbinding maken met GitHub:\n{e}")

    def _toon_update_dialoog(self, nieuwe_versie):
        changelog = "Geen changelog beschikbaar."
        try:
            with urllib.request.urlopen(GITHUB_CHANGELOG_URL, timeout=5) as response:
                changelog = response.read().decode('utf-8')
        except Exception: pass

        top = ctk.CTkToplevel()
        top.title("🚀 Update Beschikbaar!")
        top.geometry("500x400")
        top.resizable(False, False)
        top.grab_set()

        ctk.CTkLabel(top, text=f"Nieuwe versie v{nieuwe_versie} is uit!", font=("Segoe UI", 20, "bold")).pack(pady=15)
        
        txt = ctk.CTkTextbox(top, width=440, height=200, corner_radius=10)
        txt.insert("1.0", f"Changelog:\n\n{changelog}")
        txt.configure(state="disabled")
        txt.pack(pady=10)

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)

        def voer_update_uit():
            try:
                with urllib.request.urlopen(GITHUB_SCRIPT_URL) as response:
                    nieuw_script = response.read().decode('utf-8')
                huidig_script = sys.argv[0]
                with open(huidig_script, "w", encoding="utf-8") as f:
                    f.write(nieuw_script)
                messagebox.showinfo("Succes", "GC-OS is succesvol geüpdatet! De app start nu opnieuw op.")
                top.destroy()
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                messagebox.showerror("Update Mislukt", f"Er ging iets mis tijdens het overschrijven:\n{e}")

        ctk.CTkButton(btn_frame, text="Nu Updaten ⚡", fg_color="#2ed573", text_color="#000000", font=("Segoe UI", 12, "bold"), corner_radius=10, command=voer_update_uit).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Later", fg_color="#ff4757", corner_radius=10, command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------
    def show_dashboard(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=25)
        
        ctk.CTkLabel(header, text="Welkom terug 👋", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(side="left")
        
        self.clock_label = ctk.CTkLabel(header, text="", font=("Consolas", 16, "bold"), text_color=t["accent"])
        self.clock_label.pack(side="right")
        self.update_clock()

        grid = ctk.CTkFrame(self.main, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=30, pady=10)

        # Huiswerk Card
        card_hw = ctk.CTkFrame(grid, corner_radius=20, fg_color=t["bg_card"], border_width=1, border_color="#2f3542" if t["mode"]=="Dark" else "#e2e8f0")
        card_hw.place(relx=0.0, rely=0.0, relwidth=0.48, relheight=0.4)
        
        hw_open = len([h for h in self.data["huiswerk"] if not h.get("afgerond", False)])
        ctk.CTkLabel(card_hw, text="📚 Huiswerk Status", font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(card_hw, text=f"{hw_open} taken openstaan", font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=20)

        # Cijfer Card
        card_cijfer = ctk.CTkFrame(grid, corner_radius=20, fg_color=t["bg_card"], border_width=1, border_color="#2f3542" if t["mode"]=="Dark" else "#e2e8f0")
        card_cijfer.place(relx=0.52, rely=0.0, relwidth=0.48, relheight=0.4)
        
        g_cijfers = [float(c["cijfer"]) for c in self.data["cijfers"] if c.get("cijfer")]
        gem = sum(g_cijfers) / len(g_cijfers) if g_cijfers else 0.0
        
        ctk.CTkLabel(card_cijfer, text="📊 Jouw Gemiddelde", font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(card_cijfer, text=f"{gem:.2f}" if gem > 0 else "N/A", font=("Segoe UI", 42, "bold"), text_color="#2ed573" if gem >= 5.5 else t["text"]).pack(anchor="w", padx=20)

    def update_clock(self):
        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            self.clock_label.configure(text=dt.datetime.now().strftime("%H:%M:%S | %d-%m-%Y"))
            self.after(1000, self.update_clock)

    # --------------------------------------------------------
    # HUISWERK PLANNER
    # --------------------------------------------------------
    def show_huiswerk(self):
        self.clear_main()
        t = THEMES[self.theme_name]

        ctk.CTkLabel(self.main, text="📝 Huiswerk Planner", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=30, pady=25)

        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        left_frame = ctk.CTkFrame(container, corner_radius=20, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.hw_scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.hw_scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._herlaad_huiswerk_lijst()

        right_frame = ctk.CTkFrame(container, corner_radius=20, fg_color=t["bg_card"], width=300)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Nieuwe Taak", font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=20)
        
        self.hw_vak = ctk.CTkComboBox(right_frame, values=self.vakken_hw, state="readonly", corner_radius=10)
        self.hw_vak.set(self.vakken_hw[0])
        self.hw_vak.pack(fill="x", padx=20, pady=8)

        self.hw_beschrijving = ctk.CTkEntry(right_frame, placeholder_text="Wat moet je doen?", corner_radius=10)
        self.hw_beschrijving.pack(fill="x", padx=20, pady=8)

        datum_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        datum_frame.pack(fill="x", padx=20, pady=8)
        self.hw_datum = ctk.CTkEntry(datum_frame, placeholder_text="YYYY-MM-DD", corner_radius=10)
        self.hw_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(datum_frame, text="📅", width=40, corner_radius=10, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=lambda: kies_datum(self.hw_datum)).pack(side="right")

        ctk.CTkButton(
            right_frame, text="🚀 Toevoegen", font=("Segoe UI", 14, "bold"), 
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=15, height=40, command=self._voeg_huiswerk_toe
        ).pack(fill="x", padx=20, pady=25)

    def _herlaad_huiswerk_lijst(self):
        for widget in self.hw_scroll_frame.winfo_children(): widget.destroy()
        t = THEMES[self.theme_name]
        vandaag = dt.date.today()

        for i, h in enumerate(self.data["huiswerk"]):
            is_af = h.get("afgerond", False)
            try:
                deadline = dt.datetime.strptime(h.get('datum', ''), "%Y-%m-%d").date()
                te_laat = (deadline <= vandaag) and not is_af
            except Exception: te_laat = False

            row_bg = "#ff4757" if te_laat else (t["bg_root"] if not is_af else "#2ed573")
            txt_color = "#ffffff" if (te_laat or is_af) else t["text"]

            row = ctk.CTkFrame(self.hw_scroll_frame, fg_color=row_bg, corner_radius=12)
            row.pack(fill="x", pady=5, padx=5)

            status_symboon = "✅" if is_af else "⏳"
            taak_tekst = f"{status_symboon} {h.get('vak')} — {h.get('beschrijving')} \n📅 Deadline: {h.get('datum')}"
            
            lbl = ctk.CTkLabel(row, text=taak_tekst, text_color=txt_color, font=("Segoe UI", 13, "bold"), justify="left")
            lbl.pack(side="left", padx=15, pady=10)

            btn_vink = ctk.CTkButton(row, text="✓", width=35, height=30, corner_radius=8, fg_color="#ffffff" if is_af else "#2ed573", text_color="#000000", font=("Segoe UI", 14, "bold"), command=lambda idx=i: self._toggle_huiswerk(idx))
            btn_vink.pack(side="right", padx=5)

            btn_del = ctk.CTkButton(row, text="🗑", width=35, height=30, corner_radius=8, fg_color="#ff6b81", text_color="#ffffff", command=lambda idx=i: self._verwijder_huiswerk(idx))
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

    # --------------------------------------------------------
    # ROOSTER EDIT SYSTEM
    # --------------------------------------------------------
    def show_rooster(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="📅 Jouw Lesrooster", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=30, pady=20)
        
        scroll_rooster = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll_rooster.pack(fill="both", expand=True, padx=30, pady=10)
        
        dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
        self.rooster_inputs = {}
        
        for dag in dagen:
            dag_frame = ctk.CTkFrame(scroll_rooster, corner_radius=15, fg_color=t["bg_card"], border_width=1, border_color="#2f3542" if t["mode"]=="Dark" else "#e2e8f0")
            dag_frame.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(dag_frame, text=dag, font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=10)
            
            if dag not in self.data["rooster"]: self.data["rooster"][dag] = _standaard_rooster()[dag]
            self.rooster_inputs[dag] = []
            
            for i, les in enumerate(self.data["rooster"][dag]):
                les_row = ctk.CTkFrame(dag_frame, fg_color="transparent")
                les_row.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(les_row, text=f"Uur {i+1}", font=("Segoe UI", 12, "bold"), width=60, text_color=t["text"]).pack(side="left")
                
                tijd_ent = ctk.CTkEntry(les_row, width=130, corner_radius=8)
                tijd_ent.insert(0, les.get("tijd", ""))
                tijd_ent.pack(side="left", padx=5)
                
                les_ent = ctk.CTkEntry(les_row, placeholder_text="Welk vak?", corner_radius=8)
                les_ent.insert(0, les.get("les", "Geen les"))
                les_ent.pack(side="left", fill="x", expand=True, padx=5)
                
                self.rooster_inputs[dag].append({"tijd": tijd_ent, "les": les_ent})
                
        ctk.CTkButton(
            self.main, text="💾 Rooster Opslaan", font=("Segoe UI", 14, "bold"),
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=15, height=45, command=self._opslaan_rooster
        ).pack(fill="x", padx=35, pady=20)

    def _opslaan_rooster(self):
        for dag, uren in self.rooster_inputs.items():
            self.data["rooster"][dag] = [{"tijd": e["tijd"].get(), "les": e["les"].get()} for e in uren]
        opslaan(self.data)
        messagebox.showinfo("GC-OS Info", "Rooster succesvol bijgewerkt! 🔥")

    # --------------------------------------------------------
    # NOTITIES
    # --------------------------------------------------------
    def show_notities(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="🗒 Persoonlijke Notities", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=30, pady=25)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        left_frame = ctk.CTkFrame(container, corner_radius=20, fg_color=t["bg_card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.note_list = tk.Listbox(left_frame, font=("Segoe UI", 12), borderwidth=0, highlightthickness=0, activestyle="none")
        self.note_list.pack(fill="both", expand=True, padx=15, pady=15)
        self._herlaad_notitie_lijst()
        
        right_frame = ctk.CTkFrame(container, corner_radius=20, fg_color=t["bg_card"], width=340)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        self.note_txt = ctk.CTkTextbox(right_frame, font=("Segoe UI", 13), corner_radius=12, border_width=1)
        self.note_txt.pack(fill="both", expand=True, padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Opslaan", corner_radius=10, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._voeg_notitie_toe).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Verwijder", corner_radius=10, fg_color="#ff4757", text_color="#ffffff", command=self._verwijder_notitie).pack(side="right", expand=True, fill="x")

    def _herlaad_notitie_lijst(self):
        self.note_list.delete(0, tk.END)
        for n in self.data["notities"]: self.note_list.insert(tk.END, f" 📝  {n[:30]}...")

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

    # --------------------------------------------------------
    # CIJFERS MODULE + GRAFIEK
    # --------------------------------------------------------
    def show_cijfers(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        
        ctk.CTkLabel(self.main, text="📊 Cijfer Overzicht & Voortgang", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=30, pady=20)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        left_side = ctk.CTkFrame(container, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.graph_card = ctk.CTkFrame(left_side, corner_radius=20, fg_color=t["bg_card"], border_width=1, border_color="#2f3542" if t["mode"]=="Dark" else "#e2e8f0")
        self.graph_card.pack(fill="both", expand=True, pady=(0, 15))
        self._teken_gecombineerde_grafiek()
        
        list_card = ctk.CTkFrame(left_side, corner_radius=20, fg_color=t["bg_card"], height=180)
        list_card.pack(fill="x")
        list_card.pack_propagate(False)
        
        self.cijfer_list = tk.Listbox(list_card, font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, activestyle="none")
        self.cijfer_list.pack(fill="both", expand=True, padx=15, pady=15)
        self._herlaad_cijfer_lijst()
        
        right_side = ctk.CTkFrame(container, corner_radius=20, fg_color=t["bg_card"], width=280)
        right_side.pack(side="right", fill="y")
        right_side.pack_propagate(False)
        
        ctk.CTkLabel(right_side, text="Cijfer Invoeren", font=("Segoe UI", 18, "bold"), text_color=t["accent"]).pack(anchor="w", padx=20, pady=15)
        
        self.c_vak = ctk.CTkComboBox(right_side, values=self.vakken_hw, state="readonly", corner_radius=10)
        self.c_vak.set(self.vakken_hw[0])
        self.c_vak.pack(fill="x", padx=20, pady=6)
        
        self.c_num = ctk.CTkEntry(right_side, placeholder_text="Cijfer (bvb 7.8)", corner_radius=10)
        self.c_num.pack(fill="x", padx=20, pady=6)
        
        self.c_weging = ctk.CTkEntry(right_side, placeholder_text="Weging", corner_radius=10)
        self.c_weging.insert(0, "1")
        self.c_weging.pack(fill="x", padx=20, pady=6)
        
        self.c_periode = ctk.CTkComboBox(right_side, values=self.periodes, state="readonly", corner_radius=10)
        self.c_periode.set(self.periodes[0])
        self.c_periode.pack(fill="x", padx=20, pady=6)
        
        dat_f = ctk.CTkFrame(right_side, fg_color="transparent")
        dat_f.pack(fill="x", padx=20, pady=6)
        self.c_datum = ctk.CTkEntry(dat_f, placeholder_text="YYYY-MM-DD", corner_radius=10)
        self.c_datum.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dat_f, text="📅", width=40, corner_radius=10, command=lambda: kies_datum(self.c_datum)).pack(side="right")
        
        ctk.CTkButton(right_side, text="✨ Toevoegen", corner_radius=12, fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"], command=self._voeg_cijfer_toe).pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(right_side, text="🗑 Verwijder", corner_radius=12, fg_color="#ff4757", text_color="#ffffff", command=self._verwijder_cijfer).pack(fill="x", padx=20, pady=2)

    def _herlaad_cijfer_lijst(self):
        self.cijfer_list.delete(0, tk.END)
        for c in self.data["cijfers"]:
            self.cijfer_list.insert(tk.END, f" 📈 {c.get('vak')} ➔ {c.get('cijfer')}  (Weging: {c.get('weging')}x | {c.get('periode')})")

    def _teken_gecombineerde_grafiek(self):
        for widget in self.graph_card.winfo_children(): widget.destroy()
        t = THEMES[self.theme_name]
        
        is_dark = (t["mode"] == "Dark")
        bg_col = t["bg_card"]
        text_col = "#ffffff" if is_dark else "#1e293b"
        
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
            ax.text(0.5, 0.5, "Voeg cijfers toe om de live lijngrafieken te zien 🚀", color=text_col, ha='center', va='center', transform=ax.transAxes, fontname="Segoe UI", fontsize=12)
                    
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
        del self.data["cijfers"][sel[0]]
        opslaan(self.data)
        self._herlaad_cijfer_lijst()
        self._teken_gecombineerde_grafiek()

    # --------------------------------------------------------
    # INSTELLINGEN & MANUAL UPDATE ENGINE
    # --------------------------------------------------------
    def show_settings(self):
        self.clear_main()
        t = THEMES[self.theme_name]
        ctk.CTkLabel(self.main, text="⚙ Instellingen & Systeem", font=("Segoe UI", 26, "bold"), text_color=t["text"]).pack(anchor="w", padx=30, pady=25)
        
        # Kaart 1: Thema selecteren
        card_theme = ctk.CTkFrame(self.main, corner_radius=20, fg_color=t["bg_card"])
        card_theme.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(card_theme, text="Kies jouw OS Engine Skin:", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(side="left", padx=20, pady=25)
        
        self.theme_combo = ctk.CTkComboBox(card_theme, values=list(THEMES.keys()), state="readonly", corner_radius=10, command=self._verander_thema)
        self.theme_combo.set(self.theme_name)
        self.theme_combo.pack(side="left", padx=10)

        # Kaart 2: GitHub Updates
        card_update = ctk.CTkFrame(self.main, corner_radius=20, fg_color=t["bg_card"])
        card_update.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(card_update, text="Systeemupdates & GitHub Sync:", font=("Segoe UI", 15, "bold"), text_color=t["text"]).pack(side="left", padx=20, pady=25)
        
        ctk.CTkButton(
            card_update, text="🔄 Update Controleren", font=("Segoe UI", 13, "bold"),
            fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"],
            corner_radius=10, command=self._handmatige_update_check
        ).pack(side="right", padx=20, pady=20)

    def _verander_thema(self, nieuw_thema):
        self.theme_name = nieuw_thema
        self.data["settings"]["theme"] = nieuw_thema
        opslaan(self.data)
        self.apply_theme()
        self.show_settings()

# ============================================================
# EXECUTE CORE ENGINE
# ============================================================
if __name__ == "__main__":
    app = SchoolOS()
    app.mainloop()
