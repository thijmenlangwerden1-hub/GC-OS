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

HUIDIGE_VERSIE = "0.2v"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/main/version.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/Huiswerk.py"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/thijmenlangwerden1-hub/GC-OS/refs/heads/GC-OS/changelog.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BESTAND = os.path.join(SCRIPT_DIR, "gc_os_data.json")
LOG_BESTAND = os.path.join(SCRIPT_DIR, "recent_changelog.txt")
ROOD = "#ff3b30"
ORANJE = "#ff9500"
GROEN = "#34c759"
THEMES = {
 "Wit":{"mode":"Light","bg_root":"#f2f3f7","bg_sidebar":"#fff","bg_main":"#f7f8fb","bg_card":"#fff","text":"#111","muted":"#666b75","button_text":"#111","button_fg":"#e3e6ee","button_hover":"#d2d6e4","accent":"#007aff"},
 "Zwart":{"mode":"Dark","bg_root":"#111","bg_sidebar":"#18181b","bg_main":"#111","bg_card":"#1f1f23","text":"#f5f5f7","muted":"#a1a1aa","button_text":"#f5f5f7","button_fg":"#2b2b30","button_hover":"#3a3a40","accent":"#0a84ff"},
 "Blauw-Groen":{"mode":"Dark","bg_root":"#071821","bg_sidebar":"#0b2430","bg_main":"#071821","bg_card":"#0f2f3b","text":"#e6f9ff","muted":"#9cc4cc","button_text":"#e6f9ff","button_fg":"#145c63","button_hover":"#1a6f78","accent":"#00e5ff"}}

def opslaan(data):
 try:
  with open(BESTAND,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=4)
 except Exception as e: messagebox.showerror("Fout",f"Kan data niet opslaan:\n{e}")

def laden():
 standaard={"huiswerk":[],"settings":{"theme":"Wit","gebruikersnaam":"Student"}}
 if not os.path.exists(BESTAND): return standaard
 try:
  with open(BESTAND,"r",encoding="utf-8") as f: data=json.load(f)
 except Exception: return standaard
 if not isinstance(data,dict): data=standaard
 if not isinstance(data.get("huiswerk"),list): data["huiswerk"]=[]
 if not isinstance(data.get("settings"),dict): data["settings"]={}
 data["settings"].setdefault("theme","Wit"); data["settings"].setdefault("gebruikersnaam","Student")
 return data

def kies_datum(entry):
 top=ctk.CTkToplevel(); top.title("Kies deadline"); top.geometry("320x360"); top.resizable(False,False); top.grab_set()
 cal=Calendar(top,selectmode="day",date_pattern="yyyy-mm-dd"); cal.pack(padx=10,pady=10,fill="both",expand=True)
 def selecteer(): entry.delete(0,tk.END); entry.insert(0,cal.get_date()); top.destroy()
 ctk.CTkButton(top,text="✓ Deadline selecteren",command=selecteer).pack(padx=15,pady=(0,15),fill="x")


class StartupIntro(ctk.CTk):
    """Moderne korte opstartanimatie voor de Huiswerk Planner."""

    def __init__(self):
        super().__init__()
        self.title("Huiswerk Planner")
        self.geometry("700x420")
        self.resizable(False, False)
        self.configure(fg_color="#0b0d14")


        ctk.CTkLabel(
            self, text="📚", font=("Segoe UI Emoji", 58),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.29, anchor="center")

        ctk.CTkLabel(
            self, text="HUISWERK PLANNER",
            font=("Segoe UI", 32, "bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.47, anchor="center")

        ctk.CTkLabel(
            self, text="Plan. Werk. Rond af.",
            font=("Segoe UI", 14),
            text_color="#8f9bb3"
        ).place(relx=0.5, rely=0.56, anchor="center")

        self.progress = ctk.CTkProgressBar(
            self, width=460, height=7, corner_radius=5,
            fg_color="#202534", progress_color="#1677ff"
        )
        self.progress.set(0)
        self.progress.place(relx=0.5, rely=0.70, anchor="center")

        self.status = ctk.CTkLabel(
            self, text="Applicatie starten...",
            font=("Segoe UI", 11), text_color="#6f7b92"
        )
        self.status.place(relx=0.5, rely=0.79, anchor="center")

        self.step = 0
        self.after(150, self.animate)

    def animate(self):
        self.step += 1
        self.progress.set(min(self.step / 24, 1))

        messages = [
            "Applicatie starten...",
            "Huiswerk laden...",
            "Deadlines controleren...",
            "Planner voorbereiden...",
            "Bijna klaar...",
        ]
        self.status.configure(text=messages[min(self.step // 5, 4)])

        if self.step < 24:
            self.after(70, self.animate)
        else:
            self.status.configure(text="Klaar!")
            self.after(350, self.open_app)

    def open_app(self):
        self.destroy()
        app = HuiswerkApp()
        app.mainloop()



class ClosingIntro(ctk.CTk):
 def __init__(self):
  super().__init__(); self.title("Huiswerk Planner"); self.geometry("700x420"); self.overrideredirect(True); self.configure(fg_color="#0b0d14"); self.after(50, lambda: self.attributes("-fullscreen", True))
  self.update_idletasks(); x=(self.winfo_screenwidth()-700)//2; y=(self.winfo_screenheight()-420)//2; self.geometry(f"700x420+{x}+{y}")
  ctk.CTkLabel(self,text="📚",font=("Segoe UI Emoji",58),text_color="#ffffff").place(relx=.5,rely=.29,anchor="center")
  ctk.CTkLabel(self,text="TOT ZIENS!",font=("Segoe UI",32,"bold"),text_color="#ffffff").place(relx=.5,rely=.47,anchor="center")
  ctk.CTkLabel(self,text="Denk aan je huiswerk hè!",font=("Segoe UI",15),text_color="#8f9bb3").place(relx=.5,rely=.56,anchor="center")
  self.progress=ctk.CTkProgressBar(self,width=460,height=7,corner_radius=5,fg_color="#202534",progress_color="#ff3b30"); self.progress.set(0); self.progress.place(relx=.5,rely=.70,anchor="center")
  self.status=ctk.CTkLabel(self,text="App afsluiten...",font=("Segoe UI",11),text_color="#6f7b92"); self.status.place(relx=.5,rely=.79,anchor="center")
  self.step=0; self.after(100,self.animate)
 def animate(self):
  self.step+=1; self.progress.set(min(self.step/18,1)); msgs=["App afsluiten...","Huiswerk opslaan...","Alles netjes afsluiten...","Tot de volgende keer!"]; self.status.configure(text=msgs[min(self.step//5,3)])
  if self.step<18: self.after(70,self.animate)
  else: self.status.configure(text="Denk aan je huiswerk hè!"); self.after(500,self.finish)
 def finish(self):
  self.destroy(); sys.exit(0)


class HuiswerkApp(ctk.CTk):
 def __init__(self):
  super().__init__(); self.data=laden(); self.theme_name=self.data["settings"].get("theme","Wit")
  if self.theme_name not in THEMES: self.theme_name="Wit"
  ctk.set_appearance_mode(THEMES[self.theme_name]["mode"]); ctk.set_default_color_theme("blue")
  self.title("Huiswerk Planner"); self.protocol("WM_DELETE_WINDOW",self.start_close); self.geometry("1050x680"); self.minsize(900,580); self.after(100, lambda: self.attributes("-fullscreen", True))
  self.vakken=["Nederlands","Engels","Rekenen","Hardware devices","Netwerken","3D print support","Microsoft 365","service management klant","basis programmeren","install_ic"]
  self.vak_kleuren={"Nederlands":"#ff3b30","Engels":"#007aff","Rekenen":"#34c759","Hardware devices":"#ff9500","Netwerken":"#af52de","3D print support":"#5ac8fa","Microsoft 365":"#7b61ff","service management klant":"#ff6482","basis programmeren":"#00b894","install_ic":"#ffb000"}
  self.hw_list=self.clock_label=self.settings_name=self.theme_combo=None; self._build_layout(); self.apply_theme(); self.show_huiswerk(; self.after(500,self.show_update_log)
 def _build_layout(self):
  t=THEMES[self.theme_name]; self.configure(fg_color=t["bg_root"]); self.sidebar=ctk.CTkFrame(self,width=220,corner_radius=0,fg_color=t["bg_sidebar"]); self.sidebar.pack(side="left",fill="y"); self.sidebar.pack_propagate(False)
  ctk.CTkLabel(self.sidebar,text="📚 HUISWERK",font=("Segoe UI",21,"bold"),text_color=t["text"]).pack(pady=(28,4)); ctk.CTkLabel(self.sidebar,text="Deadline Planner",font=("Segoe UI",11),text_color=t["accent"]).pack(pady=(0,28))
  self.btn_huiswerk=ctk.CTkButton(self.sidebar,text="📚  Huiswerk",anchor="w",height=42,font=("Segoe UI",13,"bold"),fg_color=t["button_fg"],text_color=t["button_text"],hover_color=t["button_hover"],command=self.show_huiswerk); self.btn_huiswerk.pack(fill="x",padx=12,pady=5)
  self.btn_settings=ctk.CTkButton(self.sidebar,text="⚙️  Instellingen",anchor="w",height=42,font=("Segoe UI",13),fg_color="transparent",text_color=t["button_text"],hover_color=t["button_hover"],command=self.show_settings); self.btn_settings.pack(fill="x",padx=12,pady=5)
  self.btn_afsluiten=ctk.CTkButton(self.sidebar,text="✕  Afsluiten",anchor="w",height=42,font=("Segoe UI",13,"bold"),fg_color="#ff3b30",text_color="white",hover_color="#d92f26",command=self.start_close); self.btn_afsluiten.pack(fill="x",padx=12,pady=5)
  self.clock_label=ctk.CTkLabel(self.sidebar,text="",font=("Segoe UI",11,"bold"),text_color=t["text"]); self.clock_label.pack(side="bottom",pady=20); self._update_clock(); self.main_container=ctk.CTkFrame(self,fg_color=t["bg_main"],corner_radius=0); self.main_container.pack(side="right",fill="both",expand=True)
 def clear_main(self):
  for c in self.main_container.winfo_children(): c.destroy()
 def _update_clock(self):
  if self.clock_label and self.clock_label.winfo_exists(): self.clock_label.configure(text=dt.datetime.now().strftime("%H:%M:%S\n%d-%m-%Y")); self.after(1000,self._update_clock)
 def apply_theme(self):
  t=THEMES[self.theme_name]; self.configure(fg_color=t["bg_root"]); self.sidebar.configure(fg_color=t["bg_sidebar"]); self.main_container.configure(fg_color=t["bg_main"]); self.btn_huiswerk.configure(fg_color=t["button_fg"],text_color=t["button_text"],hover_color=t["button_hover"]); self.btn_settings.configure(text_color=t["button_text"],hover_color=t["button_hover"]); self.clock_label.configure(text_color=t["text"])
 def start_close(self):
  opslaan(self.data); self.withdraw(); closing=ClosingIntro(); closing.mainloop()
 def show_huiswerk(self):
  self.clear_main(); t=THEMES[self.theme_name]; top=ctk.CTkFrame(self.main_container,fg_color="transparent"); top.pack(fill="x",padx=32,pady=(25,8)); ctk.CTkLabel(top,text="📚 Mijn Huiswerk",font=("Segoe UI",26,"bold"),text_color=t["text"]).pack(side="left")
  count=sum(not h.get("done",False) for h in self.data["huiswerk"]); ctk.CTkLabel(top,text=f"{count} openstaand",font=("Segoe UI",12),text_color=t["muted"]).pack(side="right",pady=8)
  legend=ctk.CTkFrame(self.main_container,fg_color=t["bg_card"],corner_radius=10); legend.pack(fill="x",padx=32,pady=(5,12)); ctk.CTkLabel(legend,text="Legenda:",font=("Segoe UI",11,"bold"),text_color=t["text"]).pack(side="left",padx=(15,8),pady=9)
  for col,txt in [(ROOD,"Deadline voorbij"),(ORANJE,"Nog 0–3 dagen"),(t["accent"],"Meer dan 3 dagen")]: ctk.CTkLabel(legend,text=f"● {txt}",font=("Segoe UI",11),text_color=col).pack(side="left",padx=8)
  split=ctk.CTkFrame(self.main_container,fg_color="transparent"); split.pack(fill="both",expand=True,padx=32,pady=4); split.columnconfigure(0,weight=5); split.columnconfigure(1,weight=3); split.rowconfigure(0,weight=1)
  left=ctk.CTkFrame(split,fg_color=t["bg_card"],corner_radius=12); left.grid(row=0,column=0,sticky="nsew",padx=(0,8)); ctk.CTkLabel(left,text="Taken",font=("Segoe UI",16,"bold"),text_color=t["text"]).pack(anchor="w",padx=18,pady=(16,8)); self.hw_list=ctk.CTkScrollableFrame(left,fg_color="transparent"); self.hw_list.pack(fill="both",expand=True,padx=10,pady=(0,12))
  right=ctk.CTkFrame(split,fg_color=t["bg_card"],corner_radius=12); right.grid(row=0,column=1,sticky="nsew",padx=(8,0)); ctk.CTkLabel(right,text="➕ Huiswerk toevoegen",font=("Segoe UI",16,"bold"),text_color=t["text"]).pack(anchor="w",padx=20,pady=(16,12))
  ctk.CTkLabel(right,text="Vak",font=("Segoe UI",12),text_color=t["text"]).pack(anchor="w",padx=20,pady=(4,2)); combo=ctk.CTkComboBox(right,values=self.vakken,state="readonly",width=250); combo.set(self.vakken[0]); combo.pack(anchor="w",padx=20,pady=5)
  ctk.CTkLabel(right,text="Huiswerk / opdracht",font=("Segoe UI",12),text_color=t["text"]).pack(anchor="w",padx=20,pady=(12,2)); titel=ctk.CTkEntry(right,placeholder_text="Bijv. hoofdstuk 4 leren",width=250); titel.pack(anchor="w",padx=20,pady=5)
  ctk.CTkLabel(right,text="Deadline",font=("Segoe UI",12),text_color=t["text"]).pack(anchor="w",padx=20,pady=(12,2)); df=ctk.CTkFrame(right,fg_color="transparent"); df.pack(anchor="w",padx=20,pady=5); datum=ctk.CTkEntry(df,width=195); datum.insert(0,dt.date.today().strftime("%Y-%m-%d")); datum.pack(side="left",padx=(0,6)); ctk.CTkButton(df,text="📅",width=45,command=lambda:kies_datum(datum)).pack(side="left")
  ctk.CTkLabel(right,text="Rood = deadline voorbij. Oranje = deadline binnen 3 dagen. De kleur wordt automatisch bijgewerkt.",font=("Segoe UI",10),text_color=t["muted"],wraplength=290,justify="left").pack(anchor="w",padx=20,pady=(10,8))
  def toevoegen():
   v=combo.get().strip(); ti=titel.get().strip(); da=datum.get().strip()
   if not ti or not da: messagebox.showwarning("Invoer ontbreekt","Vul het huiswerk en de deadline in."); return
   try: dt.datetime.strptime(da,"%Y-%m-%d")
   except ValueError: messagebox.showerror("Ongeldige datum","Gebruik het formaat YYYY-MM-DD."); return
   self.data["huiswerk"].append({"vak":v,"titel":ti,"datum":da,"done":False}); opslaan(self.data); titel.delete(0,tk.END); self._render_huiswerk_lijst()
  ctk.CTkButton(right,text="➕ Toevoegen",height=42,fg_color=t["accent"],text_color="white",command=toevoegen).pack(anchor="w",padx=20,pady=18,fill="x"); self._render_huiswerk_lijst()
 def _render_huiswerk_lijst(self):
  if not self.hw_list or not self.hw_list.winfo_exists(): return
  for c in self.hw_list.winfo_children(): c.destroy()
  t=THEMES[self.theme_name]; vandaag=dt.date.today()
  def sort_key(x):
   try: d=dt.datetime.strptime(x.get("datum",""),"%Y-%m-%d").date()
   except ValueError: d=dt.date.max
   return (x.get("done",False),d)
  taken=sorted(self.data["huiswerk"],key=sort_key)
  if not taken: ctk.CTkLabel(self.hw_list,text="🎉 Nog geen huiswerk toegevoegd.",font=("Segoe UI",13),text_color=t["muted"]).pack(pady=35); return
  for item in taken:
   try: d=dt.datetime.strptime(item.get("datum",""),"%Y-%m-%d").date(); days=(d-vandaag).days
   except ValueError: days=None
   done=bool(item.get("done",False))
   if done: status=GROEN; st="✓ AFGEROND"; bg=t["bg_main"]
   elif days is not None and days<0: status=ROOD; st=f"⚠ TE LAAT ({abs(days)} d.)"; bg="#ffe5e3" if t["mode"]=="Light" else "#351b1b"
   elif days is not None and days<=3: status=ORANJE; st="⏰ VANDAAG" if days==0 else ("⏰ MORGEN" if days==1 else f"⏰ NOG {days} DAGEN"); bg="#fff1dc" if t["mode"]=="Light" else "#352818"
   else: status=t["accent"]; st=f"NOG {days} DAGEN" if days is not None else "DATUM ONBEKEND"; bg=t["bg_main"]
   row=ctk.CTkFrame(self.hw_list,fg_color=bg,corner_radius=10); row.pack(fill="x",padx=4,pady=5); tr=ctk.CTkFrame(row,fg_color="transparent"); tr.pack(fill="x",padx=12,pady=(10,2)); vak=item.get("vak","Onbekend"); vc=self.vak_kleuren.get(vak,t["accent"]); ctk.CTkLabel(tr,text=f" {vak} ",font=("Segoe UI",10,"bold"),text_color="white",fg_color=vc,corner_radius=5).pack(side="left"); ctk.CTkLabel(tr,text=st,font=("Segoe UI",10,"bold"),text_color=status).pack(side="right")
   ctk.CTkLabel(row,text=item.get("titel","Zonder titel"),font=("Segoe UI",13,"bold"),text_color=t["muted"] if done else t["text"],anchor="w").pack(fill="x",padx=12,pady=(4,1)); ctk.CTkLabel(row,text=f"Deadline: {item.get('datum','—')}",font=("Segoe UI",10),text_color=t["muted"],anchor="w").pack(fill="x",padx=12,pady=(0,7)); buttons=ctk.CTkFrame(row,fg_color="transparent"); buttons.pack(fill="x",padx=10,pady=(0,10))
   def toggle(target=item): target["done"]=not target.get("done",False); opslaan(self.data); self.show_huiswerk()
   def delete(target=item):
    if messagebox.askyesno("Huiswerk verwijderen",f"Wil je '{target.get('titel','deze taak')}' verwijderen?"): self.data["huiswerk"].remove(target); opslaan(self.data); self.show_huiswerk()
   ctk.CTkButton(buttons,text="✓ Afgerond" if not done else "↩ Openstaand",width=120,height=30,fg_color=GROEN if not done else t["button_fg"],text_color="white" if not done else t["button_text"],hover_color=t["button_hover"],command=toggle).pack(side="left",padx=2); ctk.CTkButton(buttons,text="🗑 Verwijderen",width=120,height=30,fg_color=ROOD,text_color="white",hover_color="#d82f26",command=delete).pack(side="right",padx=2)
 def show_settings(self):
  self.clear_main(); t=THEMES[self.theme_name]; ctk.CTkLabel(self.main_container,text="⚙️ Instellingen",font=("Segoe UI",26,"bold"),text_color=t["text"]).pack(anchor="w",padx=32,pady=(25,15)); card=ctk.CTkFrame(self.main_container,fg_color=t["bg_card"],corner_radius=12); card.pack(fill="both",expand=True,padx=32,pady=5)
  ctk.CTkLabel(card,text="Gebruikersnaam",font=("Segoe UI",14,"bold"),text_color=t["text"]).pack(anchor="w",padx=22,pady=(22,5)); self.settings_name=ctk.CTkEntry(card,width=300); self.settings_name.insert(0,self.data["settings"].get("gebruikersnaam","Student")); self.settings_name.pack(anchor="w",padx=22,pady=5)
  ctk.CTkLabel(card,text="Thema",font=("Segoe UI",14,"bold"),text_color=t["text"]).pack(anchor="w",padx=22,pady=(20,5)); self.theme_combo=ctk.CTkComboBox(card,values=list(THEMES.keys()),state="readonly",width=220); self.theme_combo.set(self.theme_name); self.theme_combo.pack(anchor="w",padx=22,pady=5)
  uc=ctk.CTkFrame(card,fg_color=t["bg_main"],corner_radius=10); uc.pack(fill="x",padx=22,pady=(30,10)); ctk.CTkLabel(uc,text="🔄 Updates",font=("Segoe UI",14,"bold"),text_color=t["text"]).pack(anchor="w",padx=16,pady=(14,2)); ctk.CTkLabel(uc,text=f"Huidige versie: {HUIDIGE_VERSIE}\nUpdates blijven via de bestaande GitHub-link lopen.",font=("Segoe UI",11),text_color=t["muted"],justify="left").pack(anchor="w",padx=16,pady=(0,8)); ctk.CTkButton(uc,text="🔍 Zoeken naar updates",fg_color=t["button_fg"],text_color=t["button_text"],hover_color=t["button_hover"],command=lambda:self.check_update(False)).pack(anchor="w",padx=16,pady=(0,15)); ctk.CTkButton(card,text="💾 Instellingen opslaan",height=42,fg_color=t["accent"],text_color="white",command=self.settings_opslaan).pack(side="bottom",anchor="e",padx=22,pady=22)
 def settings_opslaan(self):
  nieuw=self.theme_combo.get(); naam=self.settings_name.get().strip(); nieuw=nieuw if nieuw in THEMES else "Wit"; self.data["settings"]["theme"]=nieuw
  if naam: self.data["settings"]["gebruikersnaam"]=naam
  opslaan(self.data); self.theme_name=nieuw; ctk.set_appearance_mode(THEMES[nieuw]["mode"]); self.apply_theme(); self.show_huiswerk()
 def check_update(self,silent=False):
  win=ctk.CTkToplevel(self); t=THEMES[self.theme_name]
  win.title("Updates zoeken"); win.geometry("520x300"); win.resizable(False,False)
  win.configure(fg_color=t["bg_card"]); win.transient(self); win.grab_set()
  ctk.CTkLabel(win,text="🔄 Updates zoeken",font=("Segoe UI",21,"bold"),text_color=t["text"]).pack(pady=(28,6))
  status=ctk.CTkLabel(win,text="Verbinden met de update-server...",font=("Segoe UI",12),text_color=t["muted"]); status.pack(pady=(0,14))
  progress=ctk.CTkProgressBar(win,width=420,progress_color=t["accent"],fg_color=t["button_fg"]); progress.set(0); progress.pack(pady=8)
  percent=ctk.CTkLabel(win,text="0%",font=("Segoe UI",11,"bold"),text_color=t["text"]); percent.pack(pady=5)

  def worker():
   try:
    req=urllib.request.Request(GITHUB_VERSION_URL,headers={"User-Agent":"HuiswerkPlanner/7.0"})
    with urllib.request.urlopen(req,timeout=10) as r: nieuwste=r.read().decode("utf-8").strip()
    progress.set(1); percent.configure(text="100%")
    if nieuwste==HUIDIGE_VERSIE:
     status.configure(text=f"Geen update gevonden — versie {HUIDIGE_VERSIE} is actueel.")
     self.after(900,win.destroy); return
    status.configure(text=f"Nieuwe versie gevonden: {nieuwste}"); win.update_idletasks(); time.sleep(.6)
    win.destroy(); self.download_update(nieuwste)
   except Exception as e:
    try: win.destroy()
    except Exception: pass
    if not silent: messagebox.showerror("Update fout",f"Kan geen verbinding maken met de update-server.\n\n{e}")
  self.after(100,worker)

 def download_update(self,nieuwste):
  t=THEMES[self.theme_name]
  win=ctk.CTkToplevel(self); win.title("Update installeren"); win.geometry("560x330"); win.resizable(False,False)
  win.configure(fg_color=t["bg_card"]); win.transient(self); win.grab_set()
  ctk.CTkLabel(win,text="⬇️ Update installeren",font=("Segoe UI",21,"bold"),text_color=t["text"]).pack(pady=(25,5))
  ctk.CTkLabel(win,text=f"Nieuwe versie: {nieuwste}",font=("Segoe UI",12),text_color=t["muted"]).pack(pady=(0,12))
  progress=ctk.CTkProgressBar(win,width=440,progress_color=t["accent"],fg_color=t["button_fg"]); progress.set(0); progress.pack(pady=8)
  percent=ctk.CTkLabel(win,text="0%",font=("Segoe UI",11,"bold"),text_color=t["text"]); percent.pack(pady=3)
  speed_label=ctk.CTkLabel(win,text="0 KB/s",font=("Segoe UI",11),text_color=t["muted"]); speed_label.pack(pady=3)
  status=ctk.CTkLabel(win,text="Changelog ophalen...",font=("Segoe UI",11),text_color=t["text"]); status.pack(pady=5)

  def worker():
   temporary=None
   try:
    try:
     req=urllib.request.Request(GITHUB_CHANGELOG_URL,headers={"User-Agent":"HuiswerkPlanner/7.0"})
     with urllib.request.urlopen(req,timeout=10) as r: ch=r.read().decode("utf-8")
     with open(LOG_BESTAND,"w",encoding="utf-8") as f: f.write(ch)
    except Exception: pass

    status.configure(text="Nieuwe versie downloaden..."); win.update_idletasks()
    req=urllib.request.Request(GITHUB_SCRIPT_URL,headers={"User-Agent":"HuiswerkPlanner/7.0"})
    start_time=time.time(); total=0; chunks=[]
    with urllib.request.urlopen(req,timeout=30) as r:
     expected=int(r.headers.get("Content-Length") or 0)
     while True:
      chunk=r.read(8192)
      if not chunk: break
      chunks.append(chunk); total+=len(chunk)
      elapsed=max(time.time()-start_time,.001); speed=total/elapsed
      speed_label.configure(text=f"{speed/(1024*1024):.2f} MB/s" if speed>=1024*1024 else f"{speed/1024:.0f} KB/s")
      frac=min(total/expected,1) if expected else min(progress.get()+.02,.95)
      progress.set(frac); percent.configure(text=f"{int(frac*100)}%"); win.update_idletasks()

    script=b"".join(chunks).decode("utf-8")
    current=os.path.abspath(sys.argv[0]); temporary=current+".update"
    with open(temporary,"w",encoding="utf-8") as f: f.write(script)
    compile(script,temporary,"exec"); os.replace(temporary,current)
    progress.set(1); percent.configure(text="100%"); status.configure(text="Update geïnstalleerd. App wordt herstart..."); win.update_idletasks(); time.sleep(1)
    win.destroy(); self.destroy(); subprocess.Popen([sys.executable,current]); sys.exit()
   except Exception as e:
    if temporary and os.path.exists(temporary):
     try: os.remove(temporary)
     except OSError: pass
    try: win.destroy()
    except Exception: pass
    messagebox.showerror("Update mislukt",f"De update kon niet worden geïnstalleerd:\n{e}")
  self.after(100,worker)

 def show_update_log(self):
  if not os.path.exists(LOG_BESTAND): return
  try:
   with open(LOG_BESTAND,"r",encoding="utf-8") as f: ch=f.read().strip()
   if not ch: return
   os.remove(LOG_BESTAND)
  except Exception: return
  t=THEMES[self.theme_name]
  win=ctk.CTkToplevel(self); win.title("Wat is er veranderd?"); win.geometry("680x520"); win.configure(fg_color=t["bg_card"])
  ctk.CTkLabel(win,text="🎉 Update voltooid!",font=("Segoe UI",24,"bold"),text_color=t["text"]).pack(pady=(25,4))
  ctk.CTkLabel(win,text="Dit is er veranderd in de nieuwe versie:",font=("Segoe UI",12),text_color=t["muted"]).pack(pady=(0,15))
  box=ctk.CTkTextbox(win,font=("Segoe UI",12),fg_color=t["bg_main"],text_color=t["text"],corner_radius=10); box.pack(fill="both",expand=True,padx=25,pady=(0,15)); box.insert("1.0",ch); box.configure(state="disabled")
  ctk.CTkButton(win,text="✓ Begrepen",height=40,fg_color=t["accent"],text_color="white",command=win.destroy).pack(fill="x",padx=25,pady=(0,20))


if __name__ == "__main__":
 StartupIntro().mainloop()
