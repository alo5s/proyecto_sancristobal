"""
login_manager.py — Manejo de login y guardado de sesión
"""

from config_manager import load_config
from bot.browser_manager import BrowserManager
from bot.paginas.bot_manager import close_tour_popup


class ManagerSession:
    def __init__(self, page):
        self.page = page

    def get_page(self):
        """Devuelve la página actual"""
        return self.page

    def login(self, username, password):
        """Ejecuta login usando credenciales pasadas por parámetro"""
        config = load_config()
        login_url = config.get("login_url", "")

        if not login_url:
            print("ERROR: No se configuró login_url en config.json")
            return False

        try:
            # ✅ ASEGURAR QUE ESTAMOS EN LA PÁGINA DE LOGIN
            current_url = self.page.url
            if "login" not in current_url.lower() and "/auth" not in current_url.lower():
                print(f"[INFO] Navegando a login URL: {login_url}")
                self.page.goto(login_url, wait_until="domcontentloaded")
                print(f"[INFO] URL actual después de navegar: {self.page.url}")
            
            # Esperar campos de login
            print("[INFO] Esperando formulario de login...")
            self.page.wait_for_selector("#signInName", timeout=30000)
            print("✓ Formulario de login detectado")

            # Llenar usuario
            self.page.fill("#signInName", username)
            print("✓ Usuario ingresado")

            # Llenar contraseña
            self.page.fill("#password", password)
            print("✓ Contraseña ingresada")

            # Click en Ingresar
            self.page.click("#next")
            print("✓ Botón Ingresar presionado")

            # Esperar redirección O error
            try:
                self.page.wait_for_url("**/productores.sancristobal.com.ar/inicio", timeout=30000)
                print(f"✓ Login exitoso - URL: {self.page.url}")

                # Guardar sesión
                bm = BrowserManager.get_instance()
                bm.save_session("session.json")
                print("✓ Sesión guardada")

                # Cerrar popup de tour si aparece (llamada directa)
                close_tour_popup(self.page)

                return True

            except Exception as e:
                # Verificar dónde quedó la página
                print(f"Timeout en wait_for_url: {e}")
                print(f"URL actual: {self.page.url}")

                # Verificar si por casualidad ya está en /inicio
                if "/inicio" in self.page.url:
                    print("✓ Login exitoso (detectado por URL actual)")
                    bm = BrowserManager.get_instance()
                    bm.save_session("session.json")
                    return True

                # Verificar error
                error_elem = self.page.query_selector(".error.pageLevel p")
                if error_elem:
                    error_text = error_elem.inner_text()
                    print(f"✗ Error: {error_text}")
                    return False
                else:
                    print("No se pudo verificar el estado del login")
                    return False

        except Exception as e:
            print(f"Error durante login: {e}")
            return False

    def logout(self):
        """Cierra sesión"""
        try:
            self.page.goto("https://productores.sancristobal.com.ar/logout")
            return True
        except Exception as e:
            print(f"Error en logout: {e}")
            return False
