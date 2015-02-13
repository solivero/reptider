# *-* coding: utf-8 *-*
from . import app
from models import Student
from flask import render_template, request, g, flash, redirect
import schema

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print request.form
        return redirect('/reptider/{}'.format(request.form['person']))
    return render_template('index.html', students=Student.query.all())

@app.route('/reptider/<list:persons>/', methods=['GET', 'POST'])
def reptider(persons):
    if request.method == 'POST':
        print request.form
        if request.form['add'] != (None or ''):
            if int(request.form['add']) in persons:
                return redirect(request.url)
            return redirect("{}+{}/".format(request.url[:-1],
                                            request.form['add']))
        elif request.form['remove'] != None:
            persons.remove(int(request.form['remove']))
            url = '/reptider/'
            for id in persons:
                url += str(id) + '+'
            return redirect(url[:-1])
    minimum = 45
    if 'min' in request.args:
        try:
            minimum = int(request.args['min'])
        except ValueError:
            pass
    selected = [Student.query.get(id) for id in persons]
    ## make list of stängningstider till varje dag
    limits = (18*60, 20*60, 20*60, 20*60, 16*60)
    week = []
    for day in range(5):
        available = []
        start = 8*60
        while start < limits[day]:
            reptid = schema.get_available(selected, day, start, limits[day])
            if reptid[1]-reptid[0] >= minimum:
                available.append([(int(time),
                                schema.to_timestring(time)) for time in reptid])
            start = reptid[1]
        week.append(available)
    return render_template('reptider.html',
                           students=Student.query.all(),
                           selected=selected,
                           week=week)

@app.route('/reptider/')
def no_persons():
    return redirect('/')

@app.route('/scrape/')
def scrape():
    schema.main()
    return 'Scrape finished'
