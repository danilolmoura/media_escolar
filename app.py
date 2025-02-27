import os
import random

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Configura banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_notas.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = True
db = SQLAlchemy(app)

class Escola(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nome=db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Escola {self.id} {self.nome}>"
    
class Materia(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nome=db.Column(db.String, nullable=False)
    serie=db.Column(db.Integer,nullable=False)
    escola_id=db.Column(db.Integer,db.ForeignKey("escola.id"),nullable=False) 
    escola=db.relationship("Escola",backref=db.backref("materias",lazy=True)) 

class Aluno(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nome=db.Column(db.String, nullable=False)
    serie=db.Column(db.Integer,nullable=False)
    escola_id=db.Column(db.Integer,db.ForeignKey("escola.id"),nullable=False) 
    escola=db.relationship("Escola",backref=db.backref("alunos",lazy=True)) 

class Nota(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nota1=db.Column(db.Integer, nullable=True)
    nota2=db.Column(db.Integer, nullable=True)
    nota3=db.Column(db.Integer, nullable=True)
    materia_id=db.Column(db.Integer,db.ForeignKey("materia.id"),nullable=False) 
    materia=db.relationship("Materia",backref=db.backref("nota",lazy=True)) 
    aluno_id=db.Column(db.Integer,db.ForeignKey("aluno.id"),nullable=False) 
    aluno=db.relationship("Aluno",backref=db.backref("notas",lazy=True))    

    def media(self):
        media=(self.default(self.nota1)+
                self.default(self.nota2)+
                self.default(self.nota3))/3
        return round(media,1)
    
    
    def default(self, value):
       return value or 0
    

    def css(self, nota):
        
        if (nota==None or nota==""):
        
            return "border rounded px-2 py-1 border-secondary text-secondary bg-secondary bg-opacity-25 fw-bold"
        elif (nota >= 7):
            return "border rounded px-2 py-1 border-success text-success bg-success bg-opacity-25 fw-bold"
        elif (nota >= 5):
            return "border rounded px-2 py-1 border-warning text-warning bg-warning bg-opacity-25 fw-bold"
        else:
            return "border rounded px-2 py-1 border-danger text-danger bg-danger bg-opacity-25 fw-bold"
         
        

        
        
  
    
    
## Cria tabelas do banco
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/escolas") 
def escolas():
    escolas=Escola.query.all()
    return render_template('escolas.html',escolas=escolas) 


@app.route("/cadastrar_escola", methods=["GET", "POST"])
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
def cadastrar_materia():
    if request.method=="POST":

        nome=request.form.get("nome")
        serie=request.form.get("serie")
        escola_id=request.form.get("escola_id")
        materia=Materia(nome=nome, serie=serie, escola_id=escola_id)
        
        db.session.add(materia)
        db.session.commit()
    
        return redirect(url_for("escolas"))


@app.route("/alunos") 
def alunos():
    alunos=Aluno.query.all()
    return render_template('alunos.html',alunos=alunos) 


@app.route("/aluno", methods=["GET","POST"])
def cadastrar_alunos():
    if request.method=="POST":
    
        nome=request.form.get("nome")
        if not nome:
            return "O nome e a série é obrigatório"
        serie=request.form.get("serie")
        escola_id=request.form.get("escola_id")
        aluno=Aluno(nome=nome, serie=serie, escola_id=escola_id)
        
        db.session.add(aluno)
        db.session.commit()
    
        return redirect(url_for("alunos"))
    else:
        escolas=Escola.query.all()
        return render_template('aluno.html',escolas=escolas)
    
    
@app.route("/cadastrar_nota", methods=["GET", "POST"])
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
        return render_template('alunos.html') 
        
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
def deletar_nota():
    id=request.args.get("nota_id")
    nota=Nota.query.get(id)
    db.session.delete(nota)
    db.session.commit()
    return redirect(url_for("alunos"))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)



