import ast
import operator
import re
from datetime import datetime, timedelta

from playwright.sync_api import Page


class FormPage:
  
    OPERADORES = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def __init__(self, page: Page):
        self.page = page

        
        self.radios = page.locator('input[name="radio"]')
        self.fecha_input = page.locator('input[name="date"]')
        self.textarea = page.locator('textarea[name="text"]')
        self.checkboxes = page.locator('input[name="checkbox"]')
        self.boton_enviar = page.locator('button[type="submit"]')

        
        self.mensaje_error = page.get_by_text(
            "Ha cometido un error, intente de nuevo",
            exact=True,
        )

       
        self.enunciado_operacion = (
            self.radios
            .first
            .locator(
                "xpath=ancestor::div[contains(@class,'bg-white')][1]"
            )
            .locator("p")
            .nth(1)
        )

       
        self.enunciado_fecha = (
            self.fecha_input
            .locator(
                "xpath=ancestor::div[contains(@class,'bg-white')][1]"
            )
            .locator("p")
            .first
        )

        
        self.enunciado_texto = (
            self.textarea
            .locator(
                "xpath=ancestor::div[contains(@class,'bg-white')][1]"
            )
            .locator("p")
            .first
        )

        
        self.enunciado_multiplos = (
            self.checkboxes
            .first
            .locator(
                "xpath=ancestor::div[contains(@class,'bg-white')][1]"
            )
            .locator("p")
            .first
        )



    def _evaluar_expresion(self, expresion: str) -> int | float:
       

        def evaluar_nodo(nodo):
            if isinstance(nodo, ast.Expression):
                return evaluar_nodo(nodo.body)

            if isinstance(nodo, ast.Constant):
                if not isinstance(nodo.value, (int, float)):
                    raise ValueError(
                        "La expresión contiene un valor no permitido."
                    )

                return nodo.value

            if isinstance(nodo, ast.BinOp):
                tipo_operador = type(nodo.op)

                if tipo_operador not in self.OPERADORES:
                    raise ValueError(
                        f"Operador no permitido: {tipo_operador}"
                    )

                izquierda = evaluar_nodo(nodo.left)
                derecha = evaluar_nodo(nodo.right)

                return self.OPERADORES[tipo_operador](
                    izquierda,
                    derecha,
                )

            if isinstance(nodo, ast.UnaryOp):
                tipo_operador = type(nodo.op)

                if tipo_operador not in self.OPERADORES:
                    raise ValueError(
                        f"Operador unario no permitido: {tipo_operador}"
                    )

                return self.OPERADORES[tipo_operador](
                    evaluar_nodo(nodo.operand)
                )

            raise ValueError(
                f"Elemento no permitido: {type(nodo)}"
            )

        arbol = ast.parse(expresion, mode="eval")
        return evaluar_nodo(arbol)

    def _obtener_resultado_operacion(self) -> int | float:
        

        texto = self.enunciado_operacion.inner_text().strip()

        expresion = texto.replace("=?", "").strip()
        resultado = self._evaluar_expresion(expresion)

        if isinstance(resultado, float) and resultado.is_integer():
            resultado = int(resultado)

        print(f"Operación: {expresion}")
        print(f"Resultado correcto: {resultado}")

        return resultado

    def resolver_operacion(self) -> None:
        resultado = self._obtener_resultado_operacion()

        radio_correcto = self.page.locator(
            f'input[name="radio"][value="{resultado}"]'
        )

        if radio_correcto.count() != 1:
            raise AssertionError(
                "No se encontró exactamente una opción "
                f"con el resultado {resultado}."
            )

        radio_correcto.check()

        assert radio_correcto.is_checked(), (
            f"No se logró marcar la respuesta {resultado}."
        )

    def responder_operacion_incorrectamente(self) -> None:
       

        resultado_correcto = self._obtener_resultado_operacion()

        for indice in range(self.radios.count()):
            radio = self.radios.nth(indice)
            valor = radio.get_attribute("value")

            if valor is None:
                continue

            if valor != str(resultado_correcto):
                radio.check()

                assert radio.is_checked(), (
                    "No se pudo seleccionar la respuesta incorrecta."
                )

                print(
                    f"Respuesta correcta: {resultado_correcto}"
                )
                print(
                    f"Respuesta incorrecta seleccionada: {valor}"
                )

                return

        raise AssertionError(
            "No se encontró una opción incorrecta disponible."
        )



    def resolver_fecha(self) -> None:
        texto = self.enunciado_fecha.inner_text().strip()

        dias_match = re.search(
            r"(\d+)\s+d[ií]as",
            texto,
            re.IGNORECASE,
        )

        fecha_match = re.search(
            r"(\d{2}/\d{2}/\d{4})",
            texto,
        )

        if not dias_match or not fecha_match:
            raise ValueError(
                f"No se pudo interpretar la pregunta de fecha: {texto}"
            )

        cantidad_dias = int(dias_match.group(1))
        fecha_base_texto = fecha_match.group(1)

        fecha_base = datetime.strptime(
            fecha_base_texto,
            "%d/%m/%Y",
        )

        if "antes" in texto.lower():
            fecha_resultado = fecha_base - timedelta(
                days=cantidad_dias
            )
        else:
            fecha_resultado = fecha_base + timedelta(
                days=cantidad_dias
            )

        fecha_para_input = fecha_resultado.strftime("%Y-%m-%d")

        print(f"Pregunta fecha: {texto}")
        print(f"Fecha calculada: {fecha_para_input}")

        self.fecha_input.fill(fecha_para_input)

        valor_actual = self.fecha_input.input_value()

        assert valor_actual == fecha_para_input, (
            "La fecha no se escribió correctamente. "
            f"Esperada: {fecha_para_input}. "
            f"Actual: {valor_actual}."
        )

 

    def resolver_texto(self) -> None:
        texto = self.enunciado_texto.inner_text().strip()

        coincidencia = re.search(
            r'Escriba\s+(\d+)\s+veces\s+la\s+letra\s+'
            r'["“”\'](.{1})["“”\']',
            texto,
            re.IGNORECASE,
        )

        if not coincidencia:
            raise ValueError(
                f"No se pudo interpretar la pregunta de texto: {texto}"
            )

        cantidad = int(coincidencia.group(1))
        letra = coincidencia.group(2)

        resultado = letra * cantidad

        print(f"Letra: {letra}")
        print(f"Cantidad: {cantidad}")
        print(f"Longitud generada: {len(resultado)}")

        self.textarea.fill(resultado)

        valor_actual = self.textarea.input_value()

        assert valor_actual == resultado, (
            "El texto generado no coincide con el esperado. "
            f"Esperados: {len(resultado)} caracteres. "
            f"Actuales: {len(valor_actual)} caracteres."
        )

   

    def resolver_multiplos(self) -> None:
        texto = self.enunciado_multiplos.inner_text().strip()

        divisor_match = re.search(
            r"m[uú]ltiplos\s+de\s+(\d+)",
            texto,
            re.IGNORECASE,
        )

        if not divisor_match:
            raise ValueError(
                f"No se pudo obtener el divisor desde: {texto}"
            )

        divisor = int(divisor_match.group(1))
        seleccionados = []

        for indice in range(self.checkboxes.count()):
            checkbox = self.checkboxes.nth(indice)
            valor = checkbox.get_attribute("value")

            if valor is None:
                raise ValueError(
                    f"El checkbox de índice {indice} no tiene value."
                )

            numero = int(valor)
            es_multiplo = numero % divisor == 0

            if es_multiplo:
                checkbox.check()
                seleccionados.append(numero)

                assert checkbox.is_checked(), (
                    f"No se logró marcar el múltiplo {numero}."
                )

            else:
                assert not checkbox.is_checked(), (
                    f"El número {numero} quedó marcado, "
                    f"pero no es múltiplo de {divisor}."
                )

        print(f"Divisor: {divisor}")
        print(f"Seleccionados: {seleccionados}")

    

    def resolver_ciclo(self) -> None:
        

        self.resolver_operacion()
        self.resolver_fecha()
        self.resolver_texto()
        self.resolver_multiplos()

    def enviar(self) -> None:
       

        self.boton_enviar.click()
        self.page.wait_for_load_state("domcontentloaded")

    def esperar_formulario(self) -> None:
        

        self.fecha_input.wait_for(
            state="visible",
            timeout=10000,
        )

   

    def obtener_numero_ciclo(self) -> int:
        texto = self.page.get_by_text(
            re.compile(r"Se encuentra en el ciclo"),
            exact=False,
        ).inner_text()

        coincidencia = re.search(
            r"ciclo\s+(\d+)\s+de\s+10",
            texto,
            re.IGNORECASE,
        )

        if not coincidencia:
            raise ValueError(
                f"No se pudo obtener el ciclo desde: {texto}"
            )

        return int(coincidencia.group(1))

    def validar_resultado_envio(
        self,
        ciclo_anterior: int,
        total_ciclos: int = 10,
    ) -> None:
       

        if self.mensaje_error.is_visible():
            ciclo_actual = self.obtener_numero_ciclo()

            raise AssertionError(
                "La plataforma rechazó las respuestas y mostró: "
                "'Ha cometido un error, intente de nuevo'. "
                f"El error ocurrió al enviar el ciclo {ciclo_anterior}. "
                f"La aplicación quedó en el ciclo {ciclo_actual}."
            )

        if ciclo_anterior < total_ciclos:
            ciclo_actual = self.obtener_numero_ciclo()
            ciclo_esperado = ciclo_anterior + 1

            assert ciclo_actual == ciclo_esperado, (
                "El formulario no avanzó correctamente. "
                f"Se esperaba el ciclo {ciclo_esperado}, "
                f"pero aparece el ciclo {ciclo_actual}."
            )


    def validar_error_visible(self) -> None:
        

        self.mensaje_error.wait_for(
            state="visible",
            timeout=10000,
        )

        mensaje_actual = self.mensaje_error.inner_text().strip()
        mensaje_esperado = "Ha cometido un error, intente de nuevo"

        assert mensaje_actual == mensaje_esperado, (
            "El mensaje de error no coincide. "
            f"Esperado: '{mensaje_esperado}'. "
            f"Actual: '{mensaje_actual}'."
        )

    def validar_reinicio_en_ciclo_uno(self) -> None:
       

        ciclo_actual = self.obtener_numero_ciclo()

        assert ciclo_actual == 1, (
            "Después del error se esperaba el ciclo 1, "
            f"pero aparece el ciclo {ciclo_actual}."
        )

    def validar_formulario_limpio(self) -> None:
      

        radios_marcados = self.page.locator(
            'input[name="radio"]:checked'
        )

        checkboxes_marcados = self.page.locator(
            'input[name="checkbox"]:checked'
        )

        assert radios_marcados.count() == 0, (
            "Después del error quedó un radio seleccionado."
        )

        valor_fecha = self.fecha_input.input_value()

        assert valor_fecha == "", (
            "Después del error el campo de fecha no quedó vacío. "
            f"Valor encontrado: '{valor_fecha}'."
        )

        valor_texto = self.textarea.input_value()

        assert valor_texto == "", (
            "Después del error el textarea no quedó vacío. "
            f"Longitud encontrada: {len(valor_texto)}."
        )

        assert checkboxes_marcados.count() == 0, (
            "Después del error quedaron checkboxes seleccionados."
        )

    def validar_comportamiento_negativo(self) -> None:
       

        self.validar_error_visible()
        self.validar_reinicio_en_ciclo_uno()
        self.validar_formulario_limpio()