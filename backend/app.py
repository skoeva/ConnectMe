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
MYSQL_USER_PASSWORD = "mysqlroot"
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
# query = f"""SELECT * FROM responses"""
# data = mysql_engine.query_selector(query)
# results = data.fetchall()

# # Map user name to index in the query results
# name_to_index_map = {}
# for i, user in enumerate(results):
#     name_to_index_map[user[0]] = i

# # Create similarity matrix
# mat = [[0] * len(results) for _ in range(len(results))]
# for i in range(len(mat)):
#     for j in range(len(mat[0])):
#         # Calculate similarity based on the L1 loss
#         sim = sum([((10 - abs(v1 - v2)) / (10*(len(results[0])-1))) for v1,
#                    v2 in zip(results[i][1:], results[j][1:])])
#         mat[i][j] = "{:0.2f}".format(sim)


# Calculate similarity between two users given the similarity matrix
# def calculate_similarity(name1, name2, sim_matrix):
#     # Print statement for debugging (i.e. William Joseph 0.65)
#     # print(name1, name2, sim_matrix[name_to_index_map[name1]][name_to_index_map[name2]])
#     return sim_matrix[name_to_index_map[name1]][name_to_index_map[name2]]


@ app.route("/")
def home():
    return render_template('base.html', title="sample html")


@ app.route("/responses")
def responses_search():
    text = request.args.get("name")
    return calculate_similarity(text, text, mat)


# calculate_similarity('William', 'Joseph', mat)

# app.run(debug=True)
