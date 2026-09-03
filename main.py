import os
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import json
import arabic_reshaper
from bidi.algorithm import get_display

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")
DATA_FILE = os.path.join(BASE_DIR, "zekr_data.json")

if os.path.exists(FONT_FILE):
    LabelBase.register(name="Vazir", fn_regular=FONT_FILE)

def fa(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"count": 0}

class TestApp(App):
    def build(self):
        data = load_data()
        box = BoxLayout(orientation="vertical")
        box.add_widget(Label(text=fa("سلام تست فارسی"), font_name="Vazir", font_size="30sp"))
        box.add_widget(Label(text=str(data.get("count", 0)), font_name="Vazir", font_size="30sp"))
        return box

if __name__ == "__main__":
    TestApp().run()
