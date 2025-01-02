import os
import shutil
import zipfile
from colorama import Fore
from datetime import datetime
from utils import (copiar_directorio, registrar_log, generar_clave, cifrar_archivo, 
                   navegar_directorios, obtener_ruta_original, seleccionar_opcion, 
                   guardar_metadatos, sincronizar_bidireccional, actualizar_ruta_origen,
                   limpiar_pantalla)
RUTA_RESPALDOS = "./copias_de_seguridad"

def gestionar_respaldo():
    """Menú para gestionar copias de seguridad."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Gestionar Copias de Seguridad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")

    print("1. Sincronizar con una copia existente")
    print("2. Crear una nueva copia de seguridad")
    opcion = input("Selecciona una opción: ").strip().lower()

    if opcion == "x":
        print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
        return
    elif opcion == "1":
        sincronizar_copia()
    elif opcion == "2":
        nueva_copia()
    else:
        print(Fore.RED + "Opción no válida.")

def sincronizar_copia():
    """Sincroniza cambios con una copia de seguridad existente."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Sincronizar Copia de Seguridad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")

    respaldos = [r for r in os.listdir(RUTA_RESPALDOS) if r.endswith(".zip")]
    if not respaldos:
        print(Fore.RED + "No hay copias de seguridad existentes.")
        input(Fore.CYAN + "Presiona Enter para volver al menú principal.")
        return

    print("\nCopias de seguridad disponibles:")
    for i, respaldo in enumerate(respaldos):
        print(f"{Fore.YELLOW}{i + 1}. {respaldo}")

    while True:
        opcion = input("\nSelecciona una copia para sincronizar: ").strip().lower()
        if opcion == "x":
            print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
            return

        try:
            indice = int(opcion) - 1
            if 0 <= indice < len(respaldos):
                respaldo = respaldos[indice]
                break
            else:
                print(Fore.RED + "Opción fuera de rango. Intenta nuevamente.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, ingresa un número.")

    ruta_respaldo = os.path.join(RUTA_RESPALDOS, respaldo)
    ruta_original = obtener_ruta_original(respaldo)
    sincronizacion_exitosa = False  # Estado inicial

    if not ruta_original or not os.path.exists(ruta_original):
        print(Fore.RED + "\nNo se encontró la ruta original o esta no existe.")
        print(Fore.YELLOW + "Selecciona manualmente un nuevo directorio para sincronizar:")
        ruta_original = navegar_directorios()
        if ruta_original.lower() == "x":
            print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
            return
        actualizar_ruta_origen(respaldo, ruta_original)

    temporal = "./temporal"
    try:
        os.makedirs(temporal, exist_ok=True)
        print(Fore.CYAN + f"\nDescomprimiendo respaldo {respaldo}...")
        with zipfile.ZipFile(ruta_respaldo, 'r') as zipf:
            zipf.extractall(temporal)

        print(Fore.YELLOW + f"Sincronizando bidireccionalmente {ruta_original} con el respaldo {respaldo}...")
        sincronizacion_exitosa = sincronizar_bidireccional(ruta_original, temporal)

        print(Fore.CYAN + f"Re-comprimiendo respaldo {respaldo}...")
        with zipfile.ZipFile(ruta_respaldo, 'w') as zipf:
            for carpeta, _, archivos in os.walk(temporal):
                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta, archivo)
                    zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, temporal))
        sincronizacion_exitosa = True
    except Exception as e:
        print(Fore.RED + f"Error durante la sincronización: {e}")
        sincronizacion_exitosa = False
    finally:
        # Limpiar temporales
        shutil.rmtree(temporal, ignore_errors=True)
        print(Fore.GREEN + "Sincronización completada." if sincronizacion_exitosa else Fore.RED + "La sincronización falló.")
        # Registrar en logs
        registrar_log(ruta_original, ruta_respaldo, sincronizacion_exitosa)

    input(Fore.CYAN + "Presiona Enter para volver al menú principal.")

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
