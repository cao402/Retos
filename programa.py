from faker import Faker
import random
import pymysql
from datetime import timedelta, datetime
import cryptography

personas = {"clientes":[],"operadores":[], "departamentos":{}}

def conn_bd():
    return pymysql.connect(host='localhost',user='root',password='1234', database='mydb')


def generar_departamentos_y_operadores():
    departamentos = {'Soporte Técnico': 1001, 'Infraestructura y Redes': 1002, 'Desarrollo y Aplicaciones':1003, 'Seguridad Informática': 1004}

    for departamento in departamentos.values():
        for _ in range(random.randint(10, 30)):
            personas["operadores"].append({'nombre':Faker("es_ES").name(),'email':Faker("es_ES").email(),'departamento':departamento})
    
    try:
        conexion = conn_bd()
        cursor = conexion.cursor()
        sql ="""
                INSERT INTO departamentos (id_departamento, nombre, ubicacion)
                VALUES (%s, %s, %s)
            """
        valores = [(c[1], c[0], str(Faker().building_number()) ) for c in departamentos.items()]
        cursor.executemany(sql, valores)
        conexion.commit()
        sql ="""
                INSERT IGNORE INTO operadores (nombre, correo_operador, id_departamento)
                VALUES (%s, %s, %s)
            """
        valores = [(p['nombre'], p['email'], p['departamento']) for p in personas["operadores"]]
        cursor.executemany(sql, valores)
        conexion.commit()
        
        cursor.execute("SELECT id_operador, correo_operador FROM operadores ORDER BY id_operador DESC LIMIT 50") # Recogemos los usuarios creados para añadir el id al diccionarioconexion.close()
        for id_operador, correo in cursor.fetchall():
            for operador in personas["operadores"]:
                if operador["email"] == correo:
                    operador["id"] = id_operador
                    break

        escribir_logs(f"Departamentos y operadores insertados: {len(valores)} registros.")
    except pymysql.err.OperationalError as a:
        escribir_logs(f"No se pudo conectar con la base de datos: {a}", nivel="Error")
        print("Error de conexion.")
    except Exception as e:
        escribir_logs(f"Error inesperado a la hora de generar e insertar los departamentos y operadores: {e}.", nivel="Error")
    


def generar_clientes():
    for _ in range(50):
        personas["clientes"].append({'nombre':Faker("es_ES").name(),'email':Faker("es_ES").email(),'telefono':str(Faker("es_ES").phone_number()).replace(" ", "")})
    try:
        conexion = conn_bd()
        cursor = conexion.cursor()
        sql ="""
                INSERT INTO clientes (nombre, correo, telefono)
                VALUES (%s, %s, %s)
            """
        valores = [(c['nombre'], c['email'], c['telefono']) for c in personas["clientes"]]
        cursor.executemany(sql, valores)
        conexion.commit()
        cursor.execute("SELECT id_cliente, correo FROM clientes ORDER BY ID_cliente DESC LIMIT 50") # Recogemos los usuarios creados para añadir el id al diccionario
        
        for id_cliente, correo in cursor.fetchall():
            for cliente in personas["clientes"]:
                if cliente["email"] == correo:
                    cliente["id"] = id_cliente
                    break

        escribir_logs(f"Clientes insertados: {len(valores)} registros")
    except pymysql.err.OperationalError as a:
        escribir_logs(f"NO se pudo conectar con la base de datos: {a}", nivel = "Error")
        print("Error de conexion...")
    except Exception as e:
        escribir_logs(f"Error inesperado al insertar clientes: {e}", nivel="Error")


def generar_tickets_y_clientes():
    '''A tener en cuenta las prioridades y estados'''
    estados = ["Abierto","En proceso","Archivado","Cerrado"]
    prioridades = ["Baja", "Media", "Alta", "Critica"]
    categorias = ["Hardware", "Software", "Redes ", "Seguridad"]
    tickets = []

    for cliente in personas["clientes"]:
        cantidad_ticket = random.randint(1,5) # Cada cliente tendrá entre 1 y 5 tickets para que sea realista
        for _ in range(cantidad_ticket):
            estado = random.choice(estados) # Estado aleatorio
            prioridad = random.choice(prioridades) # Prioridad Aleatoria

            fecha_creacion = Faker("es_ES").date_time_between(start_date="-2y", end_date="now") # Genera la fecha dentro de los ultimos 2 años

            if estado == "Cerrado":
                fecha_cierre = fecha_creacion + timedelta(days=random.randint(1,30)) #Le suma los dias de diferencia que tardo en cerrarse a la fecha de creación para que la fecha de cierre sea posterior
                
                if fecha_cierre > datetime.now(): # Evitamos que los ticket que no deben estar cerrados sigan abierto
                    fecha_cierre = None
                    estado = "Abierto"
            elif estado == "Archivado":
                fecha_cierre = datetime.today()
            else:
                fecha_cierre = None
            
            # Para que los datos sean variados elegimos una clave aleatoria de cada uno

            operador = random.choice(personas["operadores"]) # Le asignamos operadores aleatorios
            categoria= random.choice(categorias)
            ticket = {
                "titulo": Faker("es_Es").sentence(nb_words=6), # Genera el titulo con 6 palabras
                "descripcion": Faker("es_ES").paragraph(nb_sentences=3),
                "fecha_creacion": fecha_creacion,
                "fecha_cierre": fecha_cierre,
                "categoria" : categoria,
                "prioridad": prioridad,
                "estado": estado,
                "correo_cliente": cliente["email"],
                "operador": operador,
                "historial": []          
            }   

            cantidad_mensajes = random.randint(4,5) # 50 clientes * 4 = 200
            fecha_mensaje = fecha_creacion
            for i in range(cantidad_mensajes):
                fecha_mensaje += timedelta(hours=random.randint(1,48)) # Maximo 48 horas

                if fecha_cierre is not None and fecha_mensaje > fecha_cierre:
                    fecha_mensaje = fecha_cierre
                emisor = random.choice(["Cliente","Operador"])
                mensaje = {"emisor": emisor, "texto": Faker("es_ES").paragraph(nb_sentences=2), "fecha" : fecha_mensaje}
                
                ticket["historial"].append(mensaje)
        tickets.append(ticket)
    
    try:
        conexion = conn_bd()
        cursor = conexion.cursor()
        # Obtenemos todos los id necesarios para enlazar los tickets con los clientes y operadores
        cursor.execute("SELECT correo, ID_cliente FROM clientes")
        idntf_clientes = {correo: id_cliente for correo, id_cliente in cursor.fetchall() } # creamos un diccionario con lo que rcoge  el fetchall de odas las filas de la consulta y las devuelve como lista de tuplas
        cursor.execute("SELECT correo_operador, id_operador FROM operadores")
        idntf_operadores = {correo: id_operador for correo, id_operador in cursor.fetchall()}
        # consultas necesarias para poder insertar los resultados finales
        sql_ticket = """
        INSERT INTO ticket (titulo, descripcion, fecha_creacion, fecha_cierre, categoria, prioridad, estado, cliente, operador)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        sql_mensaje = """
        INSERT INTO mensaje (ID_ticket, texto, fecha_hora, remitente)
        VALUES (%s, %s, %s, %s)
        """
        for ticket in tickets:
            # Insertamos los tickets
            id_clientes = idntf_clientes[ticket["correo_cliente"]] 
            id_operador = idntf_operadores[ticket["operador"]["email"]]

            cursor.execute(sql_ticket, (ticket["titulo"],
                                        ticket["descripcion"],
                                        ticket["fecha_creacion"],
                                        ticket["fecha_cierre"],
                                        ticket["categoria"],
                                        ticket["prioridad"],
                                        ticket["estado"],
                                        id_clientes,
                                        id_operador
                                        ))
            
            # Insertamos los mensajes de ese mismo ticket recorriendo el historial  y usando el id ticket que guardamo
            id_ticket = cursor.lastrowid # saca el id autoincremental
            for mensaje in ticket["historial"]: 
                cursor.execute(sql_mensaje, (
                    id_ticket,
                    mensaje["texto"],
                    mensaje["fecha"],
                    mensaje["emisor"],
                ))
        conexion.commit()
        total_mensajes = sum(len(t["historial"]) for t in tickets)
        escribir_logs(f"Tickets insertados: {len(tickets)} registros.")
        escribir_logs(f"Mensajes de historial insertados: {total_mensajes} registros.")
    except pymysql.err.OperationalError as a:
        escribir_logs(f"No se pudo conectar con la base de datos: {a}", nivel="Error")
        print("Error de conexion.")
    except Exception as e:
        escribir_logs(f"Error inesperado al insertar los tickets: {e}", nivel="Error")
    return tickets


def escribir_logs(mensaje:str, nivel: str = "Info"):
    Fecha_hora = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    texto = f"[{Fecha_hora}] [{nivel} {mensaje}]\n"
    print(texto.strip()) # Mostramos  el texto que se escribe en tiempo real en el logs hasta que se pueda acceder al archivo .logs
    with open("seed_log.txt", "a", encoding="utf-8") as fichero:
        fichero.write(texto)

generar_departamentos_y_operadores()
generar_clientes()
generar_tickets_y_clientes()
