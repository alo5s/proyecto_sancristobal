# AUTOBOT — Automatización de Cobranzas

Bot de escritorio para automatizar el proceso de cobranza en el portal **productores.sancristobal.com.ar**.

## Funcionalidad

1. **Login automático** — Inicia sesión en el portal con credenciales guardadas.
2. **Navegación y filtros** — Accede a Gestión de Cobranzas, aplica filtros por modalidad de pago (EFECTIVO) y configura paginación.
3. **Procesamiento de vencimientos** — Recorre la tabla de clientes y para cada uno:
   - Envía notificación por **correo electrónico** desde el sistema.
   - Envía notificación por **WhatsApp Web** automáticamente.
4. **Generación de reportes** — Guarda resultados en archivos CSV (`reports/`).
5. **Programación automática** — Permite configurar ejecución automática vía **cron** (Linux) en días y hora específicos.
6. **Notificaciones configurables** — Se puede habilitar/deshabilitar envío por correo y WhatsApp, y elegir procesar vencimientos a 7 días y/o 8–15 días.

## Arquitectura

```
proyecto_sancristobal/
├── main.py                    # Punto de entrada (GUI con PySide6)
├── config_manager.py          # Gestión de config.json
├── config.json                # Credenciales y configuración
├── .gitignore                 # Archivos ignorados por git
│
├── bot/
│   ├── browser_manager.py     # Singleton de Playwright, detección de navegador/perfil
│   ├── whatsapp_manager.py    # Envío automático por WhatsApp Web
│   └── paginas/
│       ├── login_manager.py   # Login en el portal
│       └── bot_manager.py     # Orquestación de etapas (filtros, tabla, notificaciones)
│
├── controller/
│   ├── app_controller.py      # Controlador principal (señales UI ↔ worker)
│   └── workers.py             # QThread con cola de tareas para Playwright
│
├── ui/
│   ├── layout/
│   │   ├── layout_login.py    # Pantalla de login
│   │   └── layout_home.py     # Pantalla principal con botón de ejecución
│   └── dialogs/
│       ├── schedule_dialog.py # Configuración de auto-inicio (cron)
│       ├── programacion_dialog.py  # Configuración de notificaciones y vencimientos
│       └── reportes_dialog.py # Visor de reportes CSV
│
└── utils/
    └── cron_helper.py         # Helper para gestionar entradas en crontab
```

## Requisitos

- **Python 3.10+**
- **Playwright** (`pip install playwright`)
- **PySide6** (`pip install PySide6`)
- Un navegador compatible instalado: Chrome, Edge, Brave o Chromium

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

## Uso

```bash
python main.py
```

1. Ingresar credenciales (se guardan en `config.json`).
2. Hacer clic en **ENTRAR** — el bot inicia sesión automáticamente.
3. En la pantalla principal, hacer clic en **EJECUTAR COBRANZA**.
4. El bot procesa clientes y envía notificaciones.

## Configuración

Desde el menú **Configuración** se accede a:
- **Notificaciones** — Habilitar/deshabilitar correo y WhatsApp.
- **Vencimientos** — Elegir procesar 7 días y/o 8–15 días.
- **Auto-inicio** — Programar ejecución automática con cron.

También desde el menú:
- **Mostrar/Ocultar navegador** — Cambia entre modo headless y visible (requiere reinicio).
- **Reportes** — Ver reportes CSV generados.

## Archivos importantes

| Archivo | Propósito |
|---------|-----------|
| `config.json` | Credenciales y configuración de ejecución |
| `reports/*.csv` | Reportes generados tras cada ejecución |
| `session/` | Datos de sesión del navegador (runtime, ignorado por git) |

## Notas

- La sesión de WhatsApp se guarda para evitar escanear QR en cada ejecución.
- El bot detecta automáticamente el navegador instalado (Chrome, Edge, Brave, Chromium).
- Compatible con Windows y Linux.
