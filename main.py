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
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput

# تنظیم رنگ پس‌زمینه پنجره برنامه
Window.clearcolor = (0.1, 0.04, 0.18, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
BACKGROUND_FILE = os.path.join(BASE_DIR, "main_banner.png")

# ثبت فونت فارسی وزیر
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
        self.valign = 'middle'
class TasbihNoorApp(App):
    def load_data(self):
        """لود کردن اطلاعات ذخیره شده تعداد ذکرها و هدف روزانه از حافظه موبایل"""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {'count': 0, 'daily_target': 100}

    def open_ble_channel(self, instance):
        """باز کردن مستقیم کانال برنامه در پیام‌رسان بله بدون واسطه مرورگر"""
        try:
            webbrowser.open("bale://channel?name=zekarnoor")
        except:
            webbrowser.open("https://ble.ir")

    def build(self):
        """ساخت و چیدمان نهایی تمام عناصر لایه گرافیکی برنامه"""
        self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
        self.data = self.load_data()
        self.root_layout = FloatLayout()
        
        if os.path.exists(BACKGROUND_FILE):
            self.root_layout.add_widget(Image(source=BACKGROUND_FILE, allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        
        content_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint=(1, 1))
        
        # ۱. بخش بالایی (ساعت زنده، تاریخ شمسی و ذکر روز)
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        self.lbl_datetime = FLabel(text="", font_size="14sp", size_hint_x=0.4, color=(1, 1, 1, 0.7))
        self.lbl_week_val = FLabel(text="", font_size="16sp", size_hint_x=0.6, bold=True, color=(1, 0.9, 0.5, 1))
        header_box.add_widget(self.lbl_datetime)
        header_box.add_widget(self.lbl_week_val)
        content_box.add_widget(header_box)
        
        # ۲. لیبل راهنما و نمایش ذکر انتخاب شده از بانک ذکر
        self.lbl_guide = FLabel(text=fa("لطفاً یک ذکر انتخاب کنید"), font_size="20sp", color=(0.4, 0.9, 0.5, 1), size_hint_y=None, height=dp(40))
        content_box.add_widget(self.lbl_guide)
        
        # ۳. کارت شیشه‌ای مرکزی (شامل اهداف و دکمه‌های کنترل)
        counter_card = GlassCard()
        
        target_val = self.data.get('daily_target', 100)
        self.lbl_target = FLabel(text=to_fa_num(target_val) + " : " + fa("هدف روزانه"), font_size="16sp", color=(1, 1, 1, 0.8))
        counter_card.add_widget(self.lbl_target)
        
        current_count = self.data.get('count', 0)
        self.lbl_count = FLabel(text=to_fa_num(current_count), font_size="48sp", bold=True, color=(1, 1, 1, 1))
        counter_card.add_widget(self.lbl_count)
        
        self.progress_bar = ProgressBar(max=target_val, value=min(current_count, target_val), size_hint_y=None, height=dp(15))
        counter_card.add_widget(self.progress_bar)
        
        # چیدمان دکمه‌های داخل کارت شیشه‌ای (ریست، هدف، منفی و مثبت)
        btn_grid = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        btn_plus = StyledBtn(text=fa("+"), bg=(0.1, 0.6, 0.3, 1))
        btn_plus.bind(on_release=self.increment_count)
        
        btn_minus = StyledBtn(text=fa("-"), bg=(0.7, 0.2, 0.2, 1))
        btn_minus.bind(on_release=self.decrement_count)
        
        btn_set_target = StyledBtn(text=fa("هدف"), bg=(0.2, 0.5, 0.7, 1))
        btn_set_target.bind(on_release=self.popup_set_target)
        
        btn_reset = StyledBtn(text=fa("ریست"), bg=(0.4, 0.4, 0.4, 1))
        btn_reset.bind(on_release=self.reset_count)
        
        btn_grid.add_widget(btn_reset)
        btn_grid.add_widget(btn_set_target)
        btn_grid.add_widget(btn_minus)
        btn_grid.add_widget(btn_plus)
        counter_card.add_widget(btn_grid)
        
        content_box.add_widget(counter_card)

        # ۴. دکمه بنفش بانک ذکر
        self.btn_bank = StyledBtn(text=fa("بانک ذکر"), bg=(0.45, 0.25, 0.8, 1))
        self.btn_bank.bind(on_release=lambda x: self.show_zekr_list())
        content_box.add_widget(self.btn_bank)

        # ۵. دکمه بزرگ حمایت راست‌چین واقعی ۲ خطه با سایز خوانا روی موبایل
        font_n = "Vazir" if FONT_NAME else None
        self.support_btn = Button(
            text=fa("لطفا از ما حمایت کنید") + "\n" + fa("امتیاز دادن و عضویت در کانال بله"),
            font_name=font_n,
            font_size=20,
            halign="right",
            valign="middle",
            padding=(dp(15), 0),
            background_normal="",
            background_color=(0.15, 0.35, 0.85, 0.4),
            size_hint=(1, None),
            height=dp(80)
        )
        self.support_btn.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
        self.support_btn.bind(on_press=self.open_ble_channel)
        content_box.add_widget(self.support_btn)
        
        self.root_layout.add_widget(content_box)
        
        # فعال‌سازی تایمر ۱ ثانیه‌ای برای آپدیت ساعت و تاریخ دستگاه
        Clock.schedule_interval(self.update_clock, 1)
        self.update_clock(0)
        
        return self.root_layout
    def update_clock(self, dt):
        """به‌روزرسانی خودکار و مداوم ساعت و تبدیل تاریخ میلادی دستگاه به شمسی"""
        try:
            now = datetime.now()
            jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            self.lbl_datetime.text = fa(now.strftime("%H:%M:%S")) + "\n" + to_fa_num(jy) + "/" + to_fa_num(jm) + "/" + to_fa_num(jd)
            wd = now.weekday()
            self.lbl_week_val.text = fa(WEEKLY_ZEKR.get(wd, ""))
        except: pass

    def save_data(self):
        """ذخیره آنی تغییرات تعداد ذکرها و هدف روزانه به صورت فایل جی‌سون در موبایل"""
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def increment_count(self, instance):
        """افزایش یک واحدی شمارنده با لمس دکمه مثبت"""
        self.data['count'] = self.data.get('count', 0) + 1
        self.lbl_count.text = to_fa_num(self.data['count'])
        self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
        self.save_data()

    def decrement_count(self, instance):
        """کاهش یک واحدی شمارنده با لمس دکمه منفی"""
        if self.data.get('count', 0) > 0:
            self.data['count'] -= 1
            self.lbl_count.text = to_fa_num(self.data['count'])
            self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
            self.save_data()

    def reset_count(self, instance):
        """صفر کردن شمارنده فعلی"""
        self.data['count'] = 0
        self.lbl_count.text = to_fa_num(0)
        self.progress_bar.value = 0
        self.save_data()

    def popup_set_target(self, instance):
        """پاپ‌آپ دریافت عدد هدف روزانه جدید از کاربر"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.txt_input = TextInput(text=str(self.data.get('daily_target', 100)), input_filter='int', multiline=False, font_size="20sp")
        btn_save = StyledBtn(text=fa("ذخیره"), bg=(0.1, 0.55, 0.3, 1))
        popup = Popup(title=fa("هدف روزانه"), content=content, size_hint=(0.85, 0.4))
        btn_save.bind(on_release=lambda x: self.save_new_target(popup))
        content.add_widget(self.txt_input)
        content.add_widget(btn_save)
        popup.open()

    def save_new_target(self, popup):
        """ذخیره و اعمال نهایی هدف روزانه جدید روی نوار پیشرفت برنامه"""
        try:
            val = int(self.txt_input.text)
            if val > 0:
                self.data['daily_target'] = val
                self.lbl_target.text = to_fa_num(val) + " : " + fa("هدف روزانه")
                self.progress_bar.max = val
                self.progress_bar.value = min(self.data.get('count', 0), val)
                self.save_data()
        except: pass
        popup.dismiss()

    def show_zekr_list(self):
        """ساخت پاپ‌آپ اول بانک ذکر همراه با ساختار اسکرول‌بار روان برای موبایل"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        main_layout.add_widget(FLabel(text=fa("دسته‌بندی اذکار نور"), font_size="18sp", bold=True, color=(1, 0.9, 0.5, 1), size_hint_y=None, height=dp(30)))
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        list_box = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        for title, icon_class, zekrs in ZEKR_FOLDERS:
            row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
            btn = StyledBtn(text=fa(title), bg=(0.25, 0.15, 0.45, 0.8), size_hint_x=0.8)
            btn.bind(on_release=lambda x, z=zekrs, t=title: self.show_sub_zekrs(t, z))
            
            if icon_class and icon_class != FloatLayout:
                icon_anchor = FloatLayout(size_hint_x=0.2)
                icon_instance = icon_class(pos_hint={'center_x': 0.5, 'center_y': 0.5})
                icon_anchor.add_widget(icon_instance)
                row.add_widget(btn)
                row.add_widget(icon_anchor)
            else:
                row.add_widget(btn)
                
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        main_layout.add_widget(scroll)
        
        self.bank_popup = Popup(title=fa("بانک ذکر"), content=main_layout, size_hint=(0.9, 0.85))
        self.bank_popup.open()

    def show_sub_zekrs(self, title, zekrs):
        """ساخت پاپ‌آپ دوم لایه درونی برای نمایش ذکرهای متنی موجود در هر پوشه فرعی"""
        sub_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        sub_layout.add_widget(FLabel(text=fa(title), font_size="18sp", bold=True, color=(1, 0.9, 0.5, 1), size_hint_y=None, height=dp(30)))
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        list_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        for zekr_text in zekrs:
            btn = StyledBtn(text=fa(zekr_text), bg=(0.15, 0.3, 0.5, 0.9), size_hint_y=None, height=dp(60))
            btn.font_size = "14sp" if len(zekr_text) > 25 else "16sp"
            btn.bind(on_release=lambda x, z=zekr_text: self.select_zekr(z))
            list_box.add_widget(btn)
            
        scroll.add_widget(list_box)
        sub_layout.add_widget(scroll)
        
        self.sub_popup = Popup(title=fa("انتخاب ذکر"), content=sub_layout, size_hint=(0.85, 0.75))
        self.sub_popup.open()

    def select_zekr(self, zekr_text):
        """اعمال نهایی متن ذکر انتخاب شده روی صفحه اصلی و بستن پاپ‌آپ‌ها"""
        self.lbl_guide.text = fa(zekr_text)
        self.reset_count(None)
        
        if hasattr(self, 'sub_popup'): self.sub_popup.dismiss()
        if hasattr(self, 'bank_popup'): self.bank_popup.dismiss()

if __name__ == '__main__':
    TasbihNoorApp().run()
