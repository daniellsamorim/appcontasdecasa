from kivy.config import Config

Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '600')
# BIBLIOTECAS PARA ABRIR DOCUMENTOS
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager

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

    # user_atual = usuario logada na tela
    # mes_ref = mes do campo de consulta
    # ano_ref = ano do campo de consulta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path
        )

    def build(self):
        self.firebase = MyFirebase()
        self.root = Builder.load_file(doc_main_kv)
        self.tema()

    def on_start(self):
        self.carregar_infos_usuario()
        # DEFINE O ANO E MES NOS BOTOES DE CONSULTA
        mes_ano = self.pegar_mes()
        self.colher_mes(mes_ano[1])
        self.colher_ano(mes_ano[2])

    def tema(self):
        self.theme_cls.theme_style = "Dark"  # Dark Light
        self.theme_cls.primary_palette = "Orange"
        MDScreen()

    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()

            # VER SE USUARIO TEM O REFRESHTOKEN PARA MANTER LOGADO
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # PEGA INFOS DO USUARIO NO DB
            requisicao = requests.get(
                f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()  # pegou dic pro id especifico

            # CARREGA FOTOS E NOMES
            foto_user1 = requisicao_dic["foto_user1"].replace("+", "\\")
            foto_user2 = requisicao_dic["foto_user2"].replace("+", "\\")
            nome_user1 = requisicao_dic["nome_user1"]
            nome_user2 = requisicao_dic["nome_user2"]
            print("tttttttttt", foto_user2)

            pagina_home = self.root.ids["homepage"]  # pega pagina pelo id
            pagina_home.ids["foto_perfil_user1"].source = f'{foto_user1}'
            pagina_home.ids["foto_perfil_user2"].source = f'{foto_user2}'
            pagina_home.ids["acoes_user1"].text = nome_user1
            pagina_home.ids["acoes_user2"].text = nome_user2

            # self.user1 = nome_user1
            # self.user2 = nome_user2

            self.mudar_tela("homepage")
        except Exception as ex:
            print("info user exceptio: ", ex)

    def pegar_nomes_usuarios(self):  # SETA OS CAMPOS DE USUÁRIOS
        # PEGA O NOME DOS USUÁRIOS CADASTRADOS
        nome_user1 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        nome_user2 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")
        # SETA OS CAMPOS DE INPUT COM OS NOMES DE USUÁRIOS
        self.enviar_parametro(pag="usernamepage", id="nome_user1", par="text", dado=nome_user1)
        self.enviar_parametro(pag="usernamepage", id="nome_user2", par="text", dado=nome_user2)
        # VAI PRA TELA DE CADASTRO DE USUÁRIOS
        self.mudar_tela('usernamepage')

    def alterar_nome_usuarios(self, nome_user1, nome_user2):

        if nome_user1 and nome_user2:
            # coloca a primeira letra em maiúscula
            nome_user1 = nome_user1.title()
            nome_user2 = nome_user2.title()

            link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            info = f'{{"nome_user1": "{nome_user1}", "nome_user2": "{nome_user2}"}}'
            requests.patch(link, data=info)

            pagina_home = self.root.ids["homepage"]  # pega pagina pelo id
            pagina_home.ids["acoes_user1"].text = nome_user1
            pagina_home.ids["acoes_user2"].text = nome_user2

            self.mudar_tela("homepage")
        else:
            pagina_nome = self.root.ids["usernamepage"]  # pega pagina pelo id
            pagina_nome.ids["label_aviso"].text = "Defina os nomes!"
            pagina_nome.ids["label_aviso"].color = (1, 0, 0, 1)

    def abrir_lista_opcoes(self, menu):  # ABRE O MENU DE OPÇOES CHAMADO
        menu_itens = []
        valor = None
        if menu == "menu_telas":
            menu_itens = ["homepage", "configpage"]
            function = self.mudar_tela
        elif menu == "menu_mes":
            mes_dic = self.pegar_mes()
            menu_itens = list(mes_dic[3].values())
            function = self.colher_mes
        elif menu == "menu_ano":
            for ano in range(2022, 2031):
                menu_itens.append(ano)
                function = self.colher_ano
        elif menu == "menu_user1":
            menu_itens = ["Cadastrar despesas", "Ver minhas despesas", "Cadastrar contas fixas", "Relatórios"]
            function = self.acoes_user
            self.user_atual = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        elif menu == "menu_user2":
            menu_itens = ["Cadastrar despesas", "Ver minhas despesas", "Cadastrar contas fixas", "Relatórios"]
            function = self.acoes_user
            self.user_atual = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")

        bottom_sheet_menu = MDListBottomSheet()
        for i in range(0, len(menu_itens)):
            if menu_itens[i] == "aluguelpage":
                bottom_sheet_menu.add_item(f"{menu_itens[i]}", lambda x, y=i: self.ver_aluguel())
            else:
                bottom_sheet_menu.add_item(f"{menu_itens[i]}", lambda x, y=i: function(f"{menu_itens[y]}"))
        bottom_sheet_menu.open()

    def acoes_user(self, acao):

        if acao == "Cadastrar despesas":
            self.pagar_conta(self.user_atual)
        if acao == "Ver minhas despesas":
            credor = self.pegar_credor(self.user_atual)
            self.preencher_banner(self.user_atual, self.mes_ref, self.ano_ref, credor)
        if acao == "Cadastrar contas fixas":
            self.ver_aluguel()
        if acao == "Relatórios":
            user_2 = self.pegar_credor(self.user_atual)
            self.relatorio_pagamento(self.user_atual, user_2)

    def pegar_credor(self, user_atual):
        user1 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        user2 = self.pegar_texto(pagina="homepage", id_pagina="acoes_user2", parametro="text")
        if user_atual == user1:
            credor = user2
        else:
            credor = user1
        return credor

    def calcular_pag_aluguel(self):

        # global aluguel_vl, condominio_vl, agua_vl, aluguel, condominio, agua
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
                        pagina_aluguel.ids[
                            "label_cond"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(condominio)})"
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
        campo = mes + "_" + ano

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
        campo = mes + "_" + ano

        try:
            requisicao = requests.get(
                f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}")
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

            self.enviar_parametro(pag="aluguelpage", id="label_aviso_aluguel", par="text",
                                  dado=f"Cadastro de: {mes}/{ano}")
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

    def pegar_cod_user(self, usuario):
        nome_user = self.pegar_texto(pagina="homepage", id_pagina="acoes_user1", parametro="text")
        if usuario == nome_user:
            cod_user = "user1"
        else:
            cod_user = "user2"
        return cod_user

    def pagar_conta(self, usuario):

        # user = self.pegar_cod_user(usuario)

        ZerarTelas.zerar_telapagar(self)

        data_now = self.pegar_mes()
        mes = self.mes_ref
        ano = self.ano_ref

        # reseta os campos da tela pagamentos
        self.reset_campos_pagamento()
        self.ver_status_contas(self.user_atual)
        # enviar parametro: Qual a pagina? Qual id? Parametro = text/color? qual dado?
        self.enviar_parametro(pag="pagarpage", id="label_aviso_pago", par="text",
                              dado=f"[color=#00CFDB]Pagamentos:[/color] {self.user_atual}")
        self.enviar_parametro(pag="pagarpage", id="lbl_mes_referencia", par="text", dado=f"Registrar em {mes}/{ano}")
        self.enviar_parametro(pag="pagarpage", id="input_data", par="text", dado=data_now[0])
        # campo do database
        campo = mes + "_" + ano
        try:
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text", dado=f"Contas fixas: {mes}")
            requisicao = requests.get(
                f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            # pegar valores database
            agua = requisicao_dic["agua_ttl"]
            cond = requisicao_dic["condominio_ttl"]
            alug = requisicao_dic["aluguel_ttl"]

            # preencher campos
            self.enviar_parametro(pag="pagarpage", id="lbl_alg_status", par="text", dado=f"Aluguel: R${alug}")
            self.enviar_parametro(pag="pagarpage", id="lbl_cond_status", par="text", dado=f"Cond.: R${cond}")
            self.enviar_parametro(pag="pagarpage", id="lbl_agua_status", par="text", dado=f"Agua: R${agua}")
            # de
            if alug == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Incluso")
            if cond == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Incluso")
            if agua == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Incluso")
        except:
            self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text", dado=f"Cadastre aluguel {mes}")

        credor = self.pegar_credor(usuario)
        self.enviar_parametro(pag="pagarpage", id="btn_user_credor", par="text", dado=f"Cadastrar devo a {credor}")
        self.mudar_tela("pagarpage")

        # vai pra tela de pagamentos (funcao: cadastrar_pagamento abaixo) levando as variaveis acima

    def cadastrar_pagamento(self, tipo):

        # pegar texto: Variavel = Qual pagina? Qual id?
        descricao = self.pegar_texto(pagina="pagarpage", id_pagina="input_desc", parametro="text").title()
        data = self.pegar_texto(pagina="pagarpage", id_pagina="input_data", parametro="text")
        valor = self.pegar_texto(pagina="pagarpage", id_pagina="input_valor", parametro="text").replace(",", ".")
        raiz = "pagamentos"
        mes, ano = self.mes_ano_solicitado()

        cod_user = self.pegar_cod_user(self.user_atual)

        try:
            valor = float(valor)

            if tipo == "devedor":
                raiz = "devedor"

            if descricao and data and valor:

                campo = cod_user + "_" + mes + "_" + ano

                # cadastrar pagamento no BD
                link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/{raiz}/{campo}.json?auth={self.id_token}"
                data = f'{{"descricao": "{descricao}", "data": "{data}", "valor": "{valor}"}}'
                requests.post(link, data)

                self.limpar_banner()
                credor = self.pegar_credor(self.user_atual)

                self.preencher_banner(self.user_atual, mes, ano, credor)

                self.mudar_tela("scrollpage")

            else:
                # enviar parametro: Qual a pagina? Qual id? Parametro = text/color? qual dado?
                toast("Nenhum campo pode ser vazio")
        except Exception as ex:
            toast("Preencha os campos corretamente!")

    def pagar_aluguel(self, *args):

        # PREENCHE OS DADOS DO BOTAO DE CONTAS FIXAS
        if args[0] == "alg":
            descricao = args[1][0:7] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Aluguel: R$", "")
        if args[0] == "cond":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Cond.: R$", "")
        if args[0] == "agua":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Agua: R$", "")
        # PREENCHE OS AUTOMATICAMENTE CAMPOS PARA PAGAMENTO DE CONTAS FIXAS
        self.enviar_parametro(pag="pagarpage", id="input_desc", par="text", dado=descricao)
        self.enviar_parametro(pag="pagarpage", id="input_valor", par="text", dado=valor)
        # VAI PARA FUNÇÃO DE PAGAMENTO
        self.cadastrar_pagamento("pagamentos")

    def apagar_item_lista(self, user):  # recebe: nome usuario(tratar texto)

        # PEGA MES E ANO DE REFERÊNCIA
        mes = self.mes_ref
        ano = self.ano_ref
        cod_user = self.pegar_cod_user(self.user_atual)
        # PREENCHE O CAMPO PARA REQUISICAO DB
        campo = cod_user + "_" + mes + "_" + ano
        # PEGA CODIGO DO ITEM A SER EXCLUIDO
        codigo = self.pegar_texto(pagina="scrollpage", id_pagina="code_input", parametro="text")

        if codigo:
            for code in self.list_chaves:
                if codigo == code[1:7].replace("-", "x").lower():
                    try:
                        # PROCURA O CODIGO EM PAGAMENTOS
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/" \
                               f"{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass
                    try:
                        # PROCURA O CODIGO EM DEVEDOR
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/" \
                               f"{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass
                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="text",
                                          dado="Item excluido com sucesso")
                    self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="color", dado=(1, 1, 0, 1))

                    credor = self.pegar_credor(cod_user)
                    self.limpar_banner()
                    self.preencher_banner(self.user_atual, mes, ano, credor)
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
            self.enviar_parametro(pag="scrollpage", id="lbl_aviso", par="color", dado=(1, 1, 0, 1))

    def limpar_banner(self):

        lista_pagamentos = self.pegar_texto(pagina="scrollpage", id_pagina="lista_pagamentos", parametro="id")
        # lista de pagamento é o scroollview, entao remove seus childrens (filhos)
        for item in list(lista_pagamentos.children):
            lista_pagamentos.remove_widget(item)

        lista_dividas = self.pegar_texto(pagina="scrollpage", id_pagina="lista_dividas", parametro="id")
        # lista de pagamento é o scroollview, entao remove seus childrens (filhos)
        for item in list(lista_dividas.children):
            lista_dividas.remove_widget(item)

    def preencher_banner(self, *args):  # recebe: usuario[0], spinner mes[1], spinner ano[2] e credor[3]

        # LIMPA O BANNER PARA ENTRADA DE NOVOS DADOS
        self.limpar_banner()
        self.enviar_parametro(pag="scrollpage", id="code_input", par="text", dado="")

        # PREENCHE TITULO DA PAGINA DE PAGAMENTOS
        self.enviar_parametro(pag="scrollpage", id="pgmt_user", par="text", dado=f"Relatório de: {args[0]}")
        self.enviar_parametro(pag="scrollpage", id="pgmt_mes", par="text", dado=f"{args[1]}/{args[2]}")

        # REQUISCAO NO BD
        cod_user = self.pegar_cod_user(args[0])
        campo = cod_user + "_" + args[1] + "_" + args[2]

        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_pagamentos = self.pegar_texto(pagina="scrollpage", id_pagina="lista_pagamentos", parametro="id")
        soma = self.publicar_banner(lista_pagamentos, requisicao_dic)

        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_pgm", par="text", dado=f"Total despesas casa: R${soma}")

        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_dividas = self.pegar_texto(pagina="scrollpage", id_pagina="lista_dividas", parametro="id")
        soma = self.publicar_banner(lista_dividas, requisicao_dic)

        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_div", par="text", dado=f"Total devo a {args[3]}: R${soma}")
        self.mudar_tela("scrollpage")

    def publicar_banner(self, *args):  # recebe lista e requisicao_dic e soma
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
            pass

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
                        on_release=self.fechar_tela,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.pegar_texto,
                    ),
                ],
            )
        self.dialog.open()

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
        lista = []
        mes_ref = self.mes_ref
        ano_ref = self.ano_ref

        try:
            campo = "user1" + "_" + mes_ref + "_" + ano_ref
            lista = self.criar_lista(campo, lista)
        except:
            pass
        try:
            campo = "user2" + "_" + mes_ref + "_" + ano_ref
            lista = self.criar_lista(campo, lista)
        except:
            pass
        # CASO ITEM NA LISTA, DESABILITA BOTAO DE PAGAMENTO
        for item in lista:
            if item == "Aluguel" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Pago")
            if item == "Cond" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Pago")
            if item == "Agua" + "_" + mes_ref + "_" + ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Pago")

    def relatorio_pagamento(self, *args):  # recebe: user1, user2

        cod_userx = self.pegar_cod_user(args[0])
        cod_usery = self.pegar_cod_user(args[1])

        mes_ref, ano_ref = self.mes_ano_solicitado()

        self.enviar_parametro(pag="relatoriopage", id="relat_mes", par="text", dado=f"{mes_ref}/{ano_ref}")
        self.enviar_parametro(pag="relatoriopage", id="lbl_rel_user1", par="text", dado=f"Relatório de {args[0]}:")
        self.enviar_parametro(pag="relatoriopage", id="lbl_rel_user2", par="text", dado=f"Relatório de {args[1]}:")

        # pegar pagamentos para user1
        total1 = self.pegar_total_pago(cod_userx, mes_ref, ano_ref, "pagamentos")
        self.enviar_parametro(pag="relatoriopage", id="lbl_pago_user1", par="text", dado=f"Despesas: R${total1:,.2f}")
        # pegar pagamentos para user2
        total2 = self.pegar_total_pago(cod_usery, mes_ref, ano_ref, "pagamentos")
        self.enviar_parametro(pag="relatoriopage", id="lbl_pago_user2", par="text", dado=f"Despesas: R${total2:,.2f}")

        total_despesas = total1 + total2
        ttl_cada = total_despesas / 2
        self.enviar_parametro(pag="relatoriopage", id="lbl_ttl_desp", par="text",
                              dado=f"Total despesas: R${total_despesas:,.2f}")
        self.enviar_parametro(pag="relatoriopage", id="lbl_ttl_cada", par="text",
                              dado=f"Total pra cada: R${total_despesas / 2:,.2f}")

        # pegar pagamentos para user1
        total3 = self.pegar_total_pago(args[0], mes_ref, ano_ref, "devedor")
        self.enviar_parametro(pag="relatoriopage", id="lbl_dev_user1", par="text",
                              dado=f"Deve a {args[1]}: R${total3:,.2f}")
        # pegar pagamentos para user2
        total4 = self.pegar_total_pago(args[1], mes_ref, ano_ref, "devedor")
        self.enviar_parametro(pag="relatoriopage", id="lbl_dev_user2", par="text",
                              dado=f"Deve a {args[0]}: R${total4:,.2f}")

        if ttl_cada < total1:  # dsa deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"{args[1]} deve a {args[0]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"R${(total1 - ttl_cada):,.2f}")
        elif ttl_cada < total2:  # za deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"{args[0]} deve a {args[1]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"R${(total2 - ttl_cada):,.2f}")
        else:
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"Não á débtos!")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"")

        if total4 < total3:  # dsa deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"{args[0]} deve a {args[1]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"R${(total3 - total4):,.2f}")
        elif total3 < total4:  # za deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"{args[1]} deve a {args[0]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"R${(total4 - total3):,.2f}")
        else:
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"Não há débito!")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"")

        self.mudar_tela("relatoriopage")

    def pegar_total_pago(self, *args): #recebe user, mes, ano e raiz
        total = 0
        try:
            campo = args[0] + "_" + args[1] + "_" + args[2]
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}"
                                      f"/{args[3]}/{campo}.json?auth={self.id_token}")
            dic = requisicao.json()

            for valor in dic:
                total = total + float((dic[valor]["valor"]))
            return total
        except:
            return total

    def criar_lista(self, campo, lista):  # PEGA LISTA DE PAGAMENTOS(CAMPO = USER+MES+ANO)

        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        dic = requisicao.json()
        for valor in dic:
            lista.append(dic[valor]["descricao"])
        return lista

    def show_alert_dialog(self):
        self.dialog = ""
        if not self.dialog:
            self.dialog = MDDialog(
                # title="Atenção!",
                text="Sair da conta?",
                buttons=[
                    MDFlatButton(
                        text="Cancelar",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.fechar_tela
                    ),
                    MDRectangleFlatButton(
                        text="Sim",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.opcao
                    ),
                ],
            )
        self.dialog.open()

    def fechar_tela(self, obj):
        self.dialog.dismiss()

    def opcao(self, obj):
        self.dialog.dismiss()
        self.fazer_logoff()

    def fazer_logoff(self):

        path = os.path.join("refreshtoken.txt")
        os.remove(path)
        self.mudar_tela("loginpage")

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    # mudar ja pegando mes e ano
    def colher_mes(self, mes):
        mes_btn = self.root.ids["homepage"]
        mes_btn.ids["btn_mes"].text = mes
        self.mes_ref = mes

    def colher_ano(self, ano):
        ano_btn = self.root.ids["homepage"]
        ano_btn.ids["btn_ano"].text = ano
        self.ano_ref = ano



    # mudar para arquivo zerar telas
    def reset_campos_pagamento(self):
        # seta botoes de pagamento
        self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Pagar")
        self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Pagar")
        self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=False)
        self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Pagar")
        # seta label de valores a pagar
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
        if par == "source":
            tela.ids[id].source = dado

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

    def pegar_mes(self):  # RETORNA(DATA DE HOJE[0], MES POR EXTENSO[1], ANO[2] E DICT DE MESES[3])

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

    def file_manager_open(self, user):
        self.user_foto = user
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        if self.user_foto == "foto_user1":
            self.enviar_parametro(pag="homepage", id="foto_perfil_user1", par="source", dado=path)
        elif self.user_foto == "foto_user2":
            self.enviar_parametro(pag="homepage", id="foto_perfil_user2", par="source", dado=path)
        self.salvar_foto_perfil(self.user_foto, path)
        toast(path)

    def salvar_foto_perfil(self, user, caminho):
        print(user, caminho)
        caminho_str = str(caminho).replace("\\", "+")
        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        info = f'{{"{user}": "{caminho_str}"}}'
        requisicao1 = requests.patch(link, data=info)
        requisicao = requisicao1.json()
        print(requisicao)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True


MainApp().run()
