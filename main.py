# -*- coding: utf-8 -*-
import traceback
import sys
import os

def log_exception(exc_type, exc_value, exc_tb):
    log_dir = '/storage/emulated/0/Android/data/com.tasbihnoor.app/files'
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'tasbih_error.log')
    with open(log_path, 'w') as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)

sys.excepthook = log_exception
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

# --------------------------
# آیکون‌های سفارشی (Canvas)
# --------------------------
class IconBase(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(36), dp(36))

class StarIcon(IconBase):
    """ستاره زرد"""
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
    """سکه طلایی"""
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
    """قفل آبی"""
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
    """پرنده صورتی"""
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
        halign = kwargs.pop('halign', 'center')
        valign = kwargs.pop('valign', 'middle')
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.font_size = size
        self.color = clr
        self.bold = bold
        self.halign = halign
        self.valign = valign
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

        with root.canvas.before:
            Color(0.1, 0.04, 0.18, 1)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)

        if os.path.exists(BANNER_FILE):
            banner = Image(source=BANNER_FILE, allow_stretch=True, keep_ratio=False,
                          color=(1, 1, 1, 0.8))
            banner.pos_hint = {'x': 0, 'y': 0}
            banner.size_hint = (1, 1)
            root.add_widget(banner)

        scroll = ScrollView(do_scroll_x=False)
        lay = BoxLayout(orientation="vertical", spacing=dp(10),
                       padding=[dp(16), dp(40), dp(16), dp(20)], size_hint_y=None)
        lay.bind(minimum_height=lay.setter("height"))

        # ==== هدر: ساعت/تاریخ چپ، ذکر روز راست ====
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))

        # چپ: ساعت + تاریخ
        left_box = BoxLayout(orientation="vertical", size_hint_x=0.5)
        self.lbl_time = FLabel(text="00:00:00", size="20sp", clr=(1, 0.83, 0.31, 1), bold=True, halign="left")
        self.lbl_date = FLabel(text="", size="13sp", clr=(0.85, 0.85, 0.85, 0.8), halign="left")
        left_box.add_widget(self.lbl_time)
        left_box.add_widget(self.lbl_date)
        header.add_widget(left_box)

        # راست: ذکر روز
        right_box = BoxLayout(orientation="vertical", size_hint_x=0.5)
        lbl_zekr_title = FLabel(text="ذکر امروز", size="10sp", clr=(1, 0.83, 0.31, 0.8), halign="right")
        self.lbl_week = FLabel(text="", size="14sp", clr=(1, 0.83, 0.31, 1), bold=True, halign="right")
        right_box.add_widget(lbl_zekr_title)
        right_box.add_widget(self.lbl_week)
        header.add_widget(right_box)

        lay.add_widget(header)

        # ==== فاصله ۵۰dp ====
        lay.add_widget(Label(text="", size_hint_y=None, height=dp(50)))

        # ==== ذکر انتخاب شده ====
        self.lbl_active = FLabel(text="ذکر خود را انتخاب کنید", size="22sp", clr=(0.29, 0.87, 0.50, 1), bold=True)
        lay.add_widget(self.lbl_active)

        # ==== فاصله ۲۰dp ====
        lay.add_widget(Label(text="", size_hint_y=None, height=dp(20)))

        # ==== کارت شمارنده ====
        card = GlassCard(radius=20)
        self.lbl_count = FLabel(text="۰", size="72sp", clr=(1, 1, 1, 1), bold=True)
        self.prog = ProgressBar(max=100, size_hint_y=None, height=dp(6))
        self.lbl_info = FLabel(text="هدف: ۱۰۰", size="12sp", clr=(0.7, 0.8, 1, 0.6))

        card.add_widget(self.lbl_count)
        card.add_widget(self.prog)
        card.add_widget(self.lbl_info)

        g1 = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(50))
        b1 = StyledBtn(text="+۱", bg=(0.66, 0.33, 0.97, 0.85))
        b1.bind(on_press=self.add_one)
        b2 = StyledBtn(text="-۱", bg=(0.39, 0.31, 0.47, 0.7))
        b2.bind(on_press=self.sub_one)
        g1.add_widget(b1)
        g1.add_widget(b2)
        card.add_widget(g1)

        g2 = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(50))
        b3 = StyledBtn(text="ریست", bg=(0.86, 0.15, 0.15, 0.85))
        b3.bind(on_press=self.reset)
        b4 = StyledBtn(text="هدف", bg=(0.13, 0.64, 0.29, 0.85))
        b4.bind(on_press=self.set_target)
        g2.add_widget(b3)
        g2.add_widget(b4)
        card.add_widget(g2)

        lay.add_widget(card)

        # ==== فاصله ۱۵dp ====
        lay.add_widget(Label(text="", size_hint_y=None, height=dp(15)))

        # ==== دکمه بانک اذکار ====
        bb = StyledBtn(text="بانک اذکار مشکل‌گشا", bg=(0.49, 0.22, 0.93, 0.9))
        bb.height = dp(56)
        bb.bind(on_press=self.open_bank)
        lay.add_widget(bb)

        # ==== بنر حمایت ====
        support_card = GlassCard(radius=14)
        support_card.padding = dp(12)
        support_card.spacing = dp(6)
        lbl_support = FLabel(text="لطفاً از ما حمایت کنید", size="13sp", clr=(1, 1, 1, 1))
        btn_support = StyledBtn(text="امتیاز دادن / عضویت در کانال", bg=(0.2, 0.15, 0.3, 0.6))
        btn_support.bind(on_press=self.open_support)
        support_card.add_widget(lbl_support)
        support_card.add_widget(btn_support)
        lay.add_widget(support_card)

        scroll.add_widget(lay)
        root.add_widget(scroll)

        Clock.schedule_interval(self.tick, 1)
        self.refresh()
        return root

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

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

    def open_support(self, *a):
        try:
            webbrowser.open("https://ble.ir/zekarnoor")
        except:
            pass

    # --------------------------
    # بانک اذکار
    # --------------------------
    def open_bank(self, *a):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))

        # عنوان
        title_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
        title_icon = StarIcon()
        title_text = FLabel(text="بانک اذکار", size="20sp", clr=(1, 0.83, 0.31, 1), bold=True, halign="right")
        title_box.add_widget(title_icon)
        title_box.add_widget(title_text)
        box.add_widget(title_box)

        sc = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        inner.bind(minimum_height=inner.setter("height"))

        folder_buttons = []
        for name, icon_cls, zekrs in ZEKR_FOLDERS:
            card = self._create_folder_card(name, icon_cls)
            folder_buttons.append((card, name, zekrs))
            inner.add_widget(card)

        custom = self.data.get("custom_zekrs", [])
        custom_buttons = []
        if custom:
            inner.add_widget(FLabel(text="──── ذکرهای شما ────", size="14sp", clr=(0.6, 0.7, 0.9, 0.7)))
            for z in custom:
                btn = StyledBtn(text=z, bg=(0.15, 0.3, 0.25, 0.9))
                custom_buttons.append((btn, z))
                inner.add_widget(btn)

        sc.add_widget(inner)
        box.add_widget(sc)

        cls = StyledBtn(text="بستن", bg=(0.35, 0.3, 0.4, 0.9))
        pop = Popup(title="", content=box, size_hint=(0.92, 0.78), separator_height=0)
        cls.bind(on_press=pop.dismiss)
        box.add_widget(cls)

        # ==== کلیک روی پوشه → نمایش اذکار داخلش ====
        for card, name, zekrs in folder_buttons:
            card.trigger.bind(on_press=lambda x, n=name, z=zekrs, p=pop: self.show_zekrs(n, z, p))
        for btn, z in custom_buttons:
            btn.bind(on_press=lambda x, zz=z, p=pop: self.pick_zekr(zz, p))

        pop.open()

    def _create_folder_card(self, name, icon_cls):
        root = FloatLayout(size_hint_y=None, height=dp(56))

        bg = BoxLayout(orientation="horizontal", padding=[dp(14), dp(8)], spacing=dp(10),
                       pos_hint={"x": 0, "y": 0}, size_hint=(1, 1))
        with bg.canvas.before:
            Color(0.15, 0.10, 0.25, 0.95)
            bg.rect = RoundedRectangle(radius=[18])
            Color(1, 1, 1, 0.06)
            bg.line = Line(rounded_rectangle=(0, 0, 100, 100, 18), width=1)

        def upd_bg(*a):
            bg.rect.pos = bg.pos
            bg.rect.size = bg.size
            bg.line.rounded_rectangle = (bg.x, bg.y, bg.width, bg.height, 18)
        bg.bind(pos=upd_bg, size=upd_bg)

        # آیکون رنگی
        icon = icon_cls()
        name_lbl = FLabel(text=name, size="16sp", clr=(0.95, 0.95, 0.95, 1), bold=True, halign="right")
        arrow_lbl = Label(text=">", font_size="24sp", color=(0.7, 0.7, 0.8, 0.6),
                          size_hint_x=None, width=dp(24), halign="center", valign="middle")

        bg.add_widget(icon)
        bg.add_widget(name_lbl)
        bg.add_widget(arrow_lbl)
        root.add_widget(bg)

        # دکمه شفاف روی کل کارت
        btn = Button(background_normal="", background_color=(0, 0, 0, 0),
                     pos_hint={"x": 0, "y": 0}, size_hint=(1, 1))
        root.add_widget(btn)
        root.trigger = btn

        return root

    def show_zekrs(self, folder_name, zekrs, parent_popup):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        sc = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        inner.bind(minimum_height=inner.setter("height"))

        zekr_buttons = []
        for z in zekrs:
            btn = StyledBtn(text=z, bg=(0.1, 0.15, 0.25, 0.9))
            zekr_buttons.append((btn, z))
            inner.add_widget(btn)

        sc.add_widget(inner)
        box.add_widget(sc)
        back = StyledBtn(text="برگشت", bg=(0.35, 0.3, 0.4, 0.9))
        pop = Popup(title=fa(folder_name), content=box, size_hint=(0.88, 0.72))
        back.bind(on_press=pop.dismiss)
        box.add_widget(back)

        # ==== کلیک روی ذکر → نمایش روی صفحه اصلی + بستن همه پنجره‌ها ====
        for btn, z in zekr_buttons:
            btn.bind(on_press=lambda x, zz=z, p=pop, pp=parent_popup: self.pick_zekr(zz, p, pp))

        pop.open()

    def pick_zekr(self, zekr_text, popup=None, parent_popup=None):
        self.lbl_active.set_text(zekr_text)
        self.lbl_active.color = (0.29, 0.95, 0.6, 1)
        if popup:
            popup.dismiss()
        if parent_popup:
            parent_popup.dismiss()

if __name__ == "__main__":
    TasbihApp().run()
