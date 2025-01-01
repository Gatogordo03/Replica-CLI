import os
import shutil
import zipfile
from datetime import datetime
from utils import (copiar_directorio, registrar_log, generar_clave, cifrar_archivo, 
                   navegar_directorios, obtener_ruta_original, seleccionar_opcion, 
                   guardar_metadatos, sincronizar_bidireccional, actualizar_ruta_origen)
RUTA_RESPALDOS = "./copias_de_seguridad"

def gestionar_respaldo():
    """Menú para gestionar copias de seguridad."""
    if not os.path.exists(RUTA_RESPALDOS):
        os.makedirs(RUTA_RESPALDOS)

    print("\nOpciones de copia de seguridad:")
    print("1. Sincronizar con una copia existente")
    print("2. Crear una nueva copia de seguridad")
    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        sincronizar_copia()
    elif opcion == "2":
        nueva_copia()
    else:
        print("Opción no válida.")

def sincronizar_copia():
    """Sincroniza cambios con una copia de seguridad existente."""
    respaldos = [r for r in os.listdir(RUTA_RESPALDOS) if r.endswith(".zip")]
    if not respaldos:
        print("No hay copias de seguridad existentes.")
        return

    print("\nCopias de seguridad disponibles:")
    for i, respaldo in enumerate(respaldos):
        print(f"{i + 1}. {respaldo}")
    indice = seleccionar_opcion("Selecciona una copia para sincronizar: ", respaldos)
    respaldo = respaldos[indice]
    ruta_respaldo = os.path.join(RUTA_RESPALDOS, respaldo)

    # Obtener la ruta de origen desde los metadatos
    ruta_original = obtener_ruta_original(respaldo)
    if not ruta_original or not os.path.exists(ruta_original):
        print("No se encontró la ruta original o esta no existe.")
        print("Selecciona manualmente un nuevo directorio para sincronizar:")
        ruta_original = navegar_directorios()
        # Actualizar la nueva ruta en los metadatos
        actualizar_ruta_origen(respaldo, ruta_original)

    # Descomprimir el respaldo
    temporal = "./temporal"
    os.makedirs(temporal, exist_ok=True)
    print(f"Descomprimiendo respaldo {respaldo}...")
    with zipfile.ZipFile(ruta_respaldo, 'r') as zipf:
        zipf.extractall(temporal)

    # Sincronizar bidireccionalmente
    print(f"Sincronizando bidireccionalmente {ruta_original} con el respaldo {respaldo}...")
    sincronizar_bidireccional(ruta_original, temporal)

    # Re-comprimir el contenido sincronizado
    print(f"Re-comprimiendo respaldo {respaldo}...")
    with zipfile.ZipFile(ruta_respaldo, 'w') as zipf:
        for carpeta, _, archivos in os.walk(temporal):
            for archivo in archivos:
                ruta_archivo = os.path.join(carpeta, archivo)
                zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, temporal))

    # Limpiar temporales
    shutil.rmtree(temporal, ignore_errors=True)
    print("Sincronización completada.")

def nueva_copia():
    """Crea una nueva copia de seguridad en la carpeta central."""
    print("Selecciona el directorio de origen para la nueva copia:")
    origen = navegar_directorios()  # Usa el navegador interactivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_respaldo = f"copia_{timestamp}.zip"
    destino_zip = os.path.join(RUTA_RESPALDOS, nombre_respaldo)

    print(f"Comprimiendo y creando nueva copia de seguridad: {destino_zip}...")
    with zipfile.ZipFile(destino_zip, 'w') as zipf:
        for carpeta, _, archivos in os.walk(origen):
            for archivo in archivos:
                ruta_archivo = os.path.join(carpeta, archivo)
                zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, origen))
    registrar_log(origen, destino_zip, True)

    # Guardar los metadatos
    guardar_metadatos(nombre_respaldo, origen)

    cifrar = input("¿Deseas cifrar esta copia de seguridad ahora? (s/n): ").strip().lower() == "s"
    if cifrar:
        cifrar_archivo(destino_zip)

def encriptar_respaldo():
    """Permite encriptar una copia de seguridad existente."""
    respaldos = os.listdir(RUTA_RESPALDOS)
    if not respaldos:
        print("No hay copias de seguridad existentes.")
        return

    print("\nCopias de seguridad disponibles para encriptar:")
    for i, respaldo in enumerate(respaldos):
        print(f"{i + 1}. {respaldo}")
    indice = int(input("Selecciona una copia para encriptar: ")) - 1
    respaldo = respaldos[indice]
    ruta_respaldo = os.path.join(RUTA_RESPALDOS, respaldo)

    if ruta_respaldo.endswith(".enc"):
        print("Esta copia ya está encriptada.")
        return

    cifrar_archivo(ruta_respaldo)
    print(f"Encriptación completada para {respaldo}.")
