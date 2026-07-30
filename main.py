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

# --------------------------
# تنظیمات پایه
# --------------------------
Window.clearcolor = (0.03, 0.03, 0.08, 1)

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

def get_data_path():
    try:
        app = App.get_running_app()
        if app:
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
        os.makedirs(os.path.dirname(path), exist_ok=True)
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

ZEKR_FOLDERS = {
    "رزق و روزی": ["یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله"],
    "گشایش مشکلات": ["یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات"],
    "آرامش قلب": ["یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"],
}

# --------------------------
# کامپوننت‌ها
# --------------------------

class FaLabel(Label):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(size=self._update)
    
    def _update(self, *args):
        self.text_size = (self.width, None)
    
    def set_fa(self, text):
        self.text = fa(text)

class Card(BoxLayout):
    """کارت با گوشه‌های گرد"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(12)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        with self.canvas.before:
            Color(0.12, 0.15, 0.25, 0.92)
            self.bg = RoundedRectangle(radius=[dp(20)])
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class StyledBtn(Button):
    def __init__(self, text="", bg_color=(0.15, 0.45, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.background_normal = ''
        self.background_color = bg_color
        self.bold = True
        self.font_size = '16sp'
        self.size_hint_y = None
        self.height = dp(50)
        self.color = (1, 1, 1, 1)

# --------------------------
# اپلیکیشن اصلی
# --------------------------

class ZekrApp(App):
    def build(self):
        self.data = load_data()
        
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
        
        # === هدر ===
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(4))
        
        self.lbl_time = FaLabel(
            text="00:00:00", 
            font_size='44sp', 
            color=(1, 0.9, 0.4, 1), 
            bold=True
        )
        header.add_widget(self.lbl_time)
        
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
        self.lbl_date = FaLabel(
            text="", 
            font_size='13sp', 
            color=(0.7, 0.75, 0.9, 1), 
            halign='left'
        )
        self.lbl_week = FaLabel(
            text="", 
            font_size='14sp', 
            color=(0.9, 0.75, 0.95, 1), 
            halign='right'
        )
        row.add_widget(self.lbl_date)
        row.add_widget(self.lbl_week)
        header.add_widget(row)
        
        root.add_widget(header)
        
        # === کارت شمارنده ===
        card = Card()
        
        self.lbl_count = FaLabel(
            text="۰", 
            font_size='80sp', 
            color=(0.35, 0.75, 1, 1), 
            bold=True
        )
        card.add_widget(self.lbl_count)
        
        # نوار پیشرفت استاندارد
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(10))
        card.add_widget(self.progress)
        
        self.lbl_target = FaLabel(
            text="هدف: ۱۰۰", 
            font_size='13sp', 
            color=(0.7, 0.75, 0.85, 1)
        )
        card.add_widget(self.lbl_target)
        
        # دکمه‌ها
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(110))
        
        btn_add = StyledBtn("+ ذکر", bg_color=(0.1, 0.5, 0.95, 1))
        btn_add.bind(on_press=self.add_zekr)
        
        btn_sub = StyledBtn("- کم کردن", bg_color=(0.35, 0.35, 0.45, 1))
        btn_sub.bind(on_press=self.remove_zekr)
        
        btn_reset = StyledBtn("ریست", bg_color=(0.75, 0.25, 0.35, 1))
        btn_reset.bind(on_press=self.reset_counter)
        
        btn_target = StyledBtn("تنظیم هدف", bg_color=(0.15, 0.55, 0.4, 1))
        btn_target.bind(on_press=self.set_target_popup)
        
        grid.add_widget(btn_add)
        grid.add_widget(btn_sub)
        grid.add_widget(btn_reset)
        grid.add_widget(btn_target)
        card.add_widget(grid)
        
        root.add_widget(card)
        
        # === دکمه بانک اذکار ===
        btn_list = StyledBtn(
            "🕌 بانک اذکار مشکل‌گشا", 
            bg_color=(0.5, 0.2, 0.7, 1), 
            font_size='18sp'
        )
        btn_list.bind(on_press=self.open_zekr_list)
        root.add_widget(btn_list)
        
        # آپدیت زمان
        Clock.schedule_interval(self.update_time, 1)
        self.update_ui()
        
        return root
    
    def update_time(self, *args):
        now = datetime.now()
        self.lbl_time.set_fa(to_fa_num(now.strftime("%H:%M:%S")))
        self.lbl_date.set_fa(to_fa_num(now.strftime("%Y/%m/%d")))
        self.lbl_week.set_fa(WEEKLY_ZEKR.get(now.weekday(), "ذکر روز"))
    
    def update_ui(self):
        c = self.data.get("count", 0)
        t = self.data.get("daily_target", 100)
        self.lbl_count.set_fa(to_fa_num(c))
        self.lbl_target.set_fa(f"هدف: {to_fa_num(t)}")
        self.progress.max = t
        self.progress.value = min(c, t)
    
    def add_zekr(self, *args):
        self.data["count"] = self.data.get("count", 0) + 1
        save_data(self.data)
        self.update_ui()
    
    def remove_zekr(self, *args):
        if self.data.get("count", 0) > 0:
            self.data["count"] -= 1
            save_data(self.data)
            self.update_ui()
    
    def reset_counter(self, *args):
        self.data["count"] = 0
        save_data(self.data)
        self.update_ui()
    
    def set_target_popup(self, *args):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        inp = TextInput(
            text=str(self.data.get("daily_target", 100)),
            multiline=False,
            input_filter='int',
            font_size='20sp',
            halign='center',
            background_color=(0.1, 0.12, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.3, 0.7, 1, 1)
        )
        if FONT_NAME:
            inp.font_name = FONT_NAME
        
        btn_ok = StyledBtn("تایید", bg_color=(0.1, 0.6, 0.4, 1))
        popup = Popup(title=fa("تنظیم هدف"), content=box, size_hint=(0.85, 0.38))
        
        box.add_widget(inp)
        box.add_widget(btn_ok)
        btn_ok.bind(on_press=lambda x: self._set_target(inp.text, popup))
        popup.open()
    
    def _set_target(self, val, popup):
        try:
            self.data["daily_target"] = int(val) if val else 100
        except:
            self.data["daily_target"] = 100
        save_data(self.data)
        self.update_ui()
        popup.dismiss()
    
    def open_zekr_list(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter('height'))
        
        for name in ZEKR_FOLDERS.keys():
            btn = StyledBtn(name, bg_color=(0.2, 0.25, 0.4, 1))
            btn.bind(on_press=lambda x, n=name: self.show_zekrs(n))
            box.add_widget(btn)
        
        scroll.add_widget(box)
        content.add_widget(scroll)
        
        btn_close = StyledBtn("بستن", bg_color=(0.4, 0.2, 0.3, 1))
        popup = Popup(title=fa("بانک اذکار"), content=content, size_hint=(0.9, 0.82))
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()
    
    def show_zekrs(self, name):
        inner = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter('height'))
        
        for zekr in ZEKR_FOLDERS[name]:
            lbl = FaLabel(
                zekr,
                font_size='18sp',
                color=(0.9, 0.85, 0.95, 1),
                size_hint_y=None,
                height=dp(48)
            )
            box.add_widget(lbl)
        
        scroll.add_widget(box)
        inner.add_widget(scroll)
        
        btn_back = StyledBtn("برگشت", bg_color=(0.3, 0.3, 0.45, 1))
        popup = Popup(title=fa(name), content=inner, size_hint=(0.9, 0.82))
        btn_back.bind(on_press=popup.dismiss)
        inner.add_widget(btn_back)
        popup.open()

if __name__ == '__main__':
    ZekrApp().run()
