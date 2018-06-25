import os
import tempfile

import pytest

from .. import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/matricula_teste'
    client = app.app.test_client()
    app.db.create_all()
    yield client
    app.db.drop_all()

def test_aluno_crud(client):
    # GET
    rv = client.get('/api/aluno')
    json_data = rv.get_json()
    print json_data
    assert json_data['num_results'] == 0

    # POST
    rv = client.post('/api/aluno', json={
      'matricula': 123456789, 'nome': 'Dioginis', 'sobrenome': 'Carvalho'
    })
    json_data = rv.get_json()

    assert json_data['matricula'] == 123456789
    assert json_data['nome'] == 'Dioginis'
    assert json_data['sobrenome'] == 'Carvalho'
    assert json_data['email'] == None
    assert json_data['pre_matricula'] == []

    # PUT
    rv = client.put('/api/aluno/123456789', json={
      'email': 'dioginis@manguaceiro.com'
    })
    json_data = rv.get_json()
    
    assert json_data['matricula'] == 123456789
    assert json_data['nome'] == 'Dioginis'
    assert json_data['sobrenome'] == 'Carvalho'
    assert json_data['email'] == 'dioginis@manguaceiro.com'
    assert json_data['pre_matricula'] == []

def test_pre_matricula(client):
    # CRIA ALUNO
    rv = client.post('/api/aluno', json={
      'matricula': 123456789, 'nome': 'Dioginis', 'sobrenome': 'Carvalho'
    })

    # CRIA DISCIPLINA
    rv = client.post('/api/disciplina', json={
      'codigo': '1234', 'nome': 'Teste de Software', 'creditos': 3,
    })

    # ADICIONA DISCIPLINA NA PRE MATRICULA
    rv = client.post('/api/pre-matricula', json={
      'matricula': 123456789, 'disciplinas': ['1234']
    })
    json_data = rv.get_json()

    print json_data
    assert json_data['message'] == "Success!"
