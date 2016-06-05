import os
import sys
import dicom
from os import walk
from bs4 import BeautifulSoup
import numpy
from matplotlib import pyplot, cm
import pylab
from flask import Flask, jsonify, send_file, render_template, request, redirect
app = Flask(__name__)

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
	
@app.route('/image')
def image():
    return send_file('IM-0001-0001.png', mimetype='image/gif')

if __name__ == '__main__':
    app.run(debug=True)
