from kivy.config import Config
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '600')

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomsheet import MDListBottomSheet
from telas import *
from botoes import *
from datetime import date
from bannerlist import BannerList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from myfirebase import MyFirebase
from zerartelas import ZerarTelas
import requests
import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()
doc_main_kv = "main.kv"

class MainApp(MDApp):

    dialog = None
    list_chaves = []
    #user_atual = usuario logada na tela
    #mes_ref = mes do campo de consulta
    #ano_ref = ano do campo de consulta


    def build(self):
        self.firebase = MyFirebase()
        self.root = Builder.load_file(doc_main_kv)
        self.tema()
        #self.preencher_banner()

    def on_start(self):
        self.carregar_infos_usuario()
        #DEFINE O ANO E MES NOS BOTOES DE CONSULTA
        mes_ano = self.pegar_mes()
        self.colher_mes(mes_ano[1])
        self.colher_ano(mes_ano[2])

    def tema(self):
        self.theme_cls.theme_style = "Dark" #Dark Light
        self.theme_cls.primary_palette = "Orange"
        MDScreen()

    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()

            # chama a funcao
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # tenta pegar info usuario (caso exista)
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()  # pegou dic pro id especifico

            # carregar as fotos e nomes
            fotom = requisicao_dic["foto_mar"]
            fotoe = requisicao_dic["foto_esp"]
            nome_m = requisicao_dic["nome_mar"]
            nome_e = requisicao_dic["nome_esp"]

            pagina_home = self.root.ids["homepage"]  # pega pagina pelo id
            pagina_home.ids["foto_perfil_user1"].source = f'fotos/{fotom}'
            pagina_home.ids["foto_perfil_user2"].source = f'fotos/{fotoe}'
            pagina_home.ids["acoes_user1"].text = nome_m
            pagina_home.ids["acoes_user2"].text = nome_e

            self.user1 = nome_m
            self.user2 = nome_e

            self.mudar_tela("homepage")
        except Exception as ex:
            print("info user exceptio: ", ex)

    def alterar_nome_usuarios(self, nome_user1, nome_user2):

        if nome_user1 and nome_user2:
            #coloca a primeira letra em maiúscula
            nome_user1 = nome_user1.title()
            nome_user2 = nome_user2.title()

            link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            info = f'{{"nome_mar": "{nome_user1}", "nome_esp": "{nome_user2}", "nome_unico": "1"}}'
            requests.patch(link, data=info)

            pagina_home = self.root.ids["homepage"]  # pega pagina pelo id
            pagina_home.ids["acoes_user1"].text = nome_user1
            pagina_home.ids["acoes_user2"].text = nome_user2

            self.mudar_tela("homepage")
        else:
            pagina_nome = self.root.ids["usernamepage"]  # pega pagina pelo id
            pagina_nome.ids["label_aviso"].text = "Defina os nomes!"
            pagina_nome.ids["label_aviso"].color = (1, 0, 0, 1)


    def abrir_lista(self, menu):
        menu_itens = []
        valor=None
        if menu == "menu_telas":
            menu_itens = ["homepage", "bannerpage", "usernamepage", "aluguelpage"]
            function = self.mudar_tela
        elif menu == "menu_mes":
            data, mes_extenso, ano, mes_dic = self.pegar_mes()
            menu_itens = list(mes_dic.values())
            function = self.colher_mes
        elif menu == "menu_ano":
            for ano in range(2022, 2031):
                menu_itens.append(ano)
                function = self.colher_ano
        elif menu == "menu_user1":
            menu_itens = ["Cadastrar pagamento", "Ver pagamentos", "Relatórios", "Configurações"]
            function = self.acoes_user
            self.user_atual = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        elif menu == "menu_user2":
            menu_itens = ["Cadastrar pagamento", "Ver pagamentos", "Relatórios", "Configurações"]
            function = self.acoes_user
            self.user_atual = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")

        bottom_sheet_menu = MDListBottomSheet()
        for i in range(0, len(menu_itens)):
            if menu_itens[i] == "aluguelpage":
                bottom_sheet_menu.add_item(f"{menu_itens[i]}", lambda x, y=i: self.ver_aluguel())
            else:
                bottom_sheet_menu.add_item(f"{menu_itens[i]}",lambda x, y=i: function(f"{menu_itens[y]}"))
        bottom_sheet_menu.open()

    def acoes_user(self, acao):

        if acao == "Cadastrar pagamento":
            user = self.user_atual
            self.pagar_conta(user)
        if acao == "Ver pagamentos":
            user = self.pegar_credor(self.user_atual)
            self.preencher_banner(self.user_atual, self.mes_ref, self.ano_ref, user)


    def pegar_credor(self, user_atual):
        user1 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        user2 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")
        if user_atual == user1:
            credor = user2
        else:
            credor = user1
        return credor



    def calcular_pag_aluguel(self):

        #global aluguel_vl, condominio_vl, agua_vl, aluguel, condominio, agua
        try:

            # pega os valores de aluguel, condominio e água
            pagina_aluguel = self.root.ids["aluguelpage"]
            aluguel_vl = pagina_aluguel.ids["preco_aluguel"].text.replace(",", ".")
            condominio_vl = pagina_aluguel.ids["preco_condominio"].text.replace(",", ".")
            agua_vl = pagina_aluguel.ids["preco_agua"].text.replace(",", ".")
            agua_inclusa = pagina_aluguel.ids["check_agua"].active
            cond_inclusa = pagina_aluguel.ids["check_cond"].active

            aluguel = aluguel_vl
            condominio = condominio_vl
            agua = agua_vl

            float(aluguel)
            float(condominio)
            float(agua)

            if aluguel != "" and condominio != "" and agua != "":
                if cond_inclusa or agua_inclusa:
                    if cond_inclusa and not agua_inclusa:
                        pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel}"
                        pagina_aluguel.ids["label_cond"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(condominio)})"
                        pagina_aluguel.ids["label_agua"].text = f"Água a pagar: R$ {agua}"
                        condominio = 0

                    if agua_inclusa:
                        if cond_inclusa:

                            pagina_aluguel.ids["label_cond"].text = f"Agua e condominio incluso"
                            pagina_aluguel.ids[
                                "label_agua"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(condominio) - float(agua)})"
                            agua = 0
                            condominio = 0
                        else:
                            pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel}"
                            pagina_aluguel.ids["label_cond"].text = f"Condominio a pagar: R$ {condominio}"
                            pagina_aluguel.ids[
                                "label_agua"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(agua)})"
                            agua = 0
                else:
                    pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel}"
                    pagina_aluguel.ids["label_cond"].text = f"Condominio a pagar: R$ {condominio}"
                    pagina_aluguel.ids["label_agua"].text = f"Água a pagar: R$ {agua}"

            else:
                toast("Cadastre todos os valores!")
        except Exception as ex:
            toast("Cadastre todos os valores!")
            print("excessao", ex)

        self.gravar_pag_aluguel(aluguel_vl, condominio_vl, agua_vl, aluguel, condominio, agua)


    def gravar_pag_aluguel(self, *args):

        mes = self.pegar_texto(pagina="homepage", id_pagina="btn_mes", parametro="text")
        ano = self.pegar_texto(pagina="homepage", id_pagina="btn_ano", parametro="text")
        campo = "aluguel_" + mes + "_" + ano

        check_agua = self.pegar_texto(pagina="aluguelpage", id_pagina="check_agua", parametro="active")
        check_cond = self.pegar_texto(pagina="aluguelpage", id_pagina="check_cond", parametro="active")

        # cadastrar valores a pagar
        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}"
        info = f'{{"aluguel": "{args[0]}", "condominio": "{args[1]}", "agua": "{args[2]}", "aluguel_ttl": "{args[3]}",' \
               f' "condominio_ttl": "{args[4]}", "agua_ttl": "{args[5]}", "check_agua": "{check_agua}",' \
               f'"check_cond": "{check_cond}"}}'
        requests.patch(link, data=info)


    def ver_aluguel(self):

        mes, ano = self.mes_ano_solicitado()
        campo = "aluguel_" + mes + "_" + ano

        try:
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            # pegar oa valores dos campos no dict
            cond = requisicao_dic["condominio"]
            aluguel = requisicao_dic["aluguel"]
            agua = requisicao_dic["agua"]
            check_cond = requisicao_dic["check_cond"]
            check_agua = requisicao_dic["check_agua"]

            if check_cond == "True":
                cond_ative = True
            else:
                cond_ative = False
            if check_agua == "True":
                agua_ative = True
            else:
                agua_ative = False

            self.enviar_parametro(pag="aluguelpage", id="label_aviso_aluguel", par="text", dado=f"Cadastro de: {mes}/{ano}")
            self.enviar_parametro(pag="aluguelpage", id="preco_aluguel", par="text", dado=str(aluguel))
            self.enviar_parametro(pag="aluguelpage", id="preco_condominio", par="text", dado=str(cond))
            self.enviar_parametro(pag="aluguelpage", id="preco_agua", par="text", dado=str(agua))
            self.enviar_parametro(pag="aluguelpage", id="check_cond", par="active", dado=cond_ative)
            self.enviar_parametro(pag="aluguelpage", id="check_agua", par="active", dado=agua_ative)

            self.mudar_tela("aluguelpage")
        except:
            # link pro firebase
            self.enviar_parametro(pag="aluguelpage", id="label_aviso_aluguel", par="text",
                                  dado=f"Cadastro mes de: {mes}")

            self.enviar_parametro(pag="aluguelpage", id="preco_aluguel", par="hint_text", dado="0")
            self.enviar_parametro(pag="aluguelpage", id="preco_condominio", par="hint_text", dado="0")
            self.enviar_parametro(pag="aluguelpage", id="preco_agua", par="hint_text", dado="0")

            self.mudar_tela("aluguelpage")

    def pagar_conta(self, usuario):

        ZerarTelas.zerar_telapagar(self)

        data_now, meses, anos, listmeses= self.pegar_mes()
        # define variaveis como globais no main.py
        #self.usuario = usuario
        mes, ano = self.mes_ano_solicitado()
        #reseta os campos da tela pagamentos
        self.reset_campos_pagamento()
        self.ver_status_contas(self.user_atual)
        # enviar parametro: Qual a pagina? Qual id? Parametro = text/color? qual dado?
        self.enviar_parametro(pag="pagarpage", id="label_aviso_pago", par="text",
                              dado=f"[color=#00CFDB]Pagamentos:[/color] {self.user_atual}")
        self.enviar_parametro(pag="pagarpage", id="input_data", par="text", dado=data_now)
        self.enviar_parametro(pag="pagarpage", id="lbl_mes_referencia", par="text",
                              dado=f"Registrar em {self.mes_ref}/{self.ano_ref}")
        #campo do database
        campo = "aluguel_" + mes + "_" + ano
        try:
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text", dado=f"Contas a pagar: {mes}")
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            #pegar valores database
            agua = requisicao_dic["agua_ttl"]
            cond = requisicao_dic["condominio_ttl"]
            alug = requisicao_dic["aluguel_ttl"]

            print(agua, cond, alug)
            #preencher campos
            self.enviar_parametro(pag="pagarpage", id="lbl_alg_status", par="text", dado=f"Aluguel: R${alug}")
            self.enviar_parametro(pag="pagarpage", id="lbl_cond_status", par="text", dado=f"Cond.: R${cond}")
            self.enviar_parametro(pag="pagarpage", id="lbl_agua_status", par="text", dado=f"Agua: R${agua}")
            #de
            if alug == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
            if cond == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
            if agua == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
        except:
            self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text", dado=f"Cadastre aluguel {mes}")

        credor = self.pegar_credor(usuario)
        self.enviar_parametro(pag="pagarpage", id="btn_user_credor", par="text", dado=f"Devo a {credor}")
        self.mudar_tela("pagarpage")

        # vai pra tela de pagamentos (funcao: cadastrar_pagamento abaixo) levando as variaveis acima


    def cadastrar_pagamento(self, tipo):

        # pegar texto: Variavel = Qual pagina? Qual id?
        descricao = self.pegar_texto(pagina="pagarpage", id_pagina="input_desc", parametro="text")
        descricao = descricao.title()
        data = self.pegar_texto(pagina="pagarpage", id_pagina="input_data", parametro="text")
        valor = self.pegar_texto(pagina="pagarpage", id_pagina="input_valor", parametro="text").replace(",", ".")
        self.raiz = "pagamentos"
        self.mes, self.ano = self.mes_ano_solicitado()

        try:
            #valor = float(valor)


            if tipo == "devedor":
                self.raiz = "devedor"


            if descricao and data and valor:

                campo = self.user_atual + "_" + self.mes + "_" + self.ano

                # cadastrar pagamento no BD
                link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/{self.raiz}/{campo}.json?auth={self.id_token}"
                data = f'{{"descricao": "{descricao}", "data": "{data}", "valor": "{valor}"}}'
                requests.post(link, data)

                self.limpar_banner()
                credor = self.pegar_credor(self.user_atual)

                self.preencher_banner(self.user_atual, self.mes, self.ano, credor)

                self.mudar_tela("scrollpage")

            else:
                # enviar parametro: Qual a pagina? Qual id? Parametro = text/color? qual dado?
                toast("Nenhum campo pode ser vazio")
        except Exception as ex:
            print("oia: ", ex)


    def pagar_aluguel(self, *args):

        if args[0] == "alg":
            descricao = args[1][0:7] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Aluguel: R$", "")
        if args[0] == "cond":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Cond.: R$", "")
        if args[0] == "agua":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Agua: R$", "")

        self.enviar_parametro(pag="pagarpage", id="input_desc", par="text", dado=descricao)
        self.enviar_parametro(pag="pagarpage", id="input_valor", par="text", dado=valor)
        self.cadastrar_pagamento("pagamentos")


    def apagar_item_lista(self, user): #recebe: nome usuario(tratar texto)

        usuario = user.replace("Relatório de: ", "")
        mes = self.pegar_texto(pagina="homepage", id_pagina="btn_mes", parametro="text")
        ano = self.pegar_texto(pagina="homepage", id_pagina="btn_ano", parametro="text")

        campo = usuario + "_" + mes + "_" + ano

        codigo = self.pegar_texto(pagina="scrollpage", id_pagina="code_input", parametro="text")

        if codigo:

            for code in self.list_chaves:
                if codigo == code[1:7].replace("-", "x").lower():

                    try:
                        # procura o item em pagamentos
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass
                    try:
                        # procura o item em devedor
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass

                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="text",dado="Item excluido com sucesso")
                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="color",dado = (1, 1, 0, 1))

                    credor = self.pegar_credor(usuario)
                    self.limpar_banner()
                    self.preencher_banner(usuario, mes, ano, credor)
                    self.enviar_parametro(pag="scrollpage", id="code_input", par="text", dado="")



                    break
                else:
                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="text",
                                          dado="COD não existe na lista")
                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="color",
                                          dado=(1, 1, 0, 1))
        else:
            self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="text",
                                  dado="COD não pode ser vazio!")
            self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="color",dado=(1, 1, 0, 1))


    def limpar_banner(self):

        lista_pagamentos= self.pegar_texto(pagina="scrollpage", id_pagina="lista_pagamentos", parametro="id")
        # lista de pagamento é o scroollview, entao remove seus childrens (filhos)
        for item in list(lista_pagamentos.children):
            lista_pagamentos.remove_widget(item)

        lista_dividas = self.pegar_texto(pagina="scrollpage", id_pagina="lista_dividas", parametro="id")
        # lista de pagamento é o scroollview, entao remove seus childrens (filhos)
        for item in list(lista_dividas.children):
            lista_dividas.remove_widget(item)

    def show_alert_dialog(self):
        self.dialog = ""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Dialog box",
                text="O que deseja fazer?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.fechar_tela
                        ),
                    MDRectangleFlatButton(
                        text="Mudar tela",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.opcao

                        ),
                    ],
                )
        self.dialog.open()



    def preencher_banner(self, *args): #recebe: usuario[0], spinner mes[1], spinner ano[2] e credor[3]

        self.usuario = args[0]
        #LIMPA O BANNER PARA ENTRADA DE NOVOS DADOS
        self.limpar_banner()
        self.enviar_parametro(pag="scrollpage", id="code_input", par="text", dado="")

        #PREENCHE TEXTO DA PAGINA DE PAGAMENTOS
        self.enviar_parametro(pag="scrollpage", id="pgmt_user", par="text",dado=f"Relatório de: {args[0]}")
        self.enviar_parametro(pag="scrollpage", id="pgmt_mes", par="text", dado=f"{args[1]}/{args[2]}")

        #REQUISCAO NO BD
        campo = args[0] + "_" + args[1] + "_" + args[2]

        requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_pagamentos = self.pegar_texto(pagina="scrollpage", id_pagina="lista_pagamentos", parametro="id")
        soma = self.publicar_banner(lista_pagamentos, requisicao_dic)

        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_pgm", par="text",dado=f"Total despesas casa: R${soma}")

        requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_dividas = self.pegar_texto(pagina="scrollpage", id_pagina="lista_dividas", parametro="id")
        soma = self.publicar_banner(lista_dividas, requisicao_dic)

        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_div", par="text",dado=f"Total devo a {args[3]}: R${soma}")
        self.mudar_tela("scrollpage")



    def publicar_banner(self, *args): #recebe lista e requisicao_dic e soma
        soma = 0

        try:
            for local_id_user in args[1]:
                valor = args[1][local_id_user]["valor"]
                valor = float(valor)
                valor = "{:.2f}".format(valor)
                data = args[1][local_id_user]["data"]
                descricao = args[1][local_id_user]["descricao"]
                soma = soma + float(valor)
                self.list_chaves.append(local_id_user)
                code = local_id_user[1:7].replace("-", "x").lower()
                banner = BannerList(descricao=descricao[0:11] + "...", data=data, valor=valor, code=code)
                args[0].add_widget(banner)
            return soma
        except:
            self.enviar_parametro(pag="homepage", id="home_aviso", par="text", dado="Nenhum registro")
            self.enviar_parametro(pag="homepage", id="home_aviso", par="color", dado=(1, 0, 0, 1))




    def fazer_login_dialog(self):
        self.dialog = ""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Entre com seus dados:",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.fechar_tela,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release= self.pegar_texto,
                    ),
                ],
            )
        self.dialog.open()

    def fechar_tela(self, obj):
        self.dialog.dismiss()
    def opcao(self, obj):
        self.dialog.dismiss()
        self.mudar_tela("bannerpage")
    def pegar_texto(self, obj):

        print(self.dialog.content_cls.ids.city.text)
        print(self.dialog.content_cls.ids.street.text)
        self.dialog.dismiss()


    def pegar_credor(self, user):
        user1 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        user2 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")
        if user1 == user:
            credor = user2
        else:
            credor = user1
        return credor

    def ver_status_contas(self, *args):

        user1 = self.pegar_texto(pagina="homepage",id_pagina="acoes_user1", parametro="text")
        user2 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")
        mes_ref = self.mes_ref
        ano_ref = self.ano_ref
        lista = []

        try:
            campo = user1 + "_" + mes_ref + "_" + ano_ref
            lista= self.criar_lista(campo, lista)
        except:
            pass
        try:
            campo = user2 + "_" + mes_ref + "_" + ano_ref
            lista = self.criar_lista(campo, lista)
        except:
            pass

        for item in lista:
            if item == "Aluguel" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Aluguel pago")
            if item == "Cond" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Cond. pagp")
            if item == "Agua" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Agua paga")


    def criar_lista(self, campo, lista):

        requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        dic = requisicao.json()
        for valor in dic:
            lista.append(dic[valor]["descricao"])

        return lista

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela
    #mudar ja pegando mes e ano
    def colher_mes(self, mes):
        mes_btn = self.root.ids["homepage"]
        mes_btn.ids["btn_mes"].text = mes
        self.mes_ref = mes

    def colher_ano(self, ano):
        ano_btn = self.root.ids["homepage"]
        ano_btn.ids["btn_ano"].text = ano
        self.ano_ref = ano

    #mudar para arquivo zerar telas
    def reset_campos_pagamento(self):
        #seta botoes de pagamento
        self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Pagar")
        self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Pagar")
        self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Pagar")
        #seta label de valores a pagar
        self.enviar_parametro(pag="pagarpage", id="lbl_alg_status", par="text", dado=f"Aluguel: R$0")
        self.enviar_parametro(pag="pagarpage", id="lbl_cond_status", par="text", dado=f"Cond.: R$0")
        self.enviar_parametro(pag="pagarpage", id="lbl_agua_status", par="text", dado=f"Agua: R$0")

    def enviar_parametro(self, pag, id, par, dado):

        tela = self.root.ids[pag]
        if par == "text":
            tela.ids[id].text = dado
        if par == "color":
            tela.ids[id].color = dado
        if par == "hint_text":
            tela.ids[id].hint_text = dado
        if par == "active":
            tela.ids[id].active = bool(dado)
        if par == "disabled":
            tela.ids[id].disabled = bool(dado)


    def pegar_texto(self, pagina, id_pagina, parametro):
        tela = self.root.ids[pagina]
        if parametro == "text":
            dado = tela.ids[id_pagina].text
        if parametro == "active":
            dado = tela.ids[id_pagina].active
        if parametro == "id":
            dado = tela.ids[id_pagina]
        return dado

    def mes_ano_solicitado(self):
        mes_solicitado = self.pegar_texto(pagina="homepage", id_pagina="btn_mes", parametro="text")
        ano_solicitado = self.pegar_texto(pagina="homepage", id_pagina="btn_ano", parametro="text")
        return mes_solicitado, ano_solicitado

    def pegar_mes(self):

        today = date.today()
        data = today.strftime("%d/%m/%Y")
        mes = today.strftime("%m")
        ano = today.strftime("%Y")

        mes_dic = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        mes_extenso = mes_dic[mes]
        return data, mes_extenso, ano, mes_dic



MainApp().run()
