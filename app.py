from flask import Flask, request, redirect, session, send_file
from fpdf import FPDF
import sqlite3

app = Flask(__name__)
app.secret_key = "orcapro_secret"

# DB
def db():
    return sqlite3.connect("orcapro.db")

conn = db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    pass TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    cliente TEXT,
    servico TEXT,
    valor REAL
)
""")

conn.commit()
conn.close()

# STYLE (APP VISUAL)
style = """
<style>
body{font-family:Arial;background:#0f0f0f;color:white;text-align:center;}
a{display:block;margin:10px;padding:12px;background:#00c896;color:black;text-decoration:none;border-radius:10px;}
input,select{padding:10px;margin:5px;width:80%;}
.card{background:#1c1c1c;margin:10px;padding:10px;border-radius:10px;}
</style>
"""

# LOGIN
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")

    return style + """
    <h1>💼 OrçaPro PRO MAX</h1>
    <a href='/login'>Login</a>
    <a href='/register'>Criar conta</a>
    """

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        conn = db()
        c = conn.cursor()
        c.execute("INSERT INTO users(user,pass) VALUES(?,?)",
                  (request.form["user"], request.form["pass"]))
        conn.commit()
        return redirect("/login")

    return style + """
    <h2>Criar conta</h2>
    <form method="POST">
        <input name="user" placeholder="Usuário"><br>
        <input name="pass" placeholder="Senha"><br>
        <button>Registrar</button>
    </form>
    """

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = db()
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE user=? AND pass=?",
                  (request.form["user"], request.form["pass"]))
        u = c.fetchone()

        if u:
            session["user"] = u[0]
            return redirect("/dashboard")

        return "Erro login"

    return style + """
    <h2>Login</h2>
    <form method="POST">
        <input name="user"><br>
        <input name="pass"><br>
        <button>Entrar</button>
    </form>
    """

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*), SUM(valor) FROM orcamentos WHERE user_id=?",
              (session["user"],))

    total, soma = c.fetchone()
    soma = soma or 0

    return style + f"""
    <h1>📊 Painel OrçaPro</h1>

    <div class='card'>
        <h3>Total orçamentos</h3>
        <p>{total}</p>
    </div>

    <div class='card'>
        <h3>Faturamento</h3>
        <p>R$ {soma}</p>
    </div>

    <a href='/novo'>Novo orçamento</a>
    <a href='/lista'>Ver lista</a>
    <a href='/logout'>Sair</a>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/novo", methods=["GET","POST"])
def novo():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        conn = db()
        c = conn.cursor()

        c.execute("""
        INSERT INTO orcamentos(user_id,cliente,servico,valor)
        VALUES(?,?,?,?)
        """,(session["user"],
             request.form["cliente"],
             request.form["servico"],
             request.form["valor"]))

        conn.commit()
        return redirect("/lista")

    return style + """
    <h2>Novo Orçamento</h2>

    <form method="POST">
        <input name="cliente" placeholder="Cliente"><br>

        <select name="servico">
            <option>Corte de cabelo</option>
            <option>Barba</option>
            <option>Mecânico</option>
            <option>Limpeza</option>
        </select><br>

        <input name="valor" placeholder="Valor"><br>

        <button>Salvar</button>
    </form>
    """

@app.route("/lista")
def lista():
    if "user" not in session:
        return redirect("/login")

    conn = db()
    c = conn.cursor()

    c.execute("SELECT * FROM orcamentos WHERE user_id=?",(session["user"],))
    dados = c.fetchall()

    html = style + "<h2>Orçamentos</h2>"

    for o in dados:

        msg = f"Olá {o[2]}, seu orçamento é {o[3]} R$ {o[4]}"
        msg = msg.replace(" ","%20")

        html += f"""
        <div class='card'>
            <p><b>{o[2]}</b></p>
            <p>{o[3]} - R$ {o[4]}</p>

            <a href='/pdf/{o[0]}'>PDF</a>
            <a href='https://wa.me/?text={msg}'>WhatsApp</a>
        </div>
        """

    return html

@app.route("/pdf/<int:id>")
def pdf(id):

    conn = db()
    c = conn.cursor()

    c.execute("SELECT * FROM orcamentos WHERE id=?",(id,))
    o = c.fetchone()

    file = f"orc_{id}.pdf"

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"ORÇAMENTO PROFISSIONAL", ln=True)

    pdf.set_font("Arial","",12)
    pdf.cell(0,10,f"Cliente: {o[2]}", ln=True)
    pdf.cell(0,10,f"Serviço: {o[3]}", ln=True)
    pdf.cell(0,10,f"Valor: R$ {o[4]}", ln=True)

    pdf.output(file)

    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
