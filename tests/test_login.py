from config import (
    EVALART_PASSWORD,
    EVALART_URL,
    EVALART_USER,
    validar_configuracion,
)

from pages.login_page import LoginPage

def test_login_exitoso(page):
    validar_configuracion()

    login_page = LoginPage(page)

    login_page.abrir(EVALART_URL)
    login_page.iniciar_sesion(
        username=EVALART_USER,
        password=EVALART_PASSWORD
    )

    
    page.get_by_text("Ciclos").wait_for()

    assert page.get_by_text("Ciclos").is_visible()