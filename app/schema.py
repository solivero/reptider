# -.- coding=utf8 -.-
import re
from requests import Session, Request, Timeout
import json
from bs4 import BeautifulSoup
from . import db
from models import Student, Lesson

s = None
postdata = json.load(open('body.txt'))
click_basedata = postdata['click']
elev_basedata = postdata['elev']
width = 1820
height = 573
urls = {}

def scrape_IDs():
    req = Request("POST", urls['schema'], data=elev_basedata.format(p_id="8A553145-C12F-409B-A8DD-2FD5BC8DD9EA"))
    resp = send(s, req, name="Elev")
    soup = BeautifulSoup(resp.text.encode('utf8'))
    #print(soup)
    for find in soup.findAll("option"):
        parts = re.match(r"(\w+)\s+(\w+\s?\w*)\,\s(\w+)", find.string)
        if parts:
            print(parts.groups())
            c.execute("INSERT INTO students(schedule_id, class, first_name, last_name) VALUES(?, ?, ?, ?)", (find['value'][1:-1], parts.groups()[0], parts.groups()[2], parts.groups()[1]))
    conn.commit()

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

def save_lesson(day, student, html, verbose=True):
    soup = BeautifulSoup(html)
    data = [unicode(info.text) for info in soup.find_all('td')]
    #print(data)
    existing = c.execute("SELECT * FROM lessons WHERE day=? AND start=? AND student_id=?", (day, data[0][:5], student))
    if existing.fetchone():
        return
    if verbose:
        print "Lektion sparad dag {}:".format(day)
        for info in data:
            print info.encode('utf8')
        print ""
    if len(data) < 6:
        data.append('')
    c.execute(
        "INSERT INTO lessons(day, start, end, subject, info, teachers, class, rooms, student_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (day,
        data[0][:5],
        data[0][-5:],
        data[1],
        data[2].strip(),
        data[3],
        data[4],
        data[5],
        student))
    conn.commit()

def click(data):
    req = Request("POST", urls['schema'], data=data, headers={"Content-Length": len(data)})
    resp = send(s, req, name="Click", verbose=False)
    if resp.history:
        req = Request("GET", urls['lesson'], headers={'Referer': urls['schema']})
        return send(s, req, name="Lesson", verbose=False)
    return None

def scrape_lessons(resume=True):
    start_id = 0
    if resume:
        last_id = c.execute('SELECT MAX(student_id) FROM lessons').fetchone()[0]
        if last_id:
            start_id = last_id
    for row in c.execute('SELECT * FROM students WHERE id>=?', (start_id,)).fetchall():
        print(u"{} {} {}".encode('utf8').format(row[2], row[3], row[4]))
        for day in range(5):
            x = day*(width/5) + width/9
            for i in range(10):
                y = i*(height/10)+23
                click_data = click_basedata.format(x=x, y=y, p_id=row[1])
                lesson = click(click_data)
                if lesson:
                    save_lesson(day, row[0], lesson.text)

def make_session():
    s = Session()
    s.headers = json.load(open('headers.txt'))
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

def main():
    global s
    s = make_session()
    #resetDB()
    scrape_IDs()
    try:
        scrape_lessons()
    except Timeout as timeout:
        print "Timeout error: " % timeout
        main()
