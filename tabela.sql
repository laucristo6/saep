CREATE DATABASE IF NOT EXISTS clinica_veterinaria;
USE clinica_veterinaria;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS donos;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raca VARCHAR(50),
    idade INT
);

CREATE TABLE donos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(200),
    pet_id INT,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
);


UPDATE usuarios SET password = 'scrypt:32768:8:1$iIyTDblnvDCsrbRm$d00af9cb2dc2a81f57b555c9055ea0f10cdb82c7c3b248c81e6d91787a003d4b47767d14e3b197f08cf84cd421901398689fed9e1f1d943be4a3c7a4cd1948bf
' WHERE user = 'admin';

SELECT id, user, password FROM usuarios;

ALTER TABLE donos DROP INDEX cpf;
ALTER TABLE donos MODIFY cpf VARCHAR(255) NOT NULL;


UPDATE usuarios SET password = 'scrypt:32768:8:1$0I4DStiF0ETT2YkH$6e1b27392bf0a0922f61a5e2a28f5aacb64f1812643c05ad8f111ad40638a73ecccf218e972f99f594fb7526f5c009d873a55cc86fc76c0c32632fede95723cd' WHERE user = 'admin';

ALTER TABLE donos MODIFY cpf VARCHAR(255) NOT NULL;

SELECT * FROM usuarios;
SELECT * FROM donos;

ALTER TABLE donos MODIFY cpf VARCHAR(255) NOT NULL;

SELECT * FROM pets;

USE clinica_veterinaria;

CREATE TABLE agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT NOT NULL,
    dono_id INT NOT NULL,
    data_consulta DATE NOT NULL,
    hora_consulta TIME NOT NULL,
    motivo VARCHAR(150) NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
    FOREIGN KEY (dono_id) REFERENCES donos(id) ON DELETE CASCADE
);

