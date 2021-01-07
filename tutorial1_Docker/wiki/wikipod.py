import wikipedia
import pymongo
import os

DATABASE = "wiki"
COLLECTION = "wikicol"               

class wikiPod:
     #Constructor
      def __init__(self,channel):
         self.channel = channel

     #subir informacion
      def subir_mensaje(dato):
         #conexion a MONGO
         myclient = pymongo.MongoClient(host=os.environ['MONGO_HOST'], port=int(os.environ['MONGO_PORT']))
         db = myclient[DATABASE]
         col = db[COLLECTION]
         col.insert_one({'title':dato.title,'content':dato.content})

     #Buscar dato
      def buscar_dato():
         dat = input("¿Qué articulo desea buscar?: ")        
         a = wikipedia.search(dat)
         for i in a:
            print(i, " ")
         datr = input("¿Cual de estos resultados en específico desea guardar?(recuerde el uso de mayusculas y minusculas): ")
         w = wikipedia.page(datr)
         wikiPod.subir_mensaje(w)
