from . import app
from models import Student
from flask import render_template, request, g, flash, redirect

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print request.form
        return redirect('/reptider/{}'.format(request.form['person']))
    return render_template('index.html')

@app.route('/reptider/<list:persons>/', methods=['GET', 'POST'])
def reptider(persons):
    if request.method == 'POST':
        if request.form['add'] != None:
            flash('YOU ADDDED SHIT', 'success')
            return redirect("{}+{}".format(request.url[:-1], request.form['add']))
    return render_template('reptider.html', persons=Student.query.get(persons))
