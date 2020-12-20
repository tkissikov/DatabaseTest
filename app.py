from neo4j import GraphDatabase
from flask import Flask, render_template, jsonify, url_for, request, redirect

driver = GraphDatabase.driver(uri='bolt://localhost:7687', auth=('neo4j','1123'))
session = driver.session()

app = Flask(__name__)

def load_db(filename):

    # 'query1' loads the csv file and creates nodes with a relationship given in the task
    query1 = """load csv with headers from 
    'file:///"""+filename+""".csv' as f create (p:Person{id:f.id,
    name:f.name,alias:f.sort_name,email:f.email,
    nationality:'GB'})-[:Membership{id:f.id,group_id:
    f.group_id}]->(o:Organization{group_id:f.group_id,
    name:f.group})"""

    # clear all nodes if there are any. I need this to avoid if the same file is loaded more than once
    session.run("match (n) detach delete n")
    
    # create the database according to 'query1'
    session.run(query1)
    return None

@app.route('/', methods=['POST','GET'])
@app.route('/home', methods=['POST','GET'])
def home():
    return render_template('index.html', message="Hi, this is database")

# this is the decorator for the load_database route. Here one has to enter the name of the csv file
# that needs to be loaded into neo4j. You have to put the csv file in qeustion into neo4j projects 
# folder in order to load it.
@app.route('/load_database', methods=['POST','GET'])
def load_database():
    if request.method == 'POST':
        filename = request.form.get("filename")
        if filename == 'gb_parliament':
            load_db(filename)
            return render_template('index.html', message=filename+"""is loaded. Now you search the database. 
        Go to 'Search in Database'""")
        else:
            return render_template('index.html', message="sorry you have to enter 'gb_parliament' name :)))")
    else:
        return render_template('load_database.html')

@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        name = request.form.get("person")
        map = {'name':name}
        records = session.run("""match (n:Person{name:$name})--(o:Organization) 
                            return n.id,n.alias,n.email,n.nationality,o.group_id""",map)
        for record in records:
            result = dict(record)
        return render_template('index.html',message=[result['n.id'],
                                                     result['n.alias'],
                                                     result['n.email'],
                                                     result['n.nationality'],
                                                     result['o.group_id']])
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True)