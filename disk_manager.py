import psutil
from utils import copiar_directorio, registrar_log

def listar_discos():
    """Muestra los discos disponibles en el sistema."""
    discos = psutil.disk_partitions()
    print("\nDiscos detectados:")
    for i, disco in enumerate(discos):
        print(f"{i + 1}. {disco.device} - {disco.fstype} ({disco.mountpoint})")
    return discos

def clonar_unidad():
    """Permite al usuario clonar una unidad completa."""
    discos = listar_discos()
    seleccion = int(input("Selecciona el disco que deseas clonar: ")) - 1
    origen = discos[seleccion].device
    destino = input("Ingresa la ruta del destino para la copia: ").strip()

    copiar_directorio(origen, destino)
    registrar_log(origen, destino, True)
