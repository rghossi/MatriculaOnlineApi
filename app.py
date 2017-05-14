import flask
import flask_sqlalchemy
import flask_restless
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ['DATABASE_URL']

db = flask_sqlalchemy.SQLAlchemy(app)

class Aluno(db.Model):
    matricula = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Unicode)
    sobrenome = db.Column(db.Unicode)
    dataNascimento = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    senha = db.Column(db.Unicode)

db.create_all()

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Aluno, methods=['GET', 'POST', 'PUT', 'DELETE'])

app.run()