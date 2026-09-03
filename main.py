from kivy.app import App
from kivy.uix.label import Label
import arabic_reshaper
from bidi.algorithm import get_display

def fa(text):
    return get_display(arabic_reshaper.reshape(str(text)))

class TestApp(App):
    def build(self):
        return Label(text=fa("سلام"), font_size="30sp")

if __name__ == "__main__":
    TestApp().run()
