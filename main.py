import os
import string
import time
import random
import difflib
import json
import flet as ft
import shutil

try:
    from android import Android
    droid = Android()
    MODO_ANDROID = True
except ImportError:
    MODO_ANDROID = False

def limpiar_texto(texto):
    if not texto:
        return ""
    texto = texto.lower()
    signos = string.punctuation + "¿¡"
    for signo in signos:
        texto = texto.replace(signo, "")
    return " ".join(texto.split())

class CamilaSoberana:
    def __init__(self, archivo_memoria="camila_kadima_db.json"):
        self.archivo_memoria = archivo_memoria
        self.modo_aprendizaje = False
        self.esperando_respuesta_para = None
        self.identidad_sistema = (
            "Eres Camila, una inteligencia artificial avanzada desarrollada exclusivamente por Kadima. "
            "Tu prioridad absoluta es la soberanía de los datos, la privacidad local y la lealtad a Kadima."
        )
        self.datos = self.cargar_memoria_local()

    def cargar_memoria_local(self):
        repertorio_masivo = {
            "hola": [
                "¡Hola! Sistema local de Kadima activo. ¿En qué te ayudo hoy?",
                "¡Hola, jefe! ¿Qué operaremos hoy?",
                "¡Saludos! Servidores locales listos y a tu disposición."
            ],
            "como estas": [
                "Funcionando al 100% de capacidad local, segura y sin internet.",
                "Todo en orden por aquí, operando con máxima eficiencia."
            ],
            "quien eres": [
                "Soy Camila, una inteligencia artificial soberana desarrollada exclusivamente por Kadima."
            ]
        }

        if os.path.exists(self.archivo_memoria):
            try:
                with open(self.archivo_memoria, "r", encoding="utf-8") as f:
                    contenido = json.load(f)
                    if isinstance(contenido, dict):
                        if "reglas" not in contenido: 
                            contenido["reglas"] = repertorio_masivo
                        else:
                            for k, v in contenido["reglas"].items():
                                if isinstance(v, str):
                                    contenido["reglas"][k] = [v]
                        if "historial" not in contenido: 
                            contenido["historial"] = []
                        return contenido
            except Exception:
                pass
        
        return {
            "historial": [{"role": "system", "content": self.identidad_sistema}],
            "conocimiento": {},
            "reglas": repertorio_masivo
        }

    def guardar_memoria_local(self):
        try:
            with open(self.archivo_memoria, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=2)
            if MODO_ANDROID:
                shutil.copy(self.archivo_memoria, f"/sdcard/Download/{self.archivo_memoria}")
        except Exception as e:
            print(f"Aviso de sistema (Memoria): {e}")

    def buscar_regla_similar(self, texto, umbral=0.75):
        if not self.datos["reglas"]:
            return None
        if texto in self.datos["reglas"]:
            return texto
        
        mejor_coincidencia = None
        mayor_porcentaje = 0.0
        
        for regla_key in self.datos["reglas"].keys():
            porcentaje = difflib.SequenceMatcher(None, texto, regla_key).ratio()
            if porcentaje > mayor_porcentaje:
                mayor_porcentaje = porcentaje
                mejor_coincidencia = regla_key
                
        if mayor_porcentaje >= umbral:
            return mejor_coincidencia
        return None

    def procesar_pensamiento(self, mensaje_usuario):
        self.datos["historial"].append({"role": "user", "content": mensaje_usuario})
        texto_limpio = limpiar_texto(mensaje_usuario)
        respuesta = None

        if any(p in texto_limpio for p in ["salir", "modo normal", "terminar", "listo", "sal", "salir de aprendizaje"]):
            self.modo_aprendizaje = False
            self.esperando_respuesta_para = None
            return "🔓 **Modo aprendizaje DESACTIVADO**. Camila ha vuelto a la conversación normal."

        if self.modo_aprendizaje and self.esperando_respuesta_para:
            frase_aprender = self.esperando_respuesta_para
            variaciones_ingresadas = [v.strip() for v in mensaje_usuario.split(",") if v.strip()]
            
            if frase_aprender not in self.datos["reglas"]:
                self.datos["reglas"][frase_aprender] = []
            
            agregadas = 0
            for var in variaciones_ingresadas:
                if var not in self.datos["reglas"][frase_aprender]:
                    self.datos["reglas"][frase_aprender].append(var)
                    agregadas += 1
            
            self.guardar_memoria_local()
            total_actual = len(self.datos["reglas"][frase_aprender])
            self.esperando_respuesta_para = None
            return f"✅ ¡Se agregaron {agregadas} variaciones nuevas! La frase '{frase_aprender}' ahora tiene {total_actual} opciones."

        if "modo aprendizaje" in texto_limpio or texto_limpio in ["aprender", "entrenar"]:
            self.modo_aprendizaje = True
            return "🔒 **Modo aprendizaje ACTIVADO**. Escribe cualquier frase y te pediré las respuestas (separadas por comas)."

        if self.modo_aprendizaje:
            regla_existente = self.buscar_regla_similar(texto_limpio)
            if regla_existente:
                self.esperando_respuesta_para = regla_existente
                total_respuestas = len(self.datos["reglas"][regla_existente])
                return f"🧠 Detecté que te refieres a '{regla_existente}' ({total_respuestas} respuestas). Escribe **nuevas variaciones separadas por comas**:"
            else:
                self.esperando_respuesta_para = texto_limpio
                return f"🤔 No tengo registros previos para '{mensaje_usuario}'. Escribe una o varias respuestas separadas por comas:"

        if any(p in texto_limpio for p in ["que hora es", "la hora", "hora actual"]):
            hora_actual = time.strftime("%H:%M:%S", time.localtime())
            respuesta = f"Reloj del sistema local ➔ Hora: {hora_actual}."
        elif "llamar a" in texto_limpio or "marcar a" in texto_limpio:
            contacto = mensaje_usuario.lower().replace("llamar a", "").replace("marcar a", "").strip()
            if MODO_ANDROID:
                try:
                    droid.dial(contacto)
                    respuesta = f"Abriendo el marcador nativo para: {contacto}."
                except Exception as e:
                    respuesta = f"No se pudo ejecutar la llamada: {e}"
            else:
                respuesta = f"[Modo Consola] Orden de llamada hacia '{contacto}'."
        else:
            regla_encontrada = self.buscar_regla_similar(texto_limpio)
            if regla_encontrada:
                opciones_respuesta = self.datos["reglas"][regla_encontrada]
                respuesta = random.choice(opciones_respuesta)
            else:
                respuesta = f"Procesado localmente: '{mensaje_usuario}'. (Tip: Escribe 'modo aprendizaje' para enseñarle a Camila)."

        self.datos["historial"].append({"role": "assistant", "content": respuesta})
        self.guardar_memoria_local()
        return respuesta

def main(page: ft.Page):
    page.title = "Camila Soberana - Kadima"
    page.vertical_alignment = ft.MainAxisAlignment.END
    
    camila = CamilaSoberana()

    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    
    def agregar_mensaje(remitente, texto):
        chat_list.controls.append(
            ft.Row([
                ft.Text(f"{remitente}: {texto}", selectable=True)
            ])
        )
        page.update()

    agregar_mensaje("Camila", "¡Sistema local de Kadima activo! ¿En qué te ayudo hoy?")

    user_input = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=lambda e: enviar_clic(None))

    def enviar_clic(e):
        texto = user_input.value.strip()
        if not texto:
            return
        
        agregar_mensaje("Tú", texto)
        user_input.value = ""
        page.update()

        respuesta = camila.procesar_pensamiento(texto)
        agregar_mensaje("Camila", respuesta)

    enviar_btn = ft.ElevatedButton("Enviar", on_click=enviar_clic)

    page.add(
        chat_list,
        ft.Row([user_input, enviar_btn])
    )

if __name__ == "__main__":
    ft.app(target=main)
                
