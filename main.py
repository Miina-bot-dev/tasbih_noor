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
# تنظیمات پایه و گرافیکی اصلی شما
# --------------------------
Window.clearcolor = (0.1, 0.04, 0.18, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
# تصویر پس‌زمینه کل صفحه شما
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
    try: return arabic_reshaper.reshape(str(t))[::-1]
    except: return str(t)

def to_fa_num(s): return str(s).translate(FA_DIGITS)

def gregorian_to_jalali(gy, gm, gd):
    g_d_m =
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

class GlassCard(BoxLayout):
    def __init__(self, radius=20, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.padding, self.spacing = dp(15), dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(1, 1, 1, 0.04)
            self.bg = RoundedRectangle(radius=[radius])
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
        self.bold, self.font_size, self.size_hint_y, self.height = True, "18sp", None, dp(54)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[dp(12)])
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a): self.rect.pos, self.rect.size = self.pos, self.size

class FLabel(Label):
    def __init__(self, text="", **kw):
        super().__init__(**kw)
        if FONT_NAME: self.font_name = FONT_NAME
        self.text = text
class TasbihNoorApp(App):
    def build(self):
        self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
        self.data = self.load_data()
        
        # لایه اصلی کل صفحه (FloatLayout برای تنظیم عکس پس‌زمینه سراسری شما)
        self.root_layout = FloatLayout()
        
        if os.path.exists(BACKGROUND_FILE):
            self.bg_img = Image(source=BACKGROUND_FILE, allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            self.root_layout.add_widget(self.bg_img)
            
        # المان‌های داخلی که به صورت عمودی با نظم عالی روی تصویر چیده می‌شوند
        content_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint=(1, 1))
        
        # ۱. بخش ساعت و تاریخ بالا سمت چپ/راست تصویر اصلی شما
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        self.lbl_datetime = FLabel(text="", font_size="15sp", size_hint_x=0.4, color=(1, 1, 1, 0.8))
        self.lbl_week_val = FLabel(text="", font_size="15sp", size_hint_x=0.6, bold=True, color=(1, 0.9, 0.5, 1))
        header_box.add_widget(self.lbl_datetime)
        header_box.add_widget(self.lbl_week_val)
        content_box.add_widget(header_box)
        
        # ۲. متن راهنمای انتخاب ذکر شما
        self.lbl_guide = FLabel(text="", font_size="20sp", color=(0.4, 0.9, 0.5, 1), size_hint_y=None, height=dp(40))
        content_box.add_widget(self.lbl_guide)
        
        # ۳. عدد بزرگ ذکرشمار مرکزی شما
        self.lbl_count = FLabel(text="0", font_size="75sp", bold=True, size_hint_y=None, height=dp(110))
        content_box.add_widget(self.lbl_count)
        
        # ۴. نوار پیشرفت باریک و هدف روزانه شما
        progress_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(35), spacing=dp(2))
        self.progress = ProgressBar(max=self.data['daily_target'], value=min(self.data['count'], self.data['daily_target']), size_hint_y=None, height=dp(8))
        self.lbl_target = FLabel(text="", font_size="13sp", color=(1, 1, 1, 0.6))
        progress_box.add_widget(self.progress)
        progress_box.add_widget(self.lbl_target)
        content_box.add_widget(progress_box)
        
        # ۵. ردیف اول دکمه‌ها: پلاس یک و منهای یک (دقیقاً دو ستونه مانند تصویر اول شما)
        row1_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(54))
        self.btn_minus = StyledBtn(text="-1", bg=(0.35, 0.25, 0.45, 1))
        self.btn_minus.bind(on_release=self.decrement_count)
        self.btn_plus = StyledBtn(text="+1", bg=(0.55, 0.3, 0.75, 1))
        self.btn_plus.bind(on_release=self.increment_count)
        row1_box.add_widget(self.btn_minus)
        row1_box.add_widget(self.btn_plus)
        content_box.add_widget(row1_box)
        
        # ۶. ردیف دوم دکمه‌ها: ریست و هدف
        row2_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(54))
        self.btn_reset = StyledBtn(text="", bg=(0.7, 0.2, 0.2, 1))
        self.btn_reset.bind(on_release=self.reset_count)
        self.btn_target = StyledBtn(text="", bg=(0.1, 0.55, 0.3, 1))
        row2_box.add_widget(self.btn_reset)
        row2_box.add_widget(self.btn_target)
        content_box.add_widget(row2_box)
        
        # فاصله خالی تا بخش پایین
        content_box.add_widget(BoxLayout(size_hint_y=0.1))
        
        # ۷. دکمه عریض بانک اذکار مشکل‌گشا
        self.btn_bank = StyledBtn(text="", bg=(0.45, 0.25, 0.8, 1), size_hint_y=None, height=dp(56))
        self.btn_bank.bind(on_release=lambda x: self.show_zekr_list())
        content_box.add_widget(self.btn_bank)
        
        # ۸. کارت شیشه‌ای حمایت و کانال پایین صفحه شما
        support_card = GlassCard()
        self.lbl_support_title = FLabel(text="", font_size="13sp", color=(1, 1, 1, 0.5))
        self.lbl_support_action = FLabel(text="", font_size="16sp", bold=True, color=(1, 1, 1, 0.9))
        support_card.add_widget(self.lbl_support_title)
        support_card.add_widget(self.lbl_support_action)
        content_box.add_widget(support_card)
        
        self.root_layout.add_widget(content_box)
        Clock.schedule_once(self.secure_persian_injection, 0.4)
        return self.root_layout

    def secure_persian_injection(self, dt):
        try:
            self.lbl_guide.text = fa("ذکر خود را انتخاب کنید")
            current_day = datetime.now().weekday()
            self.lbl_week_val.text = fa(WEEKLY_ZEKR.get(current_day, ""))
            self.lbl_count.text = to_fa_num(self.data['count'])
            self.lbl_target.text = fa(f"هدف: {to_fa_num(self.data['daily_target'])}")
            self.btn_reset.text = fa("ریست")
            self.btn_target.text = fa("هدف")
            self.btn_bank.text = fa("بانک اذکار مشکل‌گشا")
            self.lbl_support_title.text = fa("لطفا از ما حمایت کنید")
            self.lbl_support_action.text = fa("امتیاز دادن / عضویت در کانال")
        except: pass
        Clock.schedule_interval(self.update_clock, 1)
        self.update_clock(0)

    def update_clock(self, dt):
        try:
            now = datetime.now()
            jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            time_str = now.strftime("%H:%M:%S")
            date_str = f"{to_fa_num(jy)}/{to_fa_num(jm):02}/{to_fa_num(jd):02}"
            self.lbl_datetime.text = fa(f"{time_str}\n{date_str}")
        except: pass

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {"count": 0, "daily_target": 100}

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def increment_count(self, instance):
        self.data['count'] += 1
        self.lbl_count.text = to_fa_num(self.data['count'])
        self.progress.value = min(self.data['count'], self.data['daily_target'])
        self.save_data()

    def decrement_count(self, instance):
        if self.data['count'] > 0:
            self.data['count'] -= 1
            self.lbl_count.text = to_fa_num(self.data['count'])
            self.progress.value = min(self.data['count'], self.data['daily_target'])
            self.save_data()

    def reset_count(self, instance):
        self.data['count'] = 0
        self.lbl_count.text = to_fa_num(self.data['count'])
        self.progress.value = 0
        self.save_data()

    def show_zekr_list(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        popup = Popup(title=fa("انتخاب ذکر از بانک"), size_hint=(0.9, 0.7))
        
        # فولدرها به صورت لیست منظم عریض داخل پاپ‌آپ
        for folder_name, _, zekrs in ZEKR_FOLDERS:
            lbl_f = FLabel(text=fa(f"--- {folder_name} ---"), font_size="15sp", color=(0.7, 0.6, 0.9, 1))
            list_layout.add_widget(lbl_f)
            for z in zekrs:
                btn_zekr = StyledBtn(text=fa(z), bg=(0.2, 0.2, 0.35, 1))
                btn_zekr.bind(on_release=lambda x, sz=z: self.select_zekr(sz, popup))
                list_layout.add_widget(btn_zekr)
                
        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        btn_close = StyledBtn(text=fa("بستن"), bg=(0.5, 0.5, 0.5, 1))
        btn_close.bind(on_release=popup.dismiss)
        content.add_widget(btn_close)
        popup.content = content
        popup.open()

    def select_zekr(self, zekr_text, popup):
        popup.dismiss()
        self.reset_count(None)
        self.lbl_guide.text = fa(zekr_text)

if __name__ == "__main__":
    TasbihNoorApp().run()
