# -*- coding: utf-8 -*-
import os
import json
import webbrowser
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle
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
Window.clearcolor = (0.1, 0.04, 0.18, 1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
DATA_FILE = os.path.join(BASE_DIR, "zekr_data.json")
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
BANNER_FILE = os.path.join(BASE_DIR, "main_banner.png")

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
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

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

# --------------------------
# آیکون‌های سفارشی (Canvas)
# --------------------------
class IconBase(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(36), dp(36))

class StarIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.95, 0.75, 0.15, 1)
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        lbl = Label(text="★", font_size="22sp", color=(0.15, 0.1, 0.05, 1),
                    bold=True, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(lbl)

    def _upd(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size

class CoinIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.9, 0.7, 0.15, 1)
            self.circle = Ellipse(pos=self.pos, size=self.size)
            Color(0.6, 0.45, 0.05, 1)
            self.ring = Line(circle=(self.center_x, self.center_y, dp(14)), width=1.5)
        self.bind(pos=self._upd, size=self._upd)
        lbl = Label(text="$", font_size="20sp", color=(0.4, 0.3, 0.05, 1),
                    bold=True, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(lbl)

    def _upd(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size
        self.ring.circle = (self.center_x, self.center_y, dp(14))

class LockIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.25, 0.55, 0.95, 1)
            self.shackle = Ellipse(pos=(self.x+8, self.y+18), size=(20, 18))
            self.body = RoundedRectangle(pos=(self.x+4, self.y+4), size=(28, 22), radius=[dp(4)])
            Color(0.1, 0.15, 0.3, 1)
            self.hole = Ellipse(pos=(self.x+14, self.y+12), size=(8, 8))
        self.bind(pos=self._upd)

    def _upd(self, *args):
        self.shackle.pos = (self.x+8, self.y+18)
        self.shackle.size = (20, 18)
        self.body.pos = (self.x+4, self.y+4)
        self.body.size = (28, 22)
        self.hole.pos = (self.x+14, self.y+12)

class BirdIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.85, 0.4, 0.65, 1)
            self.body = Ellipse(pos=(self.x+10, self.y+10), size=(16, 14))
            Color(1, 1, 1, 0.9)
            self.wing1 = Line(points=[self.x+4, self.y+22, self.x+14, self.y+32, self.x+26, self.y+22], width=2.5)
            self.wing2 = Line(points=[self.x+8, self.y+16, self.x+16, self.y+26, self.x+28, self.y+16], width=2)
        self.bind(pos=self._upd)

    def _upd(self, *args):
        self.body.pos = (self.x+10, self.y+10)
        self.wing1.points = [self.x+4, self.y+22, self.x+14, self.y+32, self.x+26, self.y+22]
        self.wing2.points = [self.x+8, self.y+16, self.x+16, self.y+26, self.x+28, self.y+16]

ZEKR_FOLDERS = [
    ("صلوات", StarIcon, ["اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "اَللّهُمَّ صَلِّ عَلی مُحَمَّد", "صَلَّی اللهُ عَلَیهِ وَ آلِهِ"]),
    ("رزق و روزی", CoinIcon, ["یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله"]),
    ("گشایش مشکلات", LockIcon, ["یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات"]),
    ("آرامش قلب", BirdIcon, ["یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"]),
]

# --------------------------
# ویجت‌های سفارشی
# --------------------------
class GlassCard(BoxLayout):
    def __init__(self, radius=20, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(1, 1, 1, 0.06)
            self.bg = RoundedRectangle(radius=[radius])
            Color(1, 1, 1, 0.1)
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
        if FONT_NAME:
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
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        if FONT_NAME:
            self.font_name = FONT_NAME
        self.text = fa(text)

# --------------------------
# کلاس اصلی اپلیکیشن Kivy جهت بالا آمدن امن لایوت شما
# --------------------------
class TasbihNoorApp(App):
    def build(self):
        # ساخت لایوت اصلی برای بالا آمدن ویجت‌ها
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        if os.path.exists(BANNER_FILE):
            main_layout.add_widget(Image(source=BANNER_FILE, size_hint_y=0.3))
        else:
            main_layout.add_widget(FLabel(text="تسبیح نور", font_size="24sp", size_hint_y=0.1))
            
        card = GlassCard()
        card.add_widget(FLabel(text="برنامه با موفقیت اجرا شد", font_size="18sp"))
        
        btn = StyledBtn(text="ذکر روز", bg=(0.2, 0.6, 0.2, 1))
        card.add_widget(btn)
        
        main_layout.add_widget(card)
        return main_layout

if __name__ == "__main__":
    TasbihNoorApp().run()
