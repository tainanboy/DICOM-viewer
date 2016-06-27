import os
import sys
import dicom
from os import walk
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot, cm
import pylab
import flask
from flask import Flask, jsonify, send_file, render_template, request, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import json_util
import json

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'kidtest'
#app.config['MONGO_HOST'] = 'localhost'
#app.config['MONGO_PORT'] = 27017
mongo2 = PyMongo(app, config_prefix='MONGO')


@app.route('/')
def index():
	author = "DICOM Viewer"
	name = "User"
	return render_template('index.html', author=author, name=name)

@app.route('/data', methods=['GET', 'POST'])
def data():
	l = []
	RESULTS_ARRAY = []
	select = request.form.get('filename')
	RESULTS_ARRAY.append({'File':str(select)})
	for (dirpath, dirnames, filenames) in walk("/Users/frank/research/dicom/"):
		for f in filenames:
			filepath = os.path.join(dirpath, f)
			if filepath.endswith('.dcm'):
				l.append(filepath)
	file = l[1]
	filename = os.path.basename(file).split(".")[0]
	#print(filename)
	ds = dicom.read_file(file)
	RESULTS_ARRAY.append({'Name':str(ds.PatientName)})
	RESULTS_ARRAY.append({'tags':str(ds.dir())})
	return jsonify(results = RESULTS_ARRAY)
	
@app.route('/query', methods=['GET', 'POST'])
def query():
	if request.method == "POST":
		if request.form['query'] == 'find({"0008,0030" : "113850"}).count()':
			c = mongo2.db.dicoms.find({"0008,0030" : "113850"}).count()
			return 'Count %d' %c
		elif request.form['query'] =='find({"filename":"IM-0001-0002"})':
			cursor = mongo2.db.dicoms.find({"filename":"IM-0001-0002"})
			docs_list  = list(cursor)
			return json.dumps(docs_list, default=json_util.default)


@app.route('/mongo')
def mongo():
	c = mongo2.db.dicoms.find({"0008,0030" : "113850"}).count()  #mongo query
	return 'Count %d' %c 


@app.route('/image')
def image():
	return send_file('IM-0001-0001.png', mimetype='image/gif')

#app.route('/upload', methods=['GET', 'POST'])
# upload_file():

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
