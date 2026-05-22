DELIMITER $$
DROP PROCEDURE IF EXISTS crear_ticket $$
CREATE PROCEDURE crear_ticket (IN p_correo_cliente VARCHAR(35), p_nombre_cliente VARCHAR(50), p_telefono_cliente VARCHAR(15),
p_titulo_averia VARCHAR(100), p_descripcion TEXT, p_id_operador INT) #se toma todos los datos con el in
BEGIN
	
    DECLARE v_id_cliente INT; #declaramos una variable para el futuro id de cliente
    
    IF p_correo_cliente NOT IN (SELECT correo FROM clientes) THEN #comprobamos si el cliente existe, si no existe lo insertamos
		INSERT INTO clientes (correo, nombre, telefono)
        VALUES (p_correo_cliente, p_nombre_cliente, p_telefono_cliente);
    END IF;  
	
    SET v_id_cliente=(SELECT ID_cliente FROM clientes WHERE p_correo_cliente=correo); #sabiendo quien es el cliente tomamos tu id
    
    INSERT INTO ticket(titulo, descripcion, fecha_creacion, categoria, prioridad, estado, cliente, operador)  #para finalizar añadimos el ticket
    VALUES (p_titulo_averia, p_descripcion, now(), "Hardware", "Media", "abierto",v_id_cliente, p_id_operador);
    
END$$
DELIMITER ;