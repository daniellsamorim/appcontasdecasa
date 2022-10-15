from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle



class BannerList(GridLayout):


    def __init__(self, **kwargs):   #**kwargs avisa que vamos passar varios argumentos em dict
        self.rows = 1               #define o grid como 1 linha
        super().__init__()          #chama init do gridlayout

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))  #colocando a cor pr    eta no grid
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        descricao = kwargs["descricao"]
        data = kwargs["data"].replace("/2022","")
        valor = kwargs["valor"]
        code = kwargs["code"]


        esquerda1 = FloatLayout()
        esquerda1_label = Label(text=code, size_hint=(0.01, 0.2), pos_hint={"right": 0.4, "top": 0.6}, font_size=13)
        esquerda1.add_widget(esquerda1_label)

        esquerda = FloatLayout()
        esquerda_label=Label(text=descricao, size_hint=(0.01, 0.2), pos_hint={"right":0.45, "top":0.6}, font_size=13)
        esquerda.add_widget(esquerda_label)

        meio = FloatLayout()
        meio_label = Label(text=data, size_hint=(0.01, 0.2), pos_hint={"right": 0.8, "top": 0.6}, font_size=13)
        meio.add_widget(meio_label)

        direita = FloatLayout()
        direita_label_preco = Label(text=valor, size_hint=(0.01, 0.2), pos_hint={"right": 0.6, "top": 0.6}, font_size=13)
        direita.add_widget(direita_label_preco)

        self.add_widget(esquerda1)
        self.add_widget(esquerda)
        self.add_widget(meio)
        self.add_widget(direita)

    def atualizar_rec(self, *args): #*args tem que estar aqui mas nao usa pra nada
        self.rec.pos= self.pos
        self.rec.size = self.size

