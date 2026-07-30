# -*- coding: utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import os
import json
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget

# --------------------------
# تنظیمات استایل حرفه‌ای
# --------------------------
Window.clearcolor = (0.05, 0.06, 0.1, 1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "zekr_data.json")
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

# فونت: اگه فایل بود ثبت کن، اگه نبود از فونت سیستمی استفاده کن
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
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)

def to_fa_num(s):
    return str(s).translate(FA_DIGITS)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"count": 0, "daily_target": 100, "paid": False}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
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

class GlassCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(20), dp(5), dp(20), dp(20)]
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(0.12, 0.14, 0.22, 0.8)
            self.bg = RoundedRectangle(radius=[25])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class ModernBtn(Button):
    def __init__(self, text="", bg_color=(0.2, 0.4, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = fa(text)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.font_size = "17sp"
        self.size_hint_y = None
        self.height = dp(50)
        self.my_color = bg_color
        with self.canvas.before:
            Color(*self.my_color)
            self.rect = RoundedRectangle(radius=[25])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_fa(self, text):
        self.text = fa(text)

class FaLabel(Label):
    def __init__(self, text="", font_size="16sp", color=(1,1,1,1), bold=False, halign="center", **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.font_size = font_size
        self.color = color
        self.bold = bold
        self.halign = halign
        self.valign = "middle"
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

    def set_fa(self, text):
        self.text = fa(text)

class ZekrApp(App):
    def build(self):
        self.data = load_data()
        root = FloatLayout()

        # پس‌زمینه ساده بدون عکس (صددرصد بدون خطا)
        with root.canvas.before:
            Color(0.05, 0.06, 0.15, 1)
            root.bg_rect = RoundedRectangle(size=root.size, pos=root.pos)
        root.bind(size=lambda obj, val: setattr(root.bg_rect, 'size', val))
        root.bind(pos=lambda obj, val: setattr(root.bg_rect, 'pos', val))

        # محتوای اسکرول‌شونده
        self.scroll = ScrollView(do_scroll_x=False)
        self.main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(20), dp(70), dp(20), dp(40)],
            size_hint_y=None
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter("height"))

        # ساعت
        self.lbl_time = FaLabel(text="00:00:00", font_size="45sp", color=(1, 0.84, 0, 1), bold=True, halign="left")
        self.main_layout.add_widget(self.lbl_time)

        # تاریخ و ذکر
        info_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        self.lbl_date = FaLabel(text="", font_size="14sp", halign="left", color=(0.8, 0.8, 0.8, 1))
        self.lbl_week_zekr = FaLabel(text="", font_size="17sp", halign="right", color=(1, 0.9, 0.6, 1), bold=True)
        info_row.add_widget(self.lbl_date)
        info_row.add_widget(self.lbl_week_zekr)
        self.main_layout.add_widget(info_row)

        # کارت شمارنده
        card = GlassCard()
        self.lbl_count = FaLabel(text="۰", font_size="85sp", bold=True)
        self.progress = ProgressBar(max=100, size_hint_y=None, height=dp(15))
        self.lbl_target_info = FaLabel(text="هدف: ۱۰۰", font_size="14sp")

        card.add_widget(self.lbl_count)
        card.add_widget(self.progress)
        card.add_widget(self.lbl_target_info)

        # دکمه‌ها
        btns_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(55))
        btn_add = ModernBtn(text="+ ذکر", bg_color=(0.1, 0.5, 0.9, 0.9))
        btn_add.bind(on_press=self.add_zekr)
        btn_sub = ModernBtn(text="- کم کردن", bg_color=(0.3, 0.3, 0.35, 0.8))
        btn_sub.bind(on_press=self.remove_zekr)
        btns_grid.add_widget(btn_add)
        btns_grid.add_widget(btn_sub)
        card.add_widget(btns_grid)

        btns_bottom = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(55))
        btn_reset = ModernBtn(text="ریست", bg_color=(0.6, 0.2, 0.2, 0.8))
        btn_reset.bind(on_press=self.reset_counter)
        btn_target = ModernBtn(text="تنظیم هدف", bg_color=(0.2, 0.4, 0.3, 0.8))
        btn_target.bind(on_press=self.set_target_popup)
        btns_bottom.add_widget(btn_reset)
        btns_bottom.add_widget(btn_target)
        card.add_widget(btns_bottom)

        self.main_layout.add_widget(card)

        # بانک اذکار
        btn_list = ModernBtn(text="بانک اذکار مشکل‌گشا", bg_color=(0.4, 0.1, 0.6, 0.9))
        btn_list.bind(on_press=self.open_zekr_list)
        self.main_layout.add_widget(btn_list)

        self.scroll.add_widget(self.main_layout)
        root.add_widget(self.scroll)

        Clock.schedule_interval(self.update_live_data, 1)
        self.update_ui()
        return root

    def update_live_data(self, *args):
        now = datetime.now()
        self.lbl_time.set_fa(to_fa_num(now.strftime("%H:%M:%S")))
        self.lbl_date.set_fa(to_fa_num(now.strftime("%Y/%m/%d")))
        wd = now.weekday()
        self.lbl_week_zekr.set_fa(WEEKLY_ZEKR.get(wd, "ذکر روز"))

    def update_ui(self):
        count = self.data.get("count", 0)
        target = self.data.get("daily_target", 100)
        self.lbl_count.set_fa(to_fa_num(count))
        self.lbl_target_info.set_fa(f"هدف: {to_fa_num(target)}")
        self.progress.max = target
        self.progress.value = min(count, target)

    def add_zekr(self, *args):
        self.data["count"] += 1
        save_data(self.data)
        self.update_ui()

    def remove_zekr(self, *args):
        if self.data["count"] > 0:
            self.data["count"] -= 1
            save_data(self.data)
            self.update_ui()

    def reset_counter(self, *args):
        self.data["count"] = 0
        save_data(self.data)
        self.update_ui()

    def set_target_popup(self, *args):
        box = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(20))
        inp = TextInput(
            text=str(self.data["daily_target"]),
            multiline=False,
            input_filter="int",
            font_name=FONT_NAME if FONT_NAME else "Roboto",
            font_size="20sp"
        )
        btn = ModernBtn(text="تایید", bg_color=(0.1, 0.6, 0.4, 1))
        popup = Popup(title=fa("هدف جدید"), content=box, size_hint=(0.8, 0.4))
        box.add_widget(inp)
        box.add_widget(btn)
        btn.bind(on_press=lambda x: self.confirm_target(inp.text, popup))
        popup.open()

    def confirm_target(self, val, popup):
        self.data["daily_target"] = int(val) if val else 100
        save_data(self.data)
        self.update_ui()
        popup.dismiss()

    def open_zekr_list(self, *args):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        main_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        main_box.bind(minimum_height=main_box.setter("height"))
        for folder_name in ZEKR_FOLDERS.keys():
            btn = ModernBtn(text=folder_name, bg_color=(0.18, 0.22, 0.32, 1))
            btn.bind(on_press=lambda x, n=folder_name: self.show_folder_content(n))
            main_box.add_widget(btn)
        scroll.add_widget(main_box)
        content.add_widget(scroll)
        close = ModernBtn(text="بستن", bg_color=(0.3, 0.25, 0.35, 1))
        popup = Popup(title=fa("بانک اذکار"), content=content, size_hint=(0.9, 0.8))
        close.bind(on_press=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def show_folder_content(self, name):
        inner = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        items_box.bind(minimum_height=items_box.setter("height"))
        for zekr in ZEKR_FOLDERS[name]:
            items_box.add_widget(ModernBtn(text=zekr, bg_color=(0.12, 0.16, 0.24, 1)))
        scroll.add_widget(items_box)
        inner.add_widget(scroll)
        close = ModernBtn(text="برگشت", bg_color=(0.3, 0.3, 0.35, 1))
        popup = Popup(title=fa(name), content=inner, size_hint=(0.9, 0.8))
        close.bind(on_press=popup.dismiss)
        inner.add_widget(close)
        popup.open()

if __name__ == "__main__":
    ZekrApp().run()
