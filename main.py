import platform
import os
from backup_manager import gestionar_respaldo, encriptar_respaldo
from disk_manager import clonar_unidad

# Detectar el sistema operativo y definir la ruta de respaldos
sistema = platform.system()

if sistema == "Windows":
    RUTA_RESPALDOS = "C:\\copias_de_seguridad"
elif sistema in ["Linux", "Darwin"]:  # Darwin es macOS
    RUTA_RESPALDOS = os.path.expanduser("~/copias_de_seguridad")
else:
    raise OSError(f"Sistema operativo no soportado: {sistema}")

# Crear la carpeta de respaldos si no existe
if not os.path.exists(RUTA_RESPALDOS):
    os.makedirs(RUTA_RESPALDOS)

if __name__ == "__main__":
    print("Gestor de Discos y Copias de Seguridad")
    print("1. Copiar unidad")
    print("2. Realizar copia de seguridad")
    print("3. Encriptar copia de seguridad")
    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        clonar_unidad()
    elif opcion == "2":
        gestionar_respaldo()
    elif opcion == "3":
        encriptar_respaldo()
    else:
        print("Opción no válida.")
