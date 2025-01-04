# Replica: Gestor de Copias de Seguridad

Replica-CLI es una herramienta de línea de comandos (CLI) para gestionar copias de seguridad de discos y directorios. Ofrece sincronización bidireccional, cifrado, y un flujo intuitivo para usuarios en Windows, macOS, y Linux.

## Características
- **Sincronización bidireccional**: Mantén los respaldos sincronizados con su origen, incluyendo la eliminación de archivos obsoletos.
- **Cifrado seguro:** Protege tus respaldos con claves únicas.
- **Compatible con múltiples sistemas operativos.**
- **Manejo de logs**: Todos los eventos importantes (éxitos y fallos) se registran en el archivo `backup.log` automáticamente.
- **Experiencia interactiva**: Opciones fáciles de navegar con colores en la terminal, limpieza de pantalla y la posibilidad de cancelar cualquier proceso.

## Instalación
### Requisitos
- Python 3.8 o superior
- Dependencias: `psutil`, `cryptography`, `colorama`

### Instalación con pip
1. Clona este repositorio:
   ```bash
   git clone https://github.com/Gatogordo03/Replica-CLI.git
   cd Replica
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el programa:
   ```bash
   python main.py
   ```

## Uso
1. **Iniciar el programa**:
   - Ejecuta `python main.py` para acceder al menú principal.
   - Usa las opciones numéricas para seleccionar una acción.
   - Presiona `x` en cualquier momento para cancelar un proceso o salir.

2. **Visualizar logs**:
   - Desde el menú principal, selecciona la opción para ver los logs y revisa los eventos registrados.

3. **Sincronización bidireccional**:
   - Selecciona la opción de sincronización para mantener tus respaldos actualizados.
   - Si la ruta original no se encuentra, puedes seleccionar manualmente una nueva ruta.

## Licencia

Este proyecto está bajo la licencia MIT. Esto significa que puedes usar, modificar y distribuir este código para cualquier propósito, siempre que mantengas la atribución al autor original.

Consulta el archivo [LICENSE](./LICENCE) para más detalles.

### Contribuciones y Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones serán licenciadas bajo la licencia MIT, la misma que rige el proyecto.