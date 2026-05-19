"""
app_controller.py — Controlador principal de la aplicación
"""

from ui.layout.layout_login import LoginView
from ui.layout.layout_home import HomeView
from controller.workers import SessionWorker

# Colores
MUTED = "#555555"
ERROR = "#e05c5c"


class AppController:
    def __init__(self, window):
        self.window = window
        self.show_browser = True

        # ---------- worker único ----------
        self.worker = SessionWorker(self.show_browser)

        # ---------- señales del worker ----------
        self.worker.login_ok.connect(self.on_login_ok)
        self.worker.login_error.connect(self.on_login_error)
        self.worker.logout_ok.connect(self.on_logout_ok)

        self.worker.automation_ok.connect(self.on_automation_ok)
        self.worker.automation_error.connect(self.on_automation_error)
        self.worker.automation_paused.connect(self.on_automation_paused)

        self.worker.error.connect(self.on_worker_error)
        self.worker.persona_no_encontrada.connect(self.show_persona_no_encontrada)

        # ---------- vista login ----------
        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)
        self.window.setCentralWidget(self.login_view)

    # =================================================
    # CONFIG
    # =================================================
    def set_show_browser(self, value: bool):
        if self.worker:
            self.worker.show_browser = value

    # =================================================
    # LOGIN
    # =================================================
    def start_login(self, user, password):
        # login() ya se encarga de iniciar el thread
        self.worker.login(user, password)

    def on_login_ok(self, user):
        self.home = HomeView(user)

        # 🔴 CONECTAR ERROR AQUÍ (cuando home ya existe)
        self.worker.automation_error.connect(self.home.show_bot_error)

        # 🔹 conectar señales UI → worker
        self.home.logout_requested.connect(self.logout)
        self.home.start_requested.connect(self.worker.start_automation)
        self.home.pause_requested.connect(self.worker.pause_automation)
        self.home.resume_requested.connect(self.worker.resume_automation)
        self.home.stop_requested.connect(self.worker.stop_automation)

        # 🔹 conectar señal poliza_terminada → mostrar alert
        self.worker.poliza_terminada.connect(self.on_poliza_terminada)

        # Cambiar tamaño de ventana para Home (600x420)
        self.window.setFixedSize(600, 420)

        self.window.setCentralWidget(self.home)

    def on_login_error(self, msg):
        self.login_view._set_status(msg, ERROR)
        self.login_view.reset()

    # =================================================
    # LOGOUT
    # =================================================
    def logout(self):
        self.worker.logout()

    def on_logout_ok(self):
        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)

        # Cambiar tamaño de ventana para Login (360x420)
        self.window.setFixedSize(360, 420)

        self.window.setCentralWidget(self.login_view)

    # =================================================
    # AUTOMATION STATUS
    # =================================================
    def on_automation_ok(self, msg):
        # Mostrar en login_view si existe y no hay home
        if hasattr(self, "login_view") and not hasattr(self, "home"):
            self.login_view._set_status(msg, MUTED)
            return

        if not hasattr(self, "home"):
            return

        # mostrar estado
        self.home.status_label.setText(msg)
        self.home.logs.append(msg)

        # si terminó / falló / se detuvo → reset UI
        if (
            "finalizada" in msg
            or "detenida" in msg
            or msg.startswith("❌")
        ):
            self.home.reset_bot_ui()

    def on_automation_paused(self, msg):
        if hasattr(self, "home"):
            self.home.status_label.setText(msg)
            self.home.logs.append(msg)

    def on_poliza_terminada(self, msg):
        if hasattr(self, "home"):
            self.home.show_poliza_alert(msg)
            self.home.show_reportes()

    def on_automation_error(self, msg):
        if hasattr(self, "home"):
            self.home.show_bot_error(msg)

    # =================================================
    # ERRORES CRÍTICOS
    # =================================================
    def on_worker_error(self, msg):
        print("🔥 Worker error:", msg)

        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)
        self.window.setFixedSize(360, 420)
        self.window.setCentralWidget(self.login_view)
        self.login_view._set_status(msg, ERROR)

    def show_persona_no_encontrada(self, data: dict):
        if hasattr(self, "home"):
            self.home.show_persona_no_encontrada(
                data["dni"],
                data["poliza"],
                data["asegurado"]
            )
