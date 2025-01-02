import shutil
import os
import json
import colorama
from colorama import Fore, Style
from datetime import datetime
from cryptography.fernet import Fernet

# Inicializar colorama
colorama.init(autoreset=True)

def copiar_directorio(origen, destino):
    """Copia todo el contenido de un directorio a otro."""
    try:
        shutil.copytree(origen, destino, dirs_exist_ok=True)
        print(f"Directorio copiado de {origen} a {destino}.")
        return True
    except Exception as e:
        print(f"Error al copiar directorio: {e}")
        return False

def registrar_log(origen, destino, exito):
    """Registra el resultado de una operación en el archivo de log."""
    log_file = "backup.log"  # Cambiado a extensión .log

    # Verificar si el archivo de log existe y crearlo si no
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as archivo:
            archivo.write("Registro de Operaciones - Replica\n")
            archivo.write("=" * 40 + "\n")
        print(f"Archivo de log creado: {log_file}")

    # Escribir el resultado de la operación en el log
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "Éxito" if exito else "Fallo"
    mensaje = f"[{fecha_hora}] {estado}: {origen} -> {destino}\n"

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(mensaje)
    print(f"Resultado registrado en el log: {log_file}")

def ver_logs():
    """Muestra el contenido del archivo de log."""
    log_file = "backup.log"  # Cambiado a extensión .log
    if not os.path.exists(log_file):
        print(Fore.RED + "No se encontró el archivo de log. Aún no se han registrado operaciones.")
        return

    print(Fore.CYAN + "\n**** Contenido del Log ****")
    with open(log_file, "r", encoding="utf-8") as archivo:
        print(archivo.read())
    input(Fore.CYAN + "\nPresiona Enter para volver al menú principal.")

def navegar_directorios():
    """Navegador interactivo de directorios con opción para mostrar u ocultar elementos ocultos."""
    directorio_actual = os.path.expanduser("~")  # Carpeta inicial: directorio del usuario
    mostrar_ocultos = False  # Por defecto, no mostrar elementos ocultos

    while True:
        print(f"\nDirectorio actual: {directorio_actual}")
        try:
            elementos = os.listdir(directorio_actual)
            if not mostrar_ocultos:
                elementos = [e for e in elementos if not e.startswith(".")]
            elementos.insert(0, "..")  # Opción para retroceder

            for i, elemento in enumerate(elementos):
                print(f"{i}. {elemento}")

            print("\nOpciones:")
            print("- Ingresa un número para navegar.")
            print("- Ingresa -1 para seleccionar este directorio.")
            print("- Presiona 'a' para alternar mostrar/ocultar elementos ocultos.")

            entrada = input("Selecciona una opción: ").strip()
            if entrada == "a":
                mostrar_ocultos = not mostrar_ocultos
                print(f"{'Mostrando' if mostrar_ocultos else 'Ocultando'} elementos ocultos...")
            elif entrada == "-1":
                print(f"Directorio seleccionado: {directorio_actual}")
                return directorio_actual
            else:
                seleccion = int(entrada)
                if 0 <= seleccion < len(elementos):
                    seleccionado = os.path.join(directorio_actual, elementos[seleccion])
                    if os.path.isdir(seleccionado):
                        directorio_actual = seleccionado
                    else:
                        print(f"{seleccionado} no es un directorio válido.")
                else:
                    print("Número fuera de rango.")
        except ValueError:
            print("Por favor, ingresa un número válido o 'a' para alternar.")
        except Exception as e:
            print(f"Error: {e}")

def generar_clave(nombre_respaldo):
    """Genera una clave única y la guarda en una carpeta específica."""
    carpeta_claves = "./claves_respaldo"
    if not os.path.exists(carpeta_claves):
        os.makedirs(carpeta_claves)

    clave = Fernet.generate_key()
    ruta_clave = os.path.join(carpeta_claves, f"{nombre_respaldo}.key")
    with open(ruta_clave, "wb") as clave_file:
        clave_file.write(clave)
    print(f"Clave generada y guardada en: {ruta_clave}")
    return clave

def cifrar_archivo(archivo_zip):
    """Cifra un archivo ZIP usando una clave única."""
    nombre_respaldo = os.path.basename(archivo_zip).replace(".zip", "")
    clave = generar_clave(nombre_respaldo)
    fernet = Fernet(clave)

    try:
        with open(archivo_zip, "rb") as file:
            datos = file.read()
        datos_cifrados = fernet.encrypt(datos)
        ruta_cifrada = archivo_zip + ".enc"
        with open(ruta_cifrada, "wb") as archivo_cifrado:
            archivo_cifrado.write(datos_cifrados)
        print(f"Archivo cifrado guardado como: {ruta_cifrada}")
        return True
    except Exception as e:
        print(f"Error al cifrar el archivo: {e}")
        return False

def obtener_ruta_original(nombre_respaldo):
    """Busca la ruta original de un respaldo en los metadatos."""
    metadata_path = "./metadatos.json"
    if not os.path.exists(metadata_path):
        return None

    try:
        with open(metadata_path, "r", encoding="utf-8") as archivo:
            metadatos = json.load(archivo)
        for entrada in metadatos:
            if entrada.get("nombre_respaldo") == nombre_respaldo:
                return entrada.get("ruta_origen")
    except Exception as e:
        print(f"Error al leer los metadatos: {e}")
    return None

def actualizar_ruta_origen(nombre_respaldo, nueva_ruta_origen):
    """Actualiza la ruta de origen en el archivo de metadatos."""
    metadata_path = "./metadatos.json"
    if not os.path.exists(metadata_path):
        print("No se encontró el archivo de metadatos.")
        return False

    try:
        with open(metadata_path, "r", encoding="utf-8") as archivo:
            metadatos = json.load(archivo)

        # Buscar el respaldo y actualizar la ruta
        for entrada in metadatos:
            if entrada.get("nombre_respaldo") == nombre_respaldo:
                entrada["ruta_origen"] = nueva_ruta_origen
                print(f"Ruta de origen actualizada para {nombre_respaldo}: {nueva_ruta_origen}")
                break
        else:
            print(f"No se encontró el respaldo {nombre_respaldo} en los metadatos.")
            return False

        # Guardar cambios
        with open(metadata_path, "w", encoding="utf-8") as archivo:
            json.dump(metadatos, archivo, indent=4, ensure_ascii=False)
        return True

    except Exception as e:
        print(f"Error al actualizar los metadatos: {e}")
        return False

def seleccionar_opcion(mensaje, opciones):
    """Permite al usuario seleccionar una opción de una lista."""
    while True:
        try:
            seleccion = int(input(mensaje))
            if 1 <= seleccion <= len(opciones):
                return seleccion - 1
            else:
                print("Selecciona un número válido.")
        except ValueError:
            print("Por favor, ingresa un número.")

def guardar_metadatos(nombre_respaldo, ruta_origen):
    """Guarda información sobre la copia de seguridad en un archivo JSON."""
    metadata_path = "./metadatos.json"
    nuevo_metadato = {
        "nombre_respaldo": nombre_respaldo,
        "ruta_origen": ruta_origen,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Leer los metadatos existentes
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as archivo:
            metadatos = json.load(archivo)
    else:
        metadatos = []

    # Agregar la nueva entrada
    metadatos.append(nuevo_metadato)

    # Escribir de nuevo los metadatos
    with open(metadata_path, "w", encoding="utf-8") as archivo:
        json.dump(metadatos, archivo, indent=4, ensure_ascii=False)
    print(f"Metadatos actualizados en: {metadata_path}")

def sincronizar_bidireccional(origen, copia):
    """Sincroniza directorios para que sean idénticos, eliminando archivos faltantes."""
    # Eliminar archivos y directorios en la copia que no están en el origen
    for dirpath, dirnames, filenames in os.walk(copia):
        for dirname in dirnames:
            dir_origen = os.path.join(origen, os.path.relpath(os.path.join(dirpath, dirname), copia))
            if not os.path.exists(dir_origen):
                shutil.rmtree(os.path.join(dirpath, dirname))
                print(f"Directorio eliminado: {os.path.join(dirpath, dirname)}")

        for filename in filenames:
            file_origen = os.path.join(origen, os.path.relpath(os.path.join(dirpath, filename), copia))
            if not os.path.exists(file_origen):
                os.remove(os.path.join(dirpath, filename))
                print(f"Archivo eliminado: {os.path.join(dirpath, filename)}")

    # Copiar y actualizar archivos desde el origen a la copia
    for dirpath, dirnames, filenames in os.walk(origen):
        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(copia, os.path.relpath(src_file, origen))
            if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(src_file, dest_file)
                print(f"Archivo copiado/actualizado: {dest_file}")

def limpiar_pantalla():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_menu():
    """Muestra un menú con colores y formato."""
    limpiar_pantalla()
    print(Fore.CYAN + "************************************")
    print(Fore.CYAN + "*      Gestor de Copias Replica    *")
    print(Fore.CYAN + "************************************\n")
    print(Fore.YELLOW + "1. Copiar unidad")
    print(Fore.YELLOW + "2. Realizar copia de seguridad")
    print(Fore.YELLOW + "3. Encriptar copia de seguridad")
    print(Fore.YELLOW + "4. Ver logs de operaciones")
    print(Fore.RED + "x. Salir\n")
    print(Fore.CYAN + "Selecciona una opción:")
