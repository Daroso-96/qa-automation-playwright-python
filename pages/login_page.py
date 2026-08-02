from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        self.username_input = page.locator('input[name="username"]')
        self.password_input = page.locator('input[name="password"]')
        self.submit_button = page.locator('button[type="submit"]')

    def abrir(self, url: str) -> None:
        self.page.goto(url)

    def iniciar_sesion(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()