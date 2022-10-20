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

    def zerar_pagamentos(self):
        app = MDApp.get_running_app()
        # seta botoes de pagamento
        app.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=False)
        app.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Pagar")
        app.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=False)
        app.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Pagar")
        app.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=False)
        app.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Pagar")
        # seta label de valores a pagar
        app.enviar_parametro(pag="pagarpage", id="lbl_alg_status", par="text", dado=f"Aluguel: R$0")
        app.enviar_parametro(pag="pagarpage", id="lbl_cond_status", par="text", dado=f"Cond.: R$0")
        app.enviar_parametro(pag="pagarpage", id="lbl_agua_status", par="text", dado=f"Agua: R$0")
