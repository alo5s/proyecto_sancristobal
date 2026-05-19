# AUTOBOT — Automatización de Cobranzas

Bot de escritorio para automatizar el proceso de cobranza en el portal **productores.sancristobal.com.ar**.

## Funcionalidad

1. **Login automático** — Inicia sesión en el portal con credenciales guardadas.
2. **Navegación y filtros** — Accede a Gestión de Cobranzas, aplica filtros por modalidad de pago (EFECTIVO/DBITO DIRECTO/TARJETA DE CRDITO) y configura paginacin.
3. **Procesamiento de vencimientos** — Recorre la tabla de clientes y para cada uno:
   - Enva notificacin por **correo electrnico** desde el sistema.
   - Enva notificacin por **WhatsApp Web** automticamente.
4. **Generacin de reportes** — Guarda resultados en archivos CSV con timestamp (`reports/notificaciones_*_YYYYMMDD_HHMMSS.csv`). Cada cliente incluye columna de su mtodo de pago real (EFECTIVO/DBITO DIRECTO/TARJETA DE CRDITO).
5. **Visor de reportes** — Al finalizar el bot, se abre automticamente el dialogo de reportes. Se puede hacer clic en cualquier CSV para abrirlo y hay un botn "Abrir Ubicacin" para abrir la carpeta en el explorador de archivos.
6. **Programacin automtica** — Permite configurar ejecucin automtica va **cron** (Linux) en das y hora especficos.
7. **Notificaciones configurables** — Se puede habilitar/deshabilitar envo por correo y WhatsApp, y elegir procesar vencimientos a 7 das y/o 8-15 das.
8. **Sistema de licencias** — Control de uso del programa:
   - Primera ejecucin: 1 da de prueba automtico.
   - Al vencer: se deshabilita el botn "Ejecutar".
   - **Menu Licencias**: muestra estado, fecha de vencimiento y permite renovar con clave.
   - Las claves se generan con una herramienta externa (HMAC-SHA256 + Base64).

## Arquitectura

```
proyecto_sancristobal/
├── main.py                    # Punto de entrada (GUI con PySide6)
├── config_manager.py          # Gestin de configuracin (QSettings)
├── .gitignore                 # Archivos ignorados por git
├── AGENTS.md                  # Instrucciones para IA (no subir a GitHub)
├── README.md                  # Este archivo
│
├── bot/
│   ├── browser_manager.py     # Singleton de Playwright, deteccin de navegador/perfil
│   ├── whatsapp_manager.py    # Envo automtico por WhatsApp Web
│   └── paginas/
│       ├── login_manager.py   # Login en el portal
│       └── bot_manager.py     # Orquestacin de etapas (filtros, tabla, notificaciones)
│
├── controller/
│   ├── app_controller.py      # Controlador principal (seales UI worker)
│   └── workers.py             # QThread con cola de tareas para Playwright
│
├── ui/
│   ├── layout/
│   │   ├── layout_login.py    # Pantalla de login
│   │   └── layout_home.py     # Pantalla principal con botn de ejecucin
│   └── dialogs/
│       ├── schedule_dialog.py     # Configuracin de auto-inicio (cron)
│       ├── programacion_dialog.py # Configuracin de notificaciones y vencimientos
│       ├── reportes_dialog.py     # Visor de reportes CSV
│       └── license_dialog.py      # Estado y renovacin de licencia
│
├── utils/
│   ├── cron_helper.py         # Helper para gestionar entradas en crontab
│   └── license_manager.py     # Validacin de licencias (HMAC-SHA256)
│
└── tools/
    └── generar_licencia.py    # Generador de claves de licencia (herramienta aparte)
```

## Requisitos

- **Python 3.10+**
- **Playwright** (`pip install playwright`)
- **PySide6** (`pip install PySide6`)
- Un navegador compatible instalado: Chrome, Edge, Brave o Chromium

## Instalacin

```bash
pip install PySide6 playwright
playwright install chromium
```

## Uso

```bash
python main.py
```

1. Ingresar credenciales (se guardan en QSettings).
2. Hacer clic en **ENTRAR** el bot inicia sesin automticamente.
3. En la pantalla principal, hacer clic en **EJECUTAR COBRANZA**.
4. El bot procesa clientes y enva notificaciones.
5. Al finalizar, se abre automticamente el visor de reportes.

## Sistema de Licencias

El programa incluye control de licencias para limitar el uso por tiempo.

### Primer inicio
- Automticamente asigna **1 da de prueba**.
- El botn "Ejecutar" se deshabilita al vencer la licencia.

### Ver estado
- **Menu Licencias** en la barra superior.
- Muestra: fecha de vencimiento, das restantes, estado (vigente/vencida).

### Renovar
1. Generar una clave con el generador externo:
   ```bash
   python tools/generar_licencia.py --expire 2027-12-31 --machine 1
   ```
2. En el programa: **Menu Licencias** pegar la clave y clickear **Renovar**.

### Formato de la clave
- Se compone de: `fecha:ID_maquina:firma_HMAC` codificado en Base64.
- Ejemplo: `MjAyNy0wNS0xOToxOmY5ZmI3NGQxM2M4OWZkYzk`
- Secret interno: `SanCristobalLic2026` (cambiable en `utils/license_manager.py`).

## Configuracin

Desde el men **Configuracin** se accede a:
- **Auto-inicio** Programar ejecucin automtica con cron.

Desde la pantalla principal, botn **Programacin**:
- **Notificaciones** Habilitar/deshabilitar correo y WhatsApp.
- **Vencimientos** Elegir procesar 7 das y/o 8-15 das.
- **Modalidades de pago** Elegir qu modalidades procesar (EFECTIVO, DBITO DIRECTO, TARJETA DE CRDITO).

Tambin desde el men:
- **Mostrar/Ocultar navegador** Cambia entre modo headless y visible (requiere reinicio).
- **Licencias** Ver estado de licencia y renovar.

## Archivos importantes

| Archivo | Propsito |
|---------|-----------|
| `config.json` | (Ignorado por git) Credenciales y configuracin de ejecucin |
| `reports/*.csv` | Reportes generados tras cada ejecucin (con timestamp) |
| `session/` | Datos de sesin del navegador (runtime, ignorado por git) |
| `utils/license_manager.py` | Sistema de licencias (HMAC-SHA256) |
| `tools/generar_licencia.py` | Generador de claves de licencia (tool externa) |

## Notas

- La sesin de WhatsApp se guarda en `session/whatsapp_session.json` para evitar escanear QR en cada ejecucin.
- El bot detecta automticamente el navegador instalado (Chrome, Edge, Brave, Chromium).
- Compatible con Windows y Linux.
- **config.json** est en `.gitignore` para no subir credenciales a GitHub.
- Los reportes nunca se sobrescriben: cada ejecucin genera un archivo nuevo con timestamp.
- Al hacer clic en un reporte CSV se abre con el programa predeterminado del sistema.
