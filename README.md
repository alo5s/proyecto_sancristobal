# AUTOBOT — Automatización de Cobranzas

Bot de escritorio para automatizar el proceso de cobranza en el portal **productores.sancristobal.com.ar**.

## Funcionalidad

1. **Login automático** — Inicia sesión en el portal con credenciales guardadas.
2. **Navegación y filtros** — Accede a Gestión de Cobranzas, aplica filtros por modalidad de pago (EFECTIVO/DÉBITO DIRECTO/TARJETA DE CRÉDITO) y configura paginación.
3. **Procesamiento de vencimientos** — Recorre la tabla de clientes y para cada uno:
   - Envía notificación por **correo electrónico** desde el sistema.
   - Envía notificación por **WhatsApp Web** automáticamente (sesión persistente, alerta QR una sola vez).
4. **Generación de reportes** — Guarda resultados en archivos Excel `.xlsx` con timestamp (`reports/notificaciones_*_YYYYMMDD_HHMMSS.xlsx`). Cada cliente incluye columna de su método de pago real (EFECTIVO/DÉBITO DIRECTO/TARJETA DE CRÉDITO). Encabezados en negrita y columnas con ancho autoajustado.
5. **Visor de reportes** — Al finalizar el bot, se abre automáticamente el diálogo de reportes. Se puede hacer clic en cualquier `.xlsx` para abrirlo y hay un botón "Abrir Ubicación" para abrir la carpeta en el explorador de archivos.
6. **Programación automática** — Permite configurar ejecución automática vía **cron** (Linux) en días y hora específicos.
7. **Notificaciones configurables** — Se puede habilitar/deshabilitar envío por correo y WhatsApp, y elegir procesar vencimientos a 7 días y/o 8-15 días.
8. **Sistema de licencias** — Control de uso del programa:
   - Primera ejecución: 1 día de prueba automático.
   - Al vencer: se deshabilita el botón "Ejecutar".
   - **Menú Licencias**: muestra estado, fecha de vencimiento y permite renovar con clave.
   - Las claves se generan con una herramienta externa (HMAC-SHA256 + Base64).

## Arquitectura

```
proyecto_sancristobal/
├── main.py                    # Punto de entrada (GUI con PySide6)
├── config_manager.py          # Gestión de configuración (QSettings)
├── .gitignore
├── AGENTS.md                  # Instrucciones para IA (en .gitignore)
├── README.md
│
├── bot/
│   ├── browser_manager.py     # Singleton de Playwright, detección de navegador/perfil
│   ├── whatsapp_manager.py    # Envío automático por WhatsApp Web
│   └── paginas/
│       ├── login_manager.py   # Login en el portal
│       └── bot_manager.py     # Orquestación (filtros, tabla, notificaciones, popups)
│
├── controller/
│   ├── app_controller.py      # Controlador principal (señales UI ↔ worker)
│   └── workers.py             # QThread con cola de tareas para Playwright (solo etapas 1-2)
│
├── ui/
│   ├── layout/
│   │   ├── layout_login.py    # Pantalla de login
│   │   └── layout_home.py     # Pantalla principal con botón de ejecución
│   └── dialogs/
│       ├── schedule_dialog.py     # Configuración de auto-inicio (cron)
│       ├── programacion_dialog.py # Configuración de notificaciones y vencimientos
│       ├── reportes_dialog.py     # Visor de reportes Excel (.xlsx)
│       └── license_dialog.py      # Estado y renovación de licencia
│
├── utils/
│   ├── cron_helper.py         # Helper para gestionar entradas en crontab
│   └── license_manager.py     # Validación de licencias (HMAC-SHA256)
```

## Requisitos

- **Python 3.10+**
- **Playwright** (`pip install playwright`)
- **PySide6** (`pip install PySide6`)
- **openpyxl** (`pip install openpyxl`)
- Un navegador compatible instalado: Chrome, Edge, Brave o Chromium

## Instalación

```bash
pip install PySide6 playwright openpyxl
playwright install chromium
```

## Uso

```bash
python main.py
```

1. Ingresar credenciales (se guardan en QSettings).
2. Hacer clic en **ENTRAR** — el bot inicia sesión automáticamente.
3. En la pantalla principal, hacer clic en **EJECUTAR COBRANZA**.
4. El bot procesa clientes y envía notificaciones.
5. Al finalizar, se abre automáticamente el visor de reportes.

## Sistema de Licencias

El programa incluye control de licencias para limitar el uso por tiempo.

### Primer inicio
- Automáticamente asigna **1 día de prueba**.
- El botón "Ejecutar" se deshabilita al vencer la licencia.

### Ver estado
- **Menú Licencias** en la barra superior.
- Muestra: fecha de vencimiento, días restantes, estado (vigente/vencida).

### Renovar
1. Generar una clave con el generador externo:
   ```bash
   python tools/generar_licencia.py --expire 2027-12-31 --machine 1
   ```
2. En el programa: **Menú Licencias** pegar la clave y clickear **Renovar**.

### Formato de la clave
- Se compone de: `fecha:ID_maquina:firma_HMAC` codificado en Base64.
- Ejemplo: `MjAyNy0wNS0xOToxOmY5ZmI3NGQxM2M4OWZkYzk`
- Secret interno: `SanCristobalLic2026` (cambiable en `utils/license_manager.py`).

## Configuración

Desde el menú **Configuración** se accede a:
- **Auto-inicio** Programar ejecución automática con cron.

Desde la pantalla principal, botón **Programación**:
- **Notificaciones** Habilitar/deshabilitar correo y WhatsApp.
- **Vencimientos** Elegir procesar 7 días y/o 8-15 días.
- **Modalidades de pago** Elegir qué modalidades procesar (EFECTIVO, DÉBITO DIRECTO, TARJETA DE CRÉDITO).

También desde el menú:
- **Mostrar/Ocultar navegador** Cambia entre modo headless y visible (requiere reinicio).
- **Licencias** Ver estado de licencia y renovar.

## Archivos importantes

| Archivo | Propósito |
|---------|-----------|
| `reports/*.xlsx` | Reportes generados tras cada ejecución (con timestamp) |
| `session/` | Datos de sesión del navegador (runtime, ignorado por git) |
| `session/whatsapp_session.json` | Sesión persistente de WhatsApp (evita re-escanear QR) |
| `utils/license_manager.py` | Sistema de licencias (HMAC-SHA256) |

## Notas

- La sesión de WhatsApp se guarda en `session/whatsapp_session.json`. La primera vez que necesita QR muestra una alerta en pantalla; luego reutiliza la sesión guardada.
- El bot detecta automáticamente el navegador instalado (Chrome, Edge, Brave, Chromium).
- Compatible con Windows y Linux.
- Los reportes nunca se sobrescriben: cada ejecución genera un archivo `.xlsx` nuevo con timestamp.
- Al hacer clic en un reporte `.xlsx` se abre con el programa predeterminado del sistema.
- El bot solo ejecuta etapas 1-2 (filtros + notificaciones). Las etapas 3-6 fueron eliminadas por ser código muerto.
- `config.json` existe como referencia pero la app usa **QSettings**, no lo lee.
