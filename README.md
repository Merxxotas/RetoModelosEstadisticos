
# Automatización de pruebas estadisticas

Este proyecto se realizó con el objetivo de poder aplicar de manera automática todas las pruebas estadisticas:

1. Chi- Cuadrado
2. S-K
3. Rachas Ascendentes/Descendentes
4. Rachas Encima/Debajo
5. Distribución de la longitud de las rachas para Ascendentes/Descendentes
6. Distribución de la longitud de las rachas para Encima/Debajo

Este programa al cargar un archivo (de tipo Excel, ya sea `.xlsx` o `.xls`) Permite determinar si efectivamente puede considerarse como una secuencia de números aleatorios.

> [!NOTE]
Para las pruebas de Chi-Cuadrado y S-K, además de su nivel de significancia, el programa pide el número de intervalos, esto debe ser digitado en la interfaz del programa:

![imagen1](https://github.com/user-attachments/assets/a9d60023-7759-4743-af84-fff8f9202303)


Una vez ingresado estos parámetros se podra ejecutar las pruebas seleccionadas e ingresar al detalle de cada una para ver los resultados de cada prueba. Además de poder generar un archivoPDF con un resumen del resultado de estas.

## Como utilizar el programa:

1. Ejecutar el archivo `main.exe`, esto es un ejecutable en el que no hay que tener un ambiente de ejecución preparado, se podrá ejecutar en cualquier sistema windows.

2. Si se quiere hacer alguna modificación/debug del programa, se debera preparar el ambiente de desarrollo, los pasos son los siguientes:

- Tener python instalado (preferiblemente Python, 3.12 o superior) esto se puede encontrar desde: [Documentación oficial Python](https://www.python.org/)

- Clonar el repositorio.

- Activar el entorno virtual de Python, estose hace de la siguiente manera:

``` bash
python -m venv venv
```

```
#Para activar el entorno virtual
# En cmd.exe
venv\Scripts\activate.bat
# En PowerShell
venv\Scripts\Activate.ps1 
# En Linux
source myvenv/bin/activate
```

[Documentación entorno virtual Python](https://python.land/virtual-environments/virtualenv)

- Instalar las librearías que se encuentran en `requirements.txt`

``` bash
pip install -r requirements.txt
```

- Finalmente para ejecutarlo:

``` bash
python main.python
```

> [!IMPORTANT]
Tener en cuenta que el ejecutable `main.exe` no se encuentra firmado, esto como consecuencia Windows podría arrojar algunas advertencias de que el programa puede ser malicioso. Solo se deben ignorar.


## Imágenes del programa:

- ![evidencia 1](https://github.com/user-attachments/assets/391f7ce6-af04-427e-91e1-907b868a3d28)
- ![evidencia 2](https://github.com/user-attachments/assets/ae90e049-4c44-4b6c-9e05-c2517b48cf9d)
- ![evidencia 3](https://github.com/user-attachments/assets/df904956-7552-4b49-aa4e-d1b9a0d2314a)
- ![evidencia 4](https://github.com/user-attachments/assets/db21d5b5-7403-49ba-8f9a-1b6166aa0f3c)
