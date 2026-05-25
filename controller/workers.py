"""
workers.py — Worker principal con QThread para Playwright
"""

from PySide6.QtCore import QThread, Signal
from queue import Queue, Empty
from pathlib import Path


class BotState:
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class SessionWorker(QThread):
    # ---------- señales ----------
    login_ok = Signal(str)
    login_error = Signal(str)
    logout_ok = Signal()

    automation_ok = Signal(str)
    automation_error = Signal(str)
    automation_paused = Signal(str)

    error = Signal(str)

    poliza_terminada = Signal(str)
    persona_no_encontrada = Signal(dict)
    whatsapp_qr_needed = Signal(str)

    # ---------- init ----------
    def __init__(self, show_browser=True):
        super().__init__()
        self.show_browser = show_browser

        self.browser = None
        self.session = None
        self.bot = None

        self.tasks = Queue()
        self._running = True
        self.logged = False

        self.state = BotState.IDLE
        self.current_stage = 1

        # Solo mantener guardado_ubicacion para limpieza de archivos
        self.guardado_ubicacion = None

    # =================================================
    # API PÚBLICA
    # =================================================
    def login(self, user: str, password: str):
        self.tasks.put(("login", user, password))
        if not self.isRunning():
            self.start()

    def logout(self):
        self.tasks.put(("logout",))

    def start_automation(self, data: dict):
        self.tasks.put(("start", data))

    def pause_automation(self):
        self.tasks.put(("pause",))

    def resume_automation(self):
        self.tasks.put(("resume",))

    def stop_automation(self):
        self.tasks.put(("stop",))

    # =================================================
    # THREAD LOOP
    # =================================================
    def run(self):
        try:
            while self._running:
                try:
                    # Espera eficiente con timeout
                    task = self.tasks.get(timeout=0.1)
                    self._handle_task(task)
                except Empty:
                    pass

                self._run_bot_cycle()

        except Exception as e:
            import traceback
            self.error.emit(traceback.format_exc())

    # =================================================
    # TASK HANDLER
    # =================================================
    def _handle_task(self, task):
        action = task[0]

        # ---------- LOGIN ----------
        if action == "login":
            from bot.browser_manager import BrowserManager
            from bot.paginas.login_manager import ManagerSession
            from config_manager import get_settings

            if self.logged:
                return
            _, user, password = task

            # Emitir progreso
            self.automation_ok.emit("🔄 Iniciando navegador...")

            login_url = get_settings().value("login_url", "https://productores.sancristobal.com.ar")

            try:
                if not self.browser:
                    self.browser = BrowserManager.get_instance(
                        headless=not self.show_browser,
                        start_url=login_url
                    )
                    self.session = ManagerSession(self.browser.get_page())
                    self.automation_ok.emit("✓ Navegador iniciado, esperando login...")
                
                # Asegurar que estamos en la página de login
                current_url = self.browser.get_page().url
                if "login" not in current_url.lower() and "/auth" not in current_url.lower():
                    print(f"[INFO] Navegando a: {login_url}")
                    self.browser.get_page().goto(login_url, wait_until="domcontentloaded")
                    
            except Exception as e:
                print(f"[ERROR] Error iniciando navegador: {e}")
                import traceback
                print(traceback.format_exc())
                self.login_error.emit(f"❌ Error iniciando navegador: {e}")
                return

            success = self.session.login(user, password)

            if success:
                self.logged = True
                self.browser.minimize_window()
                self.login_ok.emit(user)
            else:
                self.logged = False

                # Cerrar navegador si falló
                try:
                    if self.browser:
                        self.browser.close()
                except:
                    pass

                self.browser = None
                self.session = None

                self.login_error.emit("❌ Usuario o contraseña incorrectos")

        # ---------- LOGOUT ----------
        elif action == "logout":
            if self.logged and self.session.logout():
                self.logged = False

                # Cerrar navegador completamente
                try:
                    if self.browser:
                        self.browser.close()
                except:
                    pass

                self.browser = None
                self.session = None
                self.bot = None

                self.logout_ok.emit()

        # ---------- START ----------
        elif action == "start":
            if self.logged and self.state == BotState.IDLE:
                _, data = task

                # Solo mantener guardado_ubicacion para limpieza de archivos
                self.guardado_ubicacion = data.get("guardado_ubicacion")

                self.current_stage = 1
                self.state = BotState.RUNNING
                self.automation_ok.emit("▶  Automatización iniciada")

        # ---------- PAUSE ----------
        elif action == "pause":
            if self.state == BotState.RUNNING:
                self.state = BotState.PAUSED
                self.automation_paused.emit(
                    f"⏸  Pausado en etapa {self.current_stage}"
                )

        # ---------- RESUME ----------
        elif action == "resume":
            if self.state == BotState.PAUSED:
                self.state = BotState.RUNNING
                self.automation_ok.emit(
                    f"▶  Reanudando desde etapa {self.current_stage}"
                )

        # ---------- STOP ----------
        elif action == "stop":
            self._reset_bot("⏹  Automatización detenida")

    # =================================================
    # BOT FLOW
    # =================================================
    def _run_bot_cycle(self):
        if self.state != BotState.RUNNING:
            return

        if not self.bot:
            from bot.paginas.bot_manager import ManagerBot
            self.bot = ManagerBot(self.session.get_page())
            self.bot._emit_qr_needed = self.whatsapp_qr_needed.emit

        # ---------- ETAPA 1 ----------
        if self.current_stage == 1:
            if self.bot.etapa_1():
                self.current_stage = 2
                self.automation_ok.emit("✅ Etapa 1 completada")
            else:
                self._fail("Error en Etapa 1")

        # ---------- ETAPA 2 ----------
        elif self.current_stage == 2:
            if self.bot.etapa_2():
                self.bot.navegar_a_inicio()
                self.poliza_terminada.emit("✅ El bot ha finalizado")
                self._reset_bot("✅ Bot finalizado")
            else:
                self._fail("Error en Etapa 2")

    # =================================================
    # Borra todos los archivos con ciertas extensiones dentro de la carpeta indicada.
    # =================================================
    def limpiar_archivos(self, carpeta: str, extensiones=None):
        if extensiones is None:
            extensiones = ['pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg']

        ruta = Path(carpeta)
        if not ruta.exists() or not ruta.is_dir():
            print(f"⚠️ La carpeta no existe: {carpeta}")
            return

        for ext in extensiones:
            for archivo in ruta.glob(f'*.{ext}'):
                try:
                    archivo.unlink()
                    print(f"🗑  Borrado: {archivo}")
                except Exception as e:
                    print(f"❌ Error al borrar {archivo}: {e}")

    # =================================================
    # RESET / FAIL
    # =================================================
    def _reset_bot(self, msg, finished=False):
        try:
            if self.bot:
                self.bot.detener()
        except Exception:
            pass

        self.state = BotState.IDLE
        self.current_stage = 1
        self.bot = None
        self.automation_ok.emit(msg)

        # SOLO si terminó correctamente
        if finished:
            self.poliza_terminada.emit("🎉 ¡Póliza terminada!")

            if self.guardado_ubicacion:
                self.limpiar_archivos(self.guardado_ubicacion)

    def _fail(self, msg):
        import traceback

        error_detalle = traceback.format_exc()

        print("❌ ERROR CRÍTICO:")
        print(error_detalle)

        self.automation_error.emit(error_detalle)

        self._detener()

        try:
            if self.browser:
                self.browser.close()
        except:
            pass
        self.browser = None
        self.session = None
        self.logged = False
        self.error.emit(f"Error crítico: {msg} — Navegador cerrado")

    def _detener(self):
        self.state = BotState.IDLE
        self.current_stage = 1

        if self.bot:
            try:
                self.bot.detener()
            except:
                pass

        self.bot = None
