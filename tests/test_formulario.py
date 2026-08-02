from config import (
    EVALART_PASSWORD,
    EVALART_URL,
    EVALART_USER,
    validar_configuracion,
)
from pages.form_page import FormPage
from pages.login_page import LoginPage


TOTAL_CICLOS = 10


def test_formulario_exitoso(page):
    validar_configuracion()

    login_page = LoginPage(page)
    form_page = FormPage(page)

    login_page.abrir(EVALART_URL)
    login_page.iniciar_sesion(
        username=EVALART_USER,
        password=EVALART_PASSWORD,
    )

    form_page.esperar_formulario()

    for ciclo_esperado in range(1, TOTAL_CICLOS + 1):
        ciclo_actual = form_page.obtener_numero_ciclo()

        assert ciclo_actual == ciclo_esperado, (
            f"Se esperaba iniciar el ciclo {ciclo_esperado}, "
            f"pero la página muestra el ciclo {ciclo_actual}."
        )

        print(
            f"\n========== CICLO "
            f"{ciclo_actual} DE {TOTAL_CICLOS} =========="
        )

        form_page.resolver_ciclo()
        form_page.enviar()

        form_page.validar_resultado_envio(
            ciclo_anterior=ciclo_actual,
            total_ciclos=TOTAL_CICLOS,
        )

    print(
        f"\nLos {TOTAL_CICLOS} ciclos "
        "fueron completados correctamente."
    )


