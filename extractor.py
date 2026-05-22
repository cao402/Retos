import pymysql
import pymysql.cursors
import xml.etree.ElementTree as ET
import datetime
import os

def cargarTickets():
    try:
        conexion = pymysql.connect(host='localhost',user='root',password='root', database='mydb')
        cursor = conexion.cursor()
        cursor.execute('SELECT ID_ticket FROM ticket')
        return [ticket[0] for ticket in cursor.fetchall()]
    except Exception as E:
        with open('extractor_log.txt', 'w',encoding='utf-8') as f:
            f.write('Error en conexion a la bd: \n'+ str(E))

tickets = cargarTickets()
contador = 0
if tickets:
    try:
        conexion = pymysql.connect(host='localhost',user='root',password='root', database='mydb')
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
    except Exception as E:
        with open('extractor_log.txt', 'w',encoding='utf-8') as f:
            f.write('Error en conexion a la bd: \n'+ str(E))
    else:
        for id_ticket in tickets:
            contador += 1
            if not os.path.exists('./tickets'):
                os.mkdir('./tickets')
            a_ticket = "./tickets/"+"ticket_"+ str(id_ticket) + ".xml"

            root = ET.Element("ticket")  

            cursor.execute('''SELECT t.titulo, t.descripcion, t.fecha_creacion, t.fecha_cierre, t.categoria, t.prioridad, t.estado, 
                                o.nombre AS nombre_op , o.correo_operador AS correo_op, d.nombre AS dep_op,
                                c.nombre AS nombre_cli, c.correo AS correo_cli, c.telefono AS telefono_cli
                                FROM ticket t
                                JOIN operadores o ON t.operador = o.id_operador
                                JOIN departamentos d ON o.id_departamento = d.id_departamento
                                JOIN clientes c ON t.cliente = c.ID_cliente
                                WHERE ID_ticket = %s''', id_ticket)
            resultado = cursor.fetchone()

            datos_ticket = ET.SubElement(root, "datos_ticket")
            titulo = resultado['titulo']
            descripcion = resultado['descripcion']
            fecha_creacion = resultado['fecha_creacion']
            fecha_cierre = resultado['fecha_cierre']
            categoria = resultado['categoria']
            prioridad = resultado['prioridad']
            estado = resultado['estado']
            ET.SubElement(datos_ticket, "Título").text = titulo
            ET.SubElement(datos_ticket, "Descripción").text = descripcion
            ET.SubElement(datos_ticket, "Fecha_Creacion").text = str(fecha_creacion.date())
            ET.SubElement(datos_ticket, "Fecha_Cierre").text = str(fecha_cierre.date()) if fecha_cierre else ""
            ET.SubElement(datos_ticket, "Categoría").text = categoria
            ET.SubElement(datos_ticket, "Prioridad").text = prioridad
            ET.SubElement(datos_ticket, "Estado").text = estado
            if fecha_cierre:
                if (fecha_cierre - fecha_creacion).days >= 7:
                    retraso = str((fecha_cierre - fecha_creacion).days)
                    alerta_sla = ET.SubElement(root, "alerta_sla")
                    alerta_sla.set('dias_retraso',retraso)

            datos_operador = ET.SubElement(root, "operador")
            nombre_op = resultado['nombre_op']
            correo_op = resultado['correo_op']
            dep_op = resultado['dep_op']
            ET.SubElement(datos_operador, "Nombre").text = nombre_op
            ET.SubElement(datos_operador, "Correo").text = correo_op
            ET.SubElement(datos_operador, "Departamento").text = dep_op

            datos_cliente = ET.SubElement(root, "cliente")
            nombre_cli = resultado['nombre_cli']
            correo_cli = resultado['correo_cli']
            telefono_cli = resultado['telefono_cli']
            ET.SubElement(datos_cliente, "Nombre").text = nombre_cli
            ET.SubElement(datos_cliente, "Correo").text = correo_cli
            ET.SubElement(datos_cliente, "Teléfono").text = telefono_cli

            cursor.execute('''SELECT texto, remitente, fecha_hora
                           FROM mensaje WHERE
                           ID_ticket = %s
                           ORDER BY fecha_hora ''', id_ticket)
            historial = ET.SubElement(root, "historial")
            for texto, remitente, fecha_hora in [(mensaje['texto'],mensaje['remitente'],mensaje['fecha_hora']) for mensaje in cursor.fetchall()]:
                if 'incompetentes' in texto or 'denuncia' in texto or 'vergüenza' in texto or 'lento' in texto:
                    root.set('cliente-enfadado', 'true')
                mensaje = ET.SubElement(historial, "mensaje")
                ET.SubElement(mensaje, "Remitente").text = remitente
                ET.SubElement(mensaje, "Fecha_Hora").text = str(fecha_hora)
                ET.SubElement(mensaje, "Texto").text = texto
            
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ") 
            tree.write(a_ticket,encoding="utf-8", xml_declaration=True,)

        with open('extractor_log.txt', 'w',encoding='utf-8') as f:
            f.write('Tickets Procesados hoy: '+ str(contador))