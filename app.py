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
import itertools
import collections

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
	if request.method == "POST":
		if(request.form.get('filename')):
			select = request.form.get('filename')
		elif (request.form['menu_search']):
			select = request.form.get('menu_search')
	elif request.method == "GET":
		if (request.args.get('more')):
			select = request.args.get('more')
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
	result_dict['ImagePositionPatient'] = str(ds.ImagePositionPatient)
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
		result_dict['ImagePositionPatient'] = docs_list[0]["0020,0032"]
		alltags=[]
		for k,v in docs_list[0].items():
			alltags.append(k)
		result_dict['all tags'] = str(alltags)
		#return q
		#return json.dumps(docs_list, default=json_util.default)
		return render_template('data.html', **locals())
		#return 'Count %d' %cursor

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
	d = {}
	b = 0
	e = 30
	for (dirpath, dirnames, filenames) in walk("/Users/frank/research/dicom/"):
		for f in filenames:
			if f.endswith('.dcm'):
				filepath = os.path.join(dirpath, f)
				ds = dicom.read_file(filepath)
				if("ImagePositionPatient" in ds):
					fn = str(os.path.basename(f).split(".")[0])
					imagename = 'image/'+ fn + '.png'
					d[fn] = (imagename, str(ds.ImagePositionPatient))
				else:
					fn = str(os.path.basename(f).split(".")[0])
					imagename = 'image/'+ fn + '.png'
					d[fn] = (imagename, '')					
	od = collections.OrderedDict(sorted(d.items()))
	od_list = list(od.items())[b:e]
	#s = item + '.dcm'
	#imagename = str('image/'+ item + '.png')
	#path = d.get(s)
	#ds = dicom.read_file(path)
	return render_template('gallery.html', **locals())


@app.route('/query', methods=['GET', 'POST'])
def query():
	docs_list = []
	#return str(request.form.get('Query'))
	if str(request.form.get('Query')) == '0':
		c = mongo2.db.dicoms.find({"0008,0030" : "113850"}).count()
		#return 'Count %d' %c
		docs_list.append(c)
		return render_template('query.html', **locals())
	elif str(request.form.get('Query')) == '1':
		cursor = mongo2.db.dicoms.find({"filename":"IM-0001-0002"})
		docs_list  = list(cursor)
		#return json.dumps(docs_list, default=json_util.default)
		return render_template('query.html', **locals())
	else:
		return render_template('query.html', **locals())
'''
@app.route('/mongo')
def mongo():
	c = mongo2.db.dicoms.find({"0008,0030" : "113850"}).count()  #mongo query
	return 'Count %d' %c 

@app.route('/image')
def image():
	return send_file('IM-0001-0001.png', mimetype='image/gif')
'''
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
