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
from string import Template

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'kidtest'
#app.config['MONGO_HOST'] = 'localhost'
#app.config['MONGO_PORT'] = 27017
mongo2 = PyMongo(app, config_prefix='MONGO')


@app.route('/index')
def index():
	l = []
	filelist = []
	for (dirpath, dirnames, filenames) in walk("/Users/frank/research/dicom/"):
		for f in filenames:
			filepath = os.path.join(dirpath, f)
			if filepath.endswith('.dcm'):
				l.append(filepath)	
	for item in l:
		filelist.append(os.path.basename(item).split(".")[0])
	author = "Medical Viewer"
	name = "User"
	return render_template('index.html', **locals())

@app.route('/data', methods=['GET', 'POST'])
def data():
	l = {}
	result_dict = {}
	select = request.form.get('filename')
	for (dirpath, dirnames, filenames) in walk("/Users/frank/research/dicom/"):
		for f in filenames:
			filepath = os.path.join(dirpath, f)
			if filepath.endswith('.dcm'):
				l[f] = filepath
	s = str(select) + '.dcm'
	path = l.get(s)
	ds = dicom.read_file(path)
	imagename = str('image/'+ str(select) + '.png')
	result_dict['filename'] = str(select)
	result_dict['PatientName'] = str(ds.PatientName)
	result_dict['Date'] = str(ds.StudyDate)
	result_dict['all tags'] = str(ds.dir())
	#RESULTS_ARRAY.append({'tags':str(ds.dir())})
	#return jsonify(RESULTS_ARRAY)
	return render_template('data.html', **locals())

@app.route('/xyz', methods=['GET', 'POST'])
def xyz():
	if request.method == "POST":
		result_dict = {}
		X = request.form.get('x')
		Y = request.form.get('y')
		Z = request.form.get('z')
		q = Template('$x\$y\$z')
		q = str(q.substitute(x=X, y=Y, z=Z))
		cursor = mongo2.db.dicoms.find({"0020,0032" : q})
		docs_list  = list(cursor)
		select = docs_list[0]["filename"]
		imagename = str('image/'+ str(select) + '.png')
		result_dict['filename'] = select
		result_dict['PatientName'] = docs_list[0]["0010,0010"]
		result_dict['Date'] = docs_list[0]["0008,0020"]
		alltags=[]
		for k,v in docs_list[0].items():
			alltags.append(k)
		result_dict['all tags'] = str(alltags)
		#return q
		#return json.dumps(docs_list, default=json_util.default)
		return render_template('data.html', **locals())
		#return 'Count %d' %cursor


@app.route('/query', methods=['GET', 'POST'])
def query():
	if request.form.get('Query') == 'find({"0008,0030" : "113850"}).count()':
		c = mongo2.db.dicoms.find({"0008,0030" : "113850"}).count()
		return 'Count %d' %c
	elif request.form.get('Query') =='find({"filename":"IM-0001-0002"})':
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
