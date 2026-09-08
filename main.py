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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

# جلوگیری از کرش در لایه گرافیکی اولیه با تنظیم رنگ پیش‌فرض ایمن
Window.clearcolor = (0.05, 0.05, 0.1, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
FONT_NAME = None

# سپر امنیتی ثبت فونت (اگر فایل نباشد، فونت سیستمی جایگزین می‌شود و کرش نمی‌کند)
if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except:
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
        try: return str(t).translate(FA_DIGITS)
        except: return ""

def to_fa_num(s): 
    try: return str(s).translate(FA_DIGITS)
    except: return str(s)

def gregorian_to_jalali(gy, gm, gd):
    try:
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
    except:
        return 1405, 1, 1

WEEKLY_ZEKR = {
    5: "یا رَبَّ الْعالَمین", 6: "یا ذاالْجَلالِ وَ الْاِکْرام", 0: "یا قاضِیَ الْحاجات",
    1: "یا اَرْحَمَ الرّاحِمین", 2: "یا حَیُّ یا قَیّوُم",
    3: "لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمُبین", 4: "اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد"
}

ZEKR_FOLDERS = (
    ("صلوات", ("اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "اَللّهُمَّ صَلِّ عَلی مُحَمَّد", "صَلَّی اللهُ عَلَیهِ وَ آلِهِ")),
    ("رزق و روزی", ("یا رزاق", "یا غنی", "یا واسع", "یا فتاح", "استغفرالله")),
    ("گشایش مشکلات", ("یا فتاح", "یا کاشف الکرب", "یا مجیب", "یا قاضی الحاجات")),
    ("آرامش قلب", ("یا سلام", "یا لطیف", "یا صبور", "یا نور", "یا رؤوف"))
)
class TasbihNoorApp(App):
    def load_data(self):
        """سپر امنیتی لود دیتا: اگر فایل جی‌سون خراب یا دستکاری شده باشد، کرش نمی‌کند"""
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict) and 'count' in content and 'daily_target' in content:
                        return content
        except: pass
        return {'count': 0, 'daily_target': 100}

    def save_data(self):
        """سپر امنیتی ذخیره دیتا"""
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def build(self):
        try:
            self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
            self.data = self.load_data()
            
            main_layout = FloatLayout()
            
            # ۱. بخش ساعت و تاریخ در گوشه بالا سمت چپ
            self.lbl_info_left = Label(
                text="", 
                font_size="13sp", 
                color=(1, 1, 1, 0.75),
                pos_hint={'center_x': 0.22, 'center_y': 0.94},
                font_name=FONT_NAME,
                halign='left',
                valign='middle'
            )
            self.lbl_info_left.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            main_layout.add_widget(self.lbl_info_left)
            
            # ۲. بخش ذکر روز در گوشه بالا سمت راست
            self.lbl_info_right = Label(
                text="",
                font_size="14sp",
                bold=True,
                color=(1, 0.9, 0.5, 1),
                pos_hint={'center_x': 0.78, 'center_y': 0.94},
                font_name=FONT_NAME,
                halign='right',
                valign='middle'
            )
            self.lbl_info_right.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            main_layout.add_widget(self.lbl_info_right)
            
            # ۳. عدد بزرگ شمارنده (کنار ماه)
            self.lbl_count = Label(
                text=str(self.data['count']).translate(FA_DIGITS),
                font_size="90sp",
                bold=True,
                color=(1, 1, 1, 1),
                pos_hint={'center_x': 0.65, 'center_y': 0.75},
                font_name=FONT_NAME
            )
            main_layout.add_widget(self.lbl_count)
            
            # ۴. بخش نوار پیشرفت و هدف روزانه
            target_val = self.data.get('daily_target', 100)
            self.lbl_target = Label(
                text=str(target_val).translate(FA_DIGITS) + " : " + fa("هدف روزانه"),
                font_size="16sp",
                color=(1, 1, 1, 0.7),
                pos_hint={'center_x': 0.5, 'center_y': 0.62},
                font_name=FONT_NAME
            )
            main_layout.add_widget(self.lbl_target)
            
            self.progress_bar = ProgressBar(
                max=target_val,
                value=min(self.data['count'], target_val),
                size_hint=(0.9, None),
                height=dp(10),
                pos_hint={'center_x': 0.5, 'center_y': 0.65}
            )
            main_layout.add_widget(self.progress_bar)
            
            # ۵. دکمه‌های +1 و -1
            btn_box1 = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.54})
            
            btn_plus = Button(text="+1", font_size="22sp", bold=True, background_color=(0.45, 0.3, 0.6, 1))
            btn_plus.bind(on_release=self.increment_count)
            
            btn_minus = Button(text="-1", font_size="22sp", bold=True, background_color=(0.35, 0.25, 0.45, 1))
            btn_minus.bind(on_release=self.decrement_count)
            
            btn_box1.add_widget(btn_minus)
            btn_box1.add_widget(btn_plus)
            main_layout.add_widget(btn_box1)
            
            # ۶. دکمه‌های رنگی هدف و ریست
            btn_box2 = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.44})
            
            btn_green = Button(
                text=fa("هدف"), 
                font_size="18sp", 
                background_color=(0, 0.6, 0.2, 1), 
                color=(1, 1, 1, 1), 
                background_normal="", 
                font_name=FONT_NAME
            )
            btn_green.bind(on_release=self.popup_set_target)
            
            btn_red = Button(
                text=fa("ریست"), 
                font_size="18sp", 
                background_color=(0.8, 0.1, 0.1, 1), 
                color=(1, 1, 1, 1), 
                background_normal="",
                font_name=FONT_NAME
            )
            btn_red.bind(on_release=self.reset_count)
            
            btn_box2.add_widget(btn_red)
            btn_box2.add_widget(btn_green)
            main_layout.add_widget(btn_box2)
            
            # ۷. دکمه بزرگ بنفش بانک ذکر
            btn_bank = Button(
                text=fa("بانک ذکر"),
                font_size="24sp",
                background_color=(0.45, 0.25, 0.8, 1),
                size_hint=(0.9, 0.08),
                pos_hint={'center_x': 0.5, 'center_y': 0.2},
                font_name=FONT_NAME
            )
            btn_bank.bind(on_release=lambda x: self.show_zekr_list())
            main_layout.add_widget(btn_bank)
            
            # ۸. بخش متن حمایت بزرگ شده و خوانا
            btn_support = Button(
                text=fa("لطفا از ما حمایت کنید") + "\n" + fa("امتیاز دادن و عضویت در کانال بله"),
                font_size="16sp", 
                background_color=(0, 0, 0, 0),
                size_hint=(0.9, 0.08), 
                pos_hint={'center_x': 0.5, 'center_y': 0.08},
                font_name=FONT_NAME,
                halign="center",
                valign="middle"
            )
            btn_support.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            btn_support.bind(on_press=self.open_ble_channel)
            main_layout.add_widget(btn_support)
            
            Clock.schedule_interval(self.update_clock, 1)
            self.update_clock(0)
            
            return main_layout
        except:
            fallback = FloatLayout()
            fallback.add_widget(Label(text="Tasbih Noor", font_size="24sp"))
            return fallback
    def update_clock(self, dt):
        try:
            now = datetime.now()
            jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            time_str = fa(now.strftime("%H:%M:%S"))
            date_str = to_fa_num(jy) + "/" + to_fa_num(jm) + "/" + to_fa_num(jd)
            wd = now.weekday()
            
            if hasattr(self, 'lbl_info_left') and self.lbl_info_left:
                self.lbl_info_left.text = f"{time_str}\n{date_str}"
            if hasattr(self, 'lbl_info_right') and self.lbl_info_right:
                self.lbl_info_right.text = fa(WEEKLY_ZEKR.get(wd, ""))
        except: pass

    def increment_count(self, instance):
        try:
            self.data['count'] += 1
            if hasattr(self, 'lbl_count') and self.lbl_count:
                self.lbl_count.text = str(self.data['count']).translate(FA_DIGITS)
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
            self.save_data()
        except: pass

    def decrement_count(self, instance):
        try:
            if self.data['count'] > 0:
                self.data['count'] -= 1
                if hasattr(self, 'lbl_count') and self.lbl_count:
                    self.lbl_count.text = str(self.data['count']).translate(FA_DIGITS)
                if hasattr(self, 'progress_bar') and self.progress_bar:
                    self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
                self.save_data()
        except: pass

    def reset_count(self, instance):
        try:
            self.data['count'] = 0
            if hasattr(self, 'lbl_count') and self.lbl_count:
                self.lbl_count.text = "۰"
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.value = 0
            self.save_data()
        except: pass

    def popup_set_target(self, instance):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            self.txt_input = TextInput(text=str(self.data.get('daily_target', 100)), input_filter='int', multiline=False, font_size="20sp")
            btn_save = Button(text=fa("ذخیره"), color=(1, 1, 1, 1), font_name=FONT_NAME)
            popup = Popup(title=fa("هدف روزانه"), content=content, size_hint=(0.85, 0.4))
            btn_save.bind(on_release=lambda x: self.save_new_target(popup))
            content.add_widget(self.txt_input)
            content.add_widget(btn_save)
            popup.open()
        except: pass

    def save_new_target(self, popup):
        try:
            val = int(self.txt_input.text)
            if val > 0:
                self.data['daily_target'] = val
                if hasattr(self, 'lbl_target') and self.lbl_target:
                    self.lbl_target.text = str(val).translate(FA_DIGITS) + " : " + fa("هدف روزانه")
                if hasattr(self, 'progress_bar') and self.progress_bar:
                    self.progress_bar.max = val
                    self.progress_bar.value = min(self.data['count'], val)
                self.save_data()
        except: pass
        try: popup.dismiss()
        except: pass
    def show_zekr_list(self):
        """ساخت پاپ‌آپی حاوی اسکرول‌بار برای دسته‌بندی‌های اصلی بانک ذکر"""
        try:
            main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            main_layout.add_widget(Label(text=fa("دسته‌بندی اذکار نور"), font_size="18sp", bold=True, size_hint_y=None, height=dp(30), font_name=FONT_NAME))
            
            scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            list_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            list_box.bind(minimum_height=list_box.setter('height'))
            
            for title, zekrs in ZEKR_FOLDERS:
                btn = Button(text=fa(title), color=(1, 1, 1, 1), font_name=FONT_NAME, size_hint_y=None, height=dp(50), background_color=(0.25, 0.2, 0.45, 1))
                btn.bind(on_release=lambda x, z=zekrs, t=title: self.show_sub_zekrs(t, z))
                list_box.add_widget(btn)
                
            scroll.add_widget(list_box)
            main_layout.add_widget(scroll)
            
            self.bank_popup = Popup(title=fa("بانک ذکر"), content=main_layout, size_hint=(0.85, 0.75))
            self.bank_popup.open()
        except: pass

    def show_sub_zekrs(self, title, zekrs):
        """پاپ‌آپ مرحله دوم برای نمایش متن‌های دقیق ذکرها"""
        try:
            sub_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            sub_layout.add_widget(Label(text=fa(title), font_size="18sp", bold=True, size_hint_y=None, height=dp(30), font_name=FONT_NAME))
            
            scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            list_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
            list_box.bind(minimum_height=list_box.setter('height'))
            
            for zekr_text in zekrs:
                btn = Button(text=fa(zekr_text), color=(1, 1, 1, 1), font_name=FONT_NAME, size_hint_y=None, height=dp(55), background_color=(0.15, 0.3, 0.5, 1))
                btn.font_size = "14sp" if len(zekr_text) > 25 else "16sp"
                btn.bind(on_release=lambda x, z=zekr_text: self.select_zekr(z))
                list_box.add_widget(btn)
                
            scroll.add_widget(list_box)
            sub_layout.add_widget(scroll)
            
            self.sub_popup = Popup(title=fa("انتخاب ذکر"), content=sub_layout, size_hint=(0.85, 0.75))
            self.sub_popup.open()
        except: pass

    def select_zekr(self, zekr_text):
        """بستن ایمن پاپ‌آپ‌ها پس از انتخاب ذکر توسط کاربر"""
        try:
            if hasattr(self, 'sub_popup') and self.sub_popup: self.sub_popup.dismiss()
        except: pass
        try:
            if hasattr(self, 'bank_popup') and self.bank_popup: self.bank_popup.dismiss()
        except: pass

    def open_ble_channel(self, instance):
        try: webbrowser.open("bale://channel?name=zekarnoor")
        except:
            try: webbrowser.open("https://ble.ir")
            except: pass

if __name__ == '__main__':
    try:
        TasbihNoorApp().run()
    except: pass
