# AGENTS.md

## Stack
- Python 3.10+ with **PySide6** (GUI) and **playwright** (browser automation)
- No `requirements.txt`, no `pyproject.toml` — install with `pip install PySide6 playwright`

## Commands
- **Run**: `python main.py` (entrypoint: `main.py:1`)
- **No tests, linters, or typecheckers** exist — no verification commands

## Architecture
- **MVC-like**: `main.py` (QMainWindow) → `AppController` → `SessionWorker` (QThread) → `ManagerBot` (6 stages)
- `SessionWorker` runs a Queue-based task loop inside QThread (poll every 0.1s)
- `BrowserManager` is a **singleton** shared across threads
- Window resizes: Login = 360×420, Home = 600×420
- On automation failure (`_fail` in `workers.py`), browser auto-closes and UI returns to login (360×420)

## Config
- `QSettings("SanCristobal", "AUTOBOT")` via `config_manager.get_settings()` — cross-platform, no `config.json`
- Keys: `username`, `password`, `login_url`, `headless`, `schedule` (enabled/days/time), `modalidades_pago`, `notif_correo`, `notif_whapp`, `venc_7dias`, `venc_8dias`
- **Headless toggle** requires app restart (message shown to user)
- `modalidades_pago` defaults to `[]` — user must configure via Programación dialog before running etapa 1

## Bot Flow (6 stages)
1. Navigate to gestión de cobranzas, apply filters for each modalidad in `modalidades_pago` config, set pagination to 100
2. Read `venc_7dias`/`venc_8dias` config, select date range, iterate table rows, send notifications. Reports include per-client EFECTIVO/DÉBITO DIRECTO/TARJETA DE CRÉDITO columns (read from `payment-method-column` in HTML, not from global config). After completion, `ReportesDialog` opens automatically.
3–6. **Stubs/Inactivas** — Tras etapa 2 el bot navega a `/inicio`, muestra alerta de finalización y resetea el estado. Las etapas 3-6 existen como stubs pero no se ejecutan (métodos para 4-6 existen; etapa 3 **no existe** — `workers.py:236` llamaba a `self.bot.etapa_3()` ya reemplazado)

## Two Config Dialogs (confusing names)
- Menu **Configuración** → `ScheduleDialog` (cron scheduling, uses `utils/cron_helper.py`)
- Home button **Programación** → `ProgramacionDialog` (notifications: correo/whapp + vencimientos: 7dias/8dias + modalidades de pago: EFECTIVO/DÉBITO DIRECTO/TARJETA DE CRÉDITO)

## Non-obvious
- **No virtualenv committed** — `env/` exists but is a standard venv; use `source env/bin/activate` if present
- `close_tour_popup()` is defined in `bot/paginas/bot_manager.py` but also called from `login_manager.py`
- WhatsApp session persists to `session/whatsapp_session.json` to skip QR re-scan
- Cron day conversion: Python 0=Monday → cron 0=Sunday (see `utils/cron_helper.py:88`)
- Reports go to `reports/*.csv` with timestamp (`nombre_YYYYMMDD_HHMMSS.csv`) to avoid overwrites (gitignored), sessions go to `session/` (gitignored)
- Browser auto-detection: Chrome > Edge > Brave > Chromium (Linux & Windows)
- Reportes dialog: click any CSV entry to open with system default app; has "Abrir Ubicación" button to open the reports folder in file manager. Uses `os.path.abspath()` to fix xdg-open relative path issue.
- All hardcoded colors: `#f0f0f0` bg, `#2b6de6` accent, `#555555` muted/border
