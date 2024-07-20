<h1 align="left">PROYECTO2-j.garcian</h1>

<h3 align="left">Entornos Virtuales</h3>
``Pyvenv`` normalmente instalará la versión más reciente de Python que tengas disponible; el script también se instala con un número de versión, así que si tienes varias versiones de Python en tu sistema puedes seleccionar una versión específica de Python ejecutando ``python3`` o la versión que quieras.
Para crear un entorno virtual, siga los pasos que se indican a continuación:

* Abra una terminal
* Ubiquese en la carpeta donde desee crear su entorno virtual
* Ejecute el siguiente comando para crear un entorno virtual
  ```bash
  python3 -m venv env
  ```
* Active el entorno virtual con el siguiente comando
  * En Windows, ejecute
    ```bash
    .\env\Scripts\activate
    ```
  * en Unix o Mac OS, ejecute
    ```bash
    source env/bin/activate
    ```

<h3 align="left">variable necesarias</h3>

```bash
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
```
