import json
import os
from collections import defaultdict
from flask import Flask, render_template, request, json, jsonify
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

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

# Query for all countries in dataset
query = f"""SELECT * FROM responses"""
data = mysql_engine.query_selector(query)
results = data.fetchall()
len(results)

# Map index to country name from the query results
index_to_name_map = {}
for i, country in enumerate(results):
    index_to_name_map[i] = country[0]

# Create similarity array
sim_array = [0] * len(results)
# Get user input, we'll use a dummy array for now
user = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
# Now, calculate L1 similarity for all countries with the user input
for i in range(len(results)):
    sim_array[i] = sum([((10 - abs(v1 - v2)) / (10*(len(results[0])-1))) for v1,
                        v2 in zip(results[i][1:], user)])

# Map similarity values to countries
sim_to_name_map = defaultdict(list)
for i in range(len(sim_array)):
    sim_to_name_map[sim_array[i]].append(index_to_name_map[i])

# Sort similarity array in descending order
sim_array.sort(reverse=True)

# Get the top 5 similar countries
similar_countries = []
for sim_value in sim_array[:5]:
    similar_countries.extend(sim_to_name_map[sim_value])


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route('/api/calculate_similarity', methods=['POST'])
def calculate_similarity():
    user_input = request.json.get('user_input', [])
    print(user_input)
    # top_5_countries = get_top_countries(user_input)
    top_5_countries = svd_top_countries(
        user_input)  # testing with SVD similarity
    return jsonify(top_5_countries)


def get_top_countries(user_input):
    sim_array = [0] * len(results)
    for i in range(len(results)):
        sim_array[i] = sum([((10 - abs(v1 - v2)) / (10*(len(results[0])-1))) for v1,
                            v2 in zip(results[i][1:], user_input)])
    sim_countries = sorted(
        zip(sim_array, range(len(sim_array))), reverse=True)[:5]
    top_countries = [index_to_name_map[index] for _, index in sim_countries]
    return top_countries


# This is the main idea of the SVD, can make some tweaks if necessary
def svd_top_countries(user_input):
    # Based off the original dataset, but can be changed to fit the previous top 5 countries
    data = np.array([list(row[1:]) for row in results])
    k = 5  # Number of parameters to reduce down to
    scaler = StandardScaler()
    data_standardized = scaler.fit_transform(data)

    # For svd, 1<k<min(data.shape) is required. We need to add dummy columns with value 0 to the data if that is not the case
    n_dummy_cols = 0
    if data_standardized.shape[1] <= k:
        n_dummy_cols = k - data_standardized.shape[1] + 1
    data_standardized = np.concatenate((data_standardized,
                                        np.zeros((data_standardized.shape[0], n_dummy_cols))), axis=1)

    U, sigma, V_trans = svds(data_standardized, k)  # compute SVD

    U_k = U[:, :k]
    sigma_k = np.diag(sigma[:k])
    V_trans_k = np.transpose(np.transpose(V_trans)[:k, :])
    new_data = U_k @ sigma_k @ V_trans_k  # Computing the new data based on k

    user_input_standardized = scaler.transform([user_input])

    # user_input_svd = np.dot(user_input_standardized, U)

    # imported cosine similarity function, but could do it manually as well.
    similarity_scores = cosine_similarity(user_input_standardized, new_data)

    top_country_indices = np.argsort(similarity_scores[0])[::-1][:5]
    top_countries = [index_to_name_map[index] for index in top_country_indices]

    return top_countries
