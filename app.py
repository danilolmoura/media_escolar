import os
import psycopg2
import random
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Aluno, Escola, Materia,Nota
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
app = Flask(__name__)


ENV=os.environ.get("ENV", "dev")
if ENV=="dev":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_notas.db'
else:
    database_url=os.environ["DATABASE_URL"]
    if database_url.startswith("postgres://"):
        database_url=database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY']="*****112" 

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'rebekahsarah002@gmail.com'
app.config['MAIL_PASSWORD'] = 'bewj wubz llge cnrl'

app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_DEFAULT_SENDER'] = '8eb995001@smtp-brevo.com'



mail=Mail(app)
serializer=URLSafeTimedSerializer(app.config['SECRET_KEY'])

db.init_app(app) 
migrate=Migrate(app,db)
login_manager=LoginManager()
login_manager. init_app(app)

@login_manager.user_loader
def load_user (user_id):
    return Aluno.query.get(int(user_id))

login_manager.login_view="login" 
    
    
        
       
        
        
  
    
    
## Cria tabelas do banco
with app.app_context():
    db.create_all()


@app.route("/") 
def index():
    
    if current_user.is_authenticated:
        return redirect( url_for("inicio")) 
    else: 
        return redirect(url_for("login"))
    

@app.route("/inicio")
@login_required 
def inicio():


    return render_template('inicio.html', aluno=current_user) 



@app.route("/cadastrar_escola", methods=["GET", "POST"])
# @login_required 
def cadastrar_escola():
    if request.method=="POST":

        nome=request.form.get("nome")
        escola=Escola(nome=nome)
        db.session.add(escola)
        db.session.commit()
        escolas=Escola.query.all()
        return render_template('escola.html',escolas=escolas)
        
    else: 
        escolas=Escola.query.all()
        return render_template('escola.html',escolas=escolas)


def render_materias( errors={},success={}):
    escolas=Escola.query.filter(Escola.id==current_user.escola_id).all()
    return render_template('materias.html', escolas=escolas, escola= current_user.escola, errors=errors, success=success)

@app.route("/materias")
@login_required  
def escolas():
    return render_materias()


@app.route("/cadastrar_materia", methods=["POST"])
@login_required 
def cadastrar_materia():
    errors={}
    if request.method=="POST":

        lista_materias=["Matemática","Português","História","Geografia","Ciências", "Educação Física","Artes","Inglês","Filosofia","Sociologia","Química","Biologia","Física", "Educação Religiosa", "Educação Financeira","Espanhol", "Literatura","Educação Ambiental","Tecnologia da Informação","Programação","Robótica"]
        lista_series=["1","2","3","4","5","6","7","8","9"]


        nome=request.form.get("nome")
        if nome not in lista_materias:
            errors["nome"]="Essa matéria não existe"
          
        serie=request.form.get("serie")
        if serie not in lista_series:
            errors["serie"]="Essa série não existe"
        if errors:
            return render_materias(errors=errors) 
        escola_id=request.form.get("escola_id")
        materia=Materia(nome=nome, serie=serie, escola_id=escola_id)
        db.session.add(materia)
        try:
            
            nota=Nota(materia=materia,aluno_id=current_user.id)
            db.session.add(nota)
            db.session.commit()
        except Exception as e:
            errors["nome"]="Essa matéria já existe"

            print("erro ao cadastrar matéria", e)  
            db.session.rollback()
        if errors:
            return render_materias(errors=errors)
                 
        return redirect(url_for("escolas" ))
    


@app.route("/notas") 
@login_required 
def notas():
    
 
   
   
    return render_template('notas.html', aluno=current_user) 


@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar_alunos():

    if request.method=="POST":
        escola_id=request.form.get("escola_id") 
        if  not escola_id:
            escola_nome=request.form.get("escola_nome")
            escola=Escola(nome=escola_nome) 
            db.session.add(escola)
            db.session.commit()
            escola_id=escola.id

        nome=request.form.get("nome")
        if not nome:
            return "O nome e a série é obrigatório"
        serie=request.form.get("serie")
       
        
        email=request.form.get("email")
        if not email:
            return "O email é obrigatório" 
        
        confirmacao_senha=request.form.get("confirmacao_senha")
        senha=request.form.get("senha")
        print (senha,confirmacao_senha)
        if senha != confirmacao_senha: 
            return "As senhas são diferentes" 
        
        hash_senha=generate_password_hash(senha) 
        
        aluno=Aluno(nome=nome, serie=serie, escola_id=escola_id, email=email, senha=hash_senha )
        
        db.session.add(aluno)
        try:
            db.session.commit()
        except Exception as e:

            print ("Ocorreu um erro:", e)


    
        return redirect(url_for("notas"))
    else:
        escolas=Escola.query.all()
        return render_template('cadastrar.html',escolas=escolas)
    
    
# @app.route("/cadastrar_nota:<aluno_id>" , methods=['GET', "POST"])

@app.route("/deletar_nota", methods=["GET"])
@login_required 
def deletar_nota():
    id=request.args.get("nota_id")
    nota=Nota.query.get(id)
    db.session.delete(nota)
    db.session.commit()
    return redirect(url_for("notas"))


@app.route("/deletar_materia", methods=["POST"])
@login_required
def deletar_materia():
    materia_id=request.form.get("materia_id")	
    materia=Materia.query.get(materia_id)
    for nota in materia.notas:
        db.session.delete(nota)
        
    materia_nome=materia.nome
    db.session.delete(materia)
    db.session.commit()

    return render_materias(success={materia_id:f"Matéria deletada com sucesso: {materia_nome}"})

@app.route("/atualizar_nota", methods=["POST"])
@login_required 
def atualizar_nota():
    id=request.form.get("nota_id")
    nota1=request.form.get("nota1")
    nota2=request.form.get("nota2")
    nota3=request.form.get("nota3")
    nota=Nota.query.get(id)
    nota.nota1=nota1
    nota.nota2=nota2
    nota.nota3=nota3
    db.session.add(nota)
    db.session.commit()
    return redirect(url_for("notas")) 

@app.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method=="POST":
        #Pega os valores que o usuário digitou na tela
        email=request.form.get("email")
        senha=request.form.get("senha")

        #Busca o aluno no banco de dados usando o email 

        user_aluno=Aluno.query.filter_by(email=email).first()

        #Verifica se existe o aluno com o email incerido e se a senha digitada é a mesma senha 
        #que o aluno cadastrou
        if user_aluno and check_password_hash (user_aluno.senha,senha):
           #Loga o aluno no sistema e redireciona para a tela inicial 
            login_user(user_aluno)
            return redirect(url_for("index")) 
        else: 
            return"login inválido, email ou senha incorretos."

    else:
        return render_template("login.html")
    
@app.route("/sair", methods=["GET"])
@login_required 
def sair():
    logout_user()
    return redirect(url_for("login"))


@app.route("/recuperar_senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form.get("email")
        aluno = Aluno.query.filter_by(email=email).first()
        if aluno:
            token= serializer.dumps(email, salt='recover-key') 
            link = url_for('redefinir_senha', token=token, _external=True)
            msg=Message("Recuperação de Senha", recipients=[email])
            logo_url = url_for('static', filename='logo.png')
            msg.html = f"""
                <img class="mb-4" src="{ url_for('static', filename='logo.png') }" alt="" width="72" height="57">

                <img height="auto" src="https://ci3.googleusercontent.com/meips/ADKq_NYk9VU6Pi4dE0C_d0p-K_mxwaqbBc6OzAGyXr5zQgpkjPcvaE26ovUSzLd7SmbvO-BPJh1IDh8XDPxQI6s7kvXv87kQKMRA8qSLataDPovp_tE_gcghcldRTjaLM0OXM3P5L4lWUYFFN2Ujmy7U1rf89Pbc4Bg_xKISMzmmMqY=s0-d-e1-ft#https://image.news.grupoenjoei.com.br/lib/fe90137276660c7b76/m/8/9864bde5-9286-4cc4-b041-e532788b25e3.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px" width="40" class="CToWUd" data-bit="iit">
                <a class="m_4990549332595761893o-button-primary m_4990549332595761893o-button-large" href="{link}">criar novos sonhos</a>
                
                <p>Olá {aluno.nome},</p>
                <p>Use este link para redefinir sua senha: <a href="{link}">{link}</a></p>
                <p>Se não foi você que solicitou a recuperação de senha, ignore este email.</p>
                """
            mail.send(msg)
            return render_template("recuperar_senha.html", success="Um email foi enviado com o link para redefinir sua senha.")


    else:
        return render_template("recuperar_senha.html")

@app.route("/redefinir_senha/<token>", methods=["GET", "POST"])

def redefinir_senha(token):
    if request.method=="POST":
        email= serializer.loads(token, salt="recover-key")
        senha1= request.form.get("password")
        senha2= request.form.get("password2")
        if senha1 == senha2:
           aluno = Aluno.query.filter_by(email=email).first()
           aluno.senha=generate_password_hash(senha1)
           db.session.add(aluno)
           db.session.commit()
        return render_template ("login.html")
    return render_template("redefinir_senha.html", token=token)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)



