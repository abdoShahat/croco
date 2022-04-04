import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from feature_extractor import FeatureExtractor
import numpy as np 
from pathlib import Path
from PIL import Image
import time
from io import BytesIO
import zipfile



fe = FeatureExtractor()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('test.html')

@app.route('/', methods=['POST'])
def upload_image():
	if 'files[]' not in request.files:
		flash('No file part')
		return redirect(request.url)
	files = request.files.getlist('files[]')
	file_names = []
	m = len(files)
	print("number of images is {}".format(m))
	for file in files:
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file_names.append(filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#else:
		#	flash('Allowed image types are -> png, jpg, jpeg, gif')
		#	return redirect(request.url)
	fet()
	return render_template('download.html', filenames=file_names)


def fet():
	print('in feature function')
	for img_path in sorted(Path("static/uploads").glob('*')):
		print('loading')
		feature = fe.extract(img=Image.open(img_path))
		feature_path = Path("static/feat")/(img_path.stem+".npy")
		np.save(feature_path,feature)

@app.route('/download')
def download():
	fantazy = zipfile.ZipFile('static/feat/archive.zip','w')
	for folder,subfolder,files in os.walk('static/feat'):
		for file in files:
			if file.endswith('.npy'):
				fantazy.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), 'static/feat'), compress_type = zipfile.ZIP_DEFLATED)
	fantazy.close()
	# return send_file(memory_file,
    #                  attachment_filename=fileName,
    #                  as_attachment=True)	# pass

	return send_file('static/feat/archive.zip',as_attachment=True)
# @app.route('/display/<filename>')
# def display_image(filename):
# 	#print('display_image filename: ' + filename)
# 	return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)