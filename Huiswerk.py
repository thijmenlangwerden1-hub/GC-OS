import os







import sys







import json







import datetime as dt







import subprocess







import time







import math







import threading







import urllib.request







import tkinter as tk







from tkinter import messagebox















import customtkinter as ctk







from tkcalendar import Calendar























# ============================================================







# HUISWERK PLANNER 7.0







# Robuuste versie:







# - normale opstartintro







# - GEEN automatische fullscreen/auto-zoom







# - handmatig vergroten/verkleinen via Windows-knoppen







# - veilige opslag







# - smooth UI zonder blokkerende netwerkcalls







# - update zoeken met voortgang







# - downloadsnelheid in KB/s of MB/s







# - veilige update via tijdelijk bestand







# - changelog na herstart







# - nette afsluitanimatie







# ============================================================















HUIDIGE_VERSIE = "1.4v"















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







        "mode": "Light",







        "bg_root": "#f2f3f7",







        "bg_sidebar": "#ffffff",







        "bg_main": "#f7f8fb",







        "bg_card": "#ffffff",







        "text": "#111111",







        "muted": "#666b75",







        "button_text": "#111111",







        "button_fg": "#e3e6ee",







        "button_hover": "#d2d6e4",







        "accent": "#007aff",







    },







    "Zwart": {







        "mode": "Dark",







        "bg_root": "#111111",







        "bg_sidebar": "#18181b",







        "bg_main": "#111111",







        "bg_card": "#1f1f23",







        "text": "#f5f5f7",







        "muted": "#a1a1aa",







        "button_text": "#f5f5f7",







        "button_fg": "#2b2b30",







        "button_hover": "#3a3a40",







        "accent": "#0a84ff",







    },







    "Blauw-Groen": {







        "mode": "Dark",







        "bg_root": "#071821",







        "bg_sidebar": "#0b2430",







        "bg_main": "#071821",







        "bg_card": "#0f2f3b",







        "text": "#e6f9ff",







        "muted": "#9cc4cc",







        "button_text": "#e6f9ff",







        "button_fg": "#145c63",







        "button_hover": "#1a6f78",







        "accent": "#00e5ff",







    },







}























# ============================================================







# VEILIGE DATAFUNCTIES







# ============================================================















def standaard_data():







    return {







        "huiswerk": [],







        "settings": {







            "theme": "Wit",







            "gebruikersnaam": "Student",







        },







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















   



    for item in data["huiswerk"]:



        if isinstance(item, dict):



            item.setdefault("priority", "Normaal")



            item.setdefault("in_progress", False)



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















def kies_datum(entry):







    top = ctk.CTkToplevel()







    top.title("Kies deadline")







    top.geometry("320x360")







    top.resizable(False, False)







    top.transient(entry.winfo_toplevel())







    top.grab_set()















    cal = Calendar(







        top,







        selectmode="day",







        date_pattern="yyyy-mm-dd",







    )







    cal.pack(padx=10, pady=10, fill="both", expand=True)















    def selecteer():







        try:







            entry.delete(0, tk.END)







            entry.insert(0, cal.get_date())







        finally:







            top.destroy()















    ctk.CTkButton(







        top,







        text="✓ Deadline selecteren",







        command=selecteer,







    ).pack(padx=15, pady=(0, 15), fill="x")























# ============================================================







# DEADLINE VAN BESTAANDE TAAK WIJZIGEN







# ============================================================















def wijzig_bestaande_datum(parent, target):







    top = ctk.CTkToplevel(parent)







    top.title("Deadline wijzigen")







    top.geometry("320x360")







    top.resizable(False, False)







    top.transient(parent)







    top.grab_set()















    huidige = parse_datum(target.get("datum", "")) or dt.date.today()







    cal = Calendar(







        top,







        selectmode="day",







        date_pattern="yyyy-mm-dd",







        year=huidige.year,







        month=huidige.month,







        day=huidige.day,







    )







    cal.pack(padx=10, pady=10, fill="both", expand=True)















    def opslaan_datum():







        target["datum"] = cal.get_date()







        parent._direct_ops_save_refresh("✓ Deadline opgeslagen • Dashboard vernieuwd")

        top.destroy()















    ctk.CTkButton(







        top,







        text="✓ Deadline opslaan",







        command=opslaan_datum,







    ).pack(padx=15, pady=(0, 15), fill="x")























# ============================================================







# STARTUP INTRO







# ============================================================















class StartupIntro(ctk.CTk):

    def __init__(self):

        super().__init__(); self.title("Huiswerk Planner"); self.geometry("980x620"); self.resizable(False,False); self.configure(fg_color="#05070C"); self.protocol("WM_DELETE_WINDOW",lambda:None); self.update_idletasks(); x=(self.winfo_screenwidth()-980)//2; y=(self.winfo_screenheight()-620)//2; self.geometry(f"980x620+{x}+{y}")

        self.canvas=tk.Canvas(self,bg="#05070C",highlightthickness=0,bd=0); self.canvas.pack(fill="both",expand=True)

        for box,col,w in [((-180,-220,420,380),"#102348",2),((650,300,1150,800),"#101F3C",2),((720,-180,1120,220),"#0B2A4B",1)]: self.canvas.create_oval(*box,outline=col,width=w)

        card=ctk.CTkFrame(self,fg_color="#0B1019",corner_radius=34,border_width=1,border_color="#243149"); card.place(relx=.5,rely=.5,anchor="center",relwidth=.82,relheight=.78)

        ctk.CTkLabel(card,text="H",width=96,height=96,corner_radius=30,fg_color="#121D30",text_color="#6D8CFF",font=ctk.CTkFont(size=48,weight="bold")).pack(pady=(36,14))

        ctk.CTkLabel(card,text="HUISWERK PLANNER",font=ctk.CTkFont(size=31,weight="bold"),text_color="#F7F9FC").pack(); ctk.CTkLabel(card,text="Jouw schooldag. Georganiseerd.",font=ctk.CTkFont(size=14),text_color="#8290A6").pack(pady=(5,20))

        self.phase=ctk.CTkLabel(card,text="INITIALISEREN",font=ctk.CTkFont(size=11,weight="bold"),text_color="#6D8CFF"); self.phase.pack(pady=(4,3)); self.status=ctk.CTkLabel(card,text="Applicatie voorbereiden…",font=ctk.CTkFont(size=14),text_color="#B7C0CF"); self.status.pack(pady=(0,14))

        self.progress=ctk.CTkProgressBar(card,width=570,height=10,corner_radius=8,fg_color="#172131",progress_color="#6D8CFF"); self.progress.set(0); self.progress.pack(); self.percent=ctk.CTkLabel(card,text="0%",font=ctk.CTkFont(size=12,weight="bold"),text_color="#F7F9FC"); self.percent.pack(pady=(9,0))

        ctk.CTkLabel(self,text="SECURE  •  SIMPLE  •  FOCUSED",font=ctk.CTkFont(size=10,weight="bold"),text_color="#39465B").place(relx=.5,rely=.94,anchor="center")

        self.step=0; self.messages=[("INITIALISEREN","Applicatie voorbereiden…"),("LADEN","Huiswerk en deadlines laden…"),("CONTROLEREN","Planning controleren…"),("OPTIMALISEREN","Werkruimte optimaliseren…"),("KLAAR","Alles staat klaar ✓")]; self.after(160,self.animate)

    def animate(self):

        if not self.winfo_exists(): return

        self.step+=1; total=34; v=min(self.step/total,1); self.progress.set(v); self.percent.configure(text=f"{int(v*100)}%"); ph,msg=self.messages[min(self.step//7,4)]; self.phase.configure(text=ph); self.status.configure(text=msg)

        if self.step<total:self.after(58,self.animate)

        else:self.after(550,self.open_app)

    def open_app(self):

        try:self.destroy()

        except Exception:pass

        HuiswerkApp().mainloop()





class ClosingIntro(ctk.CTk):

    def __init__(self):

        super().__init__(); self.title("Huiswerk Planner"); self.geometry("980x620"); self.resizable(False,False); self.configure(fg_color="#05070C"); self.protocol("WM_DELETE_WINDOW",lambda:None); self.update_idletasks(); x=(self.winfo_screenwidth()-980)//2; y=(self.winfo_screenheight()-620)//2; self.geometry(f"980x620+{x}+{y}")

        self.canvas=tk.Canvas(self,bg="#05070C",highlightthickness=0,bd=0); self.canvas.pack(fill="both",expand=True); self.canvas.create_oval(-180,300,400,880,outline="#10271F",width=2); self.canvas.create_oval(650,-220,1160,300,outline="#0E241D",width=2)

        card=ctk.CTkFrame(self,fg_color="#0B1019",corner_radius=34,border_width=1,border_color="#25362F"); card.place(relx=.5,rely=.5,anchor="center",relwidth=.82,relheight=.78)

        ctk.CTkLabel(card,text="✓",width=96,height=96,corner_radius=30,fg_color="#10271F",text_color="#36D58A",font=ctk.CTkFont(size=46,weight="bold")).pack(pady=(36,14)); ctk.CTkLabel(card,text="TOT DE VOLGENDE KEER",font=ctk.CTkFont(size=30,weight="bold"),text_color="#F7F9FC").pack(); ctk.CTkLabel(card,text="Denk aan je huiswerk hè! 😉",font=ctk.CTkFont(size=15),text_color="#8FA09A").pack(pady=(6,20))

        self.phase=ctk.CTkLabel(card,text="OPSLAAN",font=ctk.CTkFont(size=11,weight="bold"),text_color="#36D58A"); self.phase.pack(pady=(4,3)); self.status=ctk.CTkLabel(card,text="Wijzigingen veilig opslaan…",font=ctk.CTkFont(size=14),text_color="#B7C0CF"); self.status.pack(pady=(0,14)); self.progress=ctk.CTkProgressBar(card,width=570,height=10,corner_radius=8,fg_color="#17211F",progress_color="#36D58A"); self.progress.set(0); self.progress.pack(); self.percent=ctk.CTkLabel(card,text="0%",font=ctk.CTkFont(size=12,weight="bold"),text_color="#F7F9FC"); self.percent.pack(pady=(9,0)); ctk.CTkLabel(self,text="ALLES OPGESLAGEN  •  VEILIG AFSLUITEN",font=ctk.CTkFont(size=10,weight="bold"),text_color="#3D5048").place(relx=.5,rely=.94,anchor="center")

        self.step=0; self.messages=[("OPSLAAN","Wijzigingen veilig opslaan…"),("CONTROLEREN","Laatste gegevens controleren…"),("AFRONDEN","Alles netjes afronden…"),("AFSLUITEN","Applicatie afsluiten…"),("TOT ZIENS","Denk aan je huiswerk hè! 😉")]; self.after(150,self.animate)

    def animate(self):

        if not self.winfo_exists(): return

        self.step+=1; total=30; v=min(self.step/total,1); self.progress.set(v); self.percent.configure(text=f"{int(v*100)}%"); ph,msg=self.messages[min(self.step//6,4)]; self.phase.configure(text=ph); self.status.configure(text=msg)

        if self.step<total:self.after(65,self.animate)

        else:self.after(900,self.finish)

    def finish(self):

        try:self.destroy()

        finally:os._exit(0)





# UPDATEVENSTER







# ============================================================















class UpdateWindow(ctk.CTkToplevel):







    """Herbruikbaar updatevenster met veilige thread->UI communicatie."""















    def __init__(self, parent):







        super().__init__(parent)















        self.parent = parent







        self.busy = False







        self.download_active = False















        self.title("Updates zoeken")







        self.geometry("760x500")







        self.resizable(False, False)







        self.configure(fg_color="#05070C")







        self.transient(parent)







        self.grab_set()







        self.protocol("WM_DELETE_WINDOW", self.cancel)















        t = THEMES[parent.theme_name]















        card = ctk.CTkFrame(self, fg_color="#0B1019", corner_radius=34, border_width=1, border_color="#243149")



        card.pack(fill="both", expand=True, padx=26, pady=26)



        ctk.CTkLabel(card, text="↻", font=ctk.CTkFont(size=40, weight="bold"), text_color=t["accent"], fg_color="#121B2B", corner_radius=18, width=68, height=68).pack(pady=(30, 12))



        ctk.CTkLabel(card, text="UPDATE CENTER  •  HUISWERK PLANNER", font=ctk.CTkFont(size=27, weight="bold"), text_color=t["text"]).pack()



        ctk.CTkLabel(card, text="Je planner wordt veilig bijgewerkt", font=ctk.CTkFont(size=14), text_color=t["muted"]).pack(pady=(5, 22))















        self.status = ctk.CTkLabel(







            card,







            text="Verbinden met de update-server...",







            font=("Segoe UI", 12),







            text_color=t["muted"],







        )







        self.status.pack(pady=(0, 16))















        self.progress = ctk.CTkProgressBar(







            card,







            width=450,







            progress_color=t["accent"],







            fg_color=t["button_fg"],







        )







        self.progress.set(0)







        self.progress.pack(pady=8)















        self.percent = ctk.CTkLabel(







            card,







            text="0%",







            font=("Segoe UI", 11, "bold"),







            text_color=t["text"],







        )







        self.percent.pack(pady=3)















        self.speed = ctk.CTkLabel(







            card,







            text="",







            font=("Segoe UI", 11),







            text_color=t["muted"],







        )







        self.speed.pack(pady=3)















        self.close_button = ctk.CTkButton(







            card,







            text="Annuleren",







            command=self.cancel,







            fg_color=t["button_fg"],







            text_color=t["button_text"],







            hover_color=t["button_hover"],







        )







        self.close_button.pack(fill="x", padx=45, pady=(12, 20))















        self.protocol_running = True







        self.after(100, self.start_check)















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







            # Kleine zichtbare laadfase.







            for i in range(1, 6):







                time.sleep(0.08)







                self.safe_ui(







                    lambda i=i: (







                        self.progress.set(i / 20),







                        self.percent.configure(text=f"{i * 5}%"),







                        self.status.configure(text="Updates zoeken..."),







                    )







                )















            req = urllib.request.Request(







                GITHUB_VERSION_URL,







                headers={"User-Agent": "HuiswerkPlanner/7.0"},







            )















            with urllib.request.urlopen(req, timeout=10) as response:







                nieuwste = response.read().decode("utf-8").strip()















            self.safe_ui(lambda: self.progress.set(1))







            self.safe_ui(lambda: self.percent.configure(text="100%"))















            if not nieuwste:







                raise RuntimeError("De update-server stuurde geen versienummer.")















            if nieuwste == HUIDIGE_VERSIE:







                self.safe_ui(







                    lambda: self.finish_message(







                        f"Je gebruikt al de nieuwste versie ({HUIDIGE_VERSIE})."







                    )







                )







            else:







                self.safe_ui(lambda: self.ask_update(nieuwste))















        except Exception as e:







            self.safe_ui(lambda e=e: self.error(e))















    def ask_update(self, nieuwste):







        if not self.winfo_exists():







            return















        antwoord = messagebox.askyesno(







            "Update beschikbaar",







            f"Nieuwe versie gevonden: {nieuwste}\n\n"







            "Wil je deze nu downloaden en installeren?",







            parent=self,







        )















        if antwoord:







            self.download_update(nieuwste)







        else:







            self.cancel()















    def download_update(self, nieuwste):







        self.download_active = True







        self.status.configure(text="Update voorbereiden...")







        self.speed.configure(text="0 KB/s")







        self.percent.configure(text="0%")







        self.progress.set(0)







        self.close_button.configure(state="disabled")















        threading.Thread(







            target=self._download_worker,







            args=(nieuwste,),







            daemon=True,







        ).start()















    @staticmethod







    def format_speed(bytes_per_second):







        if bytes_per_second >= 1024 * 1024:







            return f"{bytes_per_second / (1024 * 1024):.2f} MB/s"







        return f"{max(bytes_per_second / 1024, 0):.0f} KB/s"















    def _download_worker(self, nieuwste):







        temporary = None















        try:







            # Changelog alvast ophalen. Als dat mislukt kan de update nog steeds doorgaan.







            try:







                req_log = urllib.request.Request(







                    GITHUB_CHANGELOG_URL,







                    headers={"User-Agent": "HuiswerkPlanner/7.0"},







                )







                with urllib.request.urlopen(req_log, timeout=10) as response:







                    changelog = response.read().decode("utf-8")















                with open(LOG_BESTAND, "w", encoding="utf-8") as f:







                    f.write(changelog)







            except Exception:







                # Geen crash als changelog tijdelijk niet beschikbaar is.







                pass















            self.safe_ui(







                lambda: self.status.configure(text="Nieuwe versie downloaden...")







            )















            req = urllib.request.Request(







                GITHUB_SCRIPT_URL,







                headers={"User-Agent": "HuiswerkPlanner/7.0"},







            )















            current = os.path.abspath(sys.argv[0])







            temporary = current + ".update"















            total = 0







            start_time = time.monotonic()







            chunks = []















            with urllib.request.urlopen(req, timeout=30) as response:







                header = response.headers.get("Content-Length")















                try:







                    expected = int(header) if header else None







                except (TypeError, ValueError):







                    expected = None















                while True:







                    chunk = response.read(8 * 1024)







                    if not chunk:







                        break















                    chunks.append(chunk)







                    total += len(chunk)















                    elapsed = max(time.monotonic() - start_time, 0.001)







                    speed = total / elapsed















                    if expected:







                        fraction = min(total / expected, 1.0)







                        percentage = int(fraction * 100)







                    else:







                        # Onbekende bestandsgrootte: animatie tot 95%.







                        fraction = min(0.95, 0.05 + total / (10 * 1024 * 1024))







                        percentage = int(fraction * 100)















                    speed_text = self.format_speed(speed)















                    self.safe_ui(







                        lambda fraction=fraction, percentage=percentage,







                        speed_text=speed_text, total=total: (







                            self.progress.set(fraction),







                            self.percent.configure(text=f"{percentage}%"),







                            self.speed.configure(text=speed_text),







                            self.status.configure(







                                text=f"Downloaden... {total / 1024:.1f} KB"







                            ),







                        )







                    )







                    # Rustige download: de interface blijft vloeiend en de







                    # updater trekt niet onnodig hard aan de server.







                    time.sleep(0.025)















            script = b"".join(chunks).decode("utf-8")















            if not script.strip():







                raise RuntimeError("De gedownloade update is leeg.")















            # Eerst controleren of het gedownloade Python-bestand syntactisch klopt.







            compile(script, "<huiswerk-update>", "exec")















            self.safe_ui(







                lambda: self.status.configure(







                    text="Update controleren en voorbereiden..."







                )







            )















            with open(temporary, "w", encoding="utf-8") as f:







                f.write(script)















            # Nogmaals compileren vanaf het tijdelijke bestand.







            with open(temporary, "r", encoding="utf-8") as f:







                controle = f.read()







            compile(controle, temporary, "exec")















            # Eerst oude tijdelijke backup maken.







            backup = current + ".backup"







            try:







                if os.path.exists(backup):







                    os.remove(backup)







                if os.path.exists(current):







                    os.replace(current, backup)







                os.replace(temporary, current)







            except Exception:







                # Probeer het originele bestand te herstellen.







                if os.path.exists(temporary):







                    try:







                        os.remove(temporary)







                    except OSError:







                        pass







                if not os.path.exists(current) and os.path.exists(backup):







                    try:







                        os.replace(backup, current)







                    except OSError:







                        pass







                raise















            self.safe_ui(







                lambda: (







                    self.progress.set(1),







                    self.percent.configure(text="100%"),







                    self.status.configure(







                        text="Update geïnstalleerd. App wordt herstart..."







                    ),







                )







            )















            time.sleep(1)















            # Herstart via hetzelfde Python-executable en dezelfde scriptlocatie.







            self.safe_ui(self.restart_app)















        except Exception as e:







            if temporary and os.path.exists(temporary):







                try:







                    os.remove(temporary)







                except OSError:







                    pass















            self.safe_ui(lambda e=e: self.error(e))















    def restart_app(self):







        """Show a calm circular update screen before restarting the app."""







        if not self.winfo_exists():







            return















        self.protocol_running = False







        self.busy = True















        try:







            self.grab_release()







        except Exception:







            pass















        # Reconfigure this same window instead of opening another one.







        # This avoids flicker and prevents two update windows from appearing.







        self.title("Updates uitvoeren")







        self.geometry("620x620")







        self.resizable(False, False)







        self.configure(fg_color="#05070C")















        for child in self.winfo_children():







            try:







                child.destroy()







            except tk.TclError:







                pass















        # Keep the update window on top while the restart sequence is running.







        try:







            self.attributes("-topmost", True)







        except tk.TclError:







            pass















        ctk.CTkLabel(







            self,







            text="Huiswerk Planner",







            font=("Segoe UI", 25, "bold"),







            text_color="#ffffff",







        ).pack(pady=(42, 5))















        ctk.CTkLabel(







            self,







            text="Updates uitvoeren",







            font=("Segoe UI", 14),







            text_color="#8f9bb3",







        ).pack(pady=(0, 25))















        canvas = tk.Canvas(







            self,







            width=300,







            height=300,







            highlightthickness=0,







            bd=0,







            bg="#0b0d14",







        )







        canvas.pack()















        cx, cy = 150, 150







        radius = 105















        canvas.create_oval(







            cx - radius,







            cy - radius,







            cx + radius,







            cy + radius,







            outline="#202534",







            width=15,







        )















        arc = canvas.create_arc(







            cx - radius,







            cy - radius,







            cx + radius,







            cy + radius,







            start=90,







            extent=0,







            style="arc",







            outline="#1677ff",







            width=15,







        )















        pct = ctk.CTkLabel(







            self,







            text="0%",







            font=("Segoe UI", 32, "bold"),







            text_color="#ffffff",







        )







        pct.place(relx=0.5, rely=0.485, anchor="center")















        main_text = ctk.CTkLabel(







            self,







            text="er worden updates uitgevoerd houd de computer met de app geopent",







            font=("Segoe UI", 13, "bold"),







            text_color="#ffffff",







            wraplength=500,







            justify="center",







        )







        main_text.pack(pady=(8, 8))















        sub_text = ctk.CTkLabel(







            self,







            text="Even geduld...",







            font=("Segoe UI", 11),







            text_color="#6f7b92",







        )







        sub_text.pack()















        def set_progress(value):







            if not self.winfo_exists():







                return







            value=max(0.0,min(1.0,value))







            canvas.itemconfigure(arc, extent=-360*value)







            pct.configure(text=f"{int(value*100)}%")















        def smooth_progress(target, duration=0.8, done=None):







            """Animate the ring smoothly on the Tk main thread."""







            state={"value":0.0}







            steps=max(1,int(duration*30))















            def tick(i=0):







                if not self.winfo_exists():







                    return







                # Ease-out curve: starts smoothly and slows at the target.







                p=i/steps







                eased=1-(1-p)*(1-p)







                value=target*eased







                set_progress(value)







                if i<steps:







                    self.after(33,lambda:tick(i+1))







                elif done:







                    done()















            tick()















        def fade_in_restart_message():







            if not self.winfo_exists():







                return















            message="de app word automatische opnieuw opgestart"







            shades=[







                "#30333b","#4a4d55","#62656d","#7a7d85",







                "#92959d","#aaadb5","#c2c5cc","#d9dce2","#ffffff"







            ]















            main_text.configure(text=message)















            def step(i=0):







                if not self.winfo_exists():







                    return







                main_text.configure(text_color=shades[i])







                if i < len(shades)-1:







                    self.after(80,lambda:step(i+1))







                else:







                    self.after(900,launch)















            step()















        def launch():







            if not self.winfo_exists():







                return















            try:







                self.attributes("-topmost", False)







            except tk.TclError:







                pass















            try:







                current=os.path.abspath(sys.argv[0])







                self.destroy()







                # Replace the current process. This prevents the old app and







                # new app from briefly running side-by-side.







                os.execv(sys.executable,[sys.executable,current])







            except Exception as e:







                try:







                    if not self.winfo_exists():







                        # Recreate a tiny error window only if possible.







                        messagebox.showerror(







                            "Herstart mislukt",







                            "De update is geïnstalleerd, maar de app kon niet "







                            f"automatisch opnieuw worden gestart.\n\n{e}",







                        )







                    else:







                        messagebox.showerror(







                            "Herstart mislukt",







                            "De update is geïnstalleerd, maar de app kon niet "







                            f"automatisch opnieuw worden gestart.\n\n{e}",







                            parent=self,







                        )







                except Exception:







                    pass















        # First show the full update message, then smoothly fill the circle.







        set_progress(0)







        self.after(







            250,







            lambda: smooth_progress(







                0.35,







                1.0,







                lambda: self.after(







                    150,







                    lambda: smooth_progress(







                        0.70,







                        1.1,







                        lambda: self.after(







                            150,







                            lambda: smooth_progress(







                                1.0,







                                1.2,







                                fade_in_restart_message,







                            ),







                        ),







                    ),







                ),







            ),







        )















    def finish_message(self, text):







        if not self.winfo_exists():







            return















        self.status.configure(text=text)







        self.percent.configure(text="✓")







        self.speed.configure(text="")







        self.close_button.configure(







            state="normal",







            text="Sluiten",







            command=self.cancel,







        )















    def error(self, error):







        if not self.winfo_exists():







            return















        self.busy = False







        self.download_active = False







        self.close_button.configure(







            state="normal",







            text="Sluiten",







            command=self.cancel,







        )







        self.status.configure(text="Er is iets misgegaan.")







        messagebox.showerror(







            "Update mislukt",







            f"De update kon niet worden uitgevoerd:\n\n{error}",







            parent=self,







        )















    def cancel(self):







        if self.download_active:







            # De urllib-thread kan niet altijd direct worden afgebroken.







            # Daarom sluiten we het venster en laten we de daemon-thread eindigen







            # zodra de netwerkactie klaar is.







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







    def __init__(self):







        super().__init__()















        self.data = laden()







        self.theme_name = self.data["settings"].get("theme", "Wit")















        if self.theme_name not in THEMES:







            self.theme_name = "Wit"















        ctk.set_appearance_mode(THEMES[self.theme_name]["mode"])







        ctk.set_default_color_theme("blue")















        # BELANGRIJK:







        # Geen self.attributes("-fullscreen", True)







        # Geen automatische zoom.







        self.title("Huiswerk Planner")







        self.geometry("1050x680")







        self.minsize(900, 580)







        self.resizable(True, True)















        self.protocol("WM_DELETE_WINDOW", self.start_close)















        self.vakken = [







            "Nederlands",







            "Engels",







            "Rekenen",







            "Hardware devices",







            "Netwerken",







            "3D print support",







            "Microsoft 365",







            "service management klant",







            "basis programmeren",







            "TopDesk",
            "install_ic",







        ]















        self.vak_kleuren = {







            "Nederlands": "#ff3b30",







            "Engels": "#007aff",







            "Rekenen": "#34c759",







            "Hardware devices": "#ff9500",







            "Netwerken": "#af52de",







            "3D print support": "#5ac8fa",







            "Microsoft 365": "#7b61ff",







            "service management klant": "#ff6482",







            "basis programmeren": "#00b894",







            "TopDesk": "#ff6b35",
            "install_ic": "#ffb000",







        }















        self.hw_list = None







        self.clock_label = None







        self.settings_name = None







        self.theme_combo = None







        self._closing = False



        self.task_filter = "Alles"



        self.task_search = ""



        self.task_sort = "Deadline"















        self._build_layout()







        self.apply_theme()







        self.show_huiswerk()















        # Alleen controleren of er na een update een changelog klaarstaat.







        self.after(450, self.show_update_log)















    # --------------------------------------------------------







    # LAYOUT







    # --------------------------------------------------------















    def _build_layout(self):







        t = THEMES[self.theme_name]















        self.configure(fg_color=t["bg_root"])















        self.sidebar = ctk.CTkFrame(







            self,







            width=220,







            corner_radius=0,







            fg_color=t["bg_sidebar"],







        )







        self.sidebar.pack(side="left", fill="y")







        self.sidebar.pack_propagate(False)















        ctk.CTkLabel(







            self.sidebar,







            text="📚 HUISWERK",







            font=("Segoe UI", 21, "bold"),







            text_color=t["text"],







        ).pack(pady=(28, 4))















        ctk.CTkLabel(







            self.sidebar,







            text="Deadline Planner",







            font=("Segoe UI", 11),







            text_color=t["accent"],







        ).pack(pady=(0, 28))















        self.btn_huiswerk = ctk.CTkButton(







            self.sidebar,







            text="📚  Huiswerk",







            anchor="w",







            height=42,







            font=("Segoe UI", 13, "bold"),







            fg_color=t["button_fg"],







            text_color=t["button_text"],







            hover_color=t["button_hover"],







            command=self.show_huiswerk,







        )







        self.btn_huiswerk.pack(fill="x", padx=12, pady=5)















        self.btn_settings = ctk.CTkButton(







            self.sidebar,







            text="⚙️  Instellingen",







            anchor="w",







            height=42,







            font=("Segoe UI", 13),







            fg_color="transparent",







            text_color=t["button_text"],







            hover_color=t["button_hover"],







            command=self.show_settings,







        )







        self.btn_settings.pack(fill="x", padx=12, pady=5)















        self.btn_afsluiten = ctk.CTkButton(







            self.sidebar,







            text="✕  Afsluiten",







            anchor="w",







            height=42,







            font=("Segoe UI", 13, "bold"),







            fg_color=ROOD,







            text_color="white",







            hover_color="#d92f26",







            command=self.start_close,







        )







        self.btn_afsluiten.pack(fill="x", padx=12, pady=5)















        self.clock_label = ctk.CTkLabel(







            self.sidebar,







            text="",







            font=("Segoe UI", 11, "bold"),







            text_color=t["text"],







        )







        self.clock_label.pack(side="bottom", pady=20)















        self._update_clock()















        self.main_container = ctk.CTkFrame(







            self,







            fg_color=t["bg_main"],







            corner_radius=0,







        )







        self.main_container.pack(side="right", fill="both", expand=True)

        self.bind("<FocusIn>", self._focus_refresh)















    def clear_main(self):







        self._rotation_token = getattr(self, "_rotation_token", 0) + 1







        self._rotation_running = False







        for child in self.main_container.winfo_children():







            try:







                child.destroy()







            except Exception:







                pass















    def _focus_refresh(self, event=None):

        if getattr(self, "_closing", False):

            return

        try:

            if getattr(self, "current_page", "huiswerk") == "huiswerk":

                self.show_huiswerk()

        except Exception:

            pass



    def _update_clock(self):







        if self._closing:







            return















        try:







            if self.clock_label and self.clock_label.winfo_exists():







                self.clock_label.configure(







                    text=dt.datetime.now().strftime("%H:%M:%S\n%d-%m-%Y")







                )







                self.after(1000, self._update_clock)







        except tk.TclError:







            pass















    def apply_theme(self):







        t = THEMES[self.theme_name]















        try:







            self.configure(fg_color=t["bg_root"])







            self.sidebar.configure(fg_color=t["bg_sidebar"])







            self.main_container.configure(fg_color=t["bg_main"])







            self.btn_huiswerk.configure(







                fg_color=t["button_fg"],







                text_color=t["button_text"],







                hover_color=t["button_hover"],







            )







            self.btn_settings.configure(







                text_color=t["button_text"],







                hover_color=t["button_hover"],







            )







            self.clock_label.configure(text_color=t["text"])







        except tk.TclError:







            pass















    # --------------------------------------------------------







    # AFSLUITEN







    # --------------------------------------------------------















    def start_close(self):







        if self._closing:







            return















        self._closing = True







        opslaan(self.data)















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







    # HUISWERK







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







            # Zoek automatisch de eerstvolgende OPEN taak met een deadline



            # binnen minder dan 3 dagen. De dichtstbijzijnde deadline wint.



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







                item = kandidaten[0][2]



                vak = str(item.get("vak", "Onbekend")).strip() or "Onbekend"



                text = f"🚨 Ey! Begin of ga eens verder met: {vak}"







            else:







                text = "💡 Begin eens aan de vakken die het dichtst bij de deadline zijn"







        self._rotation_state = not self._rotation_state







        self._fade_dashboard_message(text, token)















    def _fade_dashboard_message(self, new_text, token):







        if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():







            return







        t = THEMES[self.theme_name]







        fade_out = ["#eeeeee", "#cccccc", "#aaaaaa", "#888888", "#666666"]







        fade_in = ["#666666", "#888888", "#aaaaaa", "#cccccc", t["text"]]















        def fade_in_step(i=0):







            if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():







                return







            self.dashboard_message.configure(text_color=fade_in[min(i, len(fade_in)-1)])







            if i < len(fade_in)-1:







                self.after(70, lambda: fade_in_step(i+1))







            else:







                self.after(3500, lambda: self._rotate_dashboard_message(token))















        def fade_out_step(i=0):







            if token != getattr(self, "_rotation_token", None) or not self.winfo_exists():







                return







            self.dashboard_message.configure(text_color=fade_out[min(i, len(fade_out)-1)])







            if i < len(fade_out)-1:







                self.after(70, lambda: fade_out_step(i+1))







            else:







                self.dashboard_message.configure(text=new_text)







                self.after(40, fade_in_step)















        fade_out_step()



















    def _direct_ops_save_refresh(self, message="✓ Opgeslagen • Dashboard vernieuwd"):

        """Save immediately, rebuild the current page and show confirmation."""

        if not opslaan(self.data):

            self._show_save_confirmation("⚠ Opslaan mislukt", error=True)

            return False



        try:

            if getattr(self, "current_page", "huiswerk") == "huiswerk":

                self.show_huiswerk()

            elif getattr(self, "current_page", "") == "settings":

                self.show_settings()

            else:

                self._render_huiswerk_lijst()

        except Exception:

            pass



        self._show_save_confirmation(message)

        return True



    def _show_save_confirmation(self, message, error=False):

        """Non-blocking status message that survives dashboard refreshes."""

        try:

            label = getattr(self, "save_confirmation", None)

            if label is None or not label.winfo_exists():

                return

            label.configure(

                text=message,

                text_color=ROOD if error else GROEN,

            )

            old = getattr(self, "_save_confirmation_after", None)

            if old:

                try:

                    self.after_cancel(old)

                except Exception:

                    pass

            self._save_confirmation_after = self.after(

                2200,

                lambda: label.winfo_exists() and label.configure(text="")

            )

        except Exception:

            pass



    def show_huiswerk(self):



        self.current_page = "huiswerk"







        self.clear_main()







        t = THEMES[self.theme_name]















        top = ctk.CTkFrame(







            self.main_container,







            fg_color="transparent",







        )







        top.pack(fill="x", padx=32, pady=(25, 8))















        header = ctk.CTkFrame(top, fg_color="transparent")







        header.pack(side="left", fill="x", expand=True)















        naam = self.data.get("settings", {}).get("gebruikersnaam", "Student").strip() or "Student"















        ctk.CTkLabel(







            header,







            text=f"📚 Mijn Huiswerk  •  {naam}",







            font=("Segoe UI", 26, "bold"),







            text_color=t["text"],







        ).pack(anchor="w")















        self.dashboard_message = ctk.CTkLabel(







            header,







            text="",







            font=("Segoe UI", 12),







            text_color=t["text"],







            anchor="w",







        )







        self.dashboard_message.pack(anchor="w", pady=(2, 0))







        self.start_dashboard_rotation()















        count = sum(







            not bool(item.get("done", False))







            for item in self.data["huiswerk"]







        )















        bezig = next((x for x in self.data["huiswerk"] if x.get("in_progress") and not x.get("done")), None)



        upcoming = sorted([x for x in self.data["huiswerk"] if not x.get("done") and parse_datum(x.get("datum", ""))], key=lambda x: parse_datum(x.get("datum", "")))



        if bezig:



            top_status = f"▶ Bezig: {bezig.get('titel', 'taak')}"



        elif upcoming:



            d = (parse_datum(upcoming[0].get("datum", "")) - dt.date.today()).days



            top_status = "📌 Deadline vandaag" if d == 0 else f"📌 Volgende deadline over {d} d."



        else:



            top_status = "🎉 Alles onder controle"



        ctk.CTkLabel(top, text=top_status, font=("Segoe UI", 11, "bold"), text_color=t["accent"], anchor="e").pack(side="right", pady=8)















        legend = ctk.CTkFrame(







            self.main_container,







            fg_color=t["bg_card"],







            corner_radius=10,







        )







        legend.pack(fill="x", padx=32, pady=(5, 12))















        ctk.CTkLabel(







            legend,







            text="Legenda:",







            font=("Segoe UI", 11, "bold"),







            text_color=t["text"],







        ).pack(side="left", padx=(15, 8), pady=9)















        for col, label in [







            (ROOD, "Deadline voorbij"),







            (ORANJE, "Nog 0–3 dagen"),







            (t["accent"], "Meer dan 3 dagen"),







        ]:







            ctk.CTkLabel(







                legend,







                text=f"● {label}",







                font=("Segoe UI", 11),







                text_color=col,







            ).pack(side="left", padx=8)















        # Overzicht: snel zien hoeveel werk er nog ligt.



        stats = ctk.CTkFrame(self.main_container, fg_color="transparent")



        stats.pack(fill="x", padx=32, pady=(0, 8))



        vandaag = dt.date.today()



        totaal = len(self.data["huiswerk"])



        afgerond = sum(bool(x.get("done", False)) for x in self.data["huiswerk"])



        openstaand = totaal - afgerond



        urgent = sum((not bool(x.get("done", False))) and (parse_datum(x.get("datum", "")) is not None) and 0 <= (parse_datum(x.get("datum", "")) - vandaag).days <= 3 for x in self.data["huiswerk"])



        for icon, label, value, color in [("📚", "Totaal", totaal, t["text"]), ("⏳", "Openstaand", openstaand, ORANJE), ("✅", "Afgerond", afgerond, GROEN), ("🔥", "Komende 3 dagen", urgent, ROOD if urgent else t["muted"])]:



            card = ctk.CTkFrame(stats, fg_color=t["bg_card"], corner_radius=10)



            card.pack(side="left", fill="x", expand=True, padx=3)



            ctk.CTkLabel(card, text=f"{icon}  {label}", font=("Segoe UI", 10), text_color=t["muted"]).pack(anchor="w", padx=12, pady=(7, 0))



            ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 19, "bold"), text_color=color).pack(anchor="w", padx=12, pady=(0, 7))







        split = ctk.CTkFrame(







            self.main_container,







            fg_color="transparent",







        )







        split.pack(fill="both", expand=True, padx=32, pady=4)







        split.columnconfigure(0, weight=5)







        split.columnconfigure(1, weight=3)







        split.rowconfigure(0, weight=1)















        left = ctk.CTkFrame(







            split,







            fg_color=t["bg_card"],







            corner_radius=12,







        )







        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))















        ctk.CTkLabel(







            left,







            text="Taken",







            font=("Segoe UI", 16, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=18, pady=(16, 8))















        filter_row = ctk.CTkFrame(left, fg_color="transparent")



        filter_row.pack(fill="x", padx=14, pady=(12, 3))



        ctk.CTkLabel(filter_row, text="Weergave", font=("Segoe UI", 11, "bold"), text_color=t["text"]).pack(side="left", padx=3)



        filter_combo = ctk.CTkComboBox(filter_row, values=["Alles", "Openstaand", "Afgerond", "Vandaag", "Komende 3 dagen", "Te laat"], width=150, state="readonly", command=lambda value: self._set_task_filter(value))



        filter_combo.set(getattr(self, "task_filter", "Alles")); filter_combo.pack(side="left", padx=5)



        search = ctk.CTkEntry(filter_row, width=145, placeholder_text="🔎 Zoek...")



        if getattr(self, "task_search", ""): search.insert(0, self.task_search)



        search.pack(side="right", padx=3); search.bind("<KeyRelease>", lambda event: self._set_task_search(search.get()))



        sort_combo = ctk.CTkComboBox(filter_row, values=["Deadline", "Prioriteit", "Vak", "Nieuwste"], width=115, state="readonly", command=lambda value: self._set_task_sort(value))



        sort_combo.set(getattr(self, "task_sort", "Deadline"))



        sort_combo.pack(side="right", padx=5)







        self.hw_list = ctk.CTkScrollableFrame(







            left,







            fg_color="transparent",







        )







        self.hw_list.pack(







            fill="both",







            expand=True,







            padx=10,







            pady=(0, 12),







        )















        right = ctk.CTkFrame(







            split,







            fg_color=t["bg_card"],







            corner_radius=12,







        )







        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))















        ctk.CTkLabel(







            right,







            text="➕ Huiswerk toevoegen",







            font=("Segoe UI", 16, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=20, pady=(16, 12))















        ctk.CTkLabel(







            right,







            text="Vak",







            font=("Segoe UI", 12),







            text_color=t["text"],







        ).pack(anchor="w", padx=20, pady=(4, 2))















        combo = ctk.CTkComboBox(







            right,







            values=self.vakken,







            state="readonly",







            width=250,







        )







        combo.set(self.vakken[0])







        combo.pack(anchor="w", padx=20, pady=5)















        ctk.CTkLabel(







            right,







            text="Huiswerk / opdracht",







            font=("Segoe UI", 12),







            text_color=t["text"],







        ).pack(anchor="w", padx=20, pady=(12, 2))















        titel = ctk.CTkEntry(







            right,







            placeholder_text="Bijv. hoofdstuk 4 leren",







            width=250,







        )







        titel.pack(anchor="w", padx=20, pady=5)















        ctk.CTkLabel(







            right,







            text="Deadline",







            font=("Segoe UI", 12),







            text_color=t["text"],







        ).pack(anchor="w", padx=20, pady=(12, 2))















        date_frame = ctk.CTkFrame(







            right,







            fg_color="transparent",







        )







        date_frame.pack(anchor="w", padx=20, pady=5)















        datum = ctk.CTkEntry(date_frame, width=195)







        datum.insert(0, dt.date.today().strftime("%Y-%m-%d"))







        datum.pack(side="left", padx=(0, 6))















        ctk.CTkButton(







            date_frame,







            text="📅",







            width=45,







            command=lambda: kies_datum(datum),







        ).pack(side="left")















        ctk.CTkLabel(right, text="Prioriteit", font=("Segoe UI", 12), text_color=t["text"]).pack(anchor="w", padx=20, pady=(12, 2))



        prioriteit = ctk.CTkComboBox(right, values=["Laag", "Normaal", "Hoog"], state="readonly", width=250)



        prioriteit.set("Normaal")



        prioriteit.pack(anchor="w", padx=20, pady=5)







        ctk.CTkLabel(







            right,







            text=(







                "Rood = deadline voorbij. Oranje = deadline binnen 3 dagen. "







                "De kleur wordt automatisch bijgewerkt."







            ),







            font=("Segoe UI", 10),







            text_color=t["muted"],







            wraplength=290,







            justify="left",







        ).pack(anchor="w", padx=20, pady=(10, 8))















        def toevoegen():







            vak = combo.get().strip()







            titel_text = titel.get().strip()







            datum_text = datum.get().strip()















            if not titel_text or not datum_text:







                messagebox.showwarning(







                    "Invoer ontbreekt",







                    "Vul het huiswerk en de deadline in.",







                    parent=self,







                )







                return















            if parse_datum(datum_text) is None:







                messagebox.showerror(







                    "Ongeldige datum",







                    "Gebruik het formaat YYYY-MM-DD.",







                    parent=self,







                )







                return















            self.data["huiswerk"].append(







                {







                    "vak": vak,







                    "titel": titel_text,







                    "datum": datum_text,







                    "done": False,



                    "priority": prioriteit.get() or "Normaal",



                    "in_progress": False,







                }







            )



            if self._direct_ops_save_refresh("✓ Huiswerk opgeslagen • Dashboard vernieuwd"):

                titel.delete(0, tk.END)















        ctk.CTkButton(







            right,







            text="➕ Toevoegen",







            height=42,







            fg_color=t["accent"],







            text_color="white",







            command=toevoegen,







        ).pack(







            anchor="w",







            padx=20,







            pady=18,







            fill="x",







        )















        self._render_huiswerk_lijst()















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



        filt = getattr(self, "task_filter", "Alles")



        if filt == "Openstaand" and done: return False



        if filt == "Afgerond" and not done: return False



        if filt == "Vandaag" and (done or datum != vandaag): return False



        if filt == "Komende 3 dagen" and (done or datum is None or not 0 <= (datum-vandaag).days <= 3): return False



        if filt == "Te laat" and (done or datum is None or (datum-vandaag).days >= 0): return False



        zoek = getattr(self, "task_search", "")



        if zoek and zoek not in f"{item.get('vak','')} {item.get('titel','')} {item.get('datum','')}".lower(): return False



        return True







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















        t = THEMES[self.theme_name]







        vandaag = dt.date.today()















        def sort_key(item):







            datum = parse_datum(item.get("datum", ""))







            return (







                bool(item.get("done", False)),







                datum if datum else dt.date.max,







            )















        if getattr(self, "task_sort", "Deadline") == "Prioriteit":



            priority_order = {"Hoog": 0, "Normaal": 1, "Laag": 2}



            sort_key = lambda item: (bool(item.get("done", False)), priority_order.get(item.get("priority", "Normaal"), 1), parse_datum(item.get("datum", "")) or dt.date.max)



        elif getattr(self, "task_sort", "Deadline") == "Vak":



            sort_key = lambda item: (bool(item.get("done", False)), str(item.get("vak", "")).lower(), parse_datum(item.get("datum", "")) or dt.date.max)



        elif getattr(self, "task_sort", "Deadline") == "Nieuwste":



            sort_key = lambda item: (bool(item.get("done", False)), -self.data["huiswerk"].index(item))



        taken = sorted([item for item in self.data["huiswerk"] if self._task_matches_filter(item)], key=sort_key)















        if not taken:







            ctk.CTkLabel(







                self.hw_list,







                text="🔎 Geen taken gevonden met deze selectie.",







                font=("Segoe UI", 13),







                text_color=t["muted"],







            ).pack(pady=35)







            return















        for item in taken:







            datum = parse_datum(item.get("datum", ""))







            days = (datum - vandaag).days if datum else None







            done = bool(item.get("done", False))















            if done:







                # Een afgeronde taak blijft volledig groen, maar laat







                # ook altijd zien hoeveel tijd er nog tot de deadline is.







                status_color = "white"







                if days is None:







                    status_text = "✓ AFGEROND • DATUM ONBEKEND"







                elif days < 0:







                    status_text = f"✓ AFGEROND • DEADLINE {abs(days)} DAGEN GELEDEN"







                elif days == 0:







                    status_text = "✓ AFGEROND • DEADLINE VANDAAG"







                elif days == 1:







                    status_text = "✓ AFGEROND • NOG 1 DAG"







                else:







                    status_text = f"✓ AFGEROND • NOG {days} DAGEN"







                bg = GROEN







            elif days is not None and days < 0:







                status_color = ROOD







                status_text = f"⚠ TE LAAT ({abs(days)} d.)"







                bg = (







                    "#ffe5e3"







                    if t["mode"] == "Light"







                    else "#351b1b"







                )







            elif days is not None and days <= 3:







                status_color = ORANJE







                if days == 0:







                    status_text = "⏰ VANDAAG"







                elif days == 1:







                    status_text = "⏰ MORGEN"







                else:







                    status_text = f"⏰ NOG {days} DAGEN"















                bg = (







                    "#fff1dc"







                    if t["mode"] == "Light"







                    else "#352818"







                )







            else:







                status_color = t["accent"]







                status_text = (







                    f"NOG {days} DAGEN"







                    if days is not None







                    else "DATUM ONBEKEND"







                )







                bg = t["bg_main"]















            in_progress = bool(item.get("in_progress", False)) and not done



            row = ctk.CTkFrame(self.hw_list, fg_color=bg, corner_radius=10, border_width=2 if in_progress else 0, border_color=t["accent"])







            row.pack(fill="x", padx=4, pady=5)















            top_row = ctk.CTkFrame(







                row,







                fg_color="transparent",







            )







            top_row.pack(fill="x", padx=12, pady=(10, 2))















            vak = item.get("vak", "Onbekend")







            vak_color = self.vak_kleuren.get(vak, t["accent"])















            ctk.CTkLabel(







                top_row,







                text=f" {vak} ",







                font=("Segoe UI", 10, "bold"),







                text_color="white",







                fg_color=vak_color,







                corner_radius=5,







            ).pack(side="left")



            priority = item.get("priority", "Normaal")



            priority_color = ROOD if priority == "Hoog" else (ORANJE if priority == "Normaal" else t["muted"])



            ctk.CTkLabel(top_row, text=f" {priority} ", font=("Segoe UI", 9, "bold"), text_color=priority_color).pack(side="left", padx=(6, 0))



            if in_progress:



                ctk.CTkLabel(top_row, text=" ▶ BEZIG ", font=("Segoe UI", 9, "bold"), text_color="white", fg_color=t["accent"], corner_radius=5).pack(side="left", padx=5)







            ctk.CTkLabel(







                top_row,







                text=status_text,







                font=("Segoe UI", 10, "bold"),







                text_color=status_color,







            ).pack(side="right")















            ctk.CTkLabel(







                row,







                text=item.get("titel", "Zonder titel"),







                font=("Segoe UI", 13, "bold"),







                text_color="white" if done else t["text"],







                anchor="w",







            ).pack(fill="x", padx=12, pady=(4, 1))















            ctk.CTkLabel(







                row,







                text=f"Deadline: {item.get('datum', '—')}",







                font=("Segoe UI", 10),







                text_color="white" if done else t["muted"],







                anchor="w",







            ).pack(fill="x", padx=12, pady=(0, 7))















            buttons = ctk.CTkFrame(







                row,







                fg_color="transparent",







            )







            buttons.pack(fill="x", padx=10, pady=(0, 10))















            def _animatie_afgerond(target_row):







                kleuren = ["#34c759", "#45d46f", "#5ee57f", "#34c759"]















                def stap(i=0):







                    try:







                        if not target_row.winfo_exists():







                            return







                        target_row.configure(fg_color=kleuren[i])







                        if i < len(kleuren) - 1:







                            target_row.after(120, lambda: stap(i + 1))







                        else:







                            target_row.after(350, self._render_huiswerk_lijst)







                    except tk.TclError:







                        pass















                stap()















            def toggle(target=item, target_row=row):







                was_done = bool(target.get("done", False))







                target["done"] = not was_done







                if not self._direct_ops_save_refresh("✓ Status opgeslagen • Dashboard vernieuwd"):

                    return















                if target["done"]:







                    # Eerst direct groen maken en daarna de succesanimatie.







                    target_row.configure(fg_color=GROEN)







                    _animatie_afgerond(target_row)







                else:







                    self._render_huiswerk_lijst()















            def wijzig_datum(target=item):







                wijzig_bestaande_datum(self, target)















            def toggle_bezig(target=item):



                if target.get("done", False):



                    return



                was_active = bool(target.get("in_progress", False))



                for other in self.data["huiswerk"]:



                    if isinstance(other, dict):



                        other["in_progress"] = False



                target["in_progress"] = not was_active



                self._direct_ops_save_refresh(

                    "✓ Bezig-status opgeslagen • Dashboard vernieuwd"

                )







            def delete(target=item):







                if messagebox.askyesno(







                    "Huiswerk verwijderen",







                    f"Wil je '{target.get('titel', 'deze taak')}' verwijderen?",







                    parent=self,







                ):







                    try:







                        self.data["huiswerk"].remove(target)







                    except ValueError:







                        return















                    self._direct_ops_save_refresh("✓ Huiswerk verwijderd • Dashboard vernieuwd")















            if not done:



                ctk.CTkButton(buttons, text="⏹ Stop" if in_progress else "▶ Bezig", width=88, height=30, fg_color=t["accent"] if not in_progress else t["button_fg"], text_color="white" if not in_progress else t["button_text"], hover_color=t["button_hover"], command=toggle_bezig).pack(side="left", padx=2)







            ctk.CTkButton(







                buttons,







                text="✓ Afgerond" if not done else "↩ Openstaand",







                width=120,







                height=30,







                fg_color=GROEN if not done else t["button_fg"],







                text_color="white" if not done else t["button_text"],







                hover_color=t["button_hover"],







                command=toggle,







            ).pack(side="left", padx=2)















            ctk.CTkButton(







                buttons,







                text="📅 Datum",







                width=95,







                height=30,







                fg_color="white" if done else t["button_fg"],







                text_color=GROEN if done else t["button_text"],







                hover_color="#e8fff0" if done else t["button_hover"],







                command=wijzig_datum,







            ).pack(side="left", padx=2)















            ctk.CTkButton(







                buttons,







                text="🗑 Verwijderen",







                width=120,







                height=30,







                fg_color=ROOD,







                text_color="white",







                hover_color="#d82f26",







                command=delete,







            ).pack(side="right", padx=2)















    # --------------------------------------------------------







    # INSTELLINGEN







    # --------------------------------------------------------















    def show_settings(self):







        self.clear_main()







        t = THEMES[self.theme_name]















        ctk.CTkLabel(







            self.main_container,







            text="⚙️ Instellingen",







            font=("Segoe UI", 26, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=32, pady=(25, 15))















        card = ctk.CTkFrame(







            self.main_container,







            fg_color=t["bg_card"],







            corner_radius=12,







        )







        card.pack(fill="both", expand=True, padx=32, pady=5)















        ctk.CTkLabel(







            card,







            text="Gebruikersnaam",







            font=("Segoe UI", 14, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=22, pady=(22, 5))















        self.settings_name = ctk.CTkEntry(card, width=300)







        self.settings_name.insert(







            0,







            self.data["settings"].get("gebruikersnaam", "Student"),







        )







        self.settings_name.pack(anchor="w", padx=22, pady=5)

        self.settings_name.bind("<KeyRelease>", self._settings_live_change)















        ctk.CTkLabel(







            card,







            text="Thema",







            font=("Segoe UI", 14, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=22, pady=(20, 5))















        self.theme_combo = ctk.CTkComboBox(







            card,







            values=list(THEMES.keys()),







            state="readonly",







            width=220,







        )







        self.theme_combo.set(self.theme_name)







        self.theme_combo.pack(anchor="w", padx=22, pady=5)

        self.theme_combo.configure(command=self._theme_live_change)















        update_card = ctk.CTkFrame(







            card,







            fg_color=t["bg_main"],







            corner_radius=10,







        )







        update_card.pack(fill="x", padx=22, pady=(30, 10))















        ctk.CTkLabel(







            update_card,







            text="🔄 Updates",







            font=("Segoe UI", 14, "bold"),







            text_color=t["text"],







        ).pack(anchor="w", padx=16, pady=(14, 2))















        ctk.CTkLabel(







            update_card,







            text=(







                f"Huidige versie: {HUIDIGE_VERSIE}\n"







                "Updates worden gecontroleerd via de bestaande GitHub-link."







            ),







            font=("Segoe UI", 11),







            text_color=t["muted"],







            justify="left",







        ).pack(anchor="w", padx=16, pady=(0, 8))















        ctk.CTkButton(







            update_card,







            text="🔍 Zoeken naar updates",







            fg_color=t["button_fg"],







            text_color=t["button_text"],







            hover_color=t["button_hover"],







            command=self.check_update,







        ).pack(anchor="w", padx=16, pady=(0, 15))















        ctk.CTkButton(







            card,







            text="💾 Instellingen opslaan",







            height=42,







            fg_color=t["accent"],







            text_color="white",







            command=self.settings_opslaan,







        ).pack(side="bottom", anchor="e", padx=22, pady=22)















    def _settings_live_change(self, event=None):

        """Save the username immediately after each edit."""

        if not self.settings_name:

            return

        naam = self.settings_name.get().strip()

        if naam:

            self.data["settings"]["gebruikersnaam"] = naam

            if opslaan(self.data):

                self._show_save_confirmation("✓ Gebruikersnaam opgeslagen")



    def _theme_live_change(self, value=None):

        """Apply, save and refresh immediately after a theme selection."""

        nieuw = value or (self.theme_combo.get() if self.theme_combo else "")

        if nieuw not in THEMES:

            return

        self.data["settings"]["theme"] = nieuw

        self.theme_name = nieuw

        ctk.set_appearance_mode(THEMES[nieuw]["mode"])

        if opslaan(self.data):

            self.apply_theme()

            self._show_save_confirmation("✓ Thema opgeslagen")

            self.after(120, self.show_huiswerk)



    def settings_opslaan(self):







        if not self.theme_combo or not self.settings_name:







            return















        nieuw = self.theme_combo.get()







        naam = self.settings_name.get().strip()















        if nieuw not in THEMES:







            nieuw = "Wit"















        self.data["settings"]["theme"] = nieuw















        if naam:







            self.data["settings"]["gebruikersnaam"] = naam















        self.theme_name = nieuw

        ctk.set_appearance_mode(THEMES[nieuw]["mode"])

        self.apply_theme()

        self._direct_ops_save_refresh("✓ Instellingen opgeslagen • Dashboard vernieuwd")















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







            messagebox.showerror(







                "Update fout",







                f"Het updatevenster kon niet worden geopend:\n\n{e}",







                parent=self,







            )















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















        if not changelog:







            try:







                os.remove(LOG_BESTAND)







            except OSError:







                pass







            return















        try:







            os.remove(LOG_BESTAND)







        except OSError:







            pass















        t = THEMES[self.theme_name]















        win = ctk.CTkToplevel(self)







        win.title("Wat is er veranderd?")







        win.geometry("680x520")







        win.minsize(560, 420)







        win.configure(fg_color=t["bg_card"])







        win.transient(self)















        ctk.CTkLabel(







            win,







            text="🎉 Update voltooid!",







            font=("Segoe UI", 24, "bold"),







            text_color=t["text"],







        ).pack(pady=(25, 4))















        ctk.CTkLabel(







            win,







            text="Dit is er veranderd in de nieuwe versie:",







            font=("Segoe UI", 12),







            text_color=t["muted"],







        ).pack(pady=(0, 15))















        box = ctk.CTkTextbox(







            win,







            font=("Segoe UI", 12),







            fg_color=t["bg_main"],







            text_color=t["text"],







            corner_radius=10,







        )







        box.pack(fill="both", expand=True, padx=25, pady=(0, 15))















        box.insert("1.0", changelog)







        box.configure(state="disabled")















        ctk.CTkButton(







            win,







            text="✓ Begrepen",







            height=40,







            fg_color=t["accent"],







            text_color="white",







            command=win.destroy,







        ).pack(fill="x", padx=25, pady=(0, 20))























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







            messagebox.showerror(







                "Huiswerk Planner",







                f"De applicatie kon niet worden gestart:\n\n{e}",







            )







        except Exception:







            pass







        raise























if __name__ == "__main__":







    main()







