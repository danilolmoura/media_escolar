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



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)


