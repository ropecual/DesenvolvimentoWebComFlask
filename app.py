from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import urllib.request
import json


# Criação do app
app = Flask(__name__)


# Configura o banco SQLITE e define o local onde ele estará armazenado https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#installation
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cursos.sqlite3"

# create the extension
db = SQLAlchemy(app)

# Criação da classe para se trabalhar com o banco


class cursos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50))
    descricao = db.Column(db.String(100))
    cargaHoraria = db.Column(db.Integer)
# Criação do metodo construtor

    def __init__(self, nome, descricao, cargaHoraria):
        self.nome = nome
        self.descricao = descricao
        self.cargaHoraria = cargaHoraria


# Criação de rotas
#############################################################################################################################################
# Pagina Principal
frutas = []


@app.route('/', methods=["GET", "POST"])
def principal():
    # frutas =["banana","morango","Uva", "Laranja", "True", "Abacaxi"]
    if request.method == "POST" and request.form.get("fruta"):
        frutas.append(request.form.get("fruta"))

    return render_template("index.html", frutas=frutas)


# Pagina Sobre
registros = []


@app.route('/sobre', methods=["GET", "POST"])
def sobre():
    # notas = {"Roni":10.0, "Camila":10.0, "Chimito":9.0, "Ariel":9.0, "Nanaco":9.0, "Chloe":9.0}
    if request.method == "POST" and request.form.get("nome") and request.form.get("nota"):
        # Adicionado a variavel valor para servir de indice para o dropdown de notas dos alunos
        valor = len(registros)
        registros.append({"aluno": request.form.get("nome"),
                         "nota": request.form.get("nota"),
                          "id": valor})
    return render_template("sobre.html", registros=registros)


# Pagina Filmes (Utiliza Rotas Dinamicas)
@app.route('/filmes/<propriedade>')
def filmes(propriedade):

    if propriedade == 'populares':
        url = "https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=f708d6be3bc0e99dddab1593f8bcb529"
    elif propriedade == 'pontuados':
        url = "https://api.themoviedb.org/3/discover/movie/?certification_country=US&certification=R&sort_by=vote_average.desc&api_key=f708d6be3bc0e99dddab1593f8bcb529"
    elif propriedade == 'criancas':
        url = "https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=f708d6be3bc0e99dddab1593f8bcb529"
    else:
        url = "https://api.themoviedb.org/3/discover/movie?with_people=974169&sort_by=popularity.desc&api_key=f708d6be3bc0e99dddab1593f8bcb529"

    # Abre a url e adiciona seu contudo, não tratado, numa variavel
    resposta = urllib.request.urlopen(url)
    # # Leitura dos dados acessados, não tratado
    dadosBrutos = resposta.read()
    # Tratamento dos dados para JSON
    dadosJson = json.loads(dadosBrutos)

    return render_template("filmes.html", filmes=dadosJson['results'])


# Pagina Cursos
# Cuidado ao utilizar nomes iguais para mais de uma coisa, se a função tiver o mesmo nome do banco, vai dar pau
# https://stackoverflow.com/questions/65337875/flask-sqlalchemy-attributeerror-function-object-has-no-attribute-query
@app.route('/cursosDisponiveis', methods=["GET", "POST"])
def cursosDisponiveis():
    # Adicionando paginação
    pagina = request.args.get('page', 1, type=int)
    por_pagina = 4
    todos_cursos = cursos.query.paginate(page=pagina, per_page=por_pagina)
    return render_template("cursosDisponiveis.html", opcoesCursos=todos_cursos)
    #cursos.query.all() <- Caso queira utilizar sem paginação substituir a variavel de retono todos_cursos pela query ao lado
    #return render_template("cursosDisponiveis.html", opcoesCursos=cursos.query.all())

# Pagina  para adicionar Cursos
# Cuidado com os ; <- Demorei horas para notar que isso estava transformando minhas variaveis de str para lista
@app.route('/novo_curso', methods=["GET", "POST"])
def cria_curso():
    nomeAdicionado = request.form.get("nome")
    descricaoAdicionada = request.form.get("descricao")
    cargaHorariaAdicionada = request.form.get("cargaHoraria")

    if request.method == "POST":
        # Utilizando o modulo flash para mensagens e validações
        if not nomeAdicionado or not descricaoAdicionada or not cargaHorariaAdicionada:
            flash("Preencha todos os campos do formulário", "error")
        else:
            cursoAdicionado = cursos(
                nomeAdicionado, descricaoAdicionada, cargaHorariaAdicionada)
            db.session.add(cursoAdicionado)
            db.session.commit()
            return redirect(url_for('cursosDisponiveis'))

    return render_template("novo_curso.html")


# Rota para atualização dos campos do curso
# para trabalhar com atualizações, utilizamos a chave primaria como propriedade
# qndo se clicar no botão editar, ele enviará, via POST, o id
@app.route('/<int:id>/atualiza_curso', methods=["GET", "POST"])
def atualiza_curso(id):
    # Atribuo a variavel curso a pesquisa feita na tabela cursos, filtrando pelo ID recebido, ou seja, a pagina só receberá a informação relacionada ao ID
    cursoAlterado = cursos.query.filter_by(id=id).first()
    if request.method == "POST":
        # outra forma de recuperar o valor da variavel do input, mesmo resultado, porém sem o .get e utiliza-se chaves []
        nomeAlterado = request.form["nome"]
        descricaoAlterada = request.form["descricao"]
        cargaHorariaAlterada = request.form["cargaHoraria"]
        # Utilizo o SQLALchemy e suas funções para atualizar a tabela com os valores recebidos pelo Form (pagina atualiza_curso.html) Se n filtrar pelo ID, vai ser o famoso
        # "update sem where"
        cursos.query.filter_by(id=id).update({"nome":nomeAlterado, "descricao": descricaoAlterada, "cargaHoraria": cargaHorariaAlterada})
        db.session.commit()
        return redirect(url_for('cursosDisponiveis'))
    return render_template("atualiza_curso.html", curso=cursoAlterado)


# Rota para Exclusão dos campos do curso
# para trabalhar com exclusões, utilizamos a chave primaria como propriedade
@app.route('/<int:id>/exclui_curso', methods=["GET", "POST"])
def exclui_curso(id):
    # Atribuo a variavel curso a pesquisa feita na tabela cursos, filtrando pelo ID recebido, ou seja, a pagina só receberá a informação relacionada ao ID
    cursoExluido = cursos.query.filter_by(id=id).first()
    db.session.delete(cursoExluido)
    db.session.commit()
    # não é necessário um return render_template neste caso
    return redirect(url_for('cursosDisponiveis'))
  



#############################################################################################################################################

    # Inicia o app


if __name__ == '__main__':
    # Inicia os bancos https://stackoverflow.com/questions/73961938/flask-sqlalchemy-db-create-all-raises-runtimeerror-working-outside-of-applicat
    with app.app_context():
        db.create_all()
    # Necessário criar a chave secreta para rodar modulos como flash, além de dar mais segurança -
    # https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session-using-the-flask-session-extension
    app.secret_key = 'asv'
    # Inicia o App em forma de debug
    app.run(debug=True)
