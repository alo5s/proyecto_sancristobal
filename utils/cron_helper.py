"""
Cron helper para gestionar entradas en crontab
"""
import subprocess
import os
from pathlib import Path


def add_to_crontab(cron_entry, comment="AUTOBOT_SCHEDULE"):
    """
    Agrega entrada a crontab
    
    Args:
        cron_entry: Línea de cron (ej: "0 8 * * 1-5 command")
        comment: Comentario para identificar la entrada
    """
    try:
        # Obtener crontab actual
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""
        
        # Verificar si ya existe nuestra entrada
        if comment in current_cron:
            print(f"[Cron] La entrada ya existe en crontab")
            return True
        
        # Agregar nueva entrada
        new_cron = current_cron + f"\n# {comment}\n{cron_entry}\n"
        subprocess.run(['crontab', '-'], input=new_cron, text=True, check=True)
        print(f"[Cron] ✓ Entrada agregada al crontab")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Cron] ✗ Error agregando entrada: {e}")
        return False
    except Exception as e:
        print(f"[Cron] ✗ Error: {e}")
        return False


def remove_from_crontab(comment="AUTOBOT_SCHEDULE"):
    """
    Elimina entrada de crontab basada en comentario
    
    Args:
        comment: Comentario que identifica la entrada a eliminar
    """
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode != 0:
            print("[Cron] No hay crontab configurado")
            return True
        
        lines = result.stdout.split('\n')
        new_lines = []
        skip_next = False
        
        for line in lines:
            if comment in line:
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            new_lines.append(line)
        
        new_cron = '\n'.join(new_lines).strip() + '\n'
        subprocess.run(['crontab', '-'], input=new_cron, text=True, check=True)
        print(f"[Cron] ✓ Entrada eliminada del crontab")
        return True
    except Exception as e:
        print(f"[Cron] ✗ Error eliminando: {e}")
        return False


def create_schedule_entry(days, time_str, project_path=None):
    """
    Crea entrada de cron basada en configuración
    
    Args:
        days: Lista de días (0=Lunes, 6=Domingo)
        time_str: Hora en formato "HH:MM"
        project_path: Ruta del proyecto (opcional)
    
    Returns:
        str: Entrada de cron lista para usar
    """
    # Convertir días de Python (0=Lunes) a cron (0=Domingo)
    cron_days = ','.join(str((d + 1) % 7) for d in days)
    
    # Parsear hora
    hour, minute = time_str.split(':')
    
    # Ruta del proyecto
    if project_path is None:
        project_path = Path.cwd()
    
    # Comando
    command = f"cd {project_path} && python main.py"
    
    # Entrada de cron
    cron_entry = f"{minute} {hour} * * {cron_days} {command}"
    
    return cron_entry
