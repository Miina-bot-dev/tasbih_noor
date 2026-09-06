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

# --------------------------
# تنظیمات پایه و گرافیکی اصلی شما
# --------------------------
Window.clearcolor = (0.1, 0.04, 0.18, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
BACKGROUND_FILE = os.path.join(BASE_DIR, "main_banner.png")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except: FONT_NAME = None
else: FONT_NAME = None

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

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
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

ZEKR_FOLDERS = (
    ("صلوات", StarIcon if 'StarIcon' in locals() else FloatLayout, ("اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "اَللّهُمَّ صَلِّ عَلی مُحَمَّد", "صَلَّی static_folderُ عَلَیهِ وَ آلِهِ")),
    ("رزق و روزی", CoinIcon if 'CoinIcon' in locals() else FloatLayout, ("یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله")),
    ("گشایش مشکلات", LockIcon if 'LockIcon' in locals() else FloatLayout, ("یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات")),
    ("آرامش قلب", BirdIcon if 'BirdIcon' in locals() else FloatLayout, ("یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"))
)

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
    def _upd(self, *a):
        self.bg.pos, self.bg.size = self.pos, self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

class StyledBtn(Button):
    def __init__(self, text="", bg=(0.15, 0.35, 0.85, 1), **kw):
        super().__init__(**kw)
        self.text = text
        if FONT_NAME: self.font_name = FONT_NAME
        self.background_normal, self.background_color = "", (0, 0, 0, 0)
        self.bold, self.font_size, self.size_hint_y, self.height = True, "20sp", None, dp(54)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=(dp(12), dp(12), dp(12), dp(12)))
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a): self.rect.pos, self.rect.size = self.pos, self.size

class FLabel(Label):
    def __init__(self, text="", **kw):
        super().__init__(**kw)
        if FONT_NAME: self.font_name = FONT_NAME
        self.text = text
        self.halign = 'center'
class TasbihNoorApp(App):
    def build(self):
        self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
        self.data = self.load_data()
        self.root_layout = FloatLayout()
        
        if os.path.exists(BACKGROUND_FILE):
            self.root_layout.add_widget(Image(source=BACKGROUND_FILE, allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        
        content_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint=(1, 1))
        
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.lbl_datetime = FLabel(text="", font_size="14sp", size_hint_x=0.4, color=(1, 1, 1, 0.7))
        self.lbl_week_val = FLabel(text="", font_size="14sp", size_hint_x=0.6, bold=True, color=(1, 0.9, 0.5, 1))
        header_box.add_widget(self.lbl_datetime); header_box.add_widget(self.lbl_week_val); content_box.add_widget(header_box)
        
        self.lbl_guide = FLabel(text="", font_size="24sp", color=(0.4, 0.9, 0.5, 1), size_hint_y=None, height=dp(35))
        content_box.add_widget(self.lbl_guide)
        self.lbl_count = FLabel(text="0", font_size="77sp", bold=True, size_hint_y=None, height=dp(95))
        content_box.add_widget(self.lbl_count)
        
        progress_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(35), spacing=dp(2))
        self.progress = ProgressBar(max=self.data['daily_target'], value=min(self.data['count'], self.data['daily_target']), size_hint_y=None, height=dp(8))
        self.lbl_target = FLabel(text="", font_size="13sp", color=(1, 1, 1, 0.6))
        self.lbl_target.halign = 'right'; self.lbl_target.bind(size=self.lbl_target.setter('text_size'))
        progress_box.add_widget(self.progress); progress_box.add_widget(self.lbl_target); content_box.add_widget(progress_box)
        
        row1_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(52))
        self.btn_minus = StyledBtn(text="-1", bg=(0.35, 0.25, 0.45, 1)); self.btn_minus.bind(on_release=self.decrement_count)
        self.btn_plus = StyledBtn(text="+1", bg=(0.55, 0.3, 0.75, 1)); self.btn_plus.bind(on_release=self.increment_count)
        row1_box.add_widget(self.btn_minus); row1_box.add_widget(self.btn_plus); content_box.add_widget(row1_box)
        
        row2_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(52))
        self.btn_reset = StyledBtn(text="", bg=(0.7, 0.2, 0.2, 1)); self.btn_reset.bind(on_release=self.reset_count)
        self.btn_target = StyledBtn(text="", bg=(0.1, 0.55, 0.3, 1)); self.btn_target.bind(on_release=self.popup_set_target)
        row2_box.add_widget(self.btn_reset); row2_box.add_widget(self.btn_target); content_box.add_widget(row2_box)
        
        content_box.add_widget(BoxLayout(size_hint_y=0.7))
        
        self.btn_bank = StyledBtn(text="", bg=(0.45, 0.25, 0.8, 1), size_hint_y=None, height=dp(54))
        self.btn_bank.bind(on_release=lambda x: self.show_zekr_list()); content_box.add_widget(self.btn_bank)
        
        # 🎯 راهکار طلایی و رسمی: ساخت دکمه شیشه‌ای دوم دقیقاً با همان کلاس کادر کدهای خودتان
        # ارتفاع آن را ۶۵dp گذاشتم تا دو خط متن به زیبایی درونش جا شوند
        self.support_btn = StyledBtn(text="", bg=(1, 1, 1, 0.05), size_hint_y=None, height=dp(65))
        self.support_btn.bind(on_release=self.open_ble_channel)
        
        # استفاده از کاراکتر خط جدید (\n) برای نمایش دو خط متن کاملاً چسبیده و تراز وسط دقیقاً مثل عکس شما
        self.support_btn.text = fa("لطفا از ما حمایت کنید") + "\n" + fa("امتیاز دادن / عضویت در کانال")
        content_box.add_widget(self.support_btn)
        
        self.root_layout.add_widget(content_box)
        Clock.schedule_once(self.secure_persian_injection, 0.4)
        return self.root_layout

    def secure_persian_injection(self, dt):
        try:
            self.lbl_guide.text = fa("ذکر خود را انتخاب کنید")
            self.lbl_week_val.text = fa(WEEKLY_ZEKR.get(datetime.now().weekday(), ""))
            self.lbl_count.text = to_fa_num(self.data['count'])
            self.lbl_target.text = to_fa_num(self.data['daily_target']) + " : " + fa("هدف روزانه")
            self.btn_reset.text = fa("ریست"); self.btn_target.text = fa("هدف"); self.btn_bank.text = fa("بانک اذکار مشکل‌گشا")
        except: pass
        Clock.schedule_interval(self.update_clock, 1); self.update_clock(0)

    def update_clock(self, dt):
        try:
            now = datetime.now(); jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            self.lbl_datetime.text = fa(f"{now.strftime('%H:%M:%S')}\n{to_fa_num(jy)}/{to_fa_num(jm):02}/{to_fa_num(jd):02}")
        except: pass

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {"count": 0, "daily_target": 100}

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f: json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def increment_count(self, instance):
        self.data['count'] += 1; self.lbl_count.text = to_fa_num(self.data['count'])
        self.progress.value = min(self.data['count'], self.data['daily_target']); self.save_data()

    def decrement_count(self, instance):
        if self.data['count'] > 0:
            self.data['count'] -= 1; self.lbl_count.text = to_fa_num(self.data['count'])
            self.progress.value = min(self.data['count'], self.data['daily_target']); self.save_data()

    def reset_count(self, instance):
        self.data['count'] = 0; self.lbl_count.text = to_fa_num(self.data['count']); self.progress.value = 0; self.save_data()

    def popup_set_target(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.txt_input = TextInput(text=str(self.data['daily_target']), input_filter='int', multiline=False, font_size="20sp", size_hint_y=None, height=dp(50))
        btn_save = StyledBtn(text=fa("ذخیره هدف"), bg=(0.1, 0.55, 0.3, 1))
        popup = Popup(title=fa("تنظیم هدف"), content=content, size_hint=(0.85, 0.4))
        btn_save.bind(on_release=lambda x: self.save_new_target(popup))
        content.add_widget(self.txt_input); content.add_widget(btn_save); popup.open()

    def save_new_target(self, popup):
        try:
            val = int(self.txt_input.text)
            if val > 0:
                self.data['daily_target'] = val; self.progress.max = val; self.progress.value = min(self.data['count'], val)
                self.lbl_target.text = to_fa_num(val) + " : " + fa("هدف روزانه"); self.save_data()
        except: pass
        popup.dismiss()

    def open_ble_channel(self, instance):
        try: webbrowser.open("https://ble.ir")
        except: pass

    def show_zekr_list(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView(); list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height')); popup = Popup(title=fa("بانک اذکار"), size_hint=(0.9, 0.7))
        for folder_name, _, zekrs in ZEKR_FOLDERS:
            list_layout.add_widget(FLabel(text=fa(f"--- {folder_name} ---"), font_size="17sp", color=(0.7, 0.6, 0.9, 1)))
            for z in zekrs:
                b = StyledBtn(text=fa(z), bg=(0.2, 0.2, 0.35, 1)); b.font_size = "20sp"
                b.bind(on_release=lambda x, sz=z: self.select_zekr(sz, popup)); list_layout.add_widget(b)
        scroll.add_widget(list_layout); content.add_widget(scroll)
        btn_close = StyledBtn(text=fa("بستن"), bg=(0.5, 0.5, 0.5, 1)); btn_close.bind(on_release=popup.dismiss); content.add_widget(btn_close)
        popup.content = content; popup.open()

    def select_zekr(self, zekr_text, popup): popup.dismiss(); self.reset_count(None); self.lbl_guide.text = fa(zekr_text)

if __name__ == "__main__":
    TasbihNoorApp().run()
        self.valign = 'middle'
