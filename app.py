import os
import sys
import dicom
from os import walk
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot, cm
import pylab
from flask import Flask, jsonify, send_file, render_template, request, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
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
	
@app.route('/mongo')
def mongo():
	c = []
	c.append({'count': str(mongo2.db.dicoms.find({"0008,0030" : "113850"}).count())})  #mongo query
	return jsonify(results = c)


@app.route('/image')
def image():
	return send_file('IM-0001-0001.png', mimetype='image/gif')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
