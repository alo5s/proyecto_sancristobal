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
    
    def send_message(self, url: str = None, timeout: int = 50000) -> bool:
        """
        Envía un mensaje usando una URL ya construida.
        Espera TODO el flujo: carga → QR → login → chat cargado → espera 10s → mensaje enviado.
        Guarda sesión después de login exitoso.
        Cierra la página DESPUÉS DE ENVIAR.
        
        Args:
            url: URL completa (ej: de "Continuar en WhatsApp Web" link)
            timeout: Tiempo máximo de espera en ms (default: 50s)
        
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
                # PASO 2: Pide QR - esperar hasta timeout (50s máximo)
                print("[WhatsApp] ⚠ Se requiere escanear código QR")
                print(f"[WhatsApp] Esperando hasta {timeout//1000} segundos para escanear...")
                print("[WhatsApp] Por favor, escanea el código QR con tu teléfono")
                
                try:
                    self.page.wait_for_selector("div[contenteditable='true']", timeout=timeout)
                    print("[WhatsApp] ✓ QR escaneado - Sesión iniciada")
                    # Guardar sesión después de login exitoso
                    self._save_session()
                except:
                    print(f"[WhatsApp] ✗ Tiempo agotado ({timeout//1000}s) esperando QR")
                    self.page.close()
                    self.page = None
                    return False
            
            # PASO 3: Verificar si el número es inválido
            if "Phone number shared via url is invalid." in self.page.content():
                print("[WhatsApp] ✗ Número de teléfono inválido")
                self.page.close()
                self.page = None
                return False
            
            # PASO 4: Chat cargado (input visible) - esperar que cargue completamente
            print("[WhatsApp] ✓ Chat cargado, esperando 10 segundos para estabilizar...")
            self.page.wait_for_timeout(10000)
            
            # PASO 5: Verificar que el input siga visible (página cargada completamente)
            self.page.wait_for_selector("div[contenteditable='true']", timeout=5000)
            print("[WhatsApp] ✓ Página cargada completamente, enviando mensaje...")
            
            # PASO 6: Enviar mensaje (Enter)
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
