### This app is for updating an order  list based on the uploaded image . The steps are 
### 1- uploading an image , 2 - classifying it or predicting the image type as sunflower/pizza/dollar bill/dalmation/soccer ball.
###  3- If correctly predicted as the original uploaded image type , update the order  list .  



from flask import Flask, render_template, request
import pickle as p
import numpy as np
from werkzeug.utils import secure_filename
import skimage
from sklearn.utils import Bunch
from skimage.io import imread
from skimage.transform import resize
from datetime import date
import sqlite3 as sql


app = Flask(__name__)

@app.route('/')
def features():
	return render_template('Upload_order.html')

@app.route('/classify_and_update' , methods =  ['GET' , 'POST'])
def classify_and_update():
	if request.method == 'POST':
		
## read in the image and format it for model prediction.
		images = []
		flat_data = []
		target = []
		f = request.files['file']
		f.save(secure_filename(f.filename))
		img = skimage.io.imread(f.filename)
		img_resized = resize(img, output_shape=(64, 64), anti_aliasing=True, mode='reflect')
		flat_data.append(img_resized.flatten())
		images.append(img_resized)
##
## get the image type from the form.
		form_data = request.form.to_dict()
		form_data = list(form_data.values())
		form_data = list(map(int, form_data))
		target.append(form_data[0])
## get the quantity 
		quantity = form_data[1]
##
		image_dataset = Bunch(data = flat_data , target = target , target_names = 'sunflower' , images = images , DESCR = 'A pic for image classification')
		X_test = image_dataset.data
		y_test = image_dataset.target
##
## predict the image type
		predicted = model.predict(X_test)
		if predicted == 0:
			result = 'Dollar_bill'
		elif predicted == 1:
			result = 'Dalmation'
		elif predicted == 2:
			result = 'Soccer_ball'
		elif predicted == 3:
			result = 'Pizza'
		elif predicted ==4:
			result = 'Sunflower'
## check if the predicted is same as the original image type.
		if predicted == y_test:
			result_all = result + ' -Correctly Classified' 
		else:
			result_all = result + ' -Incorrectly Classified'
## get the current date for inventory date
		order_date = date.today()
## insert a new record into inventory if correctly classified.
		if predicted == y_test:
			try:
				with sql.connect("database.db") as con:
					cur = con.cursor()
					cur.execute("INSERT into Order_list (name,quantity,date) VALUES(?,?,?)",(result, quantity, order_date))
					con.commit
					msg = "Record successfully added"
			except:
				con.rollback()
				msg = 'Error in insert '
			finally:
				con.close()
			result_all = result_all + "." + msg
			
		return render_template("image_classification_prediction.html", result = result_all)
## If the user want to list the inventory 
@app.route('/list')
def get_list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute("select * from Order_list")

   rows = cur.fetchall();
   return render_template("list_order.html",rows = rows)

if __name__ == '__main__':
	modelfile = 'Images_classification_model.sav'
	model = p.load(open(modelfile, 'rb'))
	print("model loaded")
	app.run(debug = True,host = '0.0.0.0' ,  port = 5000 )
