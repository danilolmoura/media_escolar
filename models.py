from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

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
    __table_args__ = (db.UniqueConstraint('nome', 'serie', 'escola_id', name='unique_materia'),)

class Aluno( UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nome=db.Column(db.String, nullable=False)
    serie=db.Column(db.Integer,nullable=False)
    escola_id=db.Column(db.Integer,db.ForeignKey("escola.id"),nullable=False) 
    escola=db.relationship("Escola",backref=db.backref("alunos",lazy=True)) 


    email=db.Column(db.String, nullable=False)
    senha=db.Column(db.String, nullable=False)
    __table_args__ = (db.UniqueConstraint( 'email', name='unique_email'),)

class Nota(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nota1=db.Column(db.Integer, nullable=True)
    nota2=db.Column(db.Integer, nullable=True)
    nota3=db.Column(db.Integer, nullable=True)
    materia_id=db.Column(db.Integer,db.ForeignKey("materia.id"),nullable=False) 
    materia=db.relationship("Materia",backref=db.backref("notas",lazy=True)) 
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