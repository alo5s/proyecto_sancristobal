# BrowserManager.py - Versión sync para Singleton en QThread

import platform
import shutil
import os
from playwright.sync_api import sync_playwright


# ==========================================================
# DETECCIÓN DE NAVEGADOR DEL SISTEMA (Windows + Linux)
# ==========================================================

def detectar_navegador():
    """Detecta el navegador instalado y devuelve (nombre, ruta_ejecutable)."""
    system = platform.system()

    if system == "Windows":
        posibles = [
            ("chrome",   r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            ("chrome",   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            ("msedge",   r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            ("brave",    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
        for nombre, ruta in posibles:
            if os.path.exists(ruta):
                return nombre, ruta

    elif system == "Linux":
        posibles = [
            ("chrome",            "google-chrome"),
            ("msedge",            "microsoft-edge"),
            ("brave",             "brave-browser"),
            ("brave",             "brave-origin-nightly"),
            ("brave",             "brave-origin-beta"),
            ("brave",             "brave"),
            ("chromium",          "chromium"),
            ("chromium-browser",  "chromium-browser"),
        ]
        for nombre, comando in posibles:
            ruta = shutil.which(comando)
            if ruta:
                return nombre, ruta

    return None, None


# ==========================================================
# DETECCIÓN DEL PERFIL REAL DEL SISTEMA
# ==========================================================

def detectar_perfil_sistema(nombre_navegador: str) -> str | None:
    """
    Devuelve la ruta al perfil de usuario real del navegador instalado.
    """
    system = platform.system()
    home = os.path.expanduser("~")

    perfiles = {
        "Windows": {
            "chrome":   os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\User Data"),
            "msedge":   os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\User Data"),
            "brave":    os.path.join(os.environ.get("LOCALAPPDATA", ""), r"BraveSoftware\Brave-Browser\User Data"),
            "chromium": os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Chromium\User Data"),
        },
        "Linux": {
            "chrome":   os.path.join(home, ".config/google-chrome"),
            "msedge":   os.path.join(home, ".config/microsoft-edge"),
            "brave":    os.path.join(home, ".config/BraveSoftware/Brave-Browser"),
            "chromium": os.path.join(home, ".config/chromium"),
            "chromium-browser": os.path.join(home, ".config/chromium"),
        },
    }

    rutas = perfiles.get(system, {})
    ruta = rutas.get(nombre_navegador)

    if ruta and os.path.isdir(ruta):
        return ruta

    return None


# ==========================================================
# BROWSER MANAGER (Singleton Optimizado para QThread)
# ==========================================================

class BrowserManager:
    _instance = None

    def __init__(self):
        self.playwright  = None
        self.browser     = None
        self.context     = None
        self.page        = None
        self._navegador  = None

    # ----------------------------------------------------------
    # SINGLETON
    # ----------------------------------------------------------
    @classmethod
    def get_instance(
        cls,
        headless: bool   = True,
        start_url: str   = None,
        usar_perfil: bool = False,
        session_file: str = None,
    ):
        if cls._instance is None:
            cls._instance = BrowserManager()
            cls._instance._start_browser(headless, start_url, usar_perfil, session_file)
        else:
            # Si ya existe y se pasa una nueva URL, navegar a ella
            if start_url and cls._instance.page:
                try:
                    print(f"[INFO] Navegando a: {start_url}")
                    cls._instance.page.goto(start_url, wait_until="domcontentloaded")
                except Exception as e:
                    print(f"[ERROR] Error navegando a {start_url}: {e}")
        return cls._instance

    # ----------------------------------------------------------
    # INICIO DEL NAVEGADOR
    # ----------------------------------------------------------
    def _start_browser(
        self,
        headless: bool    = True,
        start_url: str    = None,
        usar_perfil: bool = False,
        session_file: str = None,
    ):
        print("[INFO] Detectando navegador del sistema...")
        navegador, ruta = detectar_navegador()

        if not navegador:
            raise Exception(
                "No se encontró un navegador compatible.\n"
                "Instale Chrome, Edge, Brave o Chromium."
            )

        print(f"[INFO] Navegador detectado: {navegador} en {ruta}")
        self._navegador = navegador
        
        print("[INFO] Iniciando Playwright...")
        self.playwright = sync_playwright().start()
        print("[INFO] Playwright iniciado correctamente")

        launch_args = [
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-blink-features=AutomationControlled",
        ]

        if usar_perfil:
            ruta_perfil = detectar_perfil_sistema(navegador)
            if ruta_perfil and os.path.isdir(ruta_perfil):
                print(f"[INFO] Usando perfil del sistema: {ruta_perfil}")
                if navegador in ["chrome", "msedge"]:
                    self.context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=ruta_perfil,
                        channel=navegador,
                        headless=headless,
                        args=launch_args,
                        locale="es-ES",
                        ignore_https_errors=True,
                        accept_downloads=True,
                    )
                else:
                    self.context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=ruta_perfil,
                        executable_path=ruta,
                        headless=headless,
                        args=launch_args,
                        locale="es-ES",
                        ignore_https_errors=True,
                        accept_downloads=True,
                    )
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                if start_url:
                    self.page.goto(start_url, wait_until="domcontentloaded")
                print("[INFO] Navegador iniciado correctamente (perfil del sistema)")
                return

        if navegador in ["chrome", "msedge"]:
            self.browser = self.playwright.chromium.launch(
                channel=navegador,
                headless=headless,
                args=launch_args,
            )
        else:
            self.browser = self.playwright.chromium.launch(
                executable_path=ruta,
                headless=headless,
                args=launch_args,
            )

        context_opts = dict(
            java_script_enabled=True,
            ignore_https_errors=True,
            locale="es-ES",
            accept_downloads=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        if session_file and os.path.exists(session_file):
            print(f"[INFO] Cargando sesión guardada: {session_file}")
            context_opts["storage_state"] = session_file

        self.context = self.browser.new_context(**context_opts)
        self.page = self.context.new_page()

        print("[INFO] Navegador iniciado correctamente (nuevo contexto)")
        
        if start_url:
            self.page.goto(start_url, wait_until="domcontentloaded")

    # ----------------------------------------------------------
    # GUARDAR SESIÓN
    # ----------------------------------------------------------
    def save_session(self, session_file: str = "session.json"):
        if self.browser is None:
            print("[AVISO] En modo perfil del sistema la sesión ya es persistente.")
            return
        self.context.storage_state(path=session_file)
        print(f"[INFO] Sesión guardada en: {session_file}")

    # ----------------------------------------------------------
    # OBTENER PAGE
    # ----------------------------------------------------------
    def get_page(self):
        return self.page

    # ----------------------------------------------------------
    # MINIMIZAR VENTANA
    # ----------------------------------------------------------
    def minimize_window(self):
        try:
            cdp = self.page.context.new_cdp_session(self.page)
            result = cdp.send("Browser.getWindowForTarget")
            cdp.send("Browser.setWindowBounds", {
                "windowId": result["windowId"],
                "bounds": {"windowState": "minimized"}
            })
            print("[INFO] Ventana del navegador minimizada")
        except Exception as e:
            print(f"[INFO] No se pudo minimizar ventana: {e}")

    # ----------------------------------------------------------
    # CERRAR NAVEGADOR
    # ----------------------------------------------------------
    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        finally:
            BrowserManager._instance = None

# =========================================================
# WHATSAPP SESSION MANAGEMENT (Module-level functions)
# =========================================================

def save_whatsapp_session(page, filename: str = "session/whatsapp_session.json"):
    """Guarda las cookies de WhatsApp Web para uso futuro"""
    try:
        import json
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        cookies = page.context.cookies(["https://web.whatsapp.com"])
        with open(filename, "w") as f:
            json.dump(cookies, f)
        print(f"✓ Sesión WhatsApp guardada en {filename}")
        return True
    except Exception as e:
        print(f"Error guardando sesión WhatsApp: {e}")
        return False


def load_whatsapp_session(context, filename: str = "session/whatsapp_session.json"):
    """Carga las cookies de WhatsApp Web si existen"""
    import os
    if os.path.exists(filename):
        try:
            import json
            with open(filename, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print(f"✓ Sesión WhatsApp cargada desde {filename}")
            return True
        except Exception as e:
            print(f"Error cargando sesión WhatsApp: {e}")
            return False
    return False


def load_brave_whatsapp_cookies(profile_path: str = None):
    """
    Lee las cookies de WhatsApp Web desde la base de datos de Brave.
    Evita escanear QR la primera vez si el usuario ya tiene sesión en Brave.
    
    Args:
        profile_path: Ruta al perfil de Brave (ej: ~/.config/BraveSoftware/Brave-Browser/Default)
    
    Returns:
        list: Lista de cookies en formato Playwright, o None si falla
    """
    import os
    import sqlite3
    import json
    
    if profile_path is None:
        home = os.path.expanduser("~")
        profile_path = os.path.join(home, ".config/BraveSoftware/Brave-Browser/Default")
    
    cookies_db = os.path.join(profile_path, "Cookies")
    
    if not os.path.exists(cookies_db):
        print(f"[AVISO] No se encontró base de datos de Brave: {cookies_db}")
        return None
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(cookies_db)
        cursor = conn.cursor()
        
        # Leer cookies de web.whatsapp.com
        cursor.execute(
            "SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite "
            "FROM cookies WHERE host_key LIKE '%whatsapp.com%'"
        )
        
        cookies = []
        import time
        for row in cursor.fetchall():
            host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite = row
            
            # Convertir expires_utc (Windows epoch) a formato UNIX
            expires = (expires_utc / 1000000) - 11644473600 if expires_utc else -1
            
            cookie = {
                "name": name,
                "value": value,
                "domain": host_key,
                "path": path,
                "expires": expires,
                "httpOnly": bool(is_httponly),
                "secure": bool(is_secure),
                "sameSite": ["Strict", "Lax", "None"][samesite] if samesite else "Lax"
            }
            cookies.append(cookie)
        
        conn.close()
        
        if cookies:
            print(f"✓ Cookies de WhatsApp leídas desde Brave: {len(cookies)} cookies")
            return cookies
        else:
            print("[AVISO] No se encontraron cookies de WhatsApp en Brave")
            return None
            
    except Exception as e:
        print(f"Error leyendo cookies de Brave: {e}")
        return None


def convert_brave_cookies_to_playwright(brave_cookies):
    """
    Convierte cookies de Brave al formato de Playwright.
    
    Args:
        brave_cookies: Lista de cookies desde load_brave_whatsapp_cookies()
    
    Returns:
        list: Cookies en formato Playwright
    """
    if not brave_cookies:
        return []
    
    # Las cookies ya vienen en formato compatible
    # Solo ajustamos campos si es necesario
    return brave_cookies
