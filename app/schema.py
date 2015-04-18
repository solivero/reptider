# -.- coding=utf8 -.-
import re
from requests import Session, Request, Timeout
import json
from bs4 import BeautifulSoup
from . import db
from models import Student, Lesson
import sqlalchemy.sql.functions as func
from math import floor


s = None
postdata = json.load(open('app/static/body.txt'))
click_basedata = postdata['click']
elev_basedata = postdata['elev']
width = 1820
height = 573
urls = {}


def scrape_IDs():
    if Student.query.count() != 0:
        return
    req = Request("POST",
                  urls['schema'],
                  data=elev_basedata.format(
                           p_id="8A553145-C12F-409B-A8DD-2FD5BC8DD9EA")
                  )
    resp = send(s, req, name="Elev")
    soup = BeautifulSoup(resp.text)
    #print(soup)
    for find in soup.findAll("option"):
        parts = re.match(r"(\w+)\s+(\w+\s?\w*)\,\s(\w+)",
                         find.string,
                         flags=re.U)
        if parts:
            print(parts.groups())
            student = Student(
                             schedule_id=find['value'][1:-1],
                             _class=parts.groups()[0],
                             first_name=parts.groups()[2],
                             last_name=parts.groups()[1]
                             )
            db.session.add(student)
    db.session.commit()

def send(s, req, verbose=False, name="", save=False):
    prep = s.prepare_request(req)
    if (prep.body):
        prep.headers['Content-Length']= len(prep.body)
    resp = s.send(prep, timeout=10)
    html = resp.text.encode('utf8')
    if save:
        f = open("{}.html".format(name), "wb")
        f.write(html)
        f.close()
    if verbose:
        print "\n"
        print "###########################################################"
        print "Request info for", name
        info = {"cookies": s.cookies,
                "history": resp.history,
                "url": resp.url,
                "status": resp.status_code,
                "reason": resp.reason,
                "client-headers": prep.headers,
                "length": len(html)}
        for key, value in info.iteritems():
            print "{}\t{}: {}".format(name, key, value)
    return resp


def to_timestamp(timestring):
    return int(timestring[:2])*60+int(timestring[3:5])

def to_timestring(timestamp):
    h = int(floor(timestamp/60))
    m = timestamp % 60
    return "{0:02d}:{1:02d}".format(h, m)

def save_lesson(day, student, html, verbose=True):
    soup = BeautifulSoup(html)
    data = [unicode(info.text) for info in soup.find_all('td')]
    # print(data)
    existing = student.lessons.filter_by(day=day,
                                         start_min=to_timestamp(data[0][:5])
                                         ).first()
    if existing != None:
        return
    if verbose:
        print "Lektion sparad dag {}:".format(day)
        for info in data:
            print info.encode('utf8')
        print ""
    if len(data) < 6:
        data.append('')
    lesson = Lesson(day=day,
                   start_min=to_timestamp(data[0][:5]),
                   end_min=to_timestamp(data[0][-5:]),
                   subject=data[1],
                   info=data[2].strip(),
                   teachers=data[3],
                   _class=data[4],
                   rooms=data[5],
                   student=student
                   )
    db.session.add(lesson)
    db.session.commit()


def click(data):
    req = Request("POST",
                  urls['schema'],
                  data=data,
                  headers={"Content-Length": len(data)})
    resp = send(s, req, name="Click", verbose=False)
    if resp.history:
        req = Request("GET",
                      urls['lesson'],
                      headers={'Referer': urls['schema']})
        return send(s, req, name="Lesson", verbose=False)
    return None


def scrape_lessons(resume=True, start_id=0):
    if resume:
        last_id = db.session.query(func.max(Lesson.student_id)).all()[0][0]
        if last_id:
            start_id = last_id
    for student in Student.query.filter(Student.id>=start_id).all():
        print u"{} {} {} {}".format(student.id,
                                    student.first_name,
                                    student.last_name,
                                    student._class)
        for day in range(5):
            day_width = width/5
            day_x_left = day*(day_width)
            subdivide_y = 20
            x_values = (day_x_left + int(day_width/3.2), day_x_left + int(day_width/2), day_x_left + int(day_width/1.3))
            for x in x_values:
                for i in range(subdivide_y):
                    y = i*(height/subdivide_y)+23
                    click_data = click_basedata.format(x=x,
                                                       y=y,
                                                       p_id=student.schedule_id)
                    lesson = click(click_data)
                    if lesson:
                        save_lesson(day, student, lesson.text)
def remove_NP():
    for student in Student.query.all():
        for lesson in student.lessons:
            if lesson.subject[:2] == "NP":
                print u"Removed {} for {}".format(lesson.subject, student.last_name)
                db.session.delete(lesson)
    db.session.commit()


def make_session():
    s = Session()
    s.headers = json.load(open('app/static/headers.txt'))
    ### Dummy variables for single use only
    p_id = "8A553145-C12F-409B-A8DD-2FD5BC8DD9EA"
    s_id = "sw3cz255idhir455hugrmw45"
    url = "http://www.novasoftware.se/webviewer/(S({}))/MZDesign1.aspx?schoolid=61030&code=77338"
    ### Some dummy requests to get fresh session ids for urls and cookie in the session
    s_id = re.search(r"S\((\w+)", s.get(url.format(s_id)).text.encode('utf8'))
    if s_id:
        s_id = s_id.groups()[0]
    urls['schema'] = url.format(s_id)
    urls['lesson'] = "http://www.novasoftware.se/webviewer/(S({}))/LessonInfo.aspx".format(s_id)
    req = Request("POST", urls['schema'], data=elev_basedata.format(p_id=p_id))
    send(s, req, name="Elev")
    urls['img'] = "http://www.novasoftware.se/ImgGen/schedulegenerator.aspx?format=png&schoolid=61030/sv-se&type=3&id=%7B{p_id}%7D&period=&week=&mode=0&printer=0&colors=32&head=0&clock=0&foot=0&day=0&width={width}&height={height}&maxwidth={width}&maxheight={height}".format(p_id=p_id, width=width, height=height)
    req = Request("GET", urls['img'])
    send(s, req, name="Image")
    return s

def main(start_id=0):
    global s
    s = make_session()
    scrape_IDs()
    try:
        scrape_lessons(resume=False, start_id=start_id)
        remove_NP()
    except Timeout as timeout:
        print "Timeout error: " % timeout
        main()

def get_available(selected, day_index, start, end):
    start = get_start(selected, day_index, start, end)
    print "Hål börjar %s" % to_timestring(start)
    end = get_end(selected, day_index, start, end)
    print "Hål slutar %s" % to_timestring(end)
    print start, end
    return (start, end)

def get_start(selected, day_index, start, end):
    print "Search start, %s %s dag %d" % (to_timestring(start), to_timestring(end), day_index)
    for stud in selected:
        for lesson in stud.lessons.filter_by(day=day_index).order_by(Lesson.start_min).all():
            print u"Testar tid {} lektion {} - {}".format(to_timestring(start),
                                         to_timestring(lesson.start_min),
                                         to_timestring(lesson.end_min))
            if lesson.start_min <= start and lesson.end_min > start:
                start = lesson.end_min
                print "Ny utgångstid %s" % to_timestring(start)
                return get_start(selected, day_index, start, end)
    return start

def get_end(selected, day_index, start, end):
    print "Search end, %s %s dag %d" % (to_timestring(start), to_timestring(end), day_index)
    for stud in selected:
        for lesson in stud.lessons.filter_by(day=day_index).order_by(Lesson.start_min).all():
            print "Testar tid {} lektion {} - {}".format(to_timestring(start),
                                                         to_timestring(lesson.start_min),
                                                         to_timestring(lesson.end_min))
            if lesson.start_min > start and lesson.start_min < end:
                end = lesson.start_min
                print "Ny sluttid för hål %s" % to_timestring(end)
                break
    return end
