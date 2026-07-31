# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0, 0, 0, 1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except:
        FONT_NAME = None
else:
    FONT_NAME = None

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except:
    HAS_ARABIC = False

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def fa(text):
    if text is None:
        return ""
    txt = str(text)
    if HAS_ARABIC and FONT_NAME:
        try:
            return get_display(arabic_reshaper.reshape(txt))
        except:
            return txt
    return txt

def to_fa_num(s):
    return str(s).translate(FA_DIGITS)

def miladi_to_shamsi(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def get_data_path():
    try:
        app = App.get_running_app()
        if app and app.user_data_dir:
            return os.path.join(app.user_data_dir, "zekr_data.json")
    except:
        pass
    return os.path.join(BASE_DIR, "zekr_data.json")

def load_data():
    path = get_data_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"count": 0, "daily_target": 100}

def save_data(data):
    try:
        path = get_data_path()
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

WEEKLY_ZEKR = {
    5: "یا رَبَّ الْعالَمین",
    6: "یا ذاالْجَلالِ وَ الْاِکْرام",
    0: "یا قاضِیَ الْحاجات",
    1: "یا اَرْحَمَ الرّاحِمین",
    2: "یا حَیُّ یا قَیّوُم",
    3: "لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمُبین",
    4: "اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد",
}

WEEKDAY_NAMES = {
    0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
    3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه",
}

ZEKR_FOLDERS = {
    "رزق و روزی": ["یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله"],
    "گشایش مشکلات": ["یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات"],
    "آرامش قلب": ["یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"],
}

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(14)
        self.spacing = dp(6)
        self.size_hint_y = None
        with self.canvas.before:
            Color(0.06, 0.06, 0.1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FaLabel(Label):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.halign = 'center'
        self.valign = 'middle'

    def set_fa(self, text):
        self.text = fa(text)

class StyledBtn(Button):
    def __init__(self, text="", bg_color=(0.15, 0.45, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.background_normal = ''
        self.background_color = bg_color
        self.bold = True
        self.font_size = '15sp'
        self.size_hint_y = None
        self.height = dp(46)
        self.color = (1, 1, 1, 1)

class ZekrApp(App):
    def build(self):
        self.data = load_data()
        root = BoxLayout(orientation='vertical', padding=[dp(16), dp(6), dp(16), dp(16)], spacing=dp(10))

        header = Card(orientation='vertical', height=dp(100))
        self.lbl_time = FaLabel(text="۰۰:۰۰:۰۰", font_size='34sp', color=(1, 0.85, 0.25, 1), bold=True, size_hint_y=None, height=dp(44))
        header.add_widget(self.lbl_time)

        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
        self.lbl_date = FaLabel(text="", font_size='13sp', color=(0.7, 0.75, 0.9, 1), halign='right')
        self.lbl_week = FaLabel(text="", font_size='13sp', color=(0.85, 0.7, 0.95, 1), halign='left')
        row.add_widget(self.lbl_week)
        row.add_widget(self.lbl_date)
        header.add_widget(row)
        root.add_widget(header)

        counter_card = Card(orientation='vertical', height=dp(130))
        self.lbl_count = FaLabel(text="۰", font_size='72sp', color=(0.3, 0.75, 1, 1), bold=True, size_hint_y=None, height=dp(82))
        counter_card.add_widget(self.lbl_count)
        self.lbl_target = FaLabel(text="هدف: ۱۰۰", font_size='12sp', color=(0.6, 0.65, 0.8, 1), size_hint_y=None, height=dp(20))
        counter_card.add_widget(self.lbl_target)
        root.add_widget(counter_card)

        prog_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(24), spacing=dp(4))
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        prog_box.add_widget(self.progress)
        root.add_widget(prog_box)

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(102))
        btn_add = StyledBtn("+ ذکر", bg_color=(0.1, 0.5, 0.95, 
