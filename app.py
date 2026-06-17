cd ~
rm -rf orcapro_final
mkdir orcapro_final
cd orcapro_final

pkg update -y
pkg install python -y
pip install flask fpdf

cat > app.py << 'EOF'
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "orcapro_secret"

@app.route("/")
def home():
    return """
    <style>
    body{font-family:Arial;background:#0f0f0f;color:white;text-align:center;}
    a{display:block;margin:10px;padding:12px;background:#00c896;color:black;text-decoration:none;border-radius:10px;}
    </style>

    <h1>💼 OrçaPro PRO</h1>

    <a href='/login'>🔐 Login</a>
    <a href='/dashboard'>📊 Dashboard</a>
    <a href='/planos'>💳 Planos</a>
    """

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user = request.form["user"]
        password = request.form["pass"]

        # LOGIN FIXO (SEM BANCO - FUNCIONA NO RENDER)
        if user == "admin" and password == "1234":
            session["user"] = 1
            return redirect("/dashboard")

        return "❌ Login inválido"

    return """
    <h2>Login OrçaPro</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário"><br><br>
        <input name="pass" placeholder="Senha"><br><br>
        <button>Entrar</button>
    </form>
    """

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return """
    <style>
    body{font-family:Arial;background:#0f0f0f;color:white;text-align:center;}
    a{display:block;margin:10px;padding:12px;background:#00c896;color:black;text-decoration:none;border-radius:10px;}
    </style>

    <h1>📊 Dashboard OrçaPro</h1>

    <p>Sistema funcionando ✔</p>

    <a href='/'>Voltar</a>
    """

@app.route("/planos")
def planos():
    return """
    <style>
    body{font-family:Arial;background:#0f0f0f;color:white;text-align:center;}
    .box{background:#1c1c1c;margin:20px;padding:20px;border-radius:10px;}
    </style>

    <h1>💳 Planos OrçaPro</h1>

    <div class="box">
        <h2>Plano Mensal</h2>
        <p>R$ 29,90 / mês</p>

        <p>PIX: SUA_CHAVE_AQUI</p>

        <p>Após pagamento, acesso será liberado manualmente.</p>
    </div>

    <a href='/'>Voltar</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
EOF

python app.py
