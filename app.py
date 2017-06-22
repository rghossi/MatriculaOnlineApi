import flask
from flask import request, jsonify
import flask_sqlalchemy
import flask_restless
import os
import json
from flask_cors import CORS, cross_origin

app = flask.Flask(__name__)
CORS(app)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ['DATABASE_URL']

db = flask_sqlalchemy.SQLAlchemy(app)

pre_matricula = db.Table('pre_matricula',
  db.Column('matricula_aluno', db.Integer, db.ForeignKey('aluno.matricula')),
  db.Column('codigo_disciplina', db.Unicode, db.ForeignKey('disciplina.codigo'))
)

pre_requisitos = db.Table('pre_requisito',
  db.Column('codigo_disciplina', db.Unicode, db.ForeignKey('disciplina.codigo')),
  db.Column('codigo_pre_requisito', db.Unicode, db.ForeignKey('disciplina.codigo'))
)

class Aluno(db.Model):
  matricula = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.Unicode)
  sobrenome = db.Column(db.Unicode)
  dataNascimento = db.Column(db.Unicode)
  email = db.Column(db.Unicode)
  senha = db.Column(db.Unicode)
  pre_matricula = db.relationship('Disciplina', 
    secondary=pre_matricula
  )

  def as_dict(self):
    pre_matricula = []
    for p in self.pre_matricula:
      pre_matricula.append(p.as_dict())
    aluno = {
      'matricula': self.matricula,
      'nome': self.nome,
      'sobrenome': self.sobrenome,
      'dataNascimento': self.dataNascimento,
      'email': self.email,
      'pre_matricula': pre_matricula
    }
    return aluno

class Disciplina(db.Model):
  codigo = db.Column(db.Unicode, primary_key=True)
  nome = db.Column(db.Unicode)
  creditos = db.Column(db.Integer)
  pre_requisitos = db.relationship('Disciplina', 
    secondary=pre_requisitos,
    primaryjoin='Disciplina.codigo==pre_requisito.c.codigo_disciplina',
    secondaryjoin='Disciplina.codigo==pre_requisito.c.codigo_pre_requisito'
  )

  def as_dict(self):
    pre_requisitos = []
    for p in self.pre_requisitos:
      pre_requisitos.append(p.as_dict())
    disciplina = {
      'codigo': self.codigo,
      'nome': self.nome,
      'creditos': self.creditos,
      'pre_requisitos': pre_requisitos
    }
    return disciplina

db.create_all()

@app.route('/api/login', methods=['POST'])
def login():
  data = request.get_json()
  matches = Aluno.query.filter_by(matricula=data["matricula"],
                                 senha=data["senha"]).all()
  if len(matches) > 0:
    return jsonify({"aluno": matches[0].as_dict()})

  response = app.response_class(
    response=json.dumps({"message": "Wrong login/password pair!"}),
    status=403,
    mimetype='application/json'
  )
  return response

@app.route('/api/disciplinas-disponiveis', methods=['GET'])
def disciplinas_disponiveis():
  data = request.get_json()
  aluno = Aluno.query.get(data["matricula"])
  if aluno:
    disciplinas = Disciplina.query.all()
    disciplinas_disponiveis = []
    for disciplina in disciplinas:
      if not disciplina.pre_requisitos:
        disciplinas_disponiveis.append(disciplina.as_dict())
    return jsonify({"disciplinas": disciplinas_disponiveis})
  
  response = app.response_class(
    response=json.dumps({"message": "Wrong login/password pair!"}),
    status=403,
    mimetype='application/json'
  )
  return response

@app.route('/api/disciplinas-disponiveis-para-quebra-de-requisito', methods=['GET'])
def disciplinas_disponiveis_para_quebra_de_requisito():
  data = request.get_json()
  aluno = Aluno.query.get("113111306")
  if aluno:
    disciplinas = Disciplina.query.all()
    disciplinas_disponiveis = []
    for disciplina in disciplinas:
      if disciplina.pre_requisitos:
        disciplinas_disponiveis.append(disciplina.as_dict())
    return jsonify({"disciplinas": disciplinas_disponiveis})
  
  response = app.response_class(
    response=json.dumps({"message": "Wrong login/password pair!"}),
    status=403,
    mimetype='application/json'
  )
  return response

@app.route('/api/pre-matricula', methods=['POST'])
def pre_matricula():
  data = request.get_json()
  aluno = Aluno.query.get(data["matricula"])
  if aluno:
    for codigo in data["disciplinas"]:
      disciplina = Disciplina.query.get(codigo)
      aluno.pre_matricula.append(disciplina)
    return jsonify({"message": "Success!"})
  else:
    response = app.response_class(
      response=json.dumps({"message": "Something went wrong!"}),
      status=403,
      mimetype='application/json'
    )
    return response

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Aluno, methods=['GET', 'POST', 'PUT', 'DELETE'], exclude_columns=["senha"])
manager.create_api(Disciplina, methods=['GET', 'POST', 'PUT', 'DELETE'])

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port)