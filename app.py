from flask import Flask, render_template, request, jsonify
from werkzeug.security import check_password_hash
from cryptography.fernet import Fernet
import mysql.connector

app = Flask(__name__)

CHAVE_CPF = b'Z7vK9mP2xL8qR4wN1tY6bF3cJ5hG0sA8eQ2uI7oP9vM='
cipher = Fernet(CHAVE_CPF)

def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="clinica_veterinaria"
    )

@app.route("/")
def login():
    return render_template("index.html")

@app.route("/fazer_login", methods=["POST"])
def fazer_login():
    try:
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE user = %s", (usuario,))
        user_bd = cursor.fetchone()
        conn.close()

        if user_bd and check_password_hash(user_bd["password"], senha):
            return jsonify({"status": "sucesso", "redirect": "/pets"})
        else:
            return jsonify({"status": "erro", "mensagem": "Usuário ou senha incorretos!"}), 401

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/logout")
def logout():
    return render_template("index.html")

@app.route("/pets")
def pagina_pets():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets ORDER BY id DESC")
    pets = cursor.fetchall()
    conn.close()
    return render_template("pet.html", pets=pets)

@app.route("/cadastrar_pet", methods=["POST"])
def cadastrar_pet():
    try:
        nome = request.form.get("nome")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        idade = request.form.get("idade")

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pets (nome, especie, raca, idade) VALUES (%s, %s, %s, %s)",
            (nome, especie, raca, idade)
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Pet cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route("/excluir_pet/<int:pet_id>", methods=["POST"])
def excluir_pet(pet_id):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pets WHERE id = %s", (pet_id,))
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Registro do pet removido!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route("/donos")
def pagina_donos():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, especie FROM pets ORDER BY nome ASC")
    pets = cursor.fetchall()
    cursor.execute("""
        SELECT donos.*, pets.nome AS nome_pet 
        FROM donos 
        LEFT JOIN pets ON donos.pet_id = pets.id
        ORDER BY donos.nome ASC
    """)
    donos = cursor.fetchall()
    conn.close()

    for dono in donos:
        try:
            dono["cpf"] = cipher.decrypt(dono["cpf"].encode()).decode()
        except Exception:
            pass

    return render_template("dono.html", donos=donos, pets=pets)

@app.route("/cadastrar_dono", methods=["POST"])
def cadastrar_dono():
    try:
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        telefone = request.form.get("telefone")
        endereco = request.form.get("endereco")
        pet_id = request.form.get("pet_id") or None

        cpf_criptografado = cipher.encrypt(cpf.encode()).decode()

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO donos (nome, cpf, telefone, endereco, pet_id) VALUES (%s, %s, %s, %s, %s)",
            (nome, cpf_criptografado, telefone, endereco, pet_id)
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Tutor cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route("/excluir_dono/<int:dono_id>", methods=["POST"])
def excluir_dono(dono_id):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM donos WHERE id = %s", (dono_id,))
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Tutor removido com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route("/agendamentos")
def pagina_agendamentos():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, especie FROM pets ORDER BY nome ASC")
    pets = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM donos ORDER BY nome ASC")
    donos = cursor.fetchall()
    cursor.execute("""
        SELECT agendamentos.id,
               DATE_FORMAT(agendamentos.data_consulta, '%d/%m/%Y') AS data_formatada,
               TIME_FORMAT(agendamentos.hora_consulta, '%H:%i') AS hora_formatada,
               agendamentos.motivo,
               pets.nome AS nome_pet,
               donos.nome AS nome_dono
        FROM agendamentos
        INNER JOIN pets ON agendamentos.pet_id = pets.id
        INNER JOIN donos ON agendamentos.dono_id = donos.id
        ORDER BY agendamentos.data_consulta ASC, agendamentos.hora_consulta ASC
    """)
    agendamentos = cursor.fetchall()
    conn.close()
    return render_template("agendamento.html", agendamentos=agendamentos, pets=pets, donos=donos)

@app.route("/cadastrar_agendamento", methods=["POST"])
def cadastrar_agendamento():
    try:
        pet_id = request.form.get("pet_id")
        dono_id = request.form.get("dono_id")
        data_consulta = request.form.get("data_consulta")
        hora_consulta = request.form.get("hora_consulta")
        motivo = request.form.get("motivo")

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agendamentos (pet_id, dono_id, data_consulta, hora_consulta, motivo) VALUES (%s, %s, %s, %s, %s)",
            (pet_id, dono_id, data_consulta, hora_consulta, motivo)
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Agendamento realizado com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route("/excluir_agendamento/<int:agendamento_id>", methods=["POST"])
def excluir_agendamento(agendamento_id):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos WHERE id = %s", (agendamento_id,))
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Agendamento cancelado com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
