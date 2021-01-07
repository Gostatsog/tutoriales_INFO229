#  Varios Tutoriales y proyecto
  
(introducción obtenida del github del ramo INFO229)
El TDD (test drive development) es una práctica simple de desarrollo de software que recomienda a un equipo de desarrolladores seguir tres pasos (en este orden) para crear software:
  
1. Escribir una prueba que falla de una funcionalidad del software 
2. Escribir el código mínimo para que la prueba pase
3. Refactorizar el código según sea necesario
  
Este proceso se conoce comúnmente como el ciclo **Red-Green-Refactor**.
  
1. Se escribe una prueba automatizada de cómo debería comportarse el nuevo código - **Rojo**
2. Se escribe el código en la aplicación hasta que su prueba pase - **Verde**
3. Se refactoriza el código para hacerlo más legible y eficiente. No hay necesidad de preocuparse de que la refactorización rompa la nueva función, sólo tiene que volver a ejecutar la prueba y asegurarse de que pasa.  - **Refactor**
  
  
##  Ejercicio
  
Desarrollaremos un microservicio web dockerizado. Dentro del proyecto usaremos una multitud de herramientas que serán explicadas, las cuales servirán por igual en reemplazo de los tutoriales individuales desde el 4 en adelante (espero xd). Entre las herramientas tenemos Flask-RESTPlus, SQLAlchemy, pytest, y otros módulos de python que estas herramientas necesitarán para expandir su funcionalidad. Hay un estudio del uso de tokens y en general un enfoque sobre los principios REST para el desarrollo de la API. La estructura general será la que se ve en la imágen a continuación (en una buena parte):
![](tutorial_data/aaaa.png?0.3570883234254578 )  
  
###  Información de importancia
  
La idea y estructura del ejerecicio es tomado del libro "Hands-On Docker for Microservices with Python", de la editorial Packt. El tutorial está en idioma ingles con lo que el mayor trabajo de este gran tutorial es traspasarlo a un español entendible (habrán palabras que preferí dejar en su idioma nativo por falta de un mejor concepto en nuestro idioma español), además de expandir conceptos y aterrizar ciertas partes del código para no sentirse perdido. Una carácterística importante del tutorial es que, aunque no profundiza en cada concepto y herramienta usada (solo lo necesario para entender nuestro código), da link de documentación de cada herramienta usada, así como de cada alternativa que valía la pena mencionar en el camino.
  
##  INTRODUCCIÓN
  
  
###  A tener en cuenta
  
1. Debido a que estará conectado externamente se necesitará una capa de seguridad que impida la acción de usuarios no autorizados. Esta capa será dada por un header, el cual tendrá información dada por el usuario backend, verificando su origen. Esto lo haremos por medio de un token JWT (JSON Web Token) el cual es un estándar y explicaremos en detalle mas tarde.
2. Se usaran los principios del diseño RESTful en nuestra API. Esto significa el uso de URIs construidos que representarán recursos y luego usar metodos HTTP para lograr acciones sobre estos recursos. La siguiente tabla muestra la estructura general de nuestra API.
  
|0| Endpoint| ¿Requiere autentificación?| Retorno|  
|---|---|---|---|  
|GET| /api/me/thoughts|Si| Lista de pensamientos del usuario|  
|POST| /api/me/thoughts| Si| El pensamiento nuevo creado|  
|GET| /api/thoughts| No| Lista de pensamientos|  
|GET| /api/thoughts/X/	| No| El pensamiento con ID X|  
|GET| /api/thoughts/?search=X	| No| Busca todos los pensamientos que contienen X|  
|DELETE| /admin/thoughts/X/	| No| Elimina el pensamiento con ID X|  
  
  
  - Expliquemos que significan estos elementos. Primero veamos nuestros endpoints. Tenemos dos elementos del API: una que empieza con /api y otra con /admin. En el caso de la primera tiene aun otra integrada dentro que es **/api/me** la cual será solo para publico autorizado (el usuario necesita autentificarse para hacer acciones en ese nivel), mientras que aquellas que van a solamente **/api** (como 3 de los GET que están en la tabla) serán para cualquier usuario  que ingrese en la página. Por el otro lado tenemos un API **/admin** que no sera expuesto publicamente. Como el nombre sugiere, permitirá operaciones que no estan diseñados sino para los administradores de la página.
3. El formato de un pensamiento es como sigue:
  ```   
thought
{
    id integer
    username string
    text string
    timestamp string($data-time)
}
```  
  - De tener en cuenta es que, si se desea, solo se necesitará del texto para ser creado pues tanto el timestamp, ID como username pueden ser creados automaticamente por los datos de autentificación. 
4. Un punto que recordar al crear recursos URI es si lo finalizamos con un slash (/) o no, pues al trabajar por ejemplo en Flask si lo hacemos de tal manera nos arrojará un código de status **308 PERMANENT_REDIRECT**, por una request sin un final apropiado. Solo busca ser consistente con tus decisiones.
5. La base de datos que usaremos será simple, pues solo nos preocupa guardar los datos de los pensamientos. Serán guardados en una tabla llamada thought_model, de modo que la estructura quede como sigue:
  
![](tutorial_data/thought_model.png?0.8658242447046256 )  
  - el codigo de esta tabla esta representada en código en thoughts_backend/models.py, descrita en formato SQLAlchemy con el siguiente codigo:
  ```   
class ThoughtModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))    
    text = db.Column(db.String(250))    
    timestamp = db.Column(db.DateTime, server_default=func.now())
```  
  - En este caso usamos este moedlo con fines de testeo, mas puede ser usado en modo de desarrollo.
  
##  Trabajando con SQLAlchemy
  
SQLAlchemy es un modulo python para trabajar con base de datos SQL. Por lo general hay dos enfoques al lidiar con base de datos en un lenguaje de alto nivel como pyhton. 
 - El primer enfoque es uno de bajo-nivel,  haciendo estamentos SQL puros, devolviendo la data que hay en la base de datos como toda la vida. En el caso de este enfoque existe una específicación de API de base de datos para Pyhton llamado PEP 249 que puede  leerse en el siguiente [link](https://www.python.org/dev/peps/pep-0249/ ). Esta especificación es bien seguida por la mayoría de base de datos como el [psycopg2](http://initd.org/psycopg/ ) que adapta PostgreSQL para Python. Este crea principalmente comandos string SQL, los ejecuta, y parsea los resultados. Esto es útil para especificar cada consulta, mas muy improductivo para operaciones comunes que lleguen a ser repetidas una y otra vez. [PonyORM](https://ponyorm.org/ ) es otro ejemplo de un nivel no ten bajo pero que aún persiste con la práctica de replicar la sintáxis y estructura SQL. 
 - El segundo enfoque es resumir la base de datos usando un **Object-Relatonal Mapper (ORM)** (Mapeo objeto-relacional), y usar la interfaz sin entrar en los detalles de como se implementa. El mejor ejemplo de este caso es probablemente [Django_ORM](https://docs.djangoproject.com/en/2.2/topics/db/ ), el cual, como decíamos, resume el acceso a la  base de datos usando un modelo definido de objetos python. Es fantástico para operaciones comunes, mas su modelo asume que la definición de la base de datos esta hecha en nuestro código Python, y mapear base de datos legacy puede ser algo traumantemente tedioso. Algunas operaciones complejas SQL creadas por el ORM pueden conllevar mucho tiempo por lo demás, mientras algo mas como el primer enfoque puede ahorrarnos tiempo. Por último puede también ser que estemos realizando lentísimas consultas sin siquiera darnos cuenta, solo porque la herramienta de nos resume demasiado del resultado final. 
  
 SQLAlchemy es bastante flexible y puede trabajar en ambos lados del espectro ya visto. Puede ser un tanto complicado en comparación con Django ORM, pero nos permite mapear las base de datos existentes dentro del ORM. Su flexibilidad es la razón principal por la cual la usaremos en el proyecto, pues puede tomar una existente y complicada base de datos legacy y mapearla, permitiendo desempeñar operaciones simples y complicadas en la manera exacta que quieras.
 (De recordar es que con todo no explicaremos a fondo como usar SQLAlchemy mas que explicar lo necesario para el presente proyecto lo cual será bastante simple. Con todo en el caso de estar migrando una compleja estructura monolítica a microservicios puede ser una buena herramienta de apoyo al tratar de la misma manera que en el monolítico las consultas SQL. En pocas palabras, si estas lidiando con base de datos complicadas aprender SQLAlchemy es invaluable. Podrás ejecutar tareas de alto y bajo nivel eficientemente, pero requerira un buen entendimiento de la materia). 
  
 Para finalizar solo redirigir por si quieren aprender mas acerca de SQLAlchemy y su integración a python. Pueden seguir el siguiente [link](https://flask-sqlalchemy.palletsprojects.com/en/2.x/ ).
  
###  Ejemplos de uso de SQLAlchemy
  
 Al definir nuestro modelo podemos ejecutar consultas al usar el atributo **query** en el modelo y filtrar en consecuencia:
 ```   
# Retrieve a single thought by its primary key
thought = ThoughtModel.query.get(thought_id)
  
# Retrieve all thoughts filtered by a username
thoughts = ThoughtModel.query.filter_by(username=username).order_by('id').all()
```  
  - En la segunda línea se muestra como obtener un pensamiento guardado en la base de dato según su thought_id (según la estructura de thought ya vista).  En la tercera línea recopilamos todos los pensamientos guardados de un usaurio en específico y posteriormente, con la función order_ by('id').all() lo que hacemos es darle un orden a la lista retornada.
Veamos ahora como guardar y eliminar filas. Para ello necesitaremos el uso de la sesión y luego committing (no encuentro una palabra entendible para traducir el concepto pero es una idea similar al concepto de commit de git). Veamos el código:
```   
# Create a new thought
new_thought = ThoughtModel(username=username, text=text, timestamp=datetime.utcnow())
db.session.add(new_thought)
db.session.commit()
  
# Retrieve and delete a thought
thought = ThoughtModel.query.get(thought_id)
db.session.delete(thought)
db.session.commit()
```  
 - No hay mucho que decir pues el código se explica bastante bien. Interesante es prestar atención a la estructura del nuevo pensamiento dado en la segunda línea. Luego la tercera línea aplica una función, en este caso **add** que quiere decir añadir, y luego en la cuarta linea hace el commit para que se actualice en la base de datos. Para el caso de eliminar es similar la estructura. Primero se toma uno de los pensamientos tomados según su el id del pensamiento, luego se aplica **delete** y finalmente se hace commit para efectuar los cambios en la base de datos. En el código dado en *ThoughtsBackend/thought_backend/db.py*, puede verse el código usado para la presente aplicación donde queda a disposición del administrador el ejecutar en formato SQLITE o POSTGRESQL.
  
##  Trabajando con Flask
  
  
Para el proyecto trabajaremos con [Flask-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/ ). Este es una extensión [Flask](https://palletsprojects.com/p/flask/ ). En resumidas cuentas flask es un conocido microframework de Python para aplicaciones web que es particularmente bueno en implementar microservicios, debido a su pequeño tamaño, su facilidad de uso, y compatibilidad con la  usual pila de tecnologías en términos de aplicaciones web, esto último dado su uso de el protocolo **Web Server Gateway Interface ([WSGI](https://wsgi.readthedocs.io/en/latest/what.html ))**.
Tenemos que con Flask somos capaces de implementar una interfaz RESTful, mas Flask-RESTPlus añade características muy interesantes que permitiran buenas prácticas y velocidad de desarrollo. Entre lo positivo podemos destacar:
1. Define namespaces, que son formas de crear prefijos y estructurar el código. Esto ayudará a la matención a largo plazo y ayudará a nivel de diseño cuando creemos nuevos endpoints. (De notar es que si tenemos mas de 10 endpoints asociados a un solo namespace bueno sería el considerar dividirlo. Lo recomendado es un namespace por archivo, a lo cual el tamaño de tal archivo debiera sernos buen indicio si es necesario hacer una división).
2. Tiene una solución completa para parsear parametros de entrada. En pocas palabras quiere decir que tendremos una manera mas sencilla de lidiar con los endpoints que requieren una gran cantidad de paramentros y validarlos. Usando el módulo *[Request_Parsing](https://flask-restplus.readthedocs.io/en/stable/parsing.html )* es similar a usar el módulo de línea de comandos *[argparse](https://docs.python.org/3/library/argparse.html )* que esta incluido por defecto en la librería de Python. La utilidad yace en poder definir los argumentos en el cuerpo de solicitudes (request), headers, strings de consultas, o incluso cookies.
3. De la misma forma tiene un framework de serialización para los objetos resultantes. Flask-RESTful le llama **[response_marshalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html )**. Esto ayuda a definir objetos que pueden ser reusados, clarificando la interfaz y simplificando el desarrollo. Si se habilita permite también asi mismo field mask, que retornan objetos parciales.
4. Tiene una completa documentación API Swagger de soporte. [Swagger](https://swagger.io/ ) es un proyecto open-source (aleluya!!) que nos ayuda en el diseño, implementación, documentación y testeo de servicios web RESTful API, siguiendo las especificaciones estándar OpenAPI. Con Flask-RESTPlus automaticamente generaremos una especificación Swagger y una página autodocumentada como vemos a continuación:
  
![](tutorial_data/SwaggerWeb.png?0.3939629653869554 )  
  
Por otro lado, lo positivo de Flask viene del hecho que es un proyecto popular y tiene en consiguiente muchas herrmientas que le han dado soporte, como por ejemplo:
 - El conector para SQLAlchemy, [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/ ). Su documentación cubre la mayoría de los casos comunes, mientras que la documentación de SQLAlchemy (ya dado el link mas arriba) es mas detallado y puede ser algo abrumador.
  
 - Para ejecutar las pruebas el módulo *[pytest-flask](https://pytest-flask.readthedocs.io/en/latest/ )* crea algunos accesorios listos para trabajar con una aplicación Flask. De ello hablaremos en un momento mas.
  
##  Manipulación de recursos
  
Una apliación tipica RESTful tiene la siguiente estructura general:
1. Un recurso definido por URL. Este recurso permite una o mas acciones por medio de metodos HTTP (*GET*,*POST*, y así otros).
2. Cuando cualquiera de las acciones son invocadas el framework rutea la solicitud hasta que el código especializado ejecuta la acción.
3. Si hay algún parametro de entrada deben pasar por validación primeramente.
4. Desempeñar la acción y obtener su valor. Esta acción normalmente tendra en cuenta uno o mas llamadas a la base de datos, lo cual será hecho en la forma de modelos. 
5. Preparar los valores de resultado devueltos y codificarlos de forma entendible al cliente, tipicamente en JSON.
6. Devolver el valor codificado al cliente con el adecuado codigo de status. 
  
Estas acciones en su mayoría son hechas por el framework. Algun trabajo de configuracion necesita ser hecho, pero es donde nuestro framework web (FLASK-RESTPlus en nuestro ejemplo) será de mas ayuda. En particular, todo desde el paso 4 será simplificado en gran manera.
  
Veamos un código bastante simple de ejemplo:
```   
api_namespace = Namespace('api', description='API operations')
  
@api_namespace.route('/thoughts/<int:thought_id>/')
class ThoughtsRetrieve(Resource):   
  
    @api_namespace.doc('retrieve_thought')    
    @api_namespace.marshal_with(thought_model)    
    def get(self, thought_id):
        '''        
        Retrieve a thought        
        '''        
        thought = ThoughtModel.query.get(thought_id)        
        if not thought:          
  
            # The thought is not present            
            return '', http.client.NOT_FOUND        
  
        return thought
```  
 - En este código podemos ver en práctica lo que hemos hablado. La primera línea de código definimos el recurso por su URL, seteando a *api_namespace* el prefijo **api** a la URL. Luego en el decorador se valida el parametro **X** como un entero. En este caso podemos ejecutar varias acciones en el mismo recurso, mas en el ejemplo solo haremos una accion **GET**. En este caso la funcionalidad que implementa en específico es la acción **GET /api/thoughts/X/**, devolviendo un solo pensamiento por el ID 'X'. De notar es que el parametro *Thought_id*, codigicado en la URL, se pasa como parametro al método (en *def get()*). Luego dentro de *def get()* ejecutamos la acción, la cual será una busqueda en la base de datos para retornar un solo objeto. Llama a *ThoughtModel* para buscar por el pensamiento especificado. Si se encuentra se devuelve con un codigo de status *http.client.OK (200)*. Si no lo enccuentra el resultado es vacío y un código de status *http.client.NOT_FOUND 404* es devuelto. El decordaor *marshal_with* describe como el objeto Pyhton debe ser serializado como una estructura JSON. Mas adelante veremos como configurarlo. Finalmente dentro de *def get(self, thought_id)* tenemos alguna documentación, incluido el docstring que será reproducido por la API Swagger autogenerada.
  
Como pudo ser visto, la mayoría de las acciones son configuradas y ejecutadas a través de Flask-RESTPlus, y la mayor parte del trabajo como desarrollador es la jugosa parte 4. Con todo hay trabajo que hacer, como configurar lo que los esperados parametros de entrada seran y validarlos, asi como también serializar los objetos retornados en un apropiado JSON.  Veremos como Flask-RESTPlus nos puede ayudar.
  
###  Parsear parámetros de entrada
  
  
Los parámetros de entrada pueden tomar diferentes formas. Cuando hablamos acerca de parametros de entrada podemos referirnos a:
 - **String de consultas de parámetros codificadas dentro de la URL**. Estos normalmente son usados para las solicitudes GET, los cuales son algo como *http://test.com/some/path?param1=X&param2=Y*. Estas son parte de la URL y serán almacenados en cualquier registro por el camino. Los parámetros están codificados en su respectivo formato, llamado *[URL_encoding](https://www.urlencoder.io/learn/ )*. Te has dado cuenta probablemente, por ejemplo, como un espacio en blanco se transforma en *%20*. (Por lo general no tenemos que decodificar pues frameworks como Flask lo hacen por nosotros, mas Pyhton en su librería estándar tiene utilidades para ello como [urllib.parse](https://docs.python.org/3/library/urllib.parse.html )). Pensemos por ejemplo en el cuerpo de una solicitud HTTP, tipicamente usada en solicitudes POST y PUT. El formato específico puede ser especificado usando el header(encabezado) *Content-type*. Por defecto este header se define como *aplication/x-www-form-urlencoded*, lo que lo codifica en codificación URL. En aplicaciones modernas esto se reemplaza con *application/json* para codificarlo en JSON. (El cuerpo de la solicitud no es guardado en registros, pues se espera que la solicitud GET produzca los mismos resultados al ser llamados muchas veces, osea que sea idempotente. Esto implica que pueda ser guardado en caché por algunos proxies y otros elementos. Esta es la razón por la que se te pide confirmación antes de enviar un solicitud POST por segunda vez, pues esta operación bien podrá dar resultados diferentes).
 - **Como parte de una URL**. Cosas como *thought_id* son parametros. Para evitar confusiones en contextos mas complejos intenta seguir principios RESTful y definir como recursos tus URLs.
 - **Headers**. Normalmente un header da información acerca de metadatos, tales como el formato de la solicitud, el formato esperado, o autentificación de datos. Con todo deben ser tratados igualmente como parametros.
  
Todos estos elementos son decodificados por Flask-RESTPlus (Aleluya! x2), de modo que no tenemos que lidiar con codificar y accesos de bajo nivel.
  
Veamos todo esto en un ejemplo de nuestro código, simplifiacod para describir mas que nada los parametros de parseo:
```   
authentication_parser = api_namespace.parser()
authentication_parser.add_argument('Authorization', 
location='headers', type=str, help='Bearer Access 
Token')
  
thought_parser = authentication_parser.copy()
thought_parser.add_argument('text', type=str, required=True, help='Text of the thought')
  
@api_namespace.route('/me/thoughts/')
class MeThoughtListCreate(Resource):
  
    @api_namespace.expect(thought_parser)
    def post(self):
        args = thought_parser.parse_args()
        username = authentication_header_parser(args['Authorization'])
        text=args['text']
        ...
```  
  
 - Podemos ver en las primeras 7 líneas como definimos nuestro parser. Analicemos este estracto. En las línea 5 vemos que *authentification_parser* es heredado por *thought_parser*, con la razón de extender la funcionalidad y combinar ambos. Cada parámetro se defunte en terminos de tipo y sobre si son requeridos o no (línea 7). En caso que un parámetro requerido este perdido u otro elemento sea incorrecto Flask-RESTPlus dará un error *400 BAD_REQUEST*, dando algo de retroalimentación acerca de porque sucedio el error. 
Dado que queremos manipular la autentificación en una manera ligeramente diferente lo etiquetamos como no requerido y permitimos que tome el valor por defecto (en nuestro framework) de *None* (línea 2-3). Una cosa mas que notar es como especificamos que el parametro de autorización deberá estar en los headers.
 - Luego tenemos las líneas de la 9 en adelante (desde el decorador). El decorador en el método **POST** nace con el fin de especificar que se espera un parametro *thought_parser*. Luego lo parseamos con parse_args como se ve en la penúltima línea. Mas aún, *args* es ahora un diccionario con todos los parámetros propiamente parseados y usado en las líneas que siguen. Para el caso de la autentificación, por ejemplo, existe una función específica para trabajar con ello el cual retorna un código de status *401 UNAUTHORIZED* a través del uso de *abort*. Este llamado inmediatamente interrumpirá una solicitud:
 ```   
def authentication_header_parser(value):
    username = validate_token_header(value, config.PUBLIC_KEY)
    if username is None:
        abort(401)
    return username
  
  
class MeThoughtListCreate(Resource):
  
    @api_namespace.expect(thought_parser)
    def post(self):
       args = thought_parser.parse_args()
       username = authentication_header_parser(args['Authentication'])
       ...
```  
  
Ahora dejaremos algo de lado la acción a ejecutar (guardar un nuevo pensamiento en la base de datos), y nos enfocaremos en otras configuraciones de framework, para serializar los resultados en un objeto JSON.
  
###  Serializar resultados
  
Debemos devolver nuestros resultados. La manera mas fácil de hacerlo es definiendo la forma que el JSON resultante deberá tener por medio de un serializador o modelo *[marshalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html )*. Un modelo serializador es definido como un diccionario con los campos esperados y un tipo de campo, como podemos ver en el siguiente código:
```   
from flask_restplus import fields
  
model = {
    'id': fields.Integer(),
    'username': fields.String(),
    'text': fields.String(),
    'timestamp': fields.DateTime(),
}
thought_model = api_namespace.model('Thought', model)
```  
El modelo tomara un objeto Pyhton y convertirá cada uno de los atributos en su correspondiente elemento JSON, como definido en el campo(línea 4):
```   
@api_namespace.route('/me/thoughts/')
class MeThoughtListCreate(Resource):
  
    @api_namespace.marshal_with(thought_model)
    def post(self):
        ...
        new_thought = ThoughtModel(...)
        return new_thought
```  
Notemos que *new_thought* es un objeto *ThoughtModel*, como es recuperado por SQLAlchemy. Lo veremos ne mayor detalle mas adelante, mas por ahora es suficiente decir que tiene todos los atributos definidos en el modelo: *id, username, text,* y *timestamp*.
  
Cualquier atributo no presente en el objeto memoria tendrá un valor de **None** por defecto, aunque puedes cambiarlo a un valor de retorno. Para esto deberás especificar una función, de modo que se invoque para recuperar el valor cuando la respuesta se genere. Esto es una forma de agregar información dinámica a tu objeto:
```   
model = {
    'timestamp': fields.DateTime(default=datetime.utcnow),
}
```  
Puedes así mismo añadir el nombre del atributo serializado, en caso que sea diferente que la salida esperada, o añadir una función lambda que será creada para recuperar dicho valor:
```   
model = {
    'thought_text': fields.String(attribute='text'),
    'thought_username': fields.String(attribute=lambda x: x.username),
 }
```  
  
Para objetos mas complejos puedes hacer valores anidados. Hay que tener en cuenta con todo que esto definirá dos modelos desde el punto de vista de la documentación y que ese elemento anidado crea un nuevo alcance. Puedes usar tambipen *List* para añadir múltiples instancias del mismo tipo:
```   
extra = {
   'info': fields.String(),
}
extra_info = api_namespace.model('ExtraInfo', extra)
  
model = {
    'extra': fields.Nested(extra),
    'extra_list': fields.List(fields.Nested(extra)),
 }
```  
Algunos de los campos disponibles tienen mas opciones, tales como el formato de fecha para los campos de *DateTime*. Sigue el siguiente [link](https://flask-restplus.readthedocs.io/en/stable/api.html#models ) para la ducumentación completa de campos.
  
Algo interesante por ejemplo es que si devuelves una lista de elementos, añadiendo el parametro *as_list = True* en el decorador *marshal_with*, como se ve aquí:
```   
@api_namespace.route('/me/thoughts/')
class MeThoughtListCreate(Resource):
  
    @api_namespace.marshal_with(thought_model, as_list=True)
    def get(self):
        ...
        thoughts = (
            ThoughtModel.query.filter(
                ThoughtModel.username == username
            )
            .order_by('id').all()
        )
        return thoughts
```  
El decorador marshal_with transformará el objeto *result* de un objeto Python a el correspondiente objeto de datos JSON.
  
Por defecto retornará un código de status *http.client.ok (200)*, mas podemos expandir tal reotrno a dos valores: El primero siendo un objeto marshal y el segundo el código de status. El código de paramentro en el decorador *marshal_with* es usado por motivos de futura documentación. De notar en este caso es que nesecitamos añadir la llamada *marshal* específica:
```   
@api_namespace.route('/me/thoughts/')
class MeThoughtListCreate(Resource):
  
    @api_namespace.marshal_with(thought_model, 
         code=http.client.CREATED)
    def post(self):
        ...
        result = api_namespace.marshal(new_thought, thought_model)
        return result, http.client.CREATED
```  
La documentación Swagger exhibirá todos los objetos *marshal* de uso definido, de una manera como muestra la imágen:
  
![](tutorial_data/SwaggerMarshal.png?0.5005437154335108 )  
  
###  Disclaimer de Flask-RESTPlus
  
  
Un punto inconveniente de Flask-RESTPlus es que para ingresar(input) y sacar(output) los mismos objetos deben ser definidos dos veces, pues los modulos de entrada y salida son diferentes. Esto no es así en otros framework RESTful, como por ejemplo *[Django REST framework](https://www.django-rest-framework.org/ )*. Los desarrolladores que mantienen Flask-RESTPlus saben bien esto y, en concordancia, están integrando un modulo externo, que probablemente sea *[marshmallow](https://marshmallow.readthedocs.io/en/stable/ )*. Puedes integrarlo por ti mismo si quieres, ya que Flask es lo suficientemente flexible para ello. Mira el ejemplo en el siguiente [link](https://marshmallow.readthedocs.io/en/stable/examples.html#quotes-api-flask-sqlalchemy ) para mas info. Mas detalles pueden ser encontrados en la documentación completa de [marshmalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html ) por Flask-RESTPlus.
  
##  Ejecutando la acción (por fin)
  
Finalmente llegamos a la sección específica donde los datos ingresados están limpios y listos para uso, sabiendo además como devolver los resultados. Esta parte tiene que ver con ejecutar alguna(s) consulta(s) de base de datos y componer los resultados. Veamos el siguiente ejemplo:
```   
@api_namespace.route('/thoughts/')
class ThoughtList(Resource):
  
    @api_namespace.doc('list_thoughts')
    @api_namespace.marshal_with(thought_model, as_list=True)
    @api_namespace.expect(search_parser)
    def get(self):
        '''
        Retrieves all the thoughts
        '''
        args = search_parser.parse_args()
        search_param = args['search']
        # Action
        query = ThoughtModel.query
        if search_param:
            query =(query.filter(
                ThoughtModel.text.contains(search_param)))
  
        query = query.order_by('id')
        thoughts = query.all()
        # Return the result
        return thoughts
```  
  
Podemos ver aquí, luego de parsear los parametros, como usamos SQLAlchemy para recuperar una consulta que, si el parametro *search* es presente, aplicará un filtro. Obtenemos todos los resultados con el comando *all()*, retornando todos los objetos de *ThoughtModel*. 
Retornar los objetos automáticamente los hace pasar por marshal (codifica en un JSON), como lo hemos específicado en el decorador *marshal_with*.
  
##  Autentificando las solicitudes (request)
  
  
La lógica de la autentificación está encapuslada en el archivo *ThoughtsBackend/thought_backend/token_validation*. Este contiene tanto la generación como la validación del header. 
Como ejemplo, la siguiente función genera el token *Bearer*:
```   
def encode_token(payload, private_key):
    return jwt.encode(payload, private_key, algorithm='RS256')
  
def generate_token_header(username, private_key):
    '''
    Generate a token header base on the username. 
    Sign using the private key.
    '''
    payload = {
        'username': username,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=2),
    }
    token = encode_token(payload, private_key)
    token = token.decode('utf8')
    return f'Bearer {token}
```  
  
Este código genera un payload JWT (el concepto de payload no tiene un concepto español que conozca que lo defina bien). Incluye *username* para ser usado como un valor personalizado, pero también así añade dos campos estándar, una fecha de expiración *exp*  y el generador de tiempo *iat* del token.
  
Luego el token se codifica usando el algoritmo **RS256**, con una llave privada, y devuelta en el formato apropiado: *Bearer < token>*.
La acción inversa es obtener el *username* desde un header codificado. El código será mas largo, pues tendremos en cuenta las diferentes opciones en las cuales podríamos recibir el header de *autentificación*.  Este header viene directamente de nuestra API pública (/api), de modo que debieramos esperar que cualquier valor y programa esten listos defensivamente para ello. 
La decodificación del token mismo es simplista, debido a que la acción *jwt.decode* lo hará por nosotros:
```   
def decode_token(token, public_key):
    return jwt.decode(token, public_key, algoritms='RS256')
```  
  
Con todo, antes de llegar a este paso necesitaremos obtener el token y verificar que el header es valido en multiples casos, de modo que chequearemos primero si es que el header está vacío, y si es que tiene el formato apropiado, extrayendo el token:
```   
def validate_token_header(header, public_key):
    if not header:
        logger.info('No header')
        return None
  
    # Retrieve the Bearer token
    parse_result = parse('Bearer {}', header)
    if not parse_result:
        logger.info(f'Wrong format for header "{header}"')
        return None
    token = parse_result[0]
```  
  
Solo después de ello podemos decodificar el token. Si no pudiera ser decodificado con la llave pública arrojará un error *DecodeError*. El token puede así también expirar:
@import "tutorial_data/tokens4
Luego chequeamos que tenga los parametros *exp* y *username* esperados. Si alguno de estos parametros está perdido significa que el formato token, luego de la decoficación, quedó incorrecto. Esto puede pasar al cambiar el código en versiones diferentes:
```   
    # Check expiry is in the token
    if 'exp' not in decoded_token:
        logger.warning('Token does not have expiry (exp)')
        return None
  
    # Check username is in the token
    if 'username' not in decoded_token:
        logger.warning('Token does not have username')
        return None
  
    logger.info('Header successfully validated')
    return decoded_token['username']
```  
  
Si todo va bien devolverá el valor del *username* en el final.
  
Cada uno de estos problemas es registrado con una severidad diferente. En la mayoría de las ocurrencias se registran con seguridad a nivel de información(info-level), dado que no son graves. Errores tales como errores de formato luego de decodificado un token puede indicar problemas con nuestro proceso de codificación.
  
Tengamos en cuenta que estamos usando un esquema de llave privado/público, en vez de un esquema de llave simetrica, a la hora de codificar y decodificar nuestros tokens. Esto significa que las llaves de decodificación y codificación son diferentes. 
  
En nuestra estructura de microservicio solo el autor de la firma (signing authority) requiere la llave privada.  Esto añade seguridad debido a que cualquier filtración de llaves en otros servicios no serán capaces de recuperar una llave capaz de firmar(signing) bearer(portadores) tokens. Necesitaremos con todo generar llaves públicas y privadas apropiadas al caso.
Para añadir estas llaves privadas/públicas solo ejecuta el siguiente comando:
```   
$ openssl genrsa -out key.pem 2048
Generating RSA private key, 2048 bit long modulus
.....................+++
.............................+++
```  
(La primera línea, pues las otras líneas son la salida del terminal)
  
Ahora para extraer la llave pública usa lo siguiente:
```   
$ openssl rsa -in key.pem -outform PEM -pubout -out key.pub
```  
  
Esto generará dos archivos: *key.pem* y *key.pub* con un par privado/público de llaves. Leerlos en formato texto sera suficiente para ocuparlas como llaves para codificar/decodificar el token JWT:
```   
>> with open('private.pem') as fp:
>> ..  private_key = fp.read()
  
>> generate_token_header('peter', private_key)
'Bearer <token>'
```  
  
De notar es que para los tests generamos un par de llaves de prueba que esta adjunto como strings. Estas llaves han sido creadas especificamente para este uso y no seran usadas en ningun otro espacio del proyecto. No son para uso sino para razones de este proyecto, no deben ocuparse para otras tareas.
  
###  Nota sobre las llaves en JWT
  
Debes tener presente que requerirás una llave privada no encriptada, no protegida por contraseña, pues el módulo JWT no permite añadir una contraseña. **No recopiles llaves secretas de producción en archivos no protegidos**. Busca la forma de inyectarlos mientras se mantienen en secreto por medio del uso de variables de ambiente. Como manejar adecuadamente con datos secretos en ambientes de producción no es parte de este tutorial. Informate.
  
##  Testeando el código
  
  
Finalmente llegamos al punto donde trabajaremos con pytest, según el enfoque TDD visto en clase. Pytest es un framework, el cual es conocido como el estándar por exelencia en ejecución de tests para aplicaciones python. 
  
En pocas palabras pytest tiene muchos plugins y complementos para lidiar con muchisimas situaciones. Estaremos usando para el proyecto, en específico, *pytest-flask*, el cual nos ayudará a ejecutar tests para una aplicación Flask (como es de esperarse).
  
Para ejecutar los tests tan solo debemos ejecutar en el comandos de línea el comando *pytest*:
```   
$ pytest
============== test session starts ==============
....
==== 17 passed, 177 warnings in 1.50 seconds =====
```  
  
Algunos prefijos a tener en cuenta en el uso del comando pytest son,
  - *-k* el cual es para ejecutar un subconjunto de pruebas coincidentes.
  - *--lf* para correr los últimos tests que fallaron
  - *-x* para detener los tests al encuentro del primer error
Estos y otros prefijos son de bastante utilidad a la hora de ejecutar test. Es recomendable chequear la documentación completa que puede verse en el siguiente [link](https://docs.pytest.org/en/latest/ ), y descubrir todas las posibilidades que tenemos a disposición.
  
Configuramos el uso básico, incluyendo el mantener habilitado ciertos flags en el archivo *ThoughtsBackend/pytest.ini* y algunos accesorios (fixtures) en *ThoughtsBackend/tests/conftest.py*.
Por tanto empezemos entendiendo algo mas acerca de estos archivos (en el caso de pytest.ini no hay mas que añadir que le quitamos las advertencias de pytest).
  
###  Definiendo los accesorios(fixtures) de pytest
  
  
Los accesorios son usados en pytest para preparar el contexto en el cual los test serán ejecutados, preparandolo y limpiandolo en el final. Los accesorios de aplicación son esperados por pytest-flask, como bien se puede leer en la documentación (de la cual ya dimos el link). Los plugins general un accesorio *client* que podremos usar para enviar solicitudes en modo test. Veremos este accesorio en acción en el accesorio *thoughts_fixture*, el cual genera tres pensamientos a través de la API y elimina todo luego de ejecutarse nuestro test.
La estructura es como sigue:
1. Generamos tres pensamientos. Recopilamos sus *thought_id*:
```   
@pytest.fixture
def thought_fixture(client):
  
    thought_ids = []
    for _ in range(3):
        thought = {
            'text': fake.text(240),
        }
        header = token_validation.generate_token_header(fake.name(),
                                                        PRIVATE_KEY)
        headers = {
            'Authorization': header,
        }
        response = client.post('/api/me/thoughts/', data=thought,
                               headers=headers)
        assert http.client.CREATED == response.status_code
        result = response.json
        thought_ids.append(result['id'])
```  
  
2. Luego añadimos *yield thought_ids* al test:
```   
yield thought_ids
```  
  
3. Recuperamos todos los pensamientos y los eliminamos uno por uno:
```   
# Clean up all thoughts
response = client.get('/api/thoughts/')
thoughts = response.json
for thought in thoughts:
    thought_id = thought['id']
    url = f'/admin/thoughts/{thought_id}/'
    response = client.delete(url)
    assert http.client.NO_CONTENT == response.status_code
```  
  
Tengamos en cuenta que usamos el módulo *faker* para generar nombres y textos inventados. Si quieres la documentación del módulo apreta en el [link](https://faker.readthedocs.io/en/stable/ ). Es una buena manera de generar valores aleatorios para tus tests que evitan el reusar *test_user* y *test_text* una y otra vez. También ayuda a dar forma a tus tests al chequear el input independientemente y no copiando ciegamente un placeholder. 
  
Otro punto importante de los tests y en especial de la integración de accesorios es como ejercitan nuestra API. Al trabajar de esta manera, aunque nuestro ejemplo es básico, nos da una buena idea de como funciona nuestro enfoque en microservicios en el servicio como un todo, demostrando que no simplemente ordenamos el código de manera estratégica para lograr operaciones triviales pero no completamente funcionales.
Por útlimo es de notar el uso de el accesorio *client*, el cual nos es provisto por *pytest-flask*.
  
###  Entendiendo test_token_validation.py
  
  
Este archivo test testea el comportamiento del header autentificación, de modo que es importante testearlo a profundidad.
  
De principio testea si el header puede ser codificado y decodificado con las llaves apropiadas. También chequea todas las diferentes posibilidades en términos de entradas validas (diferentes formas o formatos incorrectos, llaves de decodificación inválidos, o  tokens expirados). 
  
Para chequear tokens expirados usamos dos módulos:
 - *[freezegun](https://github.com/spulec/freezegun )* para hacer que el test devuelva un tiemop de test específico.
 - *[delorean](https://delorean.readthedocs.io/en/latest/ )* para parsear fechas mas facilmente (aunque el módulo es capaz de mas; cliqueando los nombres de los módulos los llevará a sus documentaciones completas).
Estos dos módulos son fáciles de usar y muy buenos en propósitos de pruebas. 
  
Como ejemplo este código es un test que chequea un token expirado:
<pre>Error: ENOENT: no such file or directory, open '/home/gosta/Desktop/UNIVERSIDAD/SEMESTRE8/tutoriales_INFO229/tutorial4_TDD/tutorial_test/pytest5'</pre>  
  
Percatemonos como el freeze time (tiempo congelado) es precisamente 1 segundo luego de el tiempo de expiración del token. 
  
Las llaves publicas y privadas usadas para los test son definidas en el archivo *ThoughtsBackend/tests/constants.py*. Hay una llave pública independiente extra usada para chequear que sucede si tu decodificas un token con una llave pública inválida.
  
###  test_thoughts.py
  
  
Este archivo chequea las interfaces API definidas. A cada API se le testea para ejecutar las acciones correctamente (crear un nuevo pensamiento, devolver pensamientos de un usuario, recuperar todos los pensamientos, buscar a través de los pensamientos, y recuperar un pensamiento por ID) así como también algunos tests de errores (solicitudes no autorizadas para crear y recuperar pensamientos de un usuario, o recuperar un pensamiento no existente).
  
En este contexto usamos nuevamente *freezegun* para determinar cuando los pensamientos son creados, en ves de crearlos con un timestamp dependiendo de los tiempos de ejecución de los test.
  