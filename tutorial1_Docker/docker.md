# Tutorial de Docker

En este tutorial veremos ciertos aspectos mas practicos a la hora de trabajar con docker. La manera en que estudiaremos estos aspectos prácticos será por medio de una tarea que fue dada en el contexto del ramo "Arquitectura de Software" en el ramo INFO229 de la Universidad Austral de Chile bajo el profesor Mathew Vernier.

## Ejercicio
 Dockerizar una aplicación Python capaz de hacer búsquedas en Wikipedia, guardarán los resultados en una base de datos.

 ### ¿Cómo hacerlo?
Tendremos que hacer uso de 4 herramientas principalmente: Docker, Python, una Base de datos como mongo y un api que permita la descarga de información de wikipedia.
 - Docker: Herramienta de administración de contenedores. Nos permite trabajar nuestra aplicación en un enfoque de microservicios. En nuestro caso no será necesario conectar muchos servicios, y en general podríamos trabajarlo en forma monolítica sin mayor problema, mas seguiremos usando docker con un contenedor.
 - Python: En este lenguaje tenemos una buena cantidad de extensiones y apis que nos permitirán lograr sin ningun problema.
 -  Base de datos: En nuestro caso usaremos mongodb. Principalmente por la facilidad en que podemos guardar información.
 - api wikipedia: Usaremos una api del mismo nombre de la pagina que es bastante fácil de usar. Para tener en cuenta es que por lo general es muy quisquilloso con las palabras que uno busca de modo que es mejor pedir al usaurio confirmación de lo que usará, así como advertir que haga un correcto uso de mayúsculas y minúsculas.

 ###  Pasos
 Crearemos una carpeta donde tendremos los requeriments, dockerfile y dos archivos python (wikipedia_app y wikipod) [Es necesario estudiar mirando los archivos de las carpetas]
  - Dockerfile: En este archivo que no tiene extensión (mas debe ser con el exacto nombre con la primera D mayúscula para que lo reconozca docker por comandos), será el que índique a docker como dockerizar nuestra app. Su estructura es la siguiente:
    - "FROM python:3.6.3": le dice a docker la versión de python a usar.
    - "ENV MONGO_HOST localhost", 
    "ENV MONGO_PORT 27017": variables de ambiente. Pueden entenderse como constantes globales que usaremos mas adelante en nuestro código.
    - "COPY ./requirements.txt /requirements.txt": Esto dice a docker que tome el archivo que está en la carpeta desde donde encontró el Dockerfile (eso significa el ./) y lo guarde en la carpeta propia de el contenedor, el cual quedará isolado del ambiente, razón por la cual necesitamos por medio del Dockerfile llevar la información necesaria.
    - Junto a este copy debemos hacer lo mismo para los otros dos archivos python.
    - "RUN pip install -r /requirements.txt": Le decimos que corra en una línea de comandos la siguiente línea que empieza desde pip, con lo cual tomará cada una de las extensiones que necesita nuestra app y colocamos en el archivo requirements.txt (Este hace referencia al archivo requirements que está en el contenedor, no el de nuestra carpeta. Por eso el COPY de este archivo se hace previo al de los dos archivos pyhton, para ejecutarlo en comandos).
    - "CMD ["python", "wikipedia_app.py"]": Finalmente dice que debe ejecutar en linea de comandos activa y visiblemente un archivo python llamado wikipedia_app.py. 
    Ahora veremos el contenido de el segundo archvo.
 - requirements.txt: Solo tendremos el nombre de las extensiones y si deseamos así tambipen la versión específica que deseamos. En nuestro caso solo haremos uso de dos extensiones:
    -  wikipedia==1.4.0 : Nos permitirá obtener datos de la página.
     - pymongo==3.9.0 : Nos permitirá trabajar con mongo dentro de pyhton.
 - wikipedia_app.py: En esta parte de nuestra aplicación solo llamaremos la función. Este tipo de estructura mas tipo monolítica tiene la intención de extender la aplicación a mas servicios o funcionalidades, aunque por ahora solo hace uso de la única clase que encontraremos en nuestro siguiente archivo.
  - wikipod.py: Esta es nuestra aplicación principal. Daremos un pequeño análisis al código. 
    - Creamos dos variables globales DATABASE y COLLECTION, las cuales serán los nombres de nuestra base de datos y colección que crearemos en mongo para poder guardar nuestras busquedas.
    - Luego todo se crea bajo la clase de Wikipod el cual tendrá tres partes principales.
        - El constructor de toda la vida. 
        - subir_mensaje: Esta función tendrá como princiál misión tomar el mensake que le es dado, conectarse a la base de datos y alojar el archivo en la colección antes especificada. En este caso lo único que guardamos son el titulo y el contenido de la busqueda de wikipedia.
        - buscarDato: Esta función hará todo el trabajo principal de buscar lo que deseamos con la api de wikipedia, aunque con todo es muy simple. Lo primero será preguntar a el usuario por la palabra que busca de wikipedoa a traves de input. Luego usa la función de wikipedia llamada search. Esta función nos regresará una lista de artículos que contienen la palabra o palabras buscadas. Debido a que es necesario ser específico a la hora de pedir artículos imprimiremos en pantalla todas estas posibilidades y pediremos una segunda vez que el usuario eliga una de esos articulos ingresado con cuidado de mayúsculas y minúsculas. Al usuario ingresar esta segunda vez el artículo deseado se usara la función page la cual bajará la información necesaria y luego mandar los datos a la función vista de subir_mensaje para ingresarlo en la base de datos.

    Finalmente Necesitaremos solamente ejecutar el contenedor. Esto se hace desde la terminal con dos simples comandos.
    El primero es "docker build -t Wikipod .",  el cual construirá el contenedor según las especificaciones que dimos en Dockerfile. El segundo comando es "docker run -ti Wikipod", el cual ejecutará el contenedor y gracias al flag -ti sera con una ejecución de comandos activo.