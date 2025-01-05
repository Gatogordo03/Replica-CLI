import os
import shutil
import zipfile
import json
from colorama import Fore
from datetime import datetime
from utils import (copiar_directorio, registrar_log, generar_clave, cifrar_archivo, 
                   navegar_directorios, obtener_ruta_original, seleccionar_opcion, 
                   guardar_metadatos, sincronizar_bidireccional, actualizar_ruta_origen,
                   limpiar_pantalla, cargar_clave, descifrar_archivo, verificar_y_crear_ruta,
                   verificar_y_crear_json)

RUTA_RESPALDOS = "./copias_de_seguridad"

def gestionar_respaldo():
    """Menú para gestionar copias de seguridad."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Gestionar Copias de Seguridad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")
    print("1. Ver lista de copias")
    print("2. Sincronizar con una copia existente")
    print("3. Crear una nueva copia de seguridad")
    print("4. Encriptar una copia de seguridad")
    print("5. Desencriptar una copia de seguridad")
    print("6. Eliminar una copia de respaldo")
    opcion = input(Fore.CYAN + "Selecciona una opción: ").strip().lower()

    if opcion == "x":
        print(Fore.RED + "Volviendo al menú principal...")
        return
    elif opcion == "1":
        ver_lista_copias()
    elif opcion == "2":
        sincronizar_copia()
    elif opcion == "3":
        nueva_copia()
    elif opcion == "4":
        encriptar_respaldo()
    elif opcion == "5":
        desencriptar_respaldo()
    elif opcion == "6":
        eliminar_copia()
    else:
        print(Fore.RED + "Opción no válida. Por favor, intenta de nuevo.")

def ver_lista_copias():
    """Muestra una lista de copias de seguridad disponibles (encriptadas o no)."""
    tipo_actual = "zip"  # Comienza mostrando las copias sin encriptar
    while True:
        limpiar_pantalla()
        tipo_texto = "Copias Sin Encriptar" if tipo_actual == "zip" else "Copias Encriptadas"
        print(Fore.CYAN + f"**** Ver {tipo_texto} ****")
        print(Fore.YELLOW + "Ingresa 'E' para alternar entre tipos de copia, o presiona Enter para volver al menú principal.\n")

        # Filtrar respaldos según el tipo actual
        extension = ".zip" if tipo_actual == "zip" else ".zip.enc"
        respaldos = [r for r in os.listdir(RUTA_RESPALDOS) if r.endswith(extension)]

        if not respaldos:
            print(Fore.RED + f"No hay {tipo_texto.lower()} disponibles.")
        else:
            print(Fore.CYAN + "Copias disponibles:")
            for i, respaldo in enumerate(respaldos):
                print(f"{Fore.YELLOW}{i + 1}. {respaldo}")

        # Entrada del usuario
        opcion = input(Fore.CYAN + "\nPresiona 'E' para alternar o Enter para volver: ").strip().lower()
        if opcion == "":
            print(Fore.GREEN + "Volviendo al menú principal...")
            return
        elif opcion == "e":
            tipo_actual = "enc" if tipo_actual == "zip" else "zip"
        else:
            print(Fore.RED + "Entrada inválida. Por favor, ingresa 'E' o presiona Enter.")

def sincronizar_copia():
    """Sincroniza cambios con una copia de seguridad existente."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Sincronizar Copia de Seguridad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")

    # Verificar y cargar el archivo JSON
    ruta_json = "metadatos.json"
    verificar_y_crear_json(ruta_json)
    with open(ruta_json, "r") as json_file:
        data = json.load(json_file)

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
    ruta_original = data.get(respaldo, {}).get("origen")  # Obtener la ruta del JSON
    sincronizacion_exitosa = False  # Estado inicial

    if not ruta_original or not os.path.exists(ruta_original):
        print(Fore.RED + "\nNo se encontró la ruta original o esta no existe.")
        print(Fore.YELLOW + "Selecciona manualmente un nuevo directorio para sincronizar:")
        ruta_original = navegar_directorios()
        if ruta_original.lower() == "x":
            print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
            return

        # Actualizar el JSON con la nueva ruta
        data[respaldo] = {"origen": ruta_original}
        with open(ruta_json, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(Fore.GREEN + f"Ruta actualizada en el archivo JSON: {ruta_original}")

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
    verificar_y_crear_ruta(RUTA_RESPALDOS)  # Asegura que la carpeta de respaldos exista

    print("Selecciona el directorio de origen para la nueva copia:")
    origen = navegar_directorios()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_respaldo = f"copia_{timestamp}.zip"
    destino_zip = os.path.join(RUTA_RESPALDOS, nombre_respaldo)

    print(Fore.YELLOW + f"\nCreando copia de seguridad: {destino_zip}...")
    exito = comprimir_copia(origen, destino_zip)
    if not exito:
        print(Fore.RED + "Error al crear la copia de seguridad.")
        registrar_log(origen, destino_zip, False)
        return

    print(Fore.YELLOW + "¿Deseas encriptar esta copia? (s/n): ")
    encriptar = input(Fore.CYAN + ">> ").strip().lower() == 's'

    if encriptar:
        exito_encriptar = cifrar_archivo(destino_zip)
        if exito_encriptar:
            os.remove(destino_zip)  # Eliminar la versión .zip
            print(Fore.GREEN + f"Copia encriptada creada con éxito: {destino_zip}.enc")
            registrar_log(origen, destino_zip + ".enc", True)
        else:
            print(Fore.RED + "Error al encriptar la copia.")
            registrar_log(origen, destino_zip, False)
    else:
        print(Fore.GREEN + f"Copia de seguridad creada con éxito: {destino_zip}")
        registrar_log(origen, destino_zip, True)

def comprimir_copia(origen, destino_zip):
    """Comprime un archivo o directorio en un archivo ZIP."""
    try:
        with zipfile.ZipFile(destino_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(origen):
                # Si el origen es un archivo
                zipf.write(origen, os.path.basename(origen))
            else:
                # Si el origen es un directorio
                for root, _, files in os.walk(origen):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=origen)
                        zipf.write(full_path, arcname)

        print(f"Copia comprimida exitosamente: {destino_zip}")
        return True
    except Exception as e:
        print(f"Error al comprimir: {e}")
        return False

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

def desencriptar_respaldo():
    """Permite desencriptar una copia de seguridad existente."""
    limpiar_pantalla()
    print(Fore.CYAN + "**** Desencriptar Copia de Seguridad ****")
    print(Fore.YELLOW + "Ingresa 'x' en cualquier momento para cancelar y volver al menú principal.\n")

    # Listar copias encriptadas
    respaldos_encriptados = [r for r in os.listdir(RUTA_RESPALDOS) if r.endswith(".zip.enc")]
    if not respaldos_encriptados:
        print(Fore.RED + "No hay copias de seguridad encriptadas disponibles.")
        input(Fore.CYAN + "Presiona Enter para volver al menú principal.")
        return

    print("\nCopias encriptadas disponibles:")
    for i, respaldo in enumerate(respaldos_encriptados):
        print(f"{Fore.YELLOW}{i + 1}. {respaldo}")

    while True:
        opcion = input("\nSelecciona una copia para desencriptar: ").strip().lower()
        if opcion == "x":
            print(Fore.RED + "Proceso cancelado. Volviendo al menú principal...")
            return

        try:
            indice = int(opcion) - 1
            if 0 <= indice < len(respaldos_encriptados):
                respaldo = respaldos_encriptados[indice]
                break
            else:
                print(Fore.RED + "Opción fuera de rango. Intenta nuevamente.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, ingresa un número.")

    ruta_respaldo_enc = os.path.join(RUTA_RESPALDOS, respaldo)
    nombre_respaldo = respaldo.replace(".zip.enc", "")
    ruta_respaldo_dec = os.path.join(RUTA_RESPALDOS, f"{nombre_respaldo}.zip")
    clave_respaldo = cargar_clave(nombre_respaldo)

    if not clave_respaldo:
        print(Fore.RED + "No se encontró la clave asociada a esta copia.")
        input(Fore.CYAN + "Presiona Enter para volver al menú principal.")
        return

    print(Fore.YELLOW + f"\nDesencriptando {respaldo}...")
    exito = descifrar_archivo(ruta_respaldo_enc, ruta_respaldo_dec, clave_respaldo)

    if exito:
        print(Fore.GREEN + f"Copia desencriptada con éxito: {ruta_respaldo_dec}")
        registrar_log(ruta_respaldo_enc, f"Desencriptado a {ruta_respaldo_dec}", True)
    else:
        print(Fore.RED + "Fallo al desencriptar la copia.")
        registrar_log(ruta_respaldo_enc, "Fallo al desencriptar", False)

    input(Fore.CYAN + "Presiona Enter para volver al menú principal.")

def eliminar_copia():
    """Elimina una copia de respaldo completa, alternando entre copias encriptadas y sin encriptar."""
    tipo_actual = "zip"  # Comienza mostrando las copias sin encriptar
    while True:
        limpiar_pantalla()
        tipo_texto = "Copias Sin Encriptar" if tipo_actual == "zip" else "Copias Encriptadas"
        print(Fore.CYAN + f"**** Eliminar {tipo_texto} ****")
        print(Fore.YELLOW + "Ingresa 'x' para cancelar o 'E' para alternar entre tipos de copia.\n")

        # Filtrar respaldos según el tipo actual
        extension = ".zip" if tipo_actual == "zip" else ".zip.enc"
        respaldos = [r for r in os.listdir(RUTA_RESPALDOS) if r.endswith(extension)]

        if not respaldos:
            print(Fore.RED + f"No hay {tipo_texto.lower()} disponibles.")
        else:
            print(Fore.CYAN + "Copias disponibles:")
            for i, respaldo in enumerate(respaldos):
                print(f"{Fore.YELLOW}{i + 1}. {respaldo}")

        # Entrada del usuario
        opcion = input(Fore.CYAN + "Selecciona una opción: ").strip().lower()

        if opcion == "x":
            print(Fore.RED + "Volviendo al menú principal...")
            return
        elif opcion == "e":
            tipo_actual = "enc" if tipo_actual == "zip" else "zip"
            continue

        try:
            indice = int(opcion) - 1
            if 0 <= indice < len(respaldos):
                respaldo = respaldos[indice]
                break
            else:
                print(Fore.RED + "Opción fuera de rango. Intenta nuevamente.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, ingresa un número o 'E'.")
            continue

    # Confirmación y eliminación
    print(Fore.RED + f"\n¡Advertencia! Esto eliminará la copia {respaldo} y todos sus archivos asociados.")
    confirmacion = input(Fore.YELLOW + "¿Estás seguro? (s/n): ").strip().lower()
    if confirmacion != "s":
        print(Fore.RED + "Eliminación cancelada. Volviendo al menú principal...")
        return

    # Eliminar archivos relacionados
    respaldo_ruta = os.path.join(RUTA_RESPALDOS, respaldo)
    nombre_respaldo = respaldo.replace(extension, "")
    clave_ruta = os.path.join("./claves_respaldo", f"{nombre_respaldo}.key")

    try:
        if os.path.exists(respaldo_ruta):
            os.remove(respaldo_ruta)
            print(Fore.GREEN + f"Eliminado: {respaldo_ruta}")

        if tipo_actual == "enc" and os.path.exists(clave_ruta):
            os.remove(clave_ruta)
            print(Fore.GREEN + f"Eliminado: {clave_ruta}")

        registrar_log(respaldo_ruta, "Eliminado", True)
        print(Fore.GREEN + "Eliminación completada con éxito.")
    except Exception as e:
        registrar_log(respaldo_ruta, "Fallo al eliminar", False)
        print(Fore.RED + f"Error al eliminar los archivos: {e}")

    input(Fore.CYAN + "\nPresiona Enter para volver al menú principal.")
