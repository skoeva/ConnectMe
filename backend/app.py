import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
# Change this to whatever your MySQL password is
MYSQL_USER_PASSWORD = ""
MYSQL_PORT = 3306
MYSQL_DATABASE = "connectmedb"

mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this

# Query for everyone in dataset
query = f"""SELECT * FROM responses"""
data = mysql_engine.query_selector(query)
results = data.fetchall()

# Map user name to index in the query results
name_to_index_map = {}
for i, user in enumerate(results):
    name_to_index_map[user[0]] = i

# Create similarity matrix
mat = [[0] * len(results) for _ in range(len(results))]
for i in range(len(mat)):
    for j in range(len(mat[0])):
        # Calculate similarity based on the L1 loss
        sim = sum([((10 - abs(v1 - v2)) / (10*(len(results[0])-1))) for v1,
                   v2 in zip(results[i][1:], results[j][1:])])
        mat[i][j] = "{:0.2f}".format(sim)


# Calculate similarity between two users given the similarity matrix
def calculate_similarity(name1, name2, sim_matrix):
    # Print statement for debugging (i.e. William Joseph 0.65)
    print(name1, name2,
          sim_matrix[name_to_index_map[name1]][name_to_index_map[name2]])
    return sim_matrix[name_to_index_map[name1]][name_to_index_map[name2]]


# def calculate_similarity(name1, name2):
    # Query for users 'name1' and 'name2'
    query_sql = f"""SELECT * FROM responses WHERE LOWER( name ) LIKE '%%{name1.lower()}%%' OR LOWER( name ) LIKE '%%{name2.lower()}%%'"""
    data = mysql_engine.query_selector(query_sql)
    users = data.fetchall()
    user1 = users[0]
    user2 = users[1]

    # Edge case: if name1 == name 2, return 100% similarity
    if len(users) == 1:
        print("{:0.2f}".format(1.00))
        return "{:0.2f}".format(1.00)

    # Calculate the similarity based on the L1 loss
    sim = sum([((10 - abs(v1 - v2)) / (10*(len(user1)-1))) for v1,
               v2 in zip(user1[1:], user2[1:])])

    # Return similarity in the following format: X.XX
    return "{:0.2f}".format(sim)


# def crazycrazy(name1, name2):
    query = f"""SELECT * FROM responses"""
    data = mysql_engine.query_selector(query)
    results = data.fetchall()

    mat = [[0] * len(results)] * len(results)

    for i in range(len(results)):
        for j in range(len(results)):
            if results[i][0] == results[j][0]:
                mat[i][j] == "{:0.2f}".format(1.00)

            sim = sum([((10 - abs(v1 - v2)) / (10*(len(results[0])-1))) for v1,
                       v2 in zip(results[i][1:], results[j][1:])])

            mat[i][j] = "{:0.2f}".format(sim)

    for i in range(len(results)):
        for j in range(len(results)):
            if (results[i][0] == name1 and results[j][0] == name2) or (results[j][0] == name1 and results[i][0] == name2):
                # print(name1, name2, mat[i][j])
                return mat[i][j]


# def create_similarity_mat(calc_sim_func):
    query = f"""SELECT * FROM responses"""
    data = mysql_engine.query_selector(query)
    results = data.fetchall()

    mat = [[0] * len(results)] * len(results)

    for i in range(len(results[0])):
        for j in range(len(results[0])):
            mat[i][j] = calc_sim_func(results[i][0], results[j][0])
    print(mat)
    return mat


# @app.route("/")
# def home():
#     return render_template('base.html', title="sample html")


# @app.route("/responses")
# def responses_search():
#     text = request.args.get("name")
#     return calculate_similarity(text)

calculate_similarity('William', 'Joseph', mat)

# app.run(debug=True)
