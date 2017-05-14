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

class Aluno(db.Model):
    matricula = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Unicode)
    sobrenome = db.Column(db.Unicode)
    dataNascimento = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    senha = db.Column(db.Unicode)

    def as_dict(self):
        aluno = {
            'matricula': self.matricula,
            'nome': self.nome,
            'sobrenome': self.sobrenome,
            'dataNascimento': self.dataNascimento,
            'email': self.email
        }
        return aluno

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

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Aluno, methods=['GET', 'POST', 'PUT', 'DELETE'], exclude_columns=["senha"])

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)