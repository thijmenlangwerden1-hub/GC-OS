import os
import sys
import json
import math
import time
import random
import threading
import urllib.request
import datetime as dt
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from tkcalendar import Calendar

# ============================================================
# HUISWERK PLANNER 8.0  •  Nieuw design
# - Zelfde functies, zelfde opslag (gc_os_data.json) en zelfde updates
# - Nieuw geanimeerd opstart- en afsluitscherm
# - Nieuw dashboard, takenkaarten, instellingen en update center
# - AutoSave blijft UIT: alleen handmatig opslaan schrijft naar schijf
# ============================================================

HUIDIGE_VERSIE = "2.4.9v"

GITHUB_VERSION_URL = (
    "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
)
GITHUB_SCRIPT_URL = (
    "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/"
    "refs/heads/GC-OS/Huiswerk.py"
)
GITHUB_CHANGELOG_URL = (
    "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/"
    "refs/heads/GC-OS/changelog.txt"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")
LOG_BESTAND = os.path.join(SCRIPT_DIR, "recent_changelog.txt")

ROOD = "#ff3b30"
ORANJE = "#ff9500"
GROEN = "#34c759"

THEMES = {
    "Wit": {
        "mode": "Light", "bg_root": "#eceef4", "bg_sidebar": "#ffffff", "bg_main": "#f4f6fb",
        "bg_card": "#ffffff", "text": "#111111", "muted": "#666b75", "button_text": "#111111",
        "button_fg": "#e3e6ee", "button_hover": "#d2d6e4", "accent": "#007aff",
    },
    "Zwart": {
        "mode": "Dark", "bg_root": "#0c0c0e", "bg_sidebar": "#18181b", "bg_main": "#111113",
        "bg_card": "#1f1f23", "text": "#f5f5f7", "muted": "#a1a1aa", "button_text": "#f5f5f7",
        "button_fg": "#2b2b30", "button_hover": "#3a3a40", "accent": "#0a84ff",
    },
    "Blauw-Groen": {
        "mode": "Dark", "bg_root": "#05121a", "bg_sidebar": "#0b2430", "bg_main": "#071821",
        "bg_card": "#0f2f3b", "text": "#e6f9ff", "muted": "#9cc4cc", "button_text": "#e6f9ff",
        "button_fg": "#145c63", "button_hover": "#1a6f78", "accent": "#00e5ff",
    },
    # Groen-Blauw GC gebruikt de exacte hoofdkleuren uit het GC-logo.
    "Groen-Blauw GC": {
        "mode": "Dark", "bg_root": "#333B94", "bg_sidebar": "#454C9B", "bg_main": "#333B94",
        "bg_card": "#454C9B", "text": "#FFFFFF", "muted": "#E7EBA4", "button_text": "#FFFFFF",
        "button_fg": "#CFD600", "button_hover": "#D5DC00", "accent": "#CFD600",
    },
    "Neon Light": {
        "mode": "Dark", "bg_root": "#05000d", "bg_sidebar": "#090014", "bg_main": "#060010",
        "bg_card": "#10001f", "text": "#f7f2ff", "muted": "#bca8d6", "button_text": "#ffffff",
        "button_fg": "#1b0730", "button_hover": "#32085a", "accent": "#ff2bd6",
    },
    "Chrome": {
        "mode": "Light", "bg_root": "#dee1e6", "bg_sidebar": "#f1f3f4", "bg_main": "#ffffff",
        "bg_card": "#f8f9fa", "text": "#202124", "muted": "#5f6368", "button_text": "#202124",
        "button_fg": "#e8eaed", "button_hover": "#d2e3fc", "accent": "#1a73e8",
    },
    "Chrome Donker": {
        "mode": "Dark", "bg_root": "#202124", "bg_sidebar": "#292a2d", "bg_main": "#202124",
        "bg_card": "#35363a", "text": "#e8eaed", "muted": "#9aa0a6", "button_text": "#e8eaed",
        "button_fg": "#3c4043", "button_hover": "#4a4d51", "accent": "#8ab4f8",
    },
}

ACTIVE_THEME = ["Wit"]


# ============================================================
# KLEUR-HULPFUNCTIES
# ============================================================

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(a, b, f):
    """Meng kleur a met kleur b (f = 0..1)."""
    ra, rb = _rgb(a), _rgb(b)
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * f) for x, y in zip(ra, rb))


def on_accent(c):
    r, g, b = _rgb(c)
    return "#111111" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def th(name=None):
    return THEMES.get(name or ACTIVE_THEME[0], THEMES["Wit"])


def border(t):
    return blend(t["bg_card"], t["text"], 0.10)


# ============================================================
# VEILIGE DATAFUNCTIES (ongewijzigd)
# ============================================================

def standaard_data():
    return {
        "huiswerk": [],
        "settings": {"theme": "Wit", "gebruikersnaam": "Student"},
    }


def opslaan(data):
    """Sla gegevens veilig op. Een mislukte opslag mag de UI niet laten crashen."""
    try:
        os.makedirs(SCRIPT_DIR, exist_ok=True)
        tijdelijke = BESTAND + ".tmp"
        with open(tijdelijke, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Atomair vervangen voorkomt een halfgeschreven JSON-bestand.
        os.replace(tijdelijke, BESTAND)
        return True
    except Exception as e:
        try:
            if os.path.exists(BESTAND + ".tmp"):
                os.remove(BESTAND + ".tmp")
        except OSError:
            pass
        try:
            messagebox.showerror("Opslaan mislukt", f"Kan data niet opslaan:\n\n{e}")
        except Exception:
            pass
        return False


def laden():
    """Laad gegevens en herstel ontbrekende/ongeldige velden."""
    standaard = standaard_data()
    if not os.path.exists(BESTAND):
        return standaard
    try:
        with open(BESTAND, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return standaard
    if not isinstance(data, dict):
        data = standaard
    if not isinstance(data.get("huiswerk"), list):
        data["huiswerk"] = []
    if not isinstance(data.get("settings"), dict):
        data["settings"] = {}
    settings = data["settings"]
    settings.setdefault("theme", "Wit")
    settings.setdefault("gebruikersnaam", "Student")
    if settings["theme"] not in THEMES:
        settings["theme"] = "Wit"
    if not isinstance(settings["gebruikersnaam"], str):
        settings["gebruikersnaam"] = "Student"
    # Beschadigde individuele taken worden genegeerd.
    schone_taken = []
    for item in data["huiswerk"]:
        if isinstance(item, dict):
            item.setdefault("vak", "Onbekend")
            item.setdefault("titel", "Zonder titel")
            item.setdefault("datum", "")
            item.setdefault("done", False)
            item.setdefault("priority", "Normaal")
            item.setdefault("in_progress", False)
            item["done"] = bool(item["done"])
            schone_taken.append(item)
    data["huiswerk"] = schone_taken
    return data


def parse_datum(value):
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ============================================================
# DATUMKIEZER
# ============================================================

def _datum_dialog(parent, titel, start, on_pick, knop):
    t = th()
    top = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    top.title(titel)
    top.geometry("340x400")
    top.resizable(False, False)
    top.configure(fg_color=t["bg_card"])
    try:
        if parent:
            top.transient(parent)
    except Exception:
        pass
    ctk.CTkLabel(top, text="📅  " + titel, font=("Segoe UI", 16, "bold"),
                 text_color=t["text"]).pack(anchor="w", padx=18, pady=(16, 6))
    kw = dict(selectmode="day", date_pattern="yyyy-mm-dd",
              background=t["accent"], foreground=on_accent(t["accent"]),
              headersbackground=t["bg_main"], headersforeground=t["muted"],
              normalbackground=t["bg_card"], normalforeground=t["text"],
              weekendbackground=t["bg_card"], weekendforeground=t["text"],
              selectbackground=t["accent"], selectforeground=on_accent(t["accent"]),
              bordercolor=border(t), othermonthbackground=t["bg_main"],
              othermonthforeground=t["muted"], othermonthwebackground=t["bg_main"],
              othermonthweforeground=t["muted"])
    if start:
        kw.update(year=start.year, month=start.month, day=start.day)
    try:
        cal = Calendar(top, **kw)
    except Exception:
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.pack(padx=14, pady=6, fill="both", expand=True)

    def kies():
        try:
            on_pick(cal.get_date())
        finally:
            top.destroy()

    ctk.CTkButton(top, text=knop, height=42, corner_radius=12, command=kies,
                  fg_color=t["accent"], text_color=on_accent(t["accent"]),
                  hover_color=blend(t["accent"], "#000000", 0.15),
                  font=("Segoe UI", 13, "bold")).pack(padx=16, pady=(4, 16), fill="x")
    try:
        top.after(80, top.grab_set)
    except Exception:
        pass


def kies_datum(entry):
    def pick(d):
        entry.delete(0, tk.END)
        entry.insert(0, d)
    _datum_dialog(entry.winfo_toplevel(), "Kies deadline", parse_datum(entry.get()), pick,
                  "✓  Deadline selecteren")


def wijzig_bestaande_datum(parent, target):
    huidige = parse_datum(target.get("datum", "")) or dt.date.today()

    def pick(d):
        # Deadline wordt alleen in het geheugen aangepast. Handmatig opslaan maakt de wijziging permanent.
        target["datum"] = d
        try:
            parent._render_huiswerk_lijst()
        except Exception:
            pass

    _datum_dialog(parent, "Deadline wijzigen", huidige, pick, "✓  Deadline klaar • Handmatig opslaan")


# ============================================================
# STARTUP- EN AFSLUITSCHERM
# ============================================================

INTRO_BG = "#060913"


class IntroBase(ctk.CTk):
    """Geanimeerd intro-scherm met zwevende deeltjes, draaiende ringen en voortgangsbalk."""
    W, H = 900, 560

    def __init__(self, accent, glyph, title, tagline, steps, dur, footer, finish):
        super().__init__()
        self.accent, self.glyph, self.title_txt = accent, glyph, title
        self.tagline, self.steps, self.dur = tagline, steps, dur
        self.footer, self.finish_cb = footer, finish
        self.title("Huiswerk Planner")
        self.configure(fg_color=INTRO_BG)
        self.resizable(False, False)
        try:
            self.overrideredirect(True)
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.W) // 2
        y = (self.winfo_screenheight() - self.H) // 2
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")
        try:
            self.attributes("-alpha", 0.0)
        except tk.TclError:
            pass
        self.cv = tk.Canvas(self, width=self.W, height=self.H, bg=INTRO_BG,
                            highlightthickness=0, bd=0)
        self.cv.pack(fill="both", expand=True)
        rng = random.Random(7)
        self.dots = [(rng.uniform(0, self.W), rng.uniform(0, self.H),
                      rng.uniform(8, 26), rng.uniform(1.2, 3.2)) for _ in range(34)]
        self.t0 = time.monotonic()
        self.after(30, self._tick)

    def _tick(self):
        if not self.winfo_exists():
            return
        t = time.monotonic() - self.t0
        p = min(t / self.dur, 1.0)
        e = p * p * (3 - 2 * p)
        a = min(1.0, t / 0.45)
        if t > self.dur + 0.25:
            a = max(0.0, 1 - (t - self.dur - 0.25) / 0.35)
        try:
            self.attributes("-alpha", a)
        except tk.TclError:
            pass
        self._draw(t, e)
        if t >= self.dur + 0.65:
            self.finish_cb()
            return
        self.after(16, self._tick)

    def _draw(self, t, e):
        c, W, H, ac, bg = self.cv, self.W, self.H, self.accent, INTRO_BG
        c.delete("all")
        cx, cy = W / 2, 200
        for i in range(9):
            r = 260 - i * 26
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=blend(bg, ac, 0.012 + i * 0.006), outline="")
        for x, y0, speed, size in self.dots:
            y = (y0 - t * speed) % H
            xx = x + math.sin(t + y0) * 6
            c.create_oval(xx - size, y - size, xx + size, y + size,
                          fill=blend(bg, ac, 0.18 + 0.05 * size), outline="")
        R = 64
        c.create_oval(cx - R, cy - R, cx + R, cy + R, outline=blend(bg, ac, .22), width=2)
        c.create_oval(cx - R - 22, cy - R - 22, cx + R + 22, cy + R + 22,
                      outline=blend(bg, ac, .10), width=1)
        c.create_arc(cx - R, cy - R, cx + R, cy + R, start=(-t * 240) % 360, extent=90,
                     style="arc", outline=ac, width=4)
        c.create_arc(cx - R - 22, cy - R - 22, cx + R + 22, cy + R + 22,
                     start=(t * 140) % 360, extent=50, style="arc",
                     outline=blend(bg, ac, .55), width=2)
        r = 46 * (1 + 0.04 * math.sin(t * 4))
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=blend(bg, ac, .16),
                      outline=blend(bg, ac, .6), width=2)
        c.create_text(cx, cy, text=self.glyph, fill=ac, font=("Segoe UI", 44, "bold"))
        c.create_text(cx, 330, text=self.title_txt, fill="#f7f9fc", font=("Segoe UI", 28, "bold"))
        c.create_text(cx, 366, text=self.tagline, fill="#7f8da5", font=("Segoe UI", 13))
        idx = min(int(e * len(self.steps)), len(self.steps) - 1)
        phase, msg = self.steps[idx]
        c.create_text(cx, 420, text=phase, fill=ac, font=("Segoe UI", 10, "bold"))
        c.create_text(cx, 444, text=msg, fill="#b7c0cf", font=("Segoe UI", 12))
        x0, x1, y = 210, 690, 490
        c.create_line(x0, y, x1, y, fill="#141c2d", width=10, capstyle="round")
        if e > 0.01:
            c.create_line(x0, y, x0 + (x1 - x0) * e, y, fill=ac, width=10, capstyle="round")
        c.create_text(cx, 518, text=f"{int(e * 100)}%", fill="#f7f9fc", font=("Segoe UI", 11, "bold"))
        c.create_text(cx, H - 18, text=self.footer, fill="#334158", font=("Segoe UI", 8, "bold"))
        c.create_rectangle(1, 1, W - 1, H - 1, outline=blend(bg, ac, .25))


class StartupIntro(IntroBase):
    def __init__(self):
        super().__init__(
            accent="#6D8CFF", glyph="H", title="HUISWERK PLANNER",
            tagline="Jouw schooldag. Georganiseerd.",
            steps=[("INITIALISEREN", "Applicatie voorbereiden…"),
                   ("LADEN", "Huiswerk en deadlines laden…"),
                   ("CONTROLEREN", "Planning controleren…"),
                   ("OPTIMALISEREN", "Werkruimte optimaliseren…"),
                   ("KLAAR", "Alles staat klaar ✓")],
            dur=2.6, footer=f"HUISWERK PLANNER  •  {HUIDIGE_VERSIE}  •  STARTING",
            finish=self.open_app)

    def open_app(self):
        try:
            self.destroy()
        except Exception:
            pass
        HuiswerkApp().mainloop()


class ClosingIntro(IntroBase):
    def __init__(self):
        super().__init__(
            accent="#36D58A", glyph="✓", title="TOT DE VOLGENDE KEER",
            tagline="Je planning is afgerond. Tijd om af te sluiten.",
            steps=[("OPSLAAN", "Wijzigingen veilig opslaan…"),
                   ("CONTROLEREN", "Laatste gegevens controleren…"),
                   ("AFRONDEN", "Alles netjes afronden…"),
                   ("AFSLUITEN", "Applicatie afsluiten…"),
                   ("TOT ZIENS", "Denk aan je huiswerk hè! 😉")],
            dur=2.2, footer="HUISWERK PLANNER  •  VEILIG AFSLUITEN", finish=self.finish)

    def finish(self):
        try:
            self.destroy()
        finally:
            os._exit(0)


# ============================================================
# UPDATE CENTER (zelfde logica, nieuw design)
# ============================================================

UP_BG, UP_CARD, UP_ROW, UP_LINE = "#070A12", "#0D1320", "#111827", "#1f2a3d"


class UpdateWindow(ctk.CTkToplevel):
    """Updatecentrum met duidelijke download- en installatiefases."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.busy = False
        self.download_active = False
        self.protocol_running = True
        self.downloaded_script = None
        self.temporary = None

        self.title("Huiswerk Planner • Update Center")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color=UP_BG)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        accent = th(parent.theme_name)["accent"]
        self.accent = accent

        card = ctk.CTkFrame(self, fg_color=UP_CARD, corner_radius=28, border_width=1, border_color=UP_LINE)
        card.pack(fill="both", expand=True, padx=22, pady=22)
        ctk.CTkFrame(card, fg_color=accent, height=4, corner_radius=4).pack(fill="x", padx=70, pady=(0, 20))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=48)
        ctk.CTkLabel(header, text="⟳", width=64, height=64, corner_radius=20,
                     fg_color=blend(UP_CARD, accent, .18), text_color=accent,
                     font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", padx=(16, 0))
        ctk.CTkLabel(titles, text="UPDATE CENTER", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#F7F9FC").pack(anchor="w")
        ctk.CTkLabel(titles, text=f"Huiswerk Planner • huidige versie {HUIDIGE_VERSIE}",
                     font=ctk.CTkFont(size=12), text_color="#7F8DA5").pack(anchor="w", pady=(2, 0))

        self.status = ctk.CTkLabel(card, text="Updates zoeken...",
                                   font=ctk.CTkFont(size=14, weight="bold"), text_color="#C1CAD8")
        self.status.pack(pady=(20, 4))
        self.version_label = ctk.CTkLabel(card, text="VERBINDEN MET UPDATE-SERVER",
                                          font=ctk.CTkFont(size=9, weight="bold"), text_color="#5F6D83")
        self.version_label.pack(pady=(0, 14))

        self.download_title, self.download_info, self.download_progress = self._step(
            card, "01", "DOWNLOADEN", "Wachten...  •  0%", accent)
        self.install_title, self.install_info, self.install_progress = self._step(
            card, "02", "INSTALLEREN", "Wacht op download...  •  0%", GROEN)
        self.install_title.configure(text_color="#5F6D83")

        self.percent = ctk.CTkLabel(card, text="0%", font=ctk.CTkFont(size=26, weight="bold"),
                                    text_color="#F7F9FC")
        self.percent.pack(pady=(10, 0))
        self.speed = ctk.CTkLabel(card, text="Gereed voor controle", font=ctk.CTkFont(size=10),
                                  text_color="#59677C")
        self.speed.pack(pady=(1, 0))

        self.close_button = ctk.CTkButton(card, text="Annuleren", height=40, corner_radius=12,
                                          command=self.cancel, fg_color="#171E2A",
                                          text_color="#8F9BB3", hover_color="#202A3A")
        self.close_button.pack(fill="x", padx=48, pady=(14, 18))
        self.after(150, self.start_check)

    def _step(self, card, nr, title, info, color):
        row = ctk.CTkFrame(card, fg_color=UP_ROW, corner_radius=16, border_width=1, border_color=UP_LINE)
        row.pack(fill="x", padx=48, pady=(0, 8))
        row.columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=nr, width=36, height=36, corner_radius=12,
                     fg_color=blend(UP_ROW, color, .2), text_color=color,
                     font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, rowspan=2,
                                                                     padx=(14, 12), pady=12)
        t = ctk.CTkLabel(row, text=title, anchor="w", font=ctk.CTkFont(size=10, weight="bold"), text_color=color)
        t.grid(row=0, column=1, sticky="w", pady=(10, 0))
        i = ctk.CTkLabel(row, text=info, anchor="w", font=ctk.CTkFont(size=10), text_color="#6F7B92")
        i.grid(row=1, column=1, sticky="w")
        bar = ctk.CTkProgressBar(row, height=8, corner_radius=8, fg_color="#172131", progress_color=color)
        bar.set(0)
        bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(4, 14))
        return t, i, bar

    def safe_ui(self, callback):
        if self.protocol_running and self.winfo_exists():
            try:
                self.after(0, callback)
            except tk.TclError:
                pass

    def start_check(self):
        if self.busy:
            return
        self.busy = True
        self.close_button.configure(state="disabled")
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _check_worker(self):
        try:
            self.safe_ui(lambda: self.status.configure(text="Update-server controleren..."))
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={"User-Agent": "HuiswerkPlanner/7.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                nieuwste = response.read().decode("utf-8").strip()
            if not nieuwste:
                raise RuntimeError("De update-server stuurde geen versienummer.")
            self.safe_ui(lambda: self.version_label.configure(text=f"BESCHIKBARE VERSIE  •  {nieuwste}"))
            if nieuwste == HUIDIGE_VERSIE:
                self.safe_ui(lambda: self.finish_message(f"Je gebruikt al de nieuwste versie ({HUIDIGE_VERSIE})."))
            else:
                self.safe_ui(lambda: self.ask_update(nieuwste))
        except Exception as e:
            self.safe_ui(lambda e=e: self.error(e))

    def ask_update(self, nieuwste):
        if not self.winfo_exists():
            return
        antwoord = messagebox.askyesno(
            "Update beschikbaar",
            f"Nieuwe versie gevonden: {nieuwste}\n\nWil je deze nu downloaden en installeren?",
            parent=self)
        if antwoord:
            self.download_update(nieuwste)
        else:
            self.cancel()

    def download_update(self, nieuwste):
        self.download_active = True
        self.busy = True
        self.close_button.configure(state="disabled")
        self.status.configure(text=f"Versie {nieuwste} wordt gedownload...")
        self.download_info.configure(text="Verbinden...  •  0%")
        self.install_info.configure(text="Wacht op download...  •  0%")
        threading.Thread(target=self._download_worker, args=(nieuwste,), daemon=True).start()
        self._animate_download(0, time.monotonic())

    def _animate_download(self, step, started):
        if not self.winfo_exists() or not self.download_active:
            return
        elapsed = time.monotonic() - started
        value = min(elapsed / 10.0, 1.0)
        pct = int(value * 100)
        self.download_progress.set(value)
        self.download_info.configure(text=f"Downloaden...  •  {pct}%  •  {10 - min(int(elapsed), 10)} sec")
        self.percent.configure(text=f"{pct}%")
        if value < 1:
            self.after(100, lambda: self._animate_download(step + 1, started))
        else:
            self.download_info.configure(text="Download voltooid  •  100%  •  ✓")
            self.percent.configure(text="100%")
            if getattr(self, "_download_ready", False):
                self.begin_install()
            else:
                self._download_timer_finished = True

    @staticmethod
    def format_speed(bytes_per_second):
        if bytes_per_second >= 1024 * 1024:
            return f"{bytes_per_second / (1024 * 1024):.2f} MB/s"
        return f"{max(bytes_per_second / 1024, 0):.0f} KB/s"

    def _download_worker(self, nieuwste):
        temporary = None
        try:
            try:
                req_log = urllib.request.Request(GITHUB_CHANGELOG_URL, headers={"User-Agent": "HuiswerkPlanner/7.0"})
                with urllib.request.urlopen(req_log, timeout=10) as response:
                    changelog = response.read().decode("utf-8")
                with open(LOG_BESTAND, "w", encoding="utf-8") as f:
                    f.write(changelog)
            except Exception:
                pass
            req = urllib.request.Request(GITHUB_SCRIPT_URL, headers={"User-Agent": "HuiswerkPlanner/7.0"})
            current = os.path.abspath(sys.argv[0])
            temporary = current + ".update"
            with urllib.request.urlopen(req, timeout=30) as response:
                script = response.read().decode("utf-8")
            if not script.strip():
                raise RuntimeError("De gedownloade update is leeg.")
            compile(script, "<huiswerk-update>", "exec")
            with open(temporary, "w", encoding="utf-8") as f:
                f.write(script)
            self.temporary = temporary
            self.downloaded_script = script
            self.safe_ui(lambda: self._download_finished())
        except Exception as e:
            if temporary and os.path.exists(temporary):
                try:
                    os.remove(temporary)
                except OSError:
                    pass
            self.safe_ui(lambda e=e: self.error(e))

    def _download_finished(self):
        self._download_ready = True
        self.speed.configure(text="Download gecontroleerd • installatie wordt voorbereid")
        if getattr(self, "_download_timer_finished", False):
            self.begin_install()

    def begin_install(self):
        if not self.winfo_exists() or getattr(self, "_install_started", False):
            return
        if not self.downloaded_script or not self.temporary:
            return
        self._install_started = True
        self.status.configure(text="Nieuwe versie installeren...")
        self.install_title.configure(text="INSTALLEREN • BEZIG", text_color=GROEN)
        self.install_info.configure(text="Bestanden vervangen en controleren...  •  0%")
        self.speed.configure(text="Installatie duurt ongeveer 15 seconden")
        self._install_started_at = time.monotonic()
        self._animate_install(self._install_started_at)

    def _animate_install(self, started):
        if not self.winfo_exists():
            return
        elapsed = time.monotonic() - started
        value = min(elapsed / 15.0, 1.0)
        pct = int(value * 100)
        self.install_progress.set(value)
        self.install_info.configure(text=f"Installeren...  •  {pct}%  •  {15 - min(int(elapsed), 15)} sec")
        self.percent.configure(text=f"{pct}%")
        if value < 1:
            self.after(100, lambda: self._animate_install(started))
            return
        try:
            current = os.path.abspath(sys.argv[0])
            with open(self.temporary, "r", encoding="utf-8") as f:
                controle = f.read()
            compile(controle, self.temporary, "exec")
            os.replace(self.temporary, current)
            self.install_info.configure(text="Installatie voltooid  •  100%  •  ✓")
            self.status.configure(text="Update succesvol geïnstalleerd!")
            self.speed.configure(text="Alles is klaar voor de nieuwe versie.")
            self.percent.configure(text="✓")
            self.after(650, self.show_restart_prompt)
        except Exception as e:
            self.error(e)

    def show_restart_prompt(self):
        if not self.winfo_exists():
            return
        prompt = ctk.CTkToplevel(self)
        prompt.title("Update voltooid")
        prompt.geometry("520x320")
        prompt.resizable(False, False)
        prompt.configure(fg_color=UP_CARD)
        prompt.transient(self)
        prompt.grab_set()
        prompt.protocol("WM_DELETE_WINDOW", lambda: None)
        ctk.CTkLabel(prompt, text="✓", width=80, height=80, corner_radius=26,
                     fg_color=blend(UP_CARD, GROEN, .2), text_color=GROEN,
                     font=ctk.CTkFont(size=40, weight="bold")).pack(pady=(32, 12))
        ctk.CTkLabel(prompt, text="Update geïnstalleerd!", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#F7F9FC").pack()
        ctk.CTkLabel(prompt, text="Wil je de Huiswerk Planner opnieuw opstarten?",
                     font=ctk.CTkFont(size=13), text_color="#8F9BB3").pack(pady=(7, 20))
        ctk.CTkButton(prompt, text="JA • OPNIEUW OPSTARTEN", height=46, corner_radius=12,
                      fg_color=self.accent, hover_color=blend(self.accent, "#000000", .15),
                      text_color=on_accent(self.accent), font=ctk.CTkFont(size=12, weight="bold"),
                      command=lambda: self._confirm_restart(prompt)).pack(fill="x", padx=55)

    def _confirm_restart(self, prompt):
        try:
            prompt.grab_release()
            prompt.destroy()
        except Exception:
            pass
        self.restart_app()

    def restart_app(self):
        if not self.winfo_exists():
            return
        self.protocol_running = False
        self.busy = True
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.title("Huiswerk Planner • Opnieuw opstarten")
        for child in self.winfo_children():
            try:
                child.destroy()
            except tk.TclError:
                pass
        ctk.CTkLabel(self, text="H", width=96, height=96, corner_radius=30,
                     fg_color=blend(UP_BG, self.accent, .2), text_color=self.accent,
                     font=ctk.CTkFont(size=48, weight="bold")).pack(pady=(140, 18))
        ctk.CTkLabel(self, text="HUISWERK PLANNER", font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#F7F9FC").pack()
        ctk.CTkLabel(self, text="Opnieuw opstarten...", font=ctk.CTkFont(size=14),
                     text_color="#8290A6").pack(pady=(6, 20))
        bar = ctk.CTkProgressBar(self, width=480, height=9, fg_color="#172131", progress_color=self.accent)
        bar.set(0)
        bar.pack()
        self._restart_bar = bar
        self._restart_step = 0
        self._restart_tick()

    def _restart_tick(self):
        if not self.winfo_exists():
            return
        self._restart_step += 1
        value = min(self._restart_step / 20, 1.0)
        self._restart_bar.set(value)
        if value < 1:
            self.after(70, self._restart_tick)
        else:
            try:
                current = os.path.abspath(sys.argv[0])
                self.destroy()
                os.execv(sys.executable, [sys.executable, current])
            except Exception as e:
                messagebox.showerror(
                    "Herstart mislukt",
                    f"De update is geïnstalleerd, maar de app kon niet automatisch opnieuw worden gestart.\n\n{e}")

    def finish_message(self, text):
        if not self.winfo_exists():
            return
        self.status.configure(text=text)
        self.percent.configure(text="✓")
        self.speed.configure(text="")
        self.close_button.configure(state="normal", text="Sluiten", command=self.cancel)

    def error(self, error):
        if not self.winfo_exists():
            return
        self.busy = False
        self.download_active = False
        self.close_button.configure(state="normal", text="Sluiten", command=self.cancel)
        self.status.configure(text="Er is iets misgegaan.")
        messagebox.showerror("Update mislukt", f"De update kon niet worden uitgevoerd:\n\n{error}", parent=self)

    def cancel(self):
        if self.download_active or getattr(self, "_install_started", False):
            return
        self.protocol_running = False
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


# ============================================================
# HOOFDAPP
# ============================================================

class HuiswerkApp(ctk.CTk):
    # AutoSave is volledig uitgeschakeld. Er wordt nergens automatisch opgeslagen of ververst.
    # Alleen expliciete opslagacties (Handmatig opslaan / Instellingen opslaan) schrijven naar disk.

    def __init__(self):
        super().__init__()
        self.data = laden()
        self.theme_name = self.data["settings"].get("theme", "Wit")
        if self.theme_name not in THEMES:
            self.theme_name = "Wit"
        ACTIVE_THEME[0] = self.theme_name
        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])
        ctk.set_default_color_theme("blue")

        # Geen fullscreen / auto-zoom: handmatig vergroten via de Windows-knoppen.
        self.title("Huiswerk Planner")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.start_close)

        self.vakken = ["Nederlands", "Engels", "Rekenen", "Hardware devices", "Netwerken",
                       "3D print support", "Microsoft 365", "service management klant",
                       "basis programmeren", "TopDesk", "install_ic"]
        self.vak_kleuren = {
            "Nederlands": "#ff3b30", "Engels": "#007aff", "Rekenen": "#34c759",
            "Hardware devices": "#ff9500", "Netwerken": "#af52de", "3D print support": "#5ac8fa",
            "Microsoft 365": "#7b61ff", "service management klant": "#ff6482",
            "basis programmeren": "#00b894", "TopDesk": "#ff6b35", "install_ic": "#ffb000",
        }
        self.hw_list = None
        self.clock_label = None
        self.settings_name = None
        self.theme_var = tk.StringVar(value=self.theme_name)
        self.stats_frame = None
        self.status_pill = None
        self.count_label = None
        self._toast = None
        self._toast_job = None
        self._clock_job = None
        self._closing = False
        self.current_page = "huiswerk"
        self.task_filter = "Alles"
        self.task_search = ""
        self.task_sort = "Deadline"

        self._build_layout()
        self.show_huiswerk()
        self.after(450, self.show_update_log)

    # --------------------------------------------------------
    # BOUWSTENEN
    # --------------------------------------------------------
    def _card(self, parent, t, radius=18, fg=None, **kw):
        return ctk.CTkFrame(parent, fg_color=fg or t["bg_card"], corner_radius=radius,
                            border_width=1, border_color=border(t), **kw)

    def _btn(self, parent, t, text, command, kind="soft", **kw):
        ac = t["accent"]
        styles = {
            "primary": dict(fg_color=ac, text_color=on_accent(ac), hover_color=blend(ac, "#000000", .15)),
            "soft": dict(fg_color=t["button_fg"], text_color=t["button_text"], hover_color=t["button_hover"]),
            "ghost": dict(fg_color="transparent", text_color=t["text"], hover_color=t["button_hover"],
                          border_width=1, border_color=border(t)),
            "danger": dict(fg_color=ROOD, text_color="white", hover_color="#d92f26"),
            "success": dict(fg_color=GROEN, text_color="white", hover_color="#2aa84c"),
        }
        opts = dict(corner_radius=10, height=32, font=("Segoe UI", 12, "bold"))
        opts.update(styles[kind])
        opts.update(kw)
        return ctk.CTkButton(parent, text=text, command=command, **opts)

    def _entry(self, parent, t, **kw):
        return ctk.CTkEntry(parent, height=38, corner_radius=10, fg_color=t["bg_main"],
                            border_color=border(t), text_color=t["text"],
                            placeholder_text_color=t["muted"], **kw)

    def _combo(self, parent, t, **kw):
        return ctk.CTkComboBox(parent, height=38, corner_radius=10, fg_color=t["bg_main"],
                               border_color=border(t), button_color=t["accent"],
                               button_hover_color=blend(t["accent"], "#000000", .15),
                               text_color=t["text"], dropdown_fg_color=t["bg_card"],
                               dropdown_text_color=t["text"], dropdown_hover_color=t["button_hover"],
                               state="readonly", **kw)

    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------
    def _build_layout(self):
        t = th(self.theme_name)
        self.configure(fg_color=t["bg_root"])
        self.sidebar = ctk.CTkFrame(self, width=244, corner_radius=0, fg_color=t["bg_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(28, 24))
        ctk.CTkLabel(brand, text="H", width=46, height=46, corner_radius=15, fg_color=t["accent"],
                     text_color=on_accent(t["accent"]), font=("Segoe UI", 23, "bold")).pack(side="left")
        names = ctk.CTkFrame(brand, fg_color="transparent")
        names.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(names, text="Huiswerk", font=("Segoe UI", 19, "bold"), text_color=t["text"]).pack(anchor="w")
        ctk.CTkLabel(names, text="Deadline Planner", font=("Segoe UI", 11), text_color=t["accent"]).pack(anchor="w")

        ctk.CTkLabel(self.sidebar, text="MENU", font=("Segoe UI", 10, "bold"),
                     text_color=t["muted"]).pack(anchor="w", padx=24, pady=(0, 6))
        self.nav = {}
        for key, label, cmd in [("huiswerk", "📚   Huiswerk", self.show_huiswerk),
                                ("settings", "⚙️   Instellingen", self.show_settings)]:
            b = ctk.CTkButton(self.sidebar, text=label, anchor="w", height=46, corner_radius=12,
                              font=("Segoe UI", 13, "bold"), fg_color="transparent",
                              text_color=t["text"], hover_color=t["button_hover"], command=cmd)
            b.pack(fill="x", padx=14, pady=3)
            self.nav[key] = b
        self.btn_huiswerk = self.nav["huiswerk"]
        self.btn_settings = self.nav["settings"]

        ctk.CTkFrame(self.sidebar, height=1, fg_color=border(t)).pack(fill="x", padx=22, pady=18)

        self.btn_handmatig_opslaan = self._btn(
            self.sidebar, t, "💾   Handmatig opslaan", self.handmatig_opslaan, "ghost",
            anchor="w", height=44, corner_radius=12, font=("Segoe UI", 13, "bold"),
            border_color=t["accent"])
        self.btn_handmatig_opslaan.pack(fill="x", padx=14, pady=3)
        self.btn_afsluiten = self._btn(
            self.sidebar, t, "✕   Afsluiten", self.start_close, "danger",
            anchor="w", height=44, corner_radius=12, font=("Segoe UI", 13, "bold"))
        self.btn_afsluiten.pack(fill="x", padx=14, pady=3)

        foot = ctk.CTkFrame(self.sidebar, fg_color=t["bg_main"], corner_radius=14)
        foot.pack(side="bottom", fill="x", padx=14, pady=16)
        self.clock_label = ctk.CTkLabel(foot, text="", font=("Segoe UI", 15, "bold"), text_color=t["text"])
        self.clock_label.pack(pady=(12, 0))
        self.date_label = ctk.CTkLabel(foot, text="", font=("Segoe UI", 11), text_color=t["muted"])
        self.date_label.pack()
        ctk.CTkLabel(foot, text=f"versie {HUIDIGE_VERSIE}", font=("Segoe UI", 10),
                     text_color=t["muted"]).pack(pady=(2, 10))
        self._update_clock()

        self.main_container = ctk.CTkFrame(self, fg_color=t["bg_main"], corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

    def _set_nav(self, active):
        t = th(self.theme_name)
        for key, b in self.nav.items():
            if key == active:
                b.configure(fg_color=blend(t["bg_sidebar"], t["accent"], .18), text_color=t["accent"])
            else:
                b.configure(fg_color="transparent", text_color=t["text"])

    def _rebuild(self):
        """Bouw het hele venster opnieuw op (na thema-wissel). Opent daarna dezelfde pagina."""
        page = self.current_page
        if self._clock_job:
            try:
                self.after_cancel(self._clock_job)
            except Exception:
                pass
        self._rotation_token = getattr(self, "_rotation_token", 0) + 1
        for w in (self.sidebar, self.main_container):
            try:
                w.destroy()
            except Exception:
                pass
        self._build_layout()
        if page == "settings":
            self.show_settings()
        else:
            self.show_huiswerk()

    def clear_main(self):
        self._rotation_token = getattr(self, "_rotation_token", 0) + 1
        self._rotation_running = False
        self.stats_frame = None
        self.status_pill = None
        self.count_label = None
        self.hw_list = None
        for child in self.main_container.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

    def _update_clock(self):
        if self._closing:
            return
        try:
            if self.clock_label and self.clock_label.winfo_exists():
                now = dt.datetime.now()
                self.clock_label.configure(text=now.strftime("%H:%M:%S"))
                self.date_label.configure(text=now.strftime("%d-%m-%Y"))
                self._clock_job = self.after(1000, self._update_clock)
        except tk.TclError:
            pass

    def apply_theme(self):
        # Behouden voor compatibiliteit: een thema-wissel bouwt het venster opnieuw op.
        self._rebuild()

    # --------------------------------------------------------
    # MELDINGEN (toast)
    # --------------------------------------------------------
    def _hide_toast(self):
        try:
            if self._toast is not None and self._toast.winfo_exists():
                self._toast.destroy()
        except Exception:
            pass
        self._toast = None

    def _show_save_confirmation(self, message, error=False):
        """Niet-blokkerende melding onderaan het scherm."""
        try:
            self._hide_toast()
            if self._toast_job:
                try:
                    self.after_cancel(self._toast_job)
                except Exception:
                    pass
            self._toast = ctk.CTkLabel(
                self.main_container, text=f"   {message}   ", height=40, corner_radius=20,
                fg_color=ROOD if error else GROEN, text_color="white", font=("Segoe UI", 12, "bold"))
            self._toast.place(relx=0.5, rely=1.0, anchor="s", y=-24)
            self._toast.lift()
            self._toast_job = self.after(2600, self._hide_toast)
        except Exception:
            pass

    # --------------------------------------------------------
    # AFSLUITEN
    # --------------------------------------------------------
    def start_close(self):
        if self._closing:
            return
        self._closing = True
        # Geen automatische opslag bij afsluiten. Alleen handmatig opslaan schrijft naar schijf.
        try:
            self.withdraw()
        except tk.TclError:
            pass
        try:
            closing = ClosingIntro()
            closing.mainloop()
        except Exception:
            os._exit(0)

    # --------------------------------------------------------
    # OPSLAAN / VERVERSEN
    # --------------------------------------------------------
    def handmatig_opslaan(self):
        """Enige centrale opslagactie: schrijf naar schijf en refresh daarna pas het scherm."""
        return self._direct_ops_save_refresh("✓ Handmatig opgeslagen • Dashboard vernieuwd")

    def handmatig_verversen(self):
        """Ververs alleen de huidige pagina. Er wordt bewust niets opgeslagen."""
        try:
            if self.current_page == "settings":
                self.show_settings()
            else:
                self.show_huiswerk()
            self._show_save_confirmation("↻ Pagina handmatig ververst • niets opgeslagen")
            return True
        except Exception as exc:
            self._show_save_confirmation(f"⚠ Verversen mislukt: {exc}", error=True)
            return False

    def _direct_ops_save_refresh(self, message="✓ Opgeslagen • Dashboard vernieuwd"):
        """Save immediately, rebuild the current page and show confirmation."""
        if not opslaan(self.data):
            self._show_save_confirmation("⚠ Opslaan mislukt", error=True)
            return False
        try:
            if self.current_page == "settings":
                self.show_settings()
            else:
                self.show_huiswerk()
        except Exception:
            pass
        self._show_save_confirmation(message)
        return True

    # --------------------------------------------------------
    # DASHBOARD: ROTERENDE BOODSCHAP
    # --------------------------------------------------------
    def start_dashboard_rotation(self):
        if getattr(self, "_rotation_running", False):
            return
        self._rotation_running = True
        self._rotation_state = False
        self._rotation_token = getattr(self, "_rotation_token", 0) + 1
        self._rotate_dashboard_message(self._rotation_token)

    def _rotate_dashboard_message(self, token):
        if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():
            return
        if not hasattr(self, "dashboard_message"):
            return
        naam = self.data.get("settings", {}).get("gebruikersnaam", "Student").strip() or "Student"
        if self._rotation_state:
            text = f"👋 Hoi {naam}!"
        else:
            # Zoek automatisch de eerstvolgende OPEN taak met een deadline binnen 3 dagen.
            vandaag = dt.date.today()
            kandidaten = []
            for item in self.data.get("huiswerk", []):
                if item.get("done", False):
                    continue
                datum = parse_datum(item.get("datum", ""))
                if datum is None:
                    continue
                dagen = (datum - vandaag).days
                if 0 <= dagen < 3:
                    kandidaten.append((dagen, datum, item))
            kandidaten.sort(key=lambda x: (x[0], x[1], str(x[2].get("vak", "")).lower()))
            if kandidaten:
                vak = str(kandidaten[0][2].get("vak", "Onbekend")).strip() or "Onbekend"
                text = f"🚨 Ey! Begin of ga eens verder met: {vak}"
            else:
                text = "💡 Begin eens aan de vakken die het dichtst bij de deadline zijn"
        self._rotation_state = not self._rotation_state
        self._fade_dashboard_message(text, token)

    def _fade_dashboard_message(self, new_text, token):
        if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():
            return
        t = th(self.theme_name)
        steps = [i / 6 for i in range(7)]

        def color(f):
            return blend(t["bg_main"], t["text"], f)

        def fade_in_step(i=0):
            if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():
                return
            self.dashboard_message.configure(text_color=color(steps[i]))
            if i < len(steps) - 1:
                self.after(60, lambda: fade_in_step(i + 1))
            else:
                self.after(3500, lambda: self._rotate_dashboard_message(token))

        def fade_out_step(i=0):
            if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():
                return
            self.dashboard_message.configure(text_color=color(steps[len(steps) - 1 - i]))
            if i < len(steps) - 1:
                self.after(60, lambda: fade_out_step(i + 1))
            else:
                self.dashboard_message.configure(text=new_text)
                self.after(40, fade_in_step)

        fade_out_step()

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------
    def _top_status(self):
        items = self.data["huiswerk"]
        bezig = next((x for x in items if x.get("in_progress") and not x.get("done")), None)
        upcoming = sorted([x for x in items if not x.get("done") and parse_datum(x.get("datum", ""))],
                          key=lambda x: parse_datum(x.get("datum", "")))
        if bezig:
            return f"▶ Bezig: {bezig.get('titel', 'taak')}"
        if upcoming:
            d = (parse_datum(upcoming[0].get("datum", "")) - dt.date.today()).days
            if d < 0:
                return f"⚠ Deadline {abs(d)} d. geleden"
            return "📌 Deadline vandaag" if d == 0 else f"📌 Volgende deadline over {d} d."
        return "🎉 Alles onder controle"

    def _render_stats(self):
        fr = self.stats_frame
        try:
            if fr is None or not fr.winfo_exists():
                return
        except tk.TclError:
            return
        for c in fr.winfo_children():
            c.destroy()
        t = th(self.theme_name)
        items = self.data["huiswerk"]
        vandaag = dt.date.today()
        totaal = len(items)
        afgerond = sum(bool(x.get("done", False)) for x in items)
        openstaand = totaal - afgerond
        urgent = sum((not bool(x.get("done", False))) and parse_datum(x.get("datum", "")) is not None
                     and 0 <= (parse_datum(x.get("datum", "")) - vandaag).days <= 3 for x in items)
        pct = afgerond / totaal if totaal else 0
        for i in range(5):
            fr.columnconfigure(i, weight=1, uniform="stat")

        card = self._card(fr, t, radius=16)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        cv = tk.Canvas(card, width=78, height=78, bg=t["bg_card"], highlightthickness=0)
        cv.pack(side="left", padx=(14, 6), pady=12)
        cv.create_oval(8, 8, 70, 70, outline=blend(t["bg_card"], t["text"], .12), width=8)
        if pct > 0:
            cv.create_arc(8, 8, 70, 70, start=90, extent=-359.9 * pct, style="arc", outline=GROEN, width=8)
        cv.create_text(39, 39, text=f"{int(pct * 100)}%", fill=t["text"], font=("Segoe UI", 13, "bold"))
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(side="left", pady=12)
        ctk.CTkLabel(box, text="VOORTGANG", font=("Segoe UI", 10, "bold"), text_color=t["muted"]).pack(anchor="w")
        ctk.CTkLabel(box, text=f"{afgerond}/{totaal}", font=("Segoe UI", 20, "bold"),
                     text_color=t["text"]).pack(anchor="w")

        for col, (icon, label, value, color) in enumerate([
                ("📚", "TOTAAL", totaal, t["accent"]),
                ("⏳", "OPENSTAAND", openstaand, ORANJE),
                ("✅", "AFGEROND", afgerond, GROEN),
                ("🔥", "KOMENDE 3 DAGEN", urgent, ROOD if urgent else t["muted"])], start=1):
            c = self._card(fr, t, radius=16)
            c.grid(row=0, column=col, sticky="nsew", padx=6 if col < 4 else (6, 0))
            ctk.CTkLabel(c, text=icon, width=44, height=44, corner_radius=14, font=("Segoe UI", 18),
                         fg_color=blend(t["bg_card"], color, .18)).pack(side="left", padx=(14, 10), pady=14)
            box = ctk.CTkFrame(c, fg_color="transparent")
            box.pack(side="left", pady=12)
            ctk.CTkLabel(box, text=label, font=("Segoe UI", 9, "bold"), text_color=t["muted"]).pack(anchor="w")
            ctk.CTkLabel(box, text=str(value), font=("Segoe UI", 24, "bold"), text_color=color).pack(anchor="w")
        try:
            if self.status_pill is not None and self.status_pill.winfo_exists():
                self.status_pill.configure(text=f"  {self._top_status()}  ")
        except tk.TclError:
            pass

    def show_huiswerk(self):
        self.current_page = "huiswerk"
        self._set_nav("huiswerk")
        self.clear_main()
        t = th(self.theme_name)
        naam = self.data.get("settings", {}).get("gebruikersnaam", "Student").strip() or "Student"
        uur = dt.datetime.now().hour
        groet = "Goedenacht" if uur < 6 else "Goedemorgen" if uur < 12 else "Goedemiddag" if uur < 18 else "Goedenavond"

        head = ctk.CTkFrame(self.main_container, fg_color="transparent")
        head.pack(fill="x", padx=32, pady=(26, 12))
        left = ctk.CTkFrame(head, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(left, text=f"{groet}, {naam}", font=("Segoe UI", 28, "bold"),
                     text_color=t["text"]).pack(anchor="w")
        self.dashboard_message = ctk.CTkLabel(left, text="", font=("Segoe UI", 13),
                                              text_color=t["text"], anchor="w")
        self.dashboard_message.pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(left, text="● AutoSave UIT  •  Alleen handmatig opslaan + refresh",
                     font=("Segoe UI", 10, "bold"), text_color=t["muted"]).pack(anchor="w", pady=(4, 0))
        self.status_pill = ctk.CTkLabel(
            head, text=f"  {self._top_status()}  ", height=36, corner_radius=18,
            fg_color=blend(t["bg_main"], t["accent"], .16), text_color=t["accent"],
            font=("Segoe UI", 12, "bold"))
        self.status_pill.pack(side="right", pady=8)
        self.start_dashboard_rotation()

        self.stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=32, pady=(4, 8))
        self._render_stats()

        legend = ctk.CTkFrame(self.main_container, fg_color="transparent")
        legend.pack(fill="x", padx=34, pady=(2, 8))
        ctk.CTkLabel(legend, text="Legenda", font=("Segoe UI", 11, "bold"),
                     text_color=t["muted"]).pack(side="left", padx=(0, 10))
        for col, label in [(ROOD, "Deadline voorbij"), (ORANJE, "Nog 0–3 dagen"),
                           (t["accent"], "Meer dan 3 dagen"), (GROEN, "Afgerond")]:
            ctk.CTkLabel(legend, text=f"●  {label}", font=("Segoe UI", 11), text_color=col).pack(side="left", padx=8)

        split = ctk.CTkFrame(self.main_container, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        split.columnconfigure(0, weight=5)
        split.columnconfigure(1, weight=3, minsize=330)
        split.rowconfigure(0, weight=1)

        # ---- linker paneel: taken
        lp = self._card(split, t, radius=20)
        lp.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        lh = ctk.CTkFrame(lp, fg_color="transparent")
        lh.pack(fill="x", padx=20, pady=(18, 6))
        ctk.CTkLabel(lh, text="Taken", font=("Segoe UI", 18, "bold"), text_color=t["text"]).pack(side="left")
        self.count_label = ctk.CTkLabel(lh, text=" 0 ", height=24, corner_radius=12,
                                        fg_color=blend(t["bg_card"], t["accent"], .18),
                                        text_color=t["accent"], font=("Segoe UI", 11, "bold"))
        self.count_label.pack(side="left", padx=10)

        fr = ctk.CTkFrame(lp, fg_color="transparent")
        fr.pack(fill="x", padx=16, pady=(4, 8))
        fc = self._combo(fr, t, values=["Alles", "Openstaand", "Afgerond", "Vandaag", "Komende 3 dagen", "Te laat"],
                         width=150, command=self._set_task_filter)
        fc.set(self.task_filter)
        fc.pack(side="left", padx=3)
        sc = self._combo(fr, t, values=["Deadline", "Prioriteit", "Vak", "Nieuwste"], width=115,
                         command=self._set_task_sort)
        sc.set(self.task_sort)
        sc.pack(side="left", padx=3)
        search = self._entry(fr, t, width=150, placeholder_text="🔎 Zoek...")
        if self.task_search:
            search.insert(0, self.task_search)
        search.pack(side="right", padx=3)
        search.bind("<KeyRelease>", lambda event: self._set_task_search(search.get()))

        self.hw_list = ctk.CTkScrollableFrame(lp, fg_color="transparent")
        self.hw_list.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ---- rechter paneel: toevoegen
        rp = self._card(split, t, radius=20)
        rp.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(rp, text="➕  Huiswerk toevoegen", font=("Segoe UI", 18, "bold"),
                     text_color=t["text"]).pack(anchor="w", padx=22, pady=(18, 6))

        def label(txt, top=10):
            ctk.CTkLabel(rp, text=txt, font=("Segoe UI", 11, "bold"), text_color=t["muted"]).pack(
                anchor="w", padx=22, pady=(top, 3))

        label("VAK")
        combo = self._combo(rp, t, values=self.vakken)
        combo.set(self.vakken[0])
        combo.pack(fill="x", padx=22)
        label("HUISWERK / OPDRACHT")
        titel = self._entry(rp, t, placeholder_text="Bijv. hoofdstuk 4 leren")
        titel.pack(fill="x", padx=22)
        label("DEADLINE")
        df = ctk.CTkFrame(rp, fg_color="transparent")
        df.pack(fill="x", padx=22)
        datum = self._entry(df, t)
        datum.insert(0, dt.date.today().strftime("%Y-%m-%d"))
        datum.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._btn(df, t, "📅", lambda: kies_datum(datum), "soft", width=46, height=38).pack(side="left")
        label("PRIORITEIT")
        prioriteit = self._combo(rp, t, values=["Laag", "Normaal", "Hoog"])
        prioriteit.set("Normaal")
        prioriteit.pack(fill="x", padx=22)

        ctk.CTkLabel(rp, text="Rood = deadline voorbij. Oranje = deadline binnen 3 dagen. "
                              "De kleur wordt automatisch bijgewerkt.",
                     font=("Segoe UI", 10), text_color=t["muted"], wraplength=270,
                     justify="left").pack(anchor="w", padx=22, pady=(12, 6))

        def toevoegen():
            vak = combo.get().strip()
            titel_text = titel.get().strip()
            datum_text = datum.get().strip()
            if not titel_text or not datum_text:
                messagebox.showwarning("Invoer ontbreekt", "Vul het huiswerk en de deadline in.", parent=self)
                return
            if parse_datum(datum_text) is None:
                messagebox.showerror("Ongeldige datum", "Gebruik het formaat YYYY-MM-DD.", parent=self)
                return
            self.data["huiswerk"].append({
                "vak": vak, "titel": titel_text, "datum": datum_text, "done": False,
                "priority": prioriteit.get() or "Normaal", "in_progress": False,
            })
            # Niet automatisch opslaan: alleen het scherm bijwerken.
            titel.delete(0, tk.END)
            self._render_huiswerk_lijst()
            self._show_save_confirmation("➕ Toegevoegd • vergeet niet handmatig op te slaan")

        self._btn(rp, t, "➕  Toevoegen", toevoegen, "primary", height=46, corner_radius=12,
                  font=("Segoe UI", 13, "bold")).pack(fill="x", padx=22, pady=(10, 8))
        self._btn(rp, t, "↻  Handmatig verversen", self.handmatig_verversen, "ghost", height=42,
                  corner_radius=12, border_color=t["accent"]).pack(fill="x", padx=22, pady=(0, 18))

        self._render_huiswerk_lijst()

    # --------------------------------------------------------
    # TAKENLIJST
    # --------------------------------------------------------
    def _set_task_filter(self, value):
        self.task_filter = value or "Alles"
        self._render_huiswerk_lijst()

    def _set_task_search(self, value):
        self.task_search = (value or "").strip().lower()
        self._render_huiswerk_lijst()

    def _set_task_sort(self, value):
        self.task_sort = value or "Deadline"
        self._render_huiswerk_lijst()

    def _task_matches_filter(self, item):
        datum = parse_datum(item.get("datum", ""))
        done = bool(item.get("done", False))
        vandaag = dt.date.today()
        filt = self.task_filter
        if filt == "Openstaand" and done:
            return False
        if filt == "Afgerond" and not done:
            return False
        if filt == "Vandaag" and (done or datum != vandaag):
            return False
        if filt == "Komende 3 dagen" and (done or datum is None or not 0 <= (datum - vandaag).days <= 3):
            return False
        if filt == "Te laat" and (done or datum is None or (datum - vandaag).days >= 0):
            return False
        zoek = self.task_search
        if zoek and zoek not in f"{item.get('vak', '')} {item.get('titel', '')} {item.get('datum', '')}".lower():
            return False
        return True

    def _status_info(self, item, t, vandaag):
        """Geeft (statustekst, statuskleur, streepkleur, achtergrond) voor een taak."""
        datum = parse_datum(item.get("datum", ""))
        days = (datum - vandaag).days if datum else None
        vak_color = self.vak_kleuren.get(item.get("vak", ""), t["accent"])
        if bool(item.get("done", False)):
            if days is None:
                txt = "✓ AFGEROND • DATUM ONBEKEND"
            elif days < 0:
                txt = f"✓ AFGEROND • DEADLINE {abs(days)} DAGEN GELEDEN"
            elif days == 0:
                txt = "✓ AFGEROND • DEADLINE VANDAAG"
            elif days == 1:
                txt = "✓ AFGEROND • NOG 1 DAG"
            else:
                txt = f"✓ AFGEROND • NOG {days} DAGEN"
            return txt, GROEN, GROEN, blend(t["bg_main"], GROEN, .16)
        if days is not None and days < 0:
            return f"⚠ TE LAAT ({abs(days)} d.)", ROOD, ROOD, blend(t["bg_main"], ROOD, .13)
        if days is not None and days <= 3:
            txt = "⏰ VANDAAG" if days == 0 else "⏰ MORGEN" if days == 1 else f"⏰ NOG {days} DAGEN"
            return txt, ORANJE, ORANJE, blend(t["bg_main"], ORANJE, .13)
        txt = f"NOG {days} DAGEN" if days is not None else "DATUM ONBEKEND"
        return txt, t["accent"], vak_color, t["bg_main"]

    def _render_huiswerk_lijst(self):
        if not self.hw_list:
            return
        try:
            if not self.hw_list.winfo_exists():
                return
        except tk.TclError:
            return
        for child in self.hw_list.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        t = th(self.theme_name)
        vandaag = dt.date.today()

        def sort_key(item):
            datum = parse_datum(item.get("datum", ""))
            return (bool(item.get("done", False)), datum if datum else dt.date.max)

        if self.task_sort == "Prioriteit":
            order = {"Hoog": 0, "Normaal": 1, "Laag": 2}
            sort_key = lambda item: (bool(item.get("done", False)), order.get(item.get("priority", "Normaal"), 1),
                                     parse_datum(item.get("datum", "")) or dt.date.max)
        elif self.task_sort == "Vak":
            sort_key = lambda item: (bool(item.get("done", False)), str(item.get("vak", "")).lower(),
                                     parse_datum(item.get("datum", "")) or dt.date.max)
        elif self.task_sort == "Nieuwste":
            sort_key = lambda item: (bool(item.get("done", False)), -self.data["huiswerk"].index(item))

        taken = sorted([i for i in self.data["huiswerk"] if self._task_matches_filter(i)], key=sort_key)
        try:
            if self.count_label is not None and self.count_label.winfo_exists():
                self.count_label.configure(text=f" {len(taken)} ")
        except tk.TclError:
            pass
        self._render_stats()

        if not taken:
            box = ctk.CTkFrame(self.hw_list, fg_color="transparent")
            box.pack(pady=40)
            ctk.CTkLabel(box, text="🔎", font=("Segoe UI", 34)).pack()
            ctk.CTkLabel(box, text="Geen taken gevonden met deze selectie.", font=("Segoe UI", 13),
                         text_color=t["muted"]).pack(pady=(6, 0))
            return

        for item in taken:
            self._maak_taakkaart(item, t, vandaag)

    def _maak_taakkaart(self, item, t, vandaag):
        done = bool(item.get("done", False))
        in_progress = bool(item.get("in_progress", False)) and not done
        status_text, status_color, stripe, bg = self._status_info(item, t, vandaag)

        row = ctk.CTkFrame(self.hw_list, fg_color=bg, corner_radius=14,
                           border_width=2 if in_progress else 1,
                           border_color=t["accent"] if in_progress else border(t))
        row.pack(fill="x", padx=4, pady=5)
        ctk.CTkFrame(row, width=6, fg_color=stripe, corner_radius=3).pack(side="left", fill="y", padx=(8, 0), pady=10)
        body = ctk.CTkFrame(row, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=8)

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(2, 2))
        vak = item.get("vak", "Onbekend")
        ctk.CTkLabel(top_row, text=f" {vak} ", font=("Segoe UI", 10, "bold"), text_color="white",
                     fg_color=self.vak_kleuren.get(vak, t["accent"]), corner_radius=6).pack(side="left")
        priority = item.get("priority", "Normaal")
        pcol = ROOD if priority == "Hoog" else (ORANJE if priority == "Normaal" else t["muted"])
        ctk.CTkLabel(top_row, text=f"● {priority}", font=("Segoe UI", 10, "bold"), text_color=pcol).pack(
            side="left", padx=(8, 0))
        if in_progress:
            ctk.CTkLabel(top_row, text=" ▶ BEZIG ", font=("Segoe UI", 9, "bold"), text_color=on_accent(t["accent"]),
                         fg_color=t["accent"], corner_radius=6).pack(side="left", padx=6)
        ctk.CTkLabel(top_row, text=status_text, font=("Segoe UI", 10, "bold"), text_color=status_color).pack(side="right")

        ctk.CTkLabel(body, text=item.get("titel", "Zonder titel"), anchor="w", justify="left", wraplength=470,
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold", overstrike=done),
                     text_color=t["muted"] if done else t["text"]).pack(fill="x", pady=(4, 1))
        ctk.CTkLabel(body, text=f"📅  Deadline: {item.get('datum', '—')}", anchor="w", font=("Segoe UI", 11),
                     text_color=t["muted"]).pack(fill="x", pady=(0, 7))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")

        def flash(target_row):
            kleuren = [blend(t["bg_main"], GROEN, f) for f in (.35, .5, .35, .16)]

            def stap(i=0):
                try:
                    if not target_row.winfo_exists():
                        return
                    target_row.configure(fg_color=kleuren[i])
                    if i < len(kleuren) - 1:
                        target_row.after(110, lambda: stap(i + 1))
                    else:
                        target_row.after(250, self._render_huiswerk_lijst)
                except tk.TclError:
                    pass
            stap()

        def toggle(target=item, target_row=row):
            target["done"] = not bool(target.get("done", False))
            # Niet automatisch opslaan.
            if target["done"]:
                target["in_progress"] = False
                flash(target_row)
            else:
                self._render_huiswerk_lijst()

        def toggle_bezig(target=item):
            if target.get("done", False):
                return
            was_active = bool(target.get("in_progress", False))
            for other in self.data["huiswerk"]:
                if isinstance(other, dict):
                    other["in_progress"] = False
            target["in_progress"] = not was_active
            # Niet automatisch opslaan, alleen het scherm bijwerken.
            self._render_huiswerk_lijst()

        def delete(target=item):
            if messagebox.askyesno("Huiswerk verwijderen",
                                   f"Wil je '{target.get('titel', 'deze taak')}' verwijderen?", parent=self):
                try:
                    self.data["huiswerk"].remove(target)
                except ValueError:
                    return
                # Alleen uit de huidige sessie verwijderen; handmatig opslaan maakt het permanent.
                self._render_huiswerk_lijst()

        if not done:
            self._btn(buttons, t, "⏹ Stop" if in_progress else "▶ Bezig", toggle_bezig,
                      "soft" if in_progress else "primary", width=86).pack(side="left", padx=(0, 4))
        self._btn(buttons, t, "✓ Afgerond" if not done else "↩ Openstaand", toggle,
                  "success" if not done else "soft", width=118).pack(side="left", padx=4)
        self._btn(buttons, t, "📅 Datum", lambda: wijzig_bestaande_datum(self, item), "soft",
                  width=92).pack(side="left", padx=4)
        self._btn(buttons, t, "🗑", delete, "danger", width=40).pack(side="right")

    # --------------------------------------------------------
    # INSTELLINGEN
    # --------------------------------------------------------
    def show_settings(self):
        self.current_page = "settings"
        self._set_nav("settings")
        self.clear_main()
        t = th(self.theme_name)
        page = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=14, pady=(6, 6))

        ctk.CTkLabel(page, text="⚙️  Instellingen", font=("Segoe UI", 28, "bold"),
                     text_color=t["text"]).pack(anchor="w", padx=18, pady=(20, 2))
        ctk.CTkLabel(page, text="● AutoSave UIT  •  Alleen handmatig opslaan + refresh",
                     font=("Segoe UI", 10, "bold"), text_color=t["muted"]).pack(anchor="w", padx=20, pady=(0, 14))

        # ---- profiel
        c1 = self._card(page, t)
        c1.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(c1, text="👤  Gebruikersnaam", font=("Segoe UI", 15, "bold"),
                     text_color=t["text"]).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(c1, text="Wordt gebruikt in de begroeting op het dashboard.", font=("Segoe UI", 11),
                     text_color=t["muted"]).pack(anchor="w", padx=22, pady=(0, 8))
        self.settings_name = self._entry(c1, t, width=320)
        self.settings_name.insert(0, self.data["settings"].get("gebruikersnaam", "Student"))
        self.settings_name.pack(anchor="w", padx=22, pady=(0, 20))
        # AutoSave UIT: gebruikersnaam wordt niet automatisch opgeslagen; gebruik "Instellingen opslaan".

        # ---- thema
        c2 = self._card(page, t)
        c2.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(c2, text="🎨  Thema", font=("Segoe UI", 15, "bold"),
                     text_color=t["text"]).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(c2, text="Kies een thema en klik daarna op 'Instellingen opslaan'.", font=("Segoe UI", 11),
                     text_color=t["muted"]).pack(anchor="w", padx=22, pady=(0, 10))
        grid = ctk.CTkFrame(c2, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 16))
        self.theme_var.set(self.theme_name)
        tiles = {}

        def select(name):
            self.theme_var.set(name)
            for n, tile in tiles.items():
                tile.configure(border_color=t["accent"] if n == name else border(t),
                               border_width=3 if n == name else 1)

        def bind_all(widget, name):
            widget.bind("<Button-1>", lambda e, n=name: select(n))
            for ch in widget.winfo_children():
                bind_all(ch, name)

        for idx, (name, tt) in enumerate(THEMES.items()):
            tile = ctk.CTkFrame(grid, width=170, height=104, corner_radius=14, fg_color=tt["bg_main"],
                                border_width=3 if name == self.theme_name else 1,
                                border_color=t["accent"] if name == self.theme_name else border(t))
            tile.grid(row=idx // 4, column=idx % 4, padx=6, pady=6)
            tile.grid_propagate(False)
            side = ctk.CTkFrame(tile, width=34, height=88, fg_color=tt["bg_sidebar"], corner_radius=10)
            side.place(x=8, y=8)
            ctk.CTkFrame(tile, width=60, height=10, fg_color=tt["accent"], corner_radius=5).place(x=52, y=14)
            ctk.CTkFrame(tile, width=96, height=22, fg_color=tt["bg_card"], corner_radius=6).place(x=52, y=32)
            ctk.CTkLabel(tile, text=name, font=("Segoe UI", 11, "bold"), text_color=tt["text"]).place(x=52, y=70)
            tiles[name] = tile
            bind_all(tile, name)

        # ---- updates
        c3 = self._card(page, t)
        c3.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(c3, text="🔄  Updates", font=("Segoe UI", 15, "bold"),
                     text_color=t["text"]).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(c3, text=f"Huidige versie: {HUIDIGE_VERSIE}\nUpdates worden gecontroleerd via de bestaande GitHub-link.",
                     font=("Segoe UI", 11), text_color=t["muted"], justify="left").pack(anchor="w", padx=22, pady=(0, 10))
        self._btn(c3, t, "🔍  Zoeken naar updates", self.check_update, "soft", height=40,
                  corner_radius=12, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=22, pady=(0, 20))

        self._btn(page, t, "💾  Instellingen opslaan", self.settings_opslaan, "primary", height=46,
                  corner_radius=12, width=240, font=("Segoe UI", 13, "bold")).pack(anchor="e", padx=22, pady=(10, 22))

    def settings_opslaan(self):
        if not self.settings_name:
            return
        nieuw = self.theme_var.get()
        naam = self.settings_name.get().strip()
        if nieuw not in THEMES:
            nieuw = "Wit"
        self.data["settings"]["theme"] = nieuw
        if naam:
            self.data["settings"]["gebruikersnaam"] = naam
        self.theme_name = nieuw
        ACTIVE_THEME[0] = nieuw
        ctk.set_appearance_mode(THEMES[nieuw]["mode"])
        ok = opslaan(self.data)
        self._rebuild()
        if ok:
            self._show_save_confirmation("✓ Instellingen handmatig opgeslagen • Dashboard vernieuwd")
        else:
            self._show_save_confirmation("⚠ Opslaan mislukt", error=True)

    # --------------------------------------------------------
    # UPDATES
    # --------------------------------------------------------
    def check_update(self):
        # Alleen één updatevenster tegelijk.
        if hasattr(self, "_update_window"):
            try:
                if self._update_window.winfo_exists():
                    self._update_window.focus()
                    return
            except tk.TclError:
                pass
        try:
            self._update_window = UpdateWindow(self)
        except Exception as e:
            messagebox.showerror("Update fout", f"Het updatevenster kon niet worden geopend:\n\n{e}", parent=self)

    # --------------------------------------------------------
    # CHANGELOG NA HERSTART
    # --------------------------------------------------------
    def show_update_log(self):
        if not os.path.exists(LOG_BESTAND):
            return
        try:
            with open(LOG_BESTAND, "r", encoding="utf-8") as f:
                changelog = f.read().strip()
        except Exception:
            return
        try:
            os.remove(LOG_BESTAND)
        except OSError:
            pass
        if not changelog:
            return
        t = th(self.theme_name)
        win = ctk.CTkToplevel(self)
        win.title("Wat is er veranderd?")
        win.geometry("700x560")
        win.minsize(560, 440)
        win.configure(fg_color=t["bg_card"])
        win.transient(self)
        ctk.CTkLabel(win, text="🎉", font=("Segoe UI", 40)).pack(pady=(24, 0))
        ctk.CTkLabel(win, text="Update voltooid!", font=("Segoe UI", 26, "bold"),
                     text_color=t["text"]).pack(pady=(0, 2))
        ctk.CTkLabel(win, text="Dit is er veranderd in de nieuwe versie:", font=("Segoe UI", 12),
                     text_color=t["muted"]).pack(pady=(0, 14))
        box = ctk.CTkTextbox(win, font=("Segoe UI", 12), fg_color=t["bg_main"], text_color=t["text"],
                             corner_radius=14, border_width=1, border_color=border(t))
        box.pack(fill="both", expand=True, padx=26, pady=(0, 14))
        box.insert("1.0", changelog)
        box.configure(state="disabled")
        self._btn(win, t, "✓  Begrepen", win.destroy, "primary", height=44, corner_radius=12,
                  font=("Segoe UI", 13, "bold")).pack(fill="x", padx=26, pady=(0, 22))


# ============================================================
# START
# ============================================================

def main():
    # Tk/CustomTkinter krijgt één duidelijke hoofdloop.
    # Eventuele fouten vóór de UI worden netjes gemeld.
    try:
        startup = StartupIntro()
        startup.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("Huiswerk Planner", f"De applicatie kon niet worden gestart:\n\n{e}")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
