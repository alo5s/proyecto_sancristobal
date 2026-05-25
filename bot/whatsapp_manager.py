"""
WhatsAppManager - Gestión de envío automático via WhatsApp Web
Reutiliza el contexto existente de BrowserManager (evita conflicto asyncio).
Usa Playwright sync API sin crear nueva instancia.
"""

from urllib.parse import quote
from pathlib import Path
import json
import os


class WhatsAppManager:
    """
    Manager para envío automático de mensajes via WhatsApp Web.
    
    Attributes:
        context: Contexto de Playwright desde BrowserManager
        page: Página de WhatsApp Web (se cierra después de cada envío)
    """
    
    SESSION_FILE = Path("session/whatsapp_session.json")
    
    def __init__(self, context):
        """
        Inicializa con contexto existente.
        
        Args:
            context: Playwright context desde BrowserManager
        """
        self.context = context
        self.page = None
    
    def _load_session(self):
        """Carga cookies de sesión guardadas"""
        if self.SESSION_FILE.exists():
            try:
                with open(self.SESSION_FILE, 'r') as f:
                    cookies = json.load(f)
                self.context.add_cookies(cookies)
                print("[WhatsApp] ✓ Sesión cargada desde archivo")
                return True
            except Exception as e:
                print(f"[WhatsApp] ✗ Error cargando sesión: {e}")
                return False
        return False
    
    def _save_session(self):
        """Guarda cookies de sesión para próxima vez"""
        try:
            cookies = self.context.cookies()
            with open(self.SESSION_FILE, 'w') as f:
                json.dump(cookies, f)
            print("[WhatsApp] ✓ Sesión guardada")
            return True
        except Exception as e:
            print(f"[WhatsApp] ✗ Error guardando sesión: {e}")
            return False
    
    def send_message(self, url: str = None, timeout: int = 50000, on_qr_needed: callable = None) -> bool:
        """
        Envía un mensaje usando una URL ya construida.
        Espera TODO el flujo: carga → QR → login → chat cargado → espera 10s → mensaje enviado.
        Guarda sesión después de login exitoso.
        Cierra la página DESPUÉS DE ENVIAR.
        
        Args:
            url: URL completa (ej: de "Continuar en WhatsApp Web" link)
            timeout: Tiempo máximo de espera en ms (default: 50s)
            on_qr_needed: Callable(msg) invoked when QR scan is required
        
        Returns:
            bool: True si se envió el mensaje correctamente
        """
        if not url:
            print("[WhatsApp] ✗ Error: Se requiere URL")
            return False
        
        # Crear página si no existe
        if self.page is None:
            self.page = self.context.new_page()
        
        # Cargar sesión guardada (si existe)
        self._load_session()
        
        print(f"[WhatsApp] Abriendo chat con URL del sistema...")
        print(f"[WhatsApp] URL: {url[:80]}...")
        
        # Navegar a la URL capturada
        self.page.goto(url, wait_until="networkidle", timeout=30000)
        
        try:
            # PASO 1: Verificar si ya está logueado (input visible)
            try:
                self.page.wait_for_selector("div[contenteditable='true']", timeout=10000)
                print("[WhatsApp] ✓ Sesión ya activa (no requiere QR)")
            except:
                # PASO 2: Esperar a que el QR se renderice
                print("[WhatsApp] ⚠ Se requiere escanear código QR")
                try:
                    self.page.wait_for_selector("canvas", timeout=15000)
                    print("[WhatsApp] ✓ QR code visible en pantalla")
                except:
                    pass

                if on_qr_needed:
                    on_qr_needed("Escaneá el código QR de WhatsApp con tu teléfono")
                print("[WhatsApp] Esperando escaneo del QR...")

                self.page.wait_for_selector("div[contenteditable='true']", timeout=300000)
                print("[WhatsApp] ✓ QR escaneado - Sesión iniciada")
                self._save_session()
            
            # PASO 3: Verificar si el número es inválido
            if "Phone number shared via url is invalid." in self.page.content():
                print("[WhatsApp] ✗ Número de teléfono inválido")
                self.page.close()
                self.page = None
                return False
            
            # PASO 4: Esperar que toda la UI termine de renderizar
            print("[WhatsApp] Esperando que la página termine de renderizar...")
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_selector("header", timeout=10000)
            self.page.wait_for_timeout(3000)
            print("[WhatsApp] ✓ Página renderizada, enviando mensaje...")
            
            # PASO 5: Enviar mensaje (Enter)
            self.page.keyboard.press("Enter")
            print("[WhatsApp] ✓ Mensaje enviado")
            
            # PASO 7: Esperar confirmación
            self.page.wait_for_timeout(2000)
            
            # PASO 8: CERRAR PÁGINA DESPUÉS DEL ENVÍO
            self.page.close()
            self.page = None
            print("[WhatsApp] ✓ Página cerrada")
            
            return True
            
        except Exception as e:
            print(f"[WhatsApp] ✗ Error enviando mensaje: {e}")
            # Cerrar página en caso de error también
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
                self.page = None
            return False
    
    def close(self):
        """Cierra la página si está abierta (pero NO el contexto)"""
        if self.page:
            try:
                self.page.close()
                print("[WhatsApp] Página cerrada")
            except Exception as e:
                print(f"[WhatsApp] Error cerrando página: {e}")
            finally:
                self.page = None


# ============================================================
# FUNCIONES DE UTILIDAD (Module-level)
# ============================================================

def send_whatsapp_message(phone: str, message: str, context=None) -> bool:
    """
    Función rápida para enviar un mensaje de WhatsApp.
    
    Args:
        phone: Número de teléfono
        message: Mensaje a enviar
        context: Playwright context (desde BrowserManager)
    
    Returns:
        bool: True si se envió correctamente
    """
    if context is None:
        print("[WhatsApp] ✗ Error: Se requiere contexto de Playwright")
        return False
    
    manager = WhatsAppManager(context)
    try:
        encoded_message = quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        return manager.send_message(url=url)
    finally:
        manager.close()
