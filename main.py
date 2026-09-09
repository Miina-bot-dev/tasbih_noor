# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import webbrowser
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
from kivy.uix.textinput import TextInput

Window.clearcolor = (0.1, 0.04, 0.18, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
BACKGROUND_FILE = os.path.join(BASE_DIR, "main_banner.png")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except:
        FONT_NAME = None
else:
    FONT_NAME = None

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def fa(t):
    if not t: return ""
    try: 
        s = str(t)
        if s.isdigit() or "/" in s or ":" in s:
            return s.translate(FA_DIGITS)
        return arabic_reshaper.reshape(s)[::-1]
    except: 
        return str(t).translate(FA_DIGITS)

def to_fa_num(s): 
    return str(s).translate(FA_DIGITS)

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
    def _upd(self, instance, value): 
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
        self.add_widget(Label(text="$", font_size="20sp", color=(0.4, 0.3, 0.05, 1), bold=True, pos_hint={'center_x': 0.5, 'center_y': 0.5}))
    def _upd(self, instance, value):
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
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, instance, value):
        self.shackle.pos = (self.x+8, self.y+18)
        self.shackle.size = (20, 18)
        self.body.pos = (self.x+4, self.y+4)
        self.body.size = (28, 22)

class BirdIcon(IconBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.85, 0.4, 0.65, 1)
            self.body = Ellipse(pos=(self.x+10, self.y+10), size=(16, 14))
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, instance, value): 
        self.body.pos = (self.x+10, self.y+10)
        self.body.size = (16, 14)

class GlassCard(BoxLayout):
    def __init__(self, radius=20, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.padding, self.spacing = dp(15), dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(1, 1, 1, 0.04)
            self.bg = RoundedRectangle(radius=(radius, radius, radius, radius))
            Color(1, 1, 1, 0.08)
            self.border = Line(rounded_rectangle=(0, 0, 100, 100, radius), width=1.1)
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

class FLabel(Label):
    def __init__(self, text="", **kw):
        super().__init__(**kw)
        if FONT_NAME: 
            self.font_name = FONT_NAME
        self.text = text
        self.halign = 'center'
        self.valign = 'middle'

class TasbihNoorApp(App):
    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: 
                pass
        return {}

    def open_support(self, instance):
        from kivy.utils import platform
        target_url = "https://ble.ir"
        
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(target_url))
                PythonActivity.mActivity.startActivity(intent)
            except:
                webbrowser.open(target_url)
        else:
            webbrowser.open(target_url)

    def build(self):
        self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
        self.data = self.load_data()
        self.root_layout = FloatLayout()
        
        if os.path.exists(BACKGROUND_FILE):
            self.root_layout.add_widget(Image(source=BACKGROUND_FILE, allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        
        content_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint=(1, 1))
        
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.lbl_datetime = FLabel(text=fa("۱۴۰۵/۰۶/۱۸"), font_size="14sp", size_hint_x=0.4, color=(1, 1, 1, 0.7))
        self.lbl_week_val = FLabel(text=fa("ذکر روز"), font_size="14sp", size_hint_x=0.6, bold=True, color=(1, 0.9, 0.5, 1))
        header_box.add_widget(self.lbl_datetime)
        header_box.add_widget(self.lbl_week_val)
        content_box.add_widget(header_box)
        
        self.lbl_guide = FLabel(text=fa("تسبیح نور"), font_size="24sp", color=(0.4, 0.9, 0.5, 1), size_hint_y=None, height=dp(35))
        content_box.add_widget(self.lbl_guide)

        self.support_btn = Button(
            text=fa("حمایت از ما و عضویت در کانال بله"),
            font_name="Vazir" if FONT_NAME else None,
            font_size=18,
            halign="center",
            valign="middle",
            background_normal="",
            background_color=(0.1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(55)
        )
        self.support_btn.bind(size=lambda s, w: setattr(s, 'text_size', w))
        self.support_btn.bind(on_press=self.open_support)
        content_box.add_widget(self.support_btn)
        
        self.root_layout.add_widget(content_box)
        return self.root_layout

if __name__ == '__main__':
    TasbihNoorApp().run()
