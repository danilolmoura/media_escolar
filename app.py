import os
import random
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Aluno, Escola, Materia,Nota
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
app = Flask(__name__)


# Configura banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_notas.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = True
app.config['SECRET_KEY']="*****112" 
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

@app.route("/materias")
@login_required  
def escolas():
    escolas=Escola.query.filter(Escola.id==current_user.escola_id).all()
    
    return render_template('materias.html',escolas=escolas) 



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


@app.route("/cadastrar_materia", methods=["POST"])
@login_required 
def cadastrar_materia():
    if request.method=="POST":

        nome=request.form.get("nome")
        serie=request.form.get("serie")
        escola_id=request.form.get("escola_id")
        materia=Materia(nome=nome, serie=serie, escola_id=escola_id)
        db.session.add(materia)
        try:
            db.session.commit()
        except Exception as e:
            print("erro ao cadastrar matéria", e)  
            db.session.rollback()
                 
        return redirect(url_for("escolas"))


@app.route("/alunos") 
@login_required 
def alunos():
    alunos=Aluno.query.all()
    return render_template('alunos.html',alunos=alunos, aluno=current_user) 


@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar_alunos():

    if request.method=="POST":
    
        nome=request.form.get("nome")
        if not nome:
            return "O nome e a série é obrigatório"
        serie=request.form.get("serie")
        escola_id=request.form.get("escola_id") 
        
        email=request.form.get("email")
        if not email:
            return "O email é obrigatório" 
        
        confirmacao_senha=request.form.get("confirmacao_senha")
        senha=request.form.get("senha")
        print (senha,confirmacao_senha)
        if senha != confirmacao_senha: 
            return "As senhas são diferentes" 
        
        hash_senha=generate_password_hash(senha) 
        aluno=Aluno(nome=nome, serie=serie, escola_id=escola_id, email=email, senha=hash_senha)
        
        db.session.add(aluno)
        try:
            db.session.commit()
        except Exception as e:

            print ("Ocorreu um erro:", e)


    
        return redirect(url_for("alunos"))
    else:
        escolas=Escola.query.all()
        return render_template('cadastrar.html',escolas=escolas)
    
    
@app.route("/cadastrar_nota", methods=["GET", "POST"])
@login_required 
def cadastrar_nota():
    if request.method=="POST":
        nota1=request.form.get('nota1')
        nota2=request.form.get('nota2')
        nota3=request.form.get('nota3')
        materia_id=request.form.get('materia_id')
        aluno_id=request.form.get('aluno_id')



     
        nota=Nota(nota1=nota1, nota2=nota2, nota3=nota3, materia_id=materia_id, aluno_id=aluno_id)
        db.session.add(nota)
        db.session.commit()
        notas=Nota.query.all()
        return redirect(url_for('alunos')) 
        
    else: 
        notas=Nota.query.all() 
        # import pdb 
        # pdb.set_trace()
        alunos=Aluno.query.all()   
        aluno_id=request.args.get('aluno_id')
        aluno=Aluno.query.filter(Aluno.id==aluno_id).first() 
        return render_template('nota.html',escola=aluno.escola,aluno=aluno)

    
# @app.route("/cadastrar_nota:<aluno_id>" , methods=['GET', "POST"])

@app.route("/deletar_nota", methods=["GET"])
@login_required 
def deletar_nota():
    id=request.args.get("nota_id")
    nota=Nota.query.get(id)
    db.session.delete(nota)
    db.session.commit()
    return redirect(url_for("alunos"))

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
    return redirect(url_for("alunos")) 

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



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)



