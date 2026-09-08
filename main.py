# -*- coding: utf-8 -*-
import os, json, webbrowser, arabic_reshaper
from datetime import datetime
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

Window.clearcolor = (0.05, 0.05, 0.1, 1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
FONT_NAME = "Vazir" if os.path.exists(FONT_FILE) else None
if FONT_NAME:
    try: LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
    except: FONT_NAME = None

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def fa(t):
    if not t: return ""
    try:
        s = str(t)
        if s.isdigit() or "/" in s or ":" in s: return s.translate(FA_DIGITS)
        return arabic_reshaper.reshape(s)[::-1]
    except: return str(t).translate(FA_DIGITS)

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
        return jy, 1 + (days // 31) if days < 186 else 7 + ((days - 186) // 30), 1 + (days % 31) if days < 186 else 1 + ((days - 186) % 30)
    except: return 1405, 1, 1

WEEKLY_ZEKR = {5: "یا رَبَّ الْعالَمین", 6: "یا ذاالْجَلالِ وَ الْاِکْرام", 0: "یا قاضِیَ الْحاجات", 1: "یا اَرْحَمَ الرّاحِمین", 2: "یا حَیُّ یا قَیّوُم", 3: "لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمُبین", 4: "اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد"}
ZEKR_FOLDERS = (("صلوات", ("اَللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد", "صَلَّی اللهُ عَلَیهِ وَ آلِهِ")), ("رزق و روزی", ("یا رزاق", "یا غنی")), ("گشایش مشکلات", ("یا کاشف الکرب", "یا قاضی الحاجات")), ("آرامش قلب", ("یا سلام", "یا لطیف")))
class TasbihNoorApp(App):
    def load_data(self):
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
        return {'count': 0, 'daily_target': 100}

    def save_data(self):
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f: json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def build(self):
        try:
            self.DATA_FILE = os.path.join(self.user_data_dir, "zekr_data.json")
            self.data = self.load_data()
            ml = FloatLayout()
            
            self.lbl_info_left = Label(text="", font_size="13sp", color=(1, 1, 1, 0.75), pos_hint={'center_x': 0.22, 'center_y': 0.94}, font_name=FONT_NAME, halign='left', valign='middle')
            self.lbl_info_left.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            ml.add_widget(self.lbl_info_left)
            
            self.lbl_info_right = Label(text="", font_size="14sp", bold=True, color=(1, 0.9, 0.5, 1), pos_hint={'center_x': 0.78, 'center_y': 0.94}, font_name=FONT_NAME, halign='right', valign='middle')
            self.lbl_info_right.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            ml.add_widget(self.lbl_info_right)
            
            self.lbl_count = Label(text=str(self.data['count']).translate(FA_DIGITS), font_size="90sp", bold=True, color=(1, 1, 1, 1), pos_hint={'center_x': 0.65, 'center_y': 0.75}, font_name=FONT_NAME)
            ml.add_widget(self.lbl_count)
            
            t_val = self.data.get('daily_target', 100)
            self.lbl_target = Label(text=str(t_val).translate(FA_DIGITS) + " : " + fa("هدف روزانه"), font_size="16sp", color=(1, 1, 1, 0.7), pos_hint={'center_x': 0.5, 'center_y': 0.62}, font_name=FONT_NAME)
            ml.add_widget(self.lbl_target)
            
            self.progress_bar = ProgressBar(max=t_val, value=min(self.data['count'], t_val), size_hint=(0.9, None), height=dp(10), pos_hint={'center_x': 0.5, 'center_y': 0.65})
            ml.add_widget(self.progress_bar)
            
            b1 = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.54})
            bp = Button(text="+1", font_size="22sp", bold=True, background_color=(0.45, 0.3, 0.6, 1))
            bp.bind(on_release=self.inc)
            bm = Button(text="-1", font_size="22sp", bold=True, background_color=(0.35, 0.25, 0.45, 1))
            bm.bind(on_release=self.dec)
            b1.add_widget(bm); b1.add_widget(bp); ml.add_widget(b1)
            
            b2 = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.44})
            bg = Button(text=fa("هدف"), font_size="18sp", background_color=(0, 0.6, 0.2, 1), color=(1, 1, 1, 1), background_normal="", font_name=FONT_NAME)
            bg.bind(on_release=self.set_t)
            br = Button(text=fa("ریست"), font_size="18sp", background_color=(0.8, 0.1, 0.1, 1), color=(1, 1, 1, 1), background_normal="", font_name=FONT_NAME)
            br.bind(on_release=self.rst)
            b2.add_widget(br); b2.add_widget(bg); ml.add_widget(b2)
            
            bb = Button(text=fa("بانک ذکر"), font_size="24sp", background_color=(0.45, 0.25, 0.8, 1), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.2}, font_name=FONT_NAME)
            bb.bind(on_release=self.show_z)
            ml.add_widget(bb)
            
            bs = Button(text=fa("لطفا از ما حمایت کنید\nامتیاز دادن و عضویت در کانال بله"), font_size="16sp", background_color=(0, 0, 0, 0), size_hint=(0.9, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.08}, font_name=FONT_NAME, halign="center", valign="middle")
            bs.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
            bs.bind(on_press=self.open_bale)
            ml.add_widget(bs)
            
            Clock.schedule_interval(self.upd, 1); self.upd(0)
            return ml
        except:
            fb = FloatLayout(); fb.add_widget(Label(text="Tasbih Noor", font_size="24sp")); return fb
    def upd(self, dt):
        try:
            now = datetime.now()
            jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
            self.lbl_info_left.text = f"{fa(now.strftime('%H:%M:%S'))}\n{str(jy).translate(FA_DIGITS)}/{str(jm).translate(FA_DIGITS)}/{str(jd).translate(FA_DIGITS)}"
            self.lbl_info_right.text = fa(WEEKLY_ZEKR.get(now.weekday(), ""))
        except: pass

    def inc(self, instance):
        try:
            self.data['count'] += 1
            self.lbl_count.text = str(self.data['count']).translate(FA_DIGITS)
            self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
            self.save_data()
        except: pass

    def dec(self, instance):
        try:
            if self.data['count'] > 0:
                self.data['count'] -= 1
                self.lbl_count.text = str(self.data['count']).translate(FA_DIGITS)
                self.progress_bar.value = min(self.data['count'], self.data.get('daily_target', 100))
                self.save_data()
        except: pass

    def rst(self, instance):
        try:
            self.data['count'] = 0
            self.lbl_count.text = "۰"
            self.progress_bar.value = 0
            self.save_data()
        except: pass

    def set_t(self, instance):
        try:
            c = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            self.txt_i = TextInput(text=str(self.data.get('daily_target', 100)), input_filter='int', multiline=False, font_size="20sp")
            bs = Button(text=fa("ذخیره"), color=(1, 1, 1, 1), font_name=FONT_NAME)
            p = Popup(title=fa("هدف روزانه"), content=c, size_hint=(0.85, 0.4))
            bs.bind(on_release=lambda x: self.save_t(p))
            c.add_widget(self.txt_i); c.add_widget(bs); p.open()
        except: pass

    def save_t(self, p):
        try:
            val = int(self.txt_i.text)
            if val > 0:
                self.data['daily_target'] = val
                self.lbl_target.text = str(val).translate(FA_DIGITS) + " : " + fa("هدف روزانه")
                self.progress_bar.max = val
                self.progress_bar.value = min(self.data['count'], val)
                self.save_data()
        except: pass
        try: p.dismiss()
        except: pass
    def show_z(self, instance):
        """ساخت پاپ‌آپی حاوی اسکرول‌بار برای دسته‌بندی‌های اصلی بانک ذکر"""
        try:
            c = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            for title, _ in ZEKR_FOLDERS:
                btn = Button(text=fa(title), color=(1, 1, 1, 1), font_name=FONT_NAME)
                c.add_widget(btn)
            Popup(title=fa("بانک ذکر"), content=c, size_hint=(0.85, 0.6)).open()
        except: pass

    def open_bale(self, instance):
        try: webbrowser.open("bale://channel?name=zekarnoor")
        except: webbrowser.open("https://ble.ir")

if __name__ == '__main__':
    try: 
        TasbihNoorApp().run()
    except: pass
