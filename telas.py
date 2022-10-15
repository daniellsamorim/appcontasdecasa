from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty


class LoginPage(Screen):
    pass

class UsernamePage(Screen):
    pass

class HomePage(Screen):
    pass

class PagarPage(Screen):
    pass

class AluguelPage(Screen):
    pass

class BannerPage(Screen):
    pass

class ScrollPage(Screen):
    pass

class Content(BoxLayout):

    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.city = StringProperty()
        self.street = StringProperty()

