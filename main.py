import platform
import os
from backup_manager import gestionar_respaldo, encriptar_respaldo
from disk_manager import clonar_unidad
from utils import limpiar_pantalla, imprimir_menu, ver_logs
from colorama import Fore

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

def main():
    while True:
        imprimir_menu()
        opcion = input("Selecciona una opción: ").strip().lower()

        if opcion == "x":
            print(Fore.RED + "\nSaliendo del programa. ¡Hasta luego!")
            break
        elif opcion == "1":
            clonar_unidad()
        elif opcion == "2":
            gestionar_respaldo()
        elif opcion == "3":
            ver_logs()
        else:
            print(Fore.RED + "Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    main()
