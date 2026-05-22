import random
from faker import Faker
import random
import pymysql
from datetime import timedelta, datetime
import cryptography

def conn_bd():
    return pymysql.connect(host='localhost',user='root',password='seguridad1', database='mydb')


def procesar_tickets_enojados():
    conexion = conn_bd()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT ID_ticket FROM ticket")
            tickets = cursor.fetchall()
            
            for ticket in tickets:
                id_ticket = ticket[0]
                
                if random.randint(1, 100) <= 10:  
                    print(f"Ticket {id_ticket}: Cliente enojado.")
                    
                    sql = "UPDATE ticket SET descripcion = CONCAT(descripcion, %s) WHERE ID_ticket = %s"
                    cursor.execute(sql, ("[ENOJADO]", id_ticket))

        conexion.commit()
        
    except Exception as e:
        print(f"Error en el proceso: {e}")
        conexion.rollback()
    finally:
        conexion.close()

if __name__ == '__main__':
    procesar_tickets_enojados()