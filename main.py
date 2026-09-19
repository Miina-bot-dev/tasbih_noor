# -*- coding: utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import os
import json
from datetime import datetime
import webbrowser
import arabic_reshaper
try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except Exception:
    # اگه پکیج python-bidi نصب نباشه، به‌جای کرش کردن، از روش جایگزین استفاده می‌کنیم
    BIDI_AVAILABLE = False
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
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

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except Exception:
        FONT_NAME = None
else:
    FONT_NAME = None

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def _smart_reverse(s):
    # مثل reshaped[::-1] برعکس می‌کنه، ولی رشته‌های عددی رو به‌صورت یک بلوک حفظ می‌کنه
    # تا عددهایی مثل ۱۰۰ برعکس (۰۰۱) نشن
    import re
    tokens = re.findall(r'[0-9۰-۹]+|.', s, flags=re.S)
    tokens.reverse()
    return ''.join(tokens)

def fa(text):
    if text is None: return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        if BIDI_AVAILABLE:
            return get_display(reshaped)
        return _smart_reverse(reshaped)
    except Exception:
        return str(text)

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

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"count": 0, "daily_target": 100, "paid": False}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    # ... بقیه اذکار در حافظه کد شما محفوظ است
}

class GlassCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(20), dp(5), dp(20), dp(10)] # کاهش پدینگ بالا/پایین برای فشرده‌تر شدن
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        # کادر پس‌زمینه حذف شد - فقط پدینگ/چیدمان می‌مونه، بدون رنگ پشت زمینه
    def _update_bg(self, *args):
        pass

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
        self.height = dp(40)
        self.my_color = bg_color
        with self.canvas.before:
            # حالت شیشه‌ای: رنگ اصلی با شفافیت کم‌تر تا پس‌زمینه دیده بشه
            r, g, b, a = self.my_color
            Color(r, g, b, a * 0.4)
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
    def set_num(self, text):
        # برای رشته‌های خالص عددی/ساعت/تاریخ - بدون reshape و بدون برعکس کردن،
        # تا ترتیب ارقام و اجزا (ساعت:دقیقه:ثانیه) از چپ به راست درست بمونه
        self.text = text

class ZekrApp(App):
    def _sync_main_height(self):
        if hasattr(self, 'main_layout') and hasattr(self, 'scroll'):
            self.main_layout.height = max(self.main_layout.minimum_height, self.scroll.height)

    def build(self):
        self.data = load_data()
        root = FloatLayout()

        # ۱. عکس پس‌زمینه (اول JPG که پایدارتر دیکود می‌شه، اگه نبود PNG)
        try:
            bg_candidates = ['main_banner.jpg', 'main_banner.jpeg', 'main_banner.png']
            bg_source = None
            for cand in bg_candidates:
                if os.path.exists(cand):
                    bg_source = cand
                    break
            if bg_source:
                bg = Image(source=bg_source, allow_stretch=True, keep_ratio=False, color=(0.6, 0.6, 0.6, 1))
                root.add_widget(bg)
        except Exception:
            pass

        # ۲. محتوای اسکرول‌شونده
        self.scroll = ScrollView(do_scroll_x=False, bar_width=0)
        # افزایش پدینگ بالا برای فاصله گرفتن از سقف
        self.main_layout = BoxLayout(orientation="vertical", spacing=dp(6), padding=[dp(20), dp(25), dp(20), dp(20)], size_hint_y=None)
        self.main_layout.bind(minimum_height=lambda *a: self._sync_main_height())
        self.scroll.bind(height=lambda *a: self._sync_main_height())
        
        # ردیف بالا: ساعت (چپ) + ذکر روز (راست، روبه‌روی ساعت)
        info_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        self.lbl_time = FaLabel(text="00:00:00", font_size="18sp", color=(1, 0.84, 0, 1), bold=True, halign="left")
        self.lbl_week_zekr = FaLabel(text="", font_size="17sp", halign="right", color=(1, 0.9, 0.6, 1), bold=True)
        info_row.add_widget(self.lbl_time)
        info_row.add_widget(self.lbl_week_zekr)
        self.main_layout.add_widget(info_row)

        # تاریخ، زیر ساعت
        self.lbl_date = FaLabel(text="", font_size="18sp", halign="left", color=(0.8, 0.8, 0.8, 1),
                                 size_hint_y=None, height=dp(22))
        self.main_layout.add_widget(self.lbl_date)

        # نمایش ذکر انتخاب‌شده از بانک اذکار
        self.lbl_selected_zekr = FaLabel(
            text="ذکر انتخابی: " + self.data.get("selected_zekr", "-"),
            font_size="16sp", color=(0.4, 0.9, 0.5, 1), bold=True,
            size_hint_y=None, height=dp(30)
        )
        self.main_layout.add_widget(self.lbl_selected_zekr)

        # کارت شمارنده
        card = GlassCard()
        self.lbl_count = FaLabel(text="۰", font_size="52sp", bold=True, size_hint_y=None, height=dp(75))
        self.progress = ProgressBar(max=100, size_hint_y=None, height=dp(15))
        self.lbl_target_info = FaLabel(text="هدف: ۱۰۰", font_size="14sp")

        card.add_widget(self.lbl_count)
        card.add_widget(self.progress)
        card.add_widget(self.lbl_target_info)
        
        # دکمه‌های کنترل
        btns_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(40))
        btn_add = ModernBtn(text="+1", bg_color=(0.55, 0.3, 0.85, 1))
        btn_add.bind(on_press=self.add_zekr)
        btn_sub = ModernBtn(text="-1", bg_color=(0.35, 0.25, 0.5, 1))
        btn_sub.bind(on_press=self.remove_zekr)
        btns_grid.add_widget(btn_sub); btns_grid.add_widget(btn_add)
        card.add_widget(btns_grid)
        
        btns_bottom = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(40))
        btn_reset = ModernBtn(text="ریست", bg_color=(0.75, 0.15, 0.15, 1))
        btn_reset.bind(on_press=self.reset_counter)
        btn_target = ModernBtn(text="هدف", bg_color=(0.1, 0.55, 0.25, 1))
        btn_target.bind(on_press=self.set_target_popup)
        btns_bottom.add_widget(btn_reset); btns_bottom.add_widget(btn_target)
        card.add_widget(btns_bottom)
        
        self.main_layout.add_widget(card)

        # فاصلهٔ خالی و منعطف - بخش بانک اذکار/حمایت رو به سمت پایین صفحه هل می‌ده
        self.main_layout.add_widget(Widget(size_hint_y=1))

        # بانک اذکار
        btn_list = ModernBtn(text="بانک اذکار مشکل‌گشا", bg_color=(0.4, 0.1, 0.6, 0.9))
        btn_list.bind(on_press=self.open_zekr_list)
        self.main_layout.add_widget(btn_list)

        # کارت حمایت از ما / امتیاز / عضویت در کانال بله
        support_card = GlassCard()
        lbl_support = FaLabel(text="لطفا از ما حمایت کنید", font_size="16sp", bold=True,
                               size_hint_y=None, height=dp(28))
        support_card.add_widget(lbl_support)

        support_btns_row = BoxLayout(orientation="horizontal", spacing=dp(10),
                                      size_hint_y=None, height=dp(50))
        btn_rate = ModernBtn(text="امتیاز دهید", bg_color=(0.85, 0.6, 0.1, 1))
        btn_rate.bind(on_press=self.open_rate)
        btn_join = ModernBtn(text="عضویت در کانال", bg_color=(0.1, 0.55, 0.25, 1))
        btn_join.bind(on_press=self.open_support)
        support_btns_row.add_widget(btn_rate)
        support_btns_row.add_widget(btn_join)
        support_card.add_widget(support_btns_row)

        # لینک کانال به‌صورت متن ساده روی صفحه - برای مواقعی که دکمه کانال رو باز نمی‌کنه
        lbl_channel_link = Label(
            text="@zekarnoor  |  ble.ir/zekarnoor",
            font_size="13sp", color=(0.7, 0.85, 1, 1),
            size_hint_y=None, height=dp(22)
        )
        support_card.add_widget(lbl_channel_link)

        self.main_layout.add_widget(support_card)

        self.scroll.add_widget(self.main_layout)
        root.add_widget(self.scroll)

        Clock.schedule_interval(self.update_live_data, 1)
        self.update_ui()
        return root

    def update_live_data(self, *args):
        now = datetime.now()
        self.lbl_time.set_num(to_fa_num(now.strftime("%H:%M:%S")))
        jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
        self.lbl_date.set_num(to_fa_num("%04d/%02d/%02d" % (jy, jm, jd)))
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
        inp = TextInput(text=str(self.data["daily_target"]), multiline=False, input_filter="int", font_name=FONT_NAME, font_size="20sp")
        btn = ModernBtn(text="تایید", bg_color=(0.1, 0.6, 0.4, 1))
        popup = Popup(title=fa("هدف جدید"), content=box, size_hint=(0.8, 0.4))
        box.add_widget(inp); box.add_widget(btn)
        btn.bind(on_press=lambda x: self.confirm_target(inp.text, popup))
        popup.open()

    def confirm_target(self, val, popup):
        self.data["daily_target"] = int(val) if val else 100
        save_data(self.data); self.update_ui(); popup.dismiss()

    def open_support(self, *args):
        # باز کردن لینک کانال @zekarnoor (نسخه ساده و مطمئن)
        from kivy.utils import platform
        target_url = "https://ble.ir/zekarnoor"

        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(target_url))
                PythonActivity.mActivity.startActivity(intent)
            except Exception:
                webbrowser.open(target_url)
        else:
            webbrowser.open(target_url)

    def open_rate(self, *args):
        # این نسخه فقط برای مایکت منتشر میشه، پس همیشه لینک امتیازدهی مایکت باز میشه
        package_name = "com.mina.tasbihnoor"
        target_url = f"https://myket.ir/app/{package_name}"

        from kivy.utils import platform
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(target_url))
                PythonActivity.mActivity.startActivity(intent)
            except Exception:
                webbrowser.open(target_url)
        else:
            webbrowser.open(target_url)

    def open_zekr_list(self, *args):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        scroll = ScrollView(); main_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        main_box.bind(minimum_height=main_box.setter("height"))
        popup = Popup(title=fa("بانک اذکار"), content=content, size_hint=(0.9, 0.8))
        for folder_name in ZEKR_FOLDERS.keys():
            btn = ModernBtn(text=folder_name, bg_color=(0.18, 0.22, 0.32, 1))
            btn.bind(on_press=lambda x, n=folder_name: self.show_folder_content(n, popup))
            main_box.add_widget(btn)
        scroll.add_widget(main_box); content.add_widget(scroll)
        close = ModernBtn(text="بستن", bg_color=(0.3, 0.25, 0.35, 1))
        close.bind(on_press=popup.dismiss); content.add_widget(close); popup.open()

    def show_folder_content(self, name, list_popup):
        inner = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        scroll = ScrollView(); items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        items_box.bind(minimum_height=items_box.setter("height"))
        popup = Popup(title=fa(name), content=inner, size_hint=(0.9, 0.8))
        for zekr in ZEKR_FOLDERS[name]:
            item_btn = ModernBtn(text=zekr, bg_color=(0.12, 0.16, 0.24, 1))
            item_btn.bind(on_press=lambda x, z=zekr: self.select_zekr(z, popup, list_popup))
            items_box.add_widget(item_btn)
        scroll.add_widget(items_box); inner.add_widget(scroll)
        close = ModernBtn(text="برگشت", bg_color=(0.3, 0.3, 0.35, 1))
        close.bind(on_press=popup.dismiss); inner.add_widget(close); popup.open()

    def select_zekr(self, zekr_text, folder_popup, list_popup):
        self.data["selected_zekr"] = zekr_text
        save_data(self.data)
        self.lbl_selected_zekr.set_fa("ذکر انتخابی: " + zekr_text)
        folder_popup.dismiss()
        list_popup.dismiss()

if __name__ == "__main__":
    import traceback
    try:
        ZekrApp().run()
    except Exception:
        try:
            with open(os.path.join(BASE_DIR, "crash_log.txt"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except:
            pass
        raise
