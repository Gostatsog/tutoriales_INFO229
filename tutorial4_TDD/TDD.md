# Tutorial TDD
(introducción obtenida del github del ramo INFO229)
El TDD (test drive development) es una práctica simple de desarrollo de software que recomienda a un equipo de desarrolladores seguir tres pasos (en este orden) para crear software:

1. Escribir una prueba que falla de una funcionalidad del software 
2. Escribir el código mínimo para que la prueba pase
3. Refactorizar el código según sea necesario

Este proceso se conoce comúnmente como el ciclo **Red-Green-Refactor**.

1. Se escribe una prueba automatizada de cómo debería comportarse el nuevo código - **Rojo**
2. Se escribe el código en la aplicación hasta que su prueba pase - **Verde**
3. Se refactoriza el código para hacerlo más legible y eficiente. No hay necesidad de preocuparse de que la refactorización rompa la nueva función, sólo tiene que volver a ejecutar la prueba y asegurarse de que pasa.  - **Refactor**

Buscaremos aplicar los conceptos mas basicos de TDD a través de un ejercicio dado en el contexto de INFO229 de la Universidad Austral de Chile bajo el profesor Mathew Vernier.

## Ejercicio
Aplicar el test en una aplicación flask dockerizada. La aplicación Consistirá en una pagina web donde se publicaran pensamientos parecido al modo en que twitter permite publicar. Hará uso de una base de datos donde guardar la información y deberá tener una arquitectura como lo que sigue:
@import "tutorial_data/aaaa.png"

### Información de importancia
La idea y estructura del ejerecicio es tomado del libro "Hands-On Docker for Microservices with Python", de la editorial Packt. La mayor parte del tutorial será basado en el idioma ingles, a expecion del presente tutorial que guiará paso a paso como entender el código.

## Paso a paso

### A tener en cuenta
1. Debido a que estará conectado externamente se necesitará una capa de seguridad que impida la acción de usuarios no autorizados. Esta capa será dada por un header, el cual tendrá información dada por el usuario backend, verificando su origen. Esto lo haremos por medio de un token JWT (JSON Web Token) el cual es un estándar y explicaremos en detalle mas tarde.
2. Se usaran los principios del diseño RESTful en nuestra API. Esto significa el uso de URIs construidos que representarán recursos y luego usar metodos HTTP para lograr acciones sobre estos recursos. La siguiente tabla tiene la siguiente estructura: URI, Endpoint, ¿Requiere autentificación?, Retorno.
    @import "tutorial_data/Apiendpoints.csv"

  - Expliquemos que significan estos elementos. Primero veamos nuestros endpoints. Tenemos dos elementos del API: una que empieza con /api y otra con /admin. En el caso de la primera tiene aun otra integrada dentro que es **/api/me** la cual será solo para publico autorizado (el usuario necesita autentificarse para hacer acciones en ese nivel), mientras que aquellas que van a solamente **/api** (como 3 de los GET que están en la tabla) serán para cualquier usuario  que ingrese en la página. Por el otro lado tenemos un API admin **/admin** que no sera expuesto publicamente. Como el nombre sugiere,permitirá operaciones que no estan diseñados sino para los administradores de la página.
3. El formato de un pensamiento es como sigue:
  @import "tutorial_data/pensamiento"
  - De tener en cuenta es que solo se necesitará del texto para ser creado, pues tanto en timestamp, ID como username son creados automaticamente por la data de autentificación. 
4. Un punto que recordar al crear recursos URI es si lo finalizamos con un slash (/) o no, pues al trabajar por ejemplo en Flask si lo hacemos de tal manera nos arrojará un código de status **308 PERMANENT_REDIRECT**, por una request sin un final apropiado. Solo busca ser consistente con tus decisiones.
5. La base de datos que usaremos será simple, pues solo nos preocupa guardar los datos de los pensamientos. Serán guardados en una tabla llamada thought_model, de modo que la estructura quede como sigue:

@import "tutorial_data/thought_model.png"
  - el codigo de esta tabla esta representada en código en thoughts_backend/models.py, descrita en formato SQLAlchemy con el siguiente codigo:
  @import "tutorial_data/models"
  - En este caso usamos este moedlo con fines de testeo, mas puede ser usado en modo de desarrollo.

## Trabajando con SQLAlchemy
SQLAlchemy es un modulo python para trabajar con base de datos SQL. Por lo general hay dos enfoques al lidiar con base de datos en un lenguaje de alto nivel como pyhton. 
 - El primer enfoque es uno de bajo-nivel,  haciendo estamentos SQL puros, devolviendo la data que hay en la base de datos como toda la vida. En el caso de este enfoque existe una específicación de API de base de datos para Pyhton llamado PEP 249 que puede  leerse en el siguiente [link](https://www.python.org/dev/peps/pep-0249/). Esta especificación es bien seguida por la mayoría de base de datos como el [psycopg2](http://initd.org/psycopg/) que adapta PostgreSQL para Python. Este crea principalmente comandos string SQL, los ejecuta, y parsea los resultados. Esto es útil para especificar cada consulta, mas muy improductivo para operaciones comunes que lleguen a ser repetidas una y otra vez. [PonyORM](https://ponyorm.org/) es otro ejemplo de un nivel no ten bajo pero que aún persiste con la práctica de replicar la sintáxis y estructura SQL. 
 - El segundo enfoque es resumir la base de datos usando un **Object-Relatonal Mapper (ORM)** (Mapeo objeto-relacional), y usar la interfaz sin entrar en los detalles de como se implementa. El mejor ejemplo de este caso es probablemente [Django_ORM](https://docs.djangoproject.com/en/2.2/topics/db/), el cual, como decíamos, resume el acceso a la  base de datos usando un modelo definido de objetos python. Es fantástico para operaciones comunes, mas su modelo asume que la definición de la base de datos esta hecha en nuestro código Python, y mapear base de datos legacy puede ser algo traumantemente tedioso. Algunas operaciones complejas SQL creadas por el ORM pueden conllevar mucho tiempo por lo demás, mientras algo mas como el primer enfoque puede ahorrarnos tiempo. Por último puede también ser que estemos realizando lentísimas consultas sin siquiera darnos cuenta, solo porque la herramienta de nos resume demasiado del resultado final. 

 SQLAlchemy es bastante flexible y puede trabajar en ambos lados del espectro ya visto. Puede ser un tanto complicado en comparación con Django ORM, pero nos permite mapear las base de datos existentes dentro del ORM. Su flexibilidad es la razón principal por la cual la usaremos en el proyecto, pues puede tomar una existente y complicada base de datos legacy y mapearla, permitiendo desempeñar operaciones simples y complicadas en la manera exacta que quieras.
 (De recordar es que con todo no explicaremos a fondo como usar SQLAlchemy mas que explicar lo necesario para el presente proyecto lo cual será bastante simple. Con todo en el caso de estar migrando una compleja estructura monolítica a microservicios puede ser una buena herramienta de apoyo al tratar de la misma manera que en el monolítico las consultas SQL. En pocas palabras, si estas lidiando con base de datos complicadas aprender SQLAlchemy es invaluable. Podrás ejecutar tareas de alto y bajo nivel eficientemente, pero requerira un buen entendimiento de la materia). 

 Para finalizar solo redirigir por si quieren aprender mas acerca de SQLAlchemy y su integración a python. Pueden seguir el siguiente [link](https://flask-sqlalchemy.palletsprojects.com/en/2.x/).

### Ejemplos de uso de SQLAlchemy
 Al definir nuestro modelo podemos ejecutar consultas al usar el atributo **query** en el modelo y filtrar en consecuencia:
 @import "tutorial_data/SQLAl1"
  - En la segunda línea se muestra como obtener un pensamiento guardado en la base de dato según su thought_id (según la estructura de thought ya vista).  En la tercera línea recopilamos todos los pensamientos guardados de un usaurio en específico y posteriormente, con la función order_ by('id').all() lo que hacemos es darle un orden a la lista retornada.
Veamos ahora como guardar y eliminar filas. Para ello necesitaremos el uso de la sesión y luego committing (no encuentro una palabra entendible para traducir el concepto pero es una idea similar al concepto de commit de git). Veamos el código:
@import "tutorial_data/SQLAl2"
 - No hay mucho que decir pues el código se explica bastante bien. Interesante es prestar atención a la estructura del nuevo pensamiento dado en la segunda línea. Luego la tercera línea aplica una función, en este caso **add** que quiere decir añadir, y luego en la cuarta linea hace el commit para que se actualice en la base de datos. Para el caso de eliminar es similar la estructura. Primero se toma uno de los pensamientos tomados según su el id del pensamiento, luego se aplica **delete** y finalmente se hace commit para efectuar los cambios en la base de datos. En el código dado en *ThoughtsBackend/thought_backend/db.py*, puede verse el código usado para la presente aplicación donde queda a disposición del administrador el ejecutar en formato SQLITE o POSTGRESQL.

## Trabajando con Flask

Para el proyecto trabajaremos con [Flask-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/). Este es una extensión [Flask](https://palletsprojects.com/p/flask/). En resumidas cuentas flask es un conocido microframework de Python para aplicaciones web que es particularmente bueno en implementar microservicios, debido a su pequeño tamaño, su facilidad de uso, y compatibilidad con la  usual pila de tecnologías en términos de aplicaciones web, esto último dado su uso de el protocolo **Web Server Gateway Interface ([WSGI](https://wsgi.readthedocs.io/en/latest/what.html))**.
Tenemos que con Flask somos capaces de implementar una interfaz RESTful, mas Flask-RESTPlus añade características muy interesantes que permitiran buenas prácticas y velocidad de desarrollo. Entre lo positivo podemos destacar:
1. Define namespaces, que son formas de crear prefijos y estructurar el código. Esto ayudará a la matención a largo plazo y ayudará a nivel de diseño cuando creemos nuevos endpoints. (De notar es que si tenemos mas de 10 endpoints asociados a un solo namespace bueno sería el considerar dividirlo. Lo recomendado es un namespace por archivo, a lo cual el tamaño de tal archivo debiera sernos buen indicio si es necesario hacer una división).
2. Tiene una solución completa para parsear parametros de entrada. En pocas palabras quiere decir que tendremos una manera mas sencilla de lidiar con los endpoints que requieren una gran cantidad de paramentros y validarlos. Usando el módulo *[Request_Parsing](https://flask-restplus.readthedocs.io/en/stable/parsing.html)* es similar a usar el módulo de línea de comandos *[argparse](https://docs.python.org/3/library/argparse.html)* que esta incluido por defecto en la librería de Python. La utilidad yace en poder definir los argumentos en el cuerpo de solicitudes (request), headers, strings de consultas, o incluso cookies.
3. De la misma forma tiene un framework de serialización para los objetos resultantes. Flask-RESTful le llama **[response_marshalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html)**. Esto ayuda a definir objetos que pueden ser reusados, clarificando la interfaz y simplificando el desarrollo. Si se habilita permite también asi mismo field mask, que retornan objetos parciales.
4. Tiene una completa documentación API Swagger de soporte. [Swagger](https://swagger.io/) es un proyecto open-source (aleluya!!) que nos ayuda en el diseño, implementación, documentación y testeo de servicios web RESTful API, siguiendo las especificaciones estándar OpenAPI. Con Flask-RESTPlus automaticamente generaremos una especificación Swagger y una página autodocumentada como vemos a continuación:
@import "tutorial_data/SwaggerWeb.png"

Por otro lado, lo positivo de Flask viene del hecho que es un proyecto popular y tiene en consiguiente muchas herrmientas que le han dado soporte, como por ejemplo:
 - El conector para SQLAlchemy, [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/). Su documentación cubre la mayoría de los casos comunes, mientras que la documentación de SQLAlchemy (ya dado el link mas arriba) es mas detallado y puede ser algo abrumador.

 - Para ejecutar las pruebas el módulo *[pytest-flask](https://pytest-flask.readthedocs.io/en/latest/)* crea algunos accesorios listos para trabajar con una aplicación Flask. De ello hablaremos en un momento mas.

## Manipulación de recursos
Una apliación tipica RESTful tiene la siguiente estructura general:
1. Un recurso definido por URL. Este recurso permite una o mas acciones por medio de metodos HTTP (*GET*,*POST*, y así otros).
2. Cuando cualquiera de las acciones son invocadas el framework rutea la solicitud hasta que el código especializado ejecuta la acción.
3. Si hay algún parametro de entrada deben pasar por validación primeramente.
4. Desempeñar la acción y obtener su valor. Esta acción normalmente tendra en cuenta uno o mas llamadas a la base de datos, lo cual será hecho en la forma de modelos. 
5. Preparar los valores de resultado devueltos y codificarlos de forma entendible al cliente, tipicamente en JSON.
6. Devolver el valor codificado al cliente con el adecuado codigo de status. 

Estas acciones en su mayoría son hechas por el framework. Algun trabajo de configuracion necesita ser hecho, pero es donde nuestro framework web (FLASK-RESTPlus en nuestro ejemplo) será de mas ayuda. En particular, todo desde el paso 4 será simplificado en gran manera.

Veamos un código bastante simple de ejemplo:
@import "tutorial_data/FlaskExample"
 - En este código podemos ver en práctica lo que hemos hablado. La primera línea de código definimos el recurso por su URL, seteando a *api_namespace* el prefijo **api** a la URL. Luego en el decorador se valida el parametro **X** como un entero. En este caso podemos ejecutar varias acciones en el mismo recurso, mas en el ejemplo solo haremos una accion **GET**. En este caso la funcionalidad que implementa en específico es la acción **GET /api/thoughts/X/**, devolviendo un solo pensamiento por el ID 'X'. De notar es que el parametro *Thought_id*, codigicado en la URL, se pasa como parametro al método (en *def get()*). Luego dentro de *def get()* ejecutamos la acción, la cual será una busqueda en la base de datos para retornar un solo objeto. Llama a *ThoughtModel* para buscar por el pensamiento especificado. Si se encuentra se devuelve con un codigo de status *http.client.OK (200)*. Si no lo enccuentra el resultado es vacío y un código de status *http.client.NOT_FOUND 404* es devuelto. El decordaor *marshal_with* describe como el objeto Pyhton debe ser serializado como una estructura JSON. Mas adelante veremos como configurarlo. Finalmente dentro de *def get(self, thought_id)* tenemos alguna documentación, incluido el docstring que será reproducido por la API Swagger autogenerada.

Como pudo ser visto, la mayoría de las acciones son configuradas y ejecutadas a través de Flask-RESTPlus, y la mayor parte del trabajo como desarrollador es la jugosa parte 4. Con todo hay trabajo que hacer, como configurar lo que los esperados parametros de entrada seran y validarlos, asi como también serializar los objetos retornados en un apropiado JSON.  Veremos como Flask-RESTPlus nos puede ayudar.

### Parsear parámetros de entrada

Los parámetros de entrada pueden tomar dos formas diferentes. Cuando hablamos acerca de parametros de entrada hablamos generalmente de dos tipos diferentes:
 - String de consultas de parámetros codificadas dentro de la URL. Estos normalmente son usados para las solicitudes GET, los cuales son algo como *http://test.com/some/path?param1=X&param2=Y*. Estas son parte de la URL y serán almacenados en cualquier registro por el camino. Los parámetros están codificados en su respectivo formato, llamado *[URL_encoding](https://www.urlencoder.io/learn/)*. Te has dado cuenta probablemente, por ejemplo, como un espacio en blanco se transforma en *%20*. (Por lo general no tenemos que decodificar pues frameworks como Flask lo hacen por nosotros, mas Pyhton en su librería estándar tiene utilidades para ello como [urllib.parse](https://docs.python.org/3/library/urllib.parse.html)).
