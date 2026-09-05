# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import arabic_reshaper

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar

# --------------------------
# تنظیمات پایه و گرافیکی
# --------------------------
Window.clearcolor = (0.1, 0.04, 0.18, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
BANNER_FILE = os.path.join(BASE_DIR, "main_banner.png")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except: FONT_NAME = None
else: FONT_NAME = None

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def fa(t):
    if not t: return ""
    try: return arabic_reshaper.reshape(str(t))[::-1]
    except: return str(t)

def to_fa_num(s): return str(s).translate(FA_DIGITS)

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

WEEKLY_ZEKR = {
    5: "یا رَبَّ الْعالَمین", 6: "یا ذاالْجَلالِ وَ الْاِکْرام", 0: "یا قاضِیَ الْحاجات",
    1: "یا اَرْحَمَ الرّاحِمین", 2: "یا حَیُّ یا قَیّوُم",
    3: "لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمُبین", 4: "اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد"
}

# --------------------------
# کلاس بازسازی شده آیکون‌های گرافیکی اورجینال شما (کاملاً پایدار)
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
        self.add_widget(Label(text="*", font_size="22sp", color=(0.15, 0.1, 0.05, 1), bold=True, pos_hint={'center_x': 0.5, 'center_y': 0.5}))
    def _upd(self, *args): self.circle.pos, self.circle.size = self.pos, self.size

class CoinIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.9, 0.7, 0.15, 1)
            self.circle = Ellipse(pos=self.pos, size=self.size)
            Color(0.6, 0.45, 0.05, 1)
            self.ring = Line(circle=(self.center_x, self.center_y, dp(14)), width=1.5)
        self.bind(pos=self._upd, size=self._upd)
        self.add_widget(Label(text="$", font_size="20sp", color=(0.4, 0.3, 0.05, 1), bold=True, pos_hint={'center_x': 0.5, 'center_y': 0.5}))
    def _upd(self, *args):
        self.circle.pos, self.circle.size = self.pos, self.size
        self.ring.circle = (self.center_x, self.center_y, dp(14))

class LockIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.25, 0.55, 0.95, 1)
            self.shackle = Ellipse(pos=(self.x+8, self.y+18), size=(20, 18))
            self.body = RoundedRectangle(pos=(self.x+4, self.y+4), size=(28, 22), radius=[dp(4)])
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *args):
        self.shackle.pos, self.shackle.size = (self.x+8, self.y+18), (20, 18)
        self.body.pos, self.body.size = (self.x+4, self.y+4), (28, 22)

class BirdIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.85, 0.4, 0.65, 1)
            self.body = Ellipse(pos=(self.x+10, self.y+10), size=(16, 14))
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *args): self.body.pos, self.body.size = (self.x+10, self.y+10), (16, 14)

ZEKR_FOLDERS = [
    ("صلوات", StarIcon, ["اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "اَللّهُمَّ صَلِّ عَلی مُحَمَّد", "صَلَّی اللهُ عَلَیهِ وَ آلِهِ"]),
    ("رزق و روزی", CoinIcon, ["یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله"]),
    ("گشایش مشکلات", LockIcon, ["یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات"]),
    ("آرامش قلب", BirdIcon, ["یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"])
]
class GlassCard(BoxLayout):
    def __init__(self, radius=20, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.padding, self.spacing = dp(15), dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(1, 1, 1, 0.06)
            self.bg = RoundedRectangle(radius=[radius])
            Color(1, 1, 1, 0.1)
            self.border = Line(rounded_rectangle=(0, 0, 100, 100, radius), width=1.2)
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a):
        self.bg.pos, self.bg.size = self.pos, self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

class StyledBtn(Button):
    def __init__(self, text="", bg=(0.15, 0.35, 0.85, 1), **kw):
        super().__init__(**kw)
        self.text = text
        if FONT_NAME: self.font_name = FONT_NAME
        self.background_normal, self.background_color = "", (0, 0, 0, 0)
        self.bold, self.font_size, self.size_hint_y, self.height = True, "16sp", None, dp(48)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[dp(16)])
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a): self.rect.pos, self.rect.size = self.pos, self.size

class FLabel(Label):
    def __init__(self, text="", **kw):
        super().__init__(**kw)
        if FONT_NAME: self.font_name = FONT_NAME
        self.text = text
        self.halign = 'center'
        self.valign = 'middle'

class TasbihNoorApp(App):
    def build(self):
        self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
        self.data = self.load_data()
        
        root_scroll = ScrollView(size_hint=(1, 1))
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12), size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))
        
        if os.path.exists(BANNER_FILE):
            self.main_layout.add_widget(Image(source=BANNER_FILE, size_hint_y=None, height=dp(140)))
        else:
            self.title_lbl = FLabel(text="Tasbih Noor", font_size="26sp", bold=True, size_hint_y=None, height=dp(50))
            self.main_layout.add_widget(self.title_lbl)
            
        self.time_card = GlassCard()
        self.lbl_datetime = FLabel(text="Loading...", font_size="16sp")
        self.time_card.add_widget(self.lbl_datetime)
        self.main_layout.add_widget(self.time_card)
        
        self.weekday_card = GlassCard()
        self.lbl_week_title = FLabel(text="Zekr", font_size="14sp", color=(0.7, 0.7, 0.9, 1))
        self.lbl_week_val = FLabel(text="...", font_size="20sp", bold=True, color=(1, 0.85, 0.3, 1))
        self.weekday_card.add_widget(self.lbl_week_title)
        self.weekday_card.add_widget(self.lbl_week_val)
        self.main_layout.add_widget(self.weekday_card)

        self.counter_card = GlassCard()
        self.lbl_count = FLabel(text="Count: 0", font_size="24sp", bold=True)
        self.counter_card.add_widget(self.lbl_count)
        
        self.progress = ProgressBar(max=self.data['daily_target'], value=min(self.data['count'], self.data['daily_target']), size_hint_y=None, height=dp(15))
        self.counter_card.add_widget(self.progress)
        
        self.lbl_target = FLabel(text="Target: 100", font_size="14sp", color=(0.6, 0.8, 0.6, 1))
        self.counter_card.add_widget(self.lbl_target)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        self.btn_reset = StyledBtn(text="Reset", bg=(0.65, 0.2, 0.2, 1))
        self.btn_reset.bind(on_release=self.reset_count)
        self.btn_count = StyledBtn(text="Count", bg=(0.15, 0.55, 0.25, 1))
        self.btn_count.bind(on_release=self.increment_count)
        
        btn_layout.add_widget(self.btn_reset)
        btn_layout.add_widget(self.btn_count)
        self.counter_card.add_widget(btn_layout)
        self.main_layout.add_widget(self.counter_card)

        self.folders_card = GlassCard()
        self.lbl_bank_title = FLabel(text="Bank", font_size="16sp", bold=True, color=(0.9, 0.6, 0.9, 1))
        self.folders_card.add_widget(self.lbl_bank_title)
        
        grid_folders = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid_folders.bind(minimum_height=grid_folders.setter('height'))
        
        self.folder_buttons = []
        for name, IconClass, zekrs in ZEKR_FOLDERS:
            box_item = BoxLayout(orientation='horizontal', padding=dp(5), spacing=dp(8))
            box_item.add_widget(IconClass())
            btn_folder = StyledBtn(text="Folder", bg=(0.2, 0.2, 0.35, 1))
            btn_folder.bind(on_release=lambda x, z=zekrs, n=name: self.show_zekr_list(n, z))
            box_item.add_widget(btn_folder)
            grid_folders.add_widget(box_item)
            self.folder_buttons.append((btn_folder, name))
            
        self.folders_card.add_widget(grid_folders)
        self.main_layout.add_widget(self.folders_card)

        root_scroll.add_widget(self.main_layout)
        Clock.schedule_once(self.secure_persian_injection, 0.5)
        return root_scroll

    def secure_persian_injection(self, dt):
        try:
            if hasattr(self, 'title_lbl') and self.title_lbl is not None:
                self.title_lbl.text = fa("تسبیح نور")
            self.lbl_week_title.text = fa("ذکر امروز هفته:")
            current_day = datetime.now().weekday()
            self.lbl_week_val.text = fa(WEEKLY_ZEKR.get(current_day, "ذکر روز یافت نشد"))
            self.lbl_count.text = fa(f"تعداد ذکر: {to_fa_num(self.data['count'])}")
            self.lbl_target.text = fa(f"هدف روزانه: {to_fa_num(self.data['daily_target'])}")
            self.btn_reset.text = fa("🔄 ریست")
            self.btn_count.text = fa("＋ شمارش ذکر")
            self.lbl_bank_title.text = fa("بانک اذکار تفکیک شده")
            for btn, name in self.folder_buttons: btn.text = fa(name)
        except: pass
        Clock.schedule_interval(self.update_clock, 1)
        self.update_clock(0)

    def update_clock(self, dt):
        try:
            now = datetime.now()
            jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            j_month_name = months[jm - 1]
            time_str = now.strftime("%H:%M:%S")
            date_str = f"{to_fa_num(jd)} {j_month_name} {to_fa_num(jy)}"
            self.lbl_datetime.text = fa(f"ساعت {time_str}  |  {date_str}")
        except: pass

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {"count": 0, "daily_target": 100, "paid": False, "custom_zekrs": []}

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def increment_count(self, instance):
        self.data['count'] += 1
        self.lbl_count.text = fa(f"تعداد ذکر: {to_fa_num(self.data['count'])}")
        self.progress.value = min(self.data['count'], self.data['daily_target'])
        self.save_data()

    def reset_count(self, instance):
        self.data['count'] = 0
        self.lbl_count.text = fa(f"تعداد ذکر: {to_fa_num(self.data['count'])}")
        self.progress.value = 0
        self.save_data()

    def show_zekr_list(self, title, zekrs):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        popup = Popup(title=fa(title), size_hint=(0.9, 0.8))
        
        for z in zekrs:
            btn_zekr = StyledBtn(text=fa(z), bg=(0.25, 0.25, 0.45, 1))
            btn_zekr.bind(on_release=lambda x, sz=z: self.select_zekr_from_bank(sz, popup))
            list_layout.add_widget(btn_zekr)
            
        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        btn_close = StyledBtn(text=fa("بستن"), bg=(0.5, 0.5, 0.5, 1))
        btn_close.bind(on_release=popup.dismiss)
        content.add_widget(btn_close)
        popup.content = content
        popup.open()

    def select_zekr_from_bank(self, zekr_text, popup):
        popup.dismiss()
        self.reset_count(None)
        info_popup = Popup(title=fa("ذکر انتخاب شد"), size_hint=(0.8, 0.3))
        info_popup.content = FLabel(text=fa(zekr_text), font_size="16sp")
        info_popup.open()

if __name__ == "__main__":
    TasbihNoorApp().run()
