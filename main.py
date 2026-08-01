# -*- coding: utf-8 -*-
import os
import json
import time
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar

# --------------------------
# تنظیمات پایه
# --------------------------
Window.clearcolor = (0.03, 0.04, 0.08, 1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "zekr_data.json")
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except Exception:
        FONT_NAME = None
else:
    FONT_NAME = None

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def fa(text):
    if text is None:
        return ""
    return get_display(arabic_reshaper.reshape(str(text)))

def to_fa_num(s):
    return str(s).translate(FA_DIGITS)

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = 979 if gy > 1600 else 0
    gy -= 1600 if gy > 1600 else 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    jm = 1 + (days // 31) if days < 186 else 7 + ((days - 186) // 30)
    jd = 1 + (days % 31) if days < 186 else 1 + ((days - 186) % 30)
    return jy, jm, jd

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"count": 0, "daily_target": 100, "paid": False, "custom_zekrs": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --------------------------
# اذکار آماده
# --------------------------
WEEKLY_ZEKR = {
    5: "یا رَبَّ الْعالَمین",
    6: "یا ذاالْجَلالِ وَ الْاِکْرام",
    0: "یا قاضِیَ الْحاجات",
    1: "یا اَرْحَمَ الرّاحِمین",
    2: "یا حَیُّ یا قَیّوُم",
    3: "لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمُبین",
    4: "اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد",
}

ZEKR_FOLDERS = {
    "صلوات": ["اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "اَللّهُمَّ صَلِّ عَلی مُحَمَّد", "صَلَّی اللهُ عَلَیهِ وَ آلِهِ"],
    "رزق و روزی": ["یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله"],
    "گشایش مشکلات": ["یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات"],
    "آرامش قلب": ["یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"],
}

# --------------------------
# ویجت‌های سفارشی
# --------------------------
class Card(BoxLayout):
    def __init__(self, radius=20, bg=(0.1, 0.12, 0.2, 0.95), **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(*bg)
            self.bg = RoundedRectangle(radius=[radius])
            Color(0.3, 0.5, 0.9, 0.3)
            self.border = Line(rounded_rectangle=(0, 0, 100, 100, radius), width=1.2)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

class StyledBtn(Button):
    def __init__(self, text="", bg=(0.15, 0.35, 0.85, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = fa(text)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.font_size = "16sp"
        self.size_hint_y = None
        self.height = dp(48)
        self.bg_color = bg
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[16])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_text(self, t):
        self.text = fa(t)

class FLabel(Label):
    def __init__(self, text="", size="16sp", clr=(1, 1, 1, 1), bold=False, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.font_size = size
        self.color = clr
        self.bold = bold
        self.halign = "center"
        self.valign = "middle"
        self.bind(size=self._upd)
    def _upd(self, *args):
        self.text_size = (self.width, None)
    def set_text(self, t):
        self.text = fa(t)

# --------------------------
# اپلیکیشن اصلی
# --------------------------
class TasbihApp(App):
    def build(self):
        self.data = load_data()
        root = FloatLayout()

        # پس‌زمینه
        bp = os.path.join(BASE_DIR, "main_banner.png")
        if os.path.exists(bp):
            root.add_widget(Image(source=bp, allow_stretch=True, keep_ratio=False, color=(0.5, 0.5, 0.5, 1)))

        scroll = ScrollView(do_scroll_x=False)
        lay = BoxLayout(orientation="vertical", spacing=dp(12), padding=[dp(16), dp(50), dp(16), dp(30)], size_hint_y=None)
        lay.bind(minimum_height=lay.setter("height"))

        # ==== هدر مینیمال ====
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        self.lbl_time = FLabel(text="00:00:00", size="22sp", clr=(1, 0.85, 0.2, 1), bold=True, halign="left")
        self.lbl_date = FLabel(text="", size="13sp", clr=(0.7, 0.7, 0.7, 1), halign="right")
        header.add_widget(self.lbl_time)
        header.add_widget(self.lbl_date)
        lay.add_widget(header)

        # ذکر هفتگی
        self.lbl_week = FLabel(text="", size="15sp", clr=(0.9, 0.75, 0.4, 1), bold=True)
        lay.add_widget(self.lbl_week)

        # ==== ذکر انتخاب شده (بزرگ و زیبا) ====
        self.lbl_active = FLabel(text="ذکر خود را انتخاب کنید", size="26sp", clr=(0.25, 0.9, 0.55, 1), bold=True)
        lay.add_widget(self.lbl_active)

        # ==== کارت شمارنده ====
        card = Card(radius=24, bg=(0.08, 0.1, 0.18, 0.95))
        self.lbl_count = FLabel(text="۰", size="80sp", clr=(1, 1, 1, 1), bold=True)
        self.prog = ProgressBar(max=100, size_hint_y=None, height=dp(10))
        self.lbl_info = FLabel(text="هدف: ۱۰۰", size="13sp", clr=(0.7, 0.8, 1, 0.8))

        card.add_widget(self.lbl_count)
        card.add_widget(self.prog)
        card.add_widget(self.lbl_info)

        # دکمه‌ها
        g1 = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(50))
        b1 = StyledBtn(text="+۱", bg=(0.1, 0.55, 0.95, 0.95))
        b1.bind(on_press=self.add_one)
        b2 = StyledBtn(text="-۱", bg=(0.35, 0.35, 0.4, 0.9))
        b2.bind(on_press=self.sub_one)
        g1.add_widget(b1)
        g1.add_widget(b2)
        card.add_widget(g1)

        g2 = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(50))
        b3 = StyledBtn(text="ریست", bg=(0.7, 0.2, 0.2, 0.85))
        b3.bind(on_press=self.reset)
        b4 = StyledBtn(text="هدف", bg=(0.2, 0.5, 0.35, 0.9))
        b4.bind(on_press=self.set_target)
        g2.add_widget(b3)
        g2.add_widget(b4)
        card.add_widget(g2)

        lay.add_widget(card)

        # ==== دکمه بانک اذکار ====
        bb = StyledBtn(text="📿 بانک اذکار مشکل‌گشا", bg=(0.5, 0.15, 0.7, 0.95))
        bb.bind(on_press=self.open_bank)
        lay.add_widget(bb)

        # ==== دکمه ذکر دلخواه ====
        bc = StyledBtn(text="✍️ افزودن ذکر دلخواه", bg=(0.15, 0.45, 0.5, 0.95))
        bc.bind(on_press=self.add_custom_zekr)
        lay.add_widget(bc)

        scroll.add_widget(lay)
        root.add_widget(scroll)

        Clock.schedule_interval(self.tick, 1)
        self.refresh()
        return root

    # --------------------------
    # توابع کمکی
    # --------------------------
    def tick(self, dt):
        now = datetime.now()
        jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
        self.lbl_time.set_text(to_fa_num(now.strftime("%H:%M:%S")))
        self.lbl_date.set_text(to_fa_num(f"{jy}/{jm:02d}/{jd:02d}"))
        wd = now.weekday()
        self.lbl_week.set_text(WEEKLY_ZEKR.get(wd, "ذکر روز"))

    def refresh(self):
        c = self.data.get("count", 0)
        t = self.data.get("daily_target", 100)
        self.lbl_count.set_text(to_fa_num(c))
        self.lbl_info.set_text(f"هدف: {to_fa_num(t)}")
        self.prog.max = t
        self.prog.value = min(c, t)

    def add_one(self, *a):
        self.data["count"] += 1
        save_data(self.data)
        self.refresh()

    def sub_one(self, *a):
        if self.data["count"] > 0:
            self.data["count"] -= 1
            save_data(self.data)
            self.refresh()

    def reset(self, *a):
        self.data["count"] = 0
        save_data(self.data)
        self.refresh()

    def set_target(self, *a):
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        inp = TextInput(text=str(self.data["daily_target"]), multiline=False, input_filter="int", font_name=FONT_NAME, font_size="18sp")
        btn = StyledBtn(text="تایید", bg=(0.1, 0.6, 0.4, 1))
        pop = Popup(title=fa("تنظیم هدف"), content=box, size_hint=(0.8, 0.35))
        box.add_widget(inp)
        box.add_widget(btn)
        btn.bind(on_press=lambda x: self._save_target(inp.text, pop))
        pop.open()

    def _save_target(self, val, pop):
        self.data["daily_target"] = int(val) if val else 100
        save_data(self.data)
        self.refresh()
        pop.dismiss()

    # --------------------------
    # بانک اذکار
    # --------------------------
    def open_bank(self, *a):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        sc = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        inner.bind(minimum_height=inner.setter("height"))

        for folder, zekrs in ZEKR_FOLDERS.items():
            btn = StyledBtn(text=folder, bg=(0.2, 0.25, 0.35, 0.95))
            btn.bind(on_press=lambda x, n=folder, z=zekrs: self.show_zekrs(n, z))
            inner.add_widget(btn)

        # اذکار دلخواه کاربر
        custom = self.data.get("custom_zekrs", [])
        if custom:
            inner.add_widget(FLabel(text="──── ذکرهای شما ────", size="14sp", clr=(0.6, 0.7, 0.9, 0.7)))
            for z in custom:
                btn = StyledBtn(text=z, bg=(0.15, 0.3, 0.25, 0.9))
                btn.bind(on_press=lambda x, zz=z: self.pick_zekr(zz))
                inner.add_widget(btn)

        sc.add_widget(inner)
        box.add_widget(sc)
        cls = StyledBtn(text="بستن", bg=(0.35, 0.3, 0.4, 0.9))
        pop = Popup(title=fa("بانک اذکار"), content=box, size_hint=(0.9, 0.75))
        cls.bind(on_press=pop.dismiss)
        box.add_widget(cls)
        pop.open()

    def show_zekrs(self, name, zekrs):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        sc = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        inner.bind(minimum_height=inner.setter("height"))

        for z in zekrs:
            btn = StyledBtn(text=z, bg=(0.1, 0.15, 0.25, 0.9))
            btn.bind(on_press=lambda x, zz=z: self.pick_zekr(zz))
            inner.add_widget(btn)

        sc.add_widget(inner)
        box.add_widget(sc)
        back = StyledBtn(text="برگشت", bg=(0.35, 0.3, 0.4, 0.9))
        pop = Popup(title=fa(name), content=box, size_hint=(0.88, 0.72))
        back.bind(on_press=pop.dismiss)
        box.add_widget(back)
        pop.open()

    def pick_zekr(self, zekr_text):
        self.lbl_active.set_text(zekr_text)
        self.lbl_active.color = (0.25, 0.95, 0.6, 1)

    # --------------------------
    # ذکر دلخواه
    # --------------------------
    def add_custom_zekr(self, *a):
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        inp = TextInput(hint_text="ذکر خود را بنویسید...", multiline=False, font_name=FONT_NAME, font_size="18sp")
        btn = StyledBtn(text="افزودن", bg=(0.1, 0.55, 0.5, 1))
        pop = Popup(title=fa("ذکر دلخواه"), content=box, size_hint=(0.85, 0.35))
        box.add_widget(inp)
        box.add_widget(btn)
        btn.bind(on_press=lambda x: self._save_custom(inp.text, pop))
        pop.open()

    def _save_custom(self, text, pop):
        t = text.strip()
        if t:
            if "custom_zekrs" not in self.data:
                self.data["custom_zekrs"] = []
            if t not in self.data["custom_zekrs"]:
                self.data["custom_zekrs"].append(t)
                save_data(self.data)
            self.pick_zekr(t)
        pop.dismiss()

if __name__ == "__main__":
    TasbihApp().run()
