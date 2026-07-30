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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.animation import Animation
from kivy.properties import ListProperty

# --------------------------
# تنظیمات پایه
# --------------------------
Window.clearcolor = (0.02, 0.02, 0.08, 1)

# بارگذاری فونت فارسی
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="Vazir", fn_regular=FONT_FILE)
        FONT_NAME = "Vazir"
    except Exception:
        FONT_NAME = None
else:
    FONT_NAME = None

# بارگذاری arabic_reshaper
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except Exception:
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
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "zekr_data.json")

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
    except Exception as e:
        print("Save error:", e)

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
# کامپوننت‌های گرافیکی
# --------------------------

class GradientWidget(Widget):
    """ویجت گرادیانت پس‌زمینه"""
    def __init__(self, colors, **kwargs):
        super().__init__(**kwargs)
        self.colors = colors
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)
        self._update()
    
    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        # ساخت تکسچر گرادیانت
        import numpy as np
        from kivy.graphics.texture import Texture
        h = int(self.height) or 100
        w = int(self.width) or 100
        arr = np.zeros((h, w, 4), dtype=np.uint8)
        for i in range(h):
            ratio = i / h
            r = int(self.colors[0][0] * 255 * (1 - ratio) + self.colors[1][0] * 255 * ratio)
            g = int(self.colors[0][1] * 255 * (1 - ratio) + self.colors[1][1] * 255 * ratio)
            b = int(self.colors[0][2] * 255 * (1 - ratio) + self.colors[1][2] * 255 * ratio)
            arr[i, :] = [r, g, b, 255]
        texture = Texture.create(size=(w, h), colorfmt='rgba')
        texture.blit_buffer(arr.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        self.rect.texture = texture

class GlassCard(BoxLayout):
    """کارت شیشه‌ای با افکت مدرن"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(12)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        
        with self.canvas.before:
            # سایه
            Color(0, 0, 0, 0.3)
            self.shadow = RoundedRectangle(radius=[dp(24)])
            # پس‌زمینه شیشه‌ای
            Color(0.15, 0.18, 0.28, 0.75)
            self.bg = RoundedRectangle(radius=[dp(24)])
            # حاشیه نورانی
            Color(0.4, 0.5, 0.9, 0.3)
            self.border = Line(rounded_rectangle=(0, 0, 0, 0, dp(24)), width=dp(1.2))
        
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        x, y = self.pos
        w, h = self.size
        # سایه کمی پایین‌تر
        self.shadow.pos = (x + dp(2), y - dp(4))
        self.shadow.size = (w, h)
        self.bg.pos = (x, y)
        self.bg.size = (w, h)
        self.border.rounded_rectangle = (x, y, w, h, dp(24))

class GlowButton(Button):
    """دکمه درخشان با انیمیشن"""
    glow_color = ListProperty([0.2, 0.5, 1, 1])
    
    def __init__(self, text="", bg_color=(0.15, 0.4, 0.95, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.text = fa(text)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.font_size = '16sp'
        self.size_hint_y = None
        self.height = dp(52)
        self.color = (1, 1, 1, 1)
        self.bg_color = bg_color
        
        with self.canvas.before:
            # سایه دکمه
            Color(0, 0, 0, 0.25)
            self.shadow = RoundedRectangle(radius=[dp(18)])
            # پس‌زمینه دکمه
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[dp(18)])
            # افکت درخشش
            Color(1, 1, 1, 0.1)
            self.glow = RoundedRectangle(radius=[dp(18)])
        
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        x, y = self.pos
        w, h = self.size
        self.shadow.pos = (x + dp(1), y - dp(3))
        self.shadow.size = (w, h)
        self.rect.pos = (x, y)
        self.rect.size = (w, h)
        self.glow.pos = (x, y + h * 0.5)
        self.glow.size = (w, h * 0.5)
    
    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.1)
        anim.start(self)
        super().on_press()
    
    def on_release(self):
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)
        super().on_release()

class FaLabel(Label):
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('font_size', '18sp')
        kwargs.setdefault('color', (1, 1, 1, 1))
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

# --------------------------
# اپلیکیشن اصلی
# --------------------------

class ZekrApp(App):
    def build(self):
        self.data = load_data()
        
        # روت اصلی
        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # پس‌زمینه گرادیانت (آبی-بنفش تیره)
        with root.canvas.before:
            Color(0.04, 0.06, 0.15, 1)
            self.bg_top = Rectangle(pos=root.pos, size=root.size)
            Color(0.08, 0.03, 0.12, 1)
            self.bg_bottom = Rectangle(pos=root.pos, size=root.size)
        
        root.bind(pos=self._update_bg, size=self._update_bg)
        self._update_bg()
        
        # اسکرول محتوا
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        main = BoxLayout(
            orientation='vertical', 
            spacing=dp(18), 
            padding=[dp(20), dp(30), dp(20), dp(30)],
            size_hint_y=None
        )
        main.bind(minimum_height=main.setter('height'))
        
        # === هدر ===
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110), spacing=dp(5))
        
        # ساعت بزرگ
        self.lbl_time = FaLabel(
            text="00:00:00", 
            font_size='48sp', 
            color=(1, 0.92, 0.6, 1),
            bold=True
        )
        header.add_widget(self.lbl_time)
        
        # تاریخ و ذکر
        info = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28))
        self.lbl_date = FaLabel(
            text="", 
            font_size='13sp', 
            color=(0.7, 0.75, 0.9, 1),
            halign='left'
        )
        self.lbl_week = FaLabel(
            text="", 
            font_size='15sp', 
            color=(0.9, 0.7, 0.95, 1),
            bold=True,
            halign='right'
        )
        info.add_widget(self.lbl_date)
        info.add_widget(self.lbl_week)
        header.add_widget(info)
        
        main.add_widget(header)
        
        # === کارت شمارنده ===
        card = GlassCard()
        
        # عدد شمارنده
        self.lbl_count = FaLabel(
            text="۰", 
            font_size='90sp', 
            color=(0.3, 0.75, 1, 1),
            bold=True
        )
        card.add_widget(self.lbl_count)
        
        # نوار پیشرفت
        progress_box = BoxLayout(size_hint_y=None, height=dp(8), padding=[dp(10), 0, dp(10), 0])
        with progress_box.canvas.before:
            Color(0.1, 0.12, 0.2, 1)
            self.pb_bg = RoundedRectangle(radius=[dp(4)])
            Color(0.2, 0.6, 0.95, 1)
            self.pb_fill = RoundedRectangle(radius=[dp(4)])
        progress_box.bind(pos=self._update_progress, size=self._update_progress)
        card.add_widget(progress_box)
        
        self.lbl_target = FaLabel(
            text="هدف روزانه: ۱۰۰", 
            font_size='13sp', 
            color=(0.65, 0.7, 0.85, 1)
        )
        card.add_widget(self.lbl_target)
        
        # دکمه‌های کنترل
        grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(120))
        
        btn_add = GlowButton("+ ذکر", bg_color=(0.1, 0.5, 0.95, 1))
        btn_add.bind(on_press=self.add_zekr)
        
        btn_sub = GlowButton("- کم کردن", bg_color=(0.35, 0.35, 0.45, 1))
        btn_sub.bind(on_press=self.remove_zekr)
        
        btn_reset = GlowButton("ریست", bg_color=(0.8, 0.25, 0.35, 1))
        btn_reset.bind(on_press=self.reset_counter)
        
        btn_target = GlowButton("تنظیم هدف", bg_color=(0.15, 0.55, 0.4, 1))
        btn_target.bind(on_press=self.set_target_popup)
        
        grid.add_widget(btn_add)
        grid.add_widget(btn_sub)
        grid.add_widget(btn_reset)
        grid.add_widget(btn_target)
        card.add_widget(grid)
        
        main.add_widget(card)
        
        # === کارت بانک اذکار ===
        zekr_card = GlassCard()
        zekr_card.padding = [dp(15), dp(15), dp(15), dp(15)]
        
        btn_list = GlowButton(
            "🕌 بانک اذکار مشکل‌گشا", 
            bg_color=(0.45, 0.15, 0.7, 1),
            font_size='18sp'
        )
        btn_list.bind(on_press=self.open_zekr_list)
        zekr_card.add_widget(btn_list)
        
        main.add_widget(zekr_card)
        
        scroll.add_widget(main)
        root.add_widget(scroll)
        
        # آپدیت زمان
        Clock.schedule_interval(self.update_time, 1)
        self.update_ui()
        
        return root
    
    def _update_bg(self, *args):
        w, h = Window.size
        self.bg_top.pos = (0, h * 0.5)
        self.bg_top.size = (w, h * 0.5)
        self.bg_bottom.pos = (0, 0)
        self.bg_bottom.size = (w, h * 0.5)
    
    def _update_progress(self, obj, *args):
        x, y = obj.pos
        w, h = obj.size
        self.pb_bg.pos = (x, y)
        self.pb_bg.size = (w, h)
        # پر شدن بر اساس پیشرفت
        target = self.data.get("daily_target", 100)
        count = self.data.get("count", 0)
        ratio = min(count / target, 1.0) if target > 0 else 0
        self.pb_fill.pos = (x, y)
        self.pb_fill.size = (w * ratio, h)
    
    def update_time(self, *args):
        now = datetime.now()
        self.lbl_time.set_fa(to_fa_num(now.strftime("%H:%M:%S")))
        self.lbl_date.set_fa(to_fa_num(now.strftime("%Y/%m/%d")))
        self.lbl_week.set_fa(WEEKLY_ZEKR.get(now.weekday(), "ذکر روز"))
    
    def update_ui(self):
        c = self.data.get("count", 0)
        t = self.data.get("daily_target", 100)
        self.lbl_count.set_fa(to_fa_num(c))
        self.lbl_target.set_fa(f"هدف روزانه: {to_fa_num(t)}")
        # آپدیت نوار پیشرفت
        self._update_progress(self.lbl_target.parent)
    
    def add_zekr(self, *args):
        self.data["count"] = self.data.get("count", 0) + 1
        save_data(self.data)
        self.update_ui()
        # انیمیشن عدد
        anim = Animation(font_size='110sp', duration=0.1) + Animation(font_size='90sp', duration=0.2)
        anim.start(self.lbl_count)
    
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
        box.add_widget(FaLabel("هدف جدید را وارد کنید:", font_size='16sp', color=(0.8, 0.8, 0.9, 1)))
        
        inp = TextInput(
            text=str(self.data.get("daily_target", 100)), 
            multiline=False, 
            input_filter='int', 
            font_size='22sp',
            halign='center',
            background_color=(0.1, 0.12, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.3, 0.7, 1, 1),
            padding=[dp(10), dp(10)]
        )
        if FONT_NAME:
            inp.font_name = FONT_NAME
        box.add_widget(inp)
        
        btn_ok = GlowButton("✓ تایید", bg_color=(0.1, 0.6, 0.4, 1))
        popup = Popup(
            title=fa("تنظیم هدف"), 
            content=box, 
            size_hint=(0.85, 0.4),
            background_color=(0.08, 0.1, 0.18, 0.95)
        )
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
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        box.bind(minimum_height=box.setter('height'))
        
        for name in ZEKR_FOLDERS.keys():
            btn = GlowButton(name, bg_color=(0.2, 0.25, 0.4, 1), font_size='17sp')
            btn.bind(on_press=lambda x, n=name: self.show_zekrs(n))
            box.add_widget(btn)
        
        scroll.add_widget(box)
        content.add_widget(scroll)
        
        btn_close = GlowButton("✕ بستن", bg_color=(0.5, 0.2, 0.3, 1))
        popup = Popup(
            title=fa("بانک اذکار مشکل‌گشا"), 
            content=content, 
            size_hint=(0.92, 0.85),
            background_color=(0.06, 0.08, 0.15, 0.97)
        )
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()
    
    def show_zekrs(self, name):
        inner = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        box.bind(minimum_height=box.setter('height'))
        
        for zekr in ZEKR_FOLDERS[name]:
            lbl = FaLabel(
                zekr, 
                font_size='20sp', 
                color=(0.9, 0.85, 0.95, 1),
                size_hint_y=None,
                height=dp(50)
            )
            box.add_widget(lbl)
        
        scroll.add_widget(box)
        inner.add_widget(scroll)
        
        btn_back = GlowButton("← برگشت", bg_color=(0.3, 0.3, 0.45, 1))
        popup = Popup(
            title=fa(name), 
            content=inner, 
            size_hint=(0.92, 0.85),
            background_color=(0.06, 0.08, 0.15, 0.97)
        )
        btn_back.bind(on_press=popup.dismiss)
        inner.add_widget(btn_back)
        popup.open()

if __name__ == '__main__':
    ZekrApp().run()
