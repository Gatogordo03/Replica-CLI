import psutil
from utils import copiar_directorio, registrar_log, limpiar_pantalla
from colorama import Fore

def listar_discos():
    """Muestra los discos disponibles en el sistema."""
    discos = psutil.disk_partitions()
    print("\nDiscos detectados:")
    for i, disco in enumerate(discos):
        print(f"{i + 1}. {disco.device} - {disco.fstype} ({disco.mountpoint})")
    return discos

def clonar_unidad():
    """Permite al usuario clonar una unidad completa."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Clonar Unidad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")

    # Listar discos disponibles
    discos = listar_discos()
    if not discos:
        print(Fore.RED + "No se encontraron discos disponibles.")
        return

    while True:
        try:
            opcion = input("Selecciona el disco que deseas clonar: ").strip().lower()
            if opcion == "x":
                print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
                return

            indice = int(opcion) - 1
            if 0 <= indice < len(discos):
                origen = discos[indice].device
                break
            else:
                print(Fore.RED + "Opción fuera de rango. Intenta nuevamente.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor ingresa un número.")

    destino = input("Ingresa la ruta del destino para la copia: ").strip()
    if destino.lower() == "x":
        print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
        return

    limpiar_pantalla()
    print(Fore.YELLOW + f"Clonando unidad {origen} a {destino}...")
    exito = copiar_directorio(origen, destino)
    registrar_log(origen, destino, exito)