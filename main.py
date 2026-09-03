import os
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.label import Label
import arabic_reshaper
from bidi.algorithm import get_display

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

if os.path.exists(FONT_FILE):
    LabelBase.register(name="Vazir", fn_regular=FONT_FILE)

def fa(text):
    return get_display(arabic_reshaper.reshape(str(text)))

class TestApp(App):
    def build(self):
        return Label(text=fa("سلام تست"), font_name="Vazir", font_size="30sp")

if __name__ == "__main__":
    TestApp().run()
