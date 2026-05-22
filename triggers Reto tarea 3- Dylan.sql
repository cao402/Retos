
/*Tabla auditoria*/
CREATE TABLE IF NOT EXISTS `mydb`.`Auditoria_Tickets` (
    `ID_auditoria` INT NOT NULL AUTO_INCREMENT,
    `ID_ticket` INT NOT NULL,
    `estado_anterior` ENUM('Abierto', 'En Proceso', 'Cerrado', 'Archivado') NOT NULL,
    `estado_nuevo` ENUM('Abierto', 'En Proceso', 'Cerrado', 'Archivado') NOT NULL,
    `fecha_cambio` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`ID_auditoria`),
    INDEX `idx_ticket` (`ID_ticket` ASC),
    CONSTRAINT `fk_auditoria_ticket`
        FOREIGN KEY (`ID_ticket`)
        REFERENCES `mydb`.`ticket` (`ID_ticket`)
        ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

/*Primer trigger: tipo adecuado(evita cerrar un ticket sin mensjaes) */

DELIMITER $$
CREATE TRIGGER `before_ticket_close`
BEFORE UPDATE ON `mydb`.`ticket`
FOR EACH ROW
BEGIN
    DECLARE total_mensajes INT;

    IF NEW.estado = 'Cerrado' AND OLD.estado <> 'Cerrado' THEN

        SELECT COUNT(*)
        INTO total_mensajes
        FROM `mydb`.`mensaje`
        WHERE ID_ticket = OLD.ID_ticket;

        IF total_mensajes = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede cerrar un ticket sin historial de mensajes';
        END IF;

    END IF;
END$$
DELIMITER ;

/*Segundo trigger: registro de cambios de estado*/

DELIMITER $$
CREATE TRIGGER `after_ticket_status_change`
AFTER UPDATE ON `mydb`.`ticket`
FOR EACH ROW
BEGIN

    IF OLD.estado <> NEW.estado THEN

        INSERT INTO `mydb`.`Auditoria_Tickets`
        (
            ID_ticket,
            estado_anterior,
            estado_nuevo,
            fecha_cambio
        )
        VALUES
        (
            OLD.ID_ticket,
            OLD.estado,
            NEW.estado,
            NOW()
        );

    END IF;
END$$
DELIMITER ;

