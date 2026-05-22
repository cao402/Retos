DELIMITER $$
DROP EVENT IF EXISTS mantenimiento_tickets $$
CREATE EVENT mantenimiento_tickets
ON SCHEDULE 
    EVERY 1 DAY
    STARTS TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 3 HOUR) #creamos un evento que todos los dias (every 1 day) tome a las 3 am (INTERVAL 1 DAY + INTERVAL 3 HOUR)
DO
	UPDATE ticket
    SET estado="Archivado"
    WHERE estado="Cerrado" AND fecha_cierre < NOW() - INTERVAL 1095 DAY; #hacemos un uodate y con el where comprobamos cual esta cerrado y si ahora aun pasando 1095 dias es mas tiempo que el momento donde se cerrero el procedimiento
END$$

DELIMITER ;