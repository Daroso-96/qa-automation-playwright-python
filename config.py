import os

from dotenv import load_dotenv


load_dotenv()

EVALART_URL = os.getenv("EVALART_URL")
EVALART_USER = os.getenv("EVALART_USER")
EVALART_PASSWORD = os.getenv("EVALART_PASSWORD")


def validar_configuracion() -> None:
    variables = {
        "EVALART_URL": EVALART_URL,
        "EVALART_USER": EVALART_USER,
        "EVALART_PASSWORD": EVALART_PASSWORD,
    }

    faltantes = [
        nombre
        for nombre, valor in variables.items()
        if not valor
    ]

    if faltantes:
        raise ValueError(
            "Faltan variables de entorno: "
            + ", ".join(faltantes)
        )