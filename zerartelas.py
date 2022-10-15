from kivymd.app import MDApp

class ZerarTelas():

    def zerar_telapagar(self):
        app = MDApp.get_running_app()

        app.enviar_parametro(pag="pagarpage", id="input_desc", par="text", dado="")
        app.enviar_parametro(pag="pagarpage", id="input_valor", par="text", dado="")
        app.enviar_parametro(pag="pagarpage", id="input_data", par="text", dado="")
        #app.enviar_parametro(pag="pagarpage", id="check_divida", par="active", dado=False)

    def zerar_telaredefinir(self):
        app = MDApp.get_running_app()

        aviso = "Um email será enviado para redefinição de senha, redefina sua senha e faça login novamente!"
        app.enviar_parametro(pag="redefinirsenha", id="email_input", par="text", dado="")
        app.enviar_parametro(pag="redefinirsenha", id="lbl_aviso", par="text", dado=aviso)
        app.enviar_parametro(pag="redefinirsenha", id="lbl_aviso", par="color", dado=(1, 1, 1, 1))

    def zerar_telalogin(self):
        app = MDApp.get_running_app()

        aviso = "Um email será enviado para redefinição de senha, redefina sua senha e faça login novamente!"
        app.enviar_parametro(pag="loginpage", id="email_input", par="text", dado="")
        app.enviar_parametro(pag="loginpage", id="senha_input", par="text", dado="")
        app.enviar_parametro(pag="loginpage", id="mensagem_login", par="text", dado="Faça seu login")
        app.enviar_parametro(pag="loginpage", id="mensagem_login", par="color", dado=(1, 1, 1, 1))


