import re
import json
from requests import Session, Request
from bs4 import BeautifulSoup
from main import log
from models import Student, Lesson


class NovaSchemScraper:

    def __init__(self, code, school_id, width=1820, height=573):
        self.height = height
        self.width = width
        self.school_id = school_id
        self.code = code
        self.urls = {
            'schema': (
                "http://www.novasoftware.se/webviewer/(S())/MZDesign1.aspx?"
                "schoolid={school_id}&"
                "code={code}".format(
                    school_id=self.school_id,
                    code=self.code
                )
            ),
            'lesson': (
                "http://www.novasoftware.se/webviewer/(S({}))/LessonInfo.aspx"
            ),
            'img': (
                "http://www.novasoftware.se/ImgGen/schedulegenerator.aspx?"
                "format=png&schoolid={school_id}"
                "/sv-se&type=3&id=%7B{p_id}%7D&period=&week=&mode=0&"
                "printer=0&colors=32&head=0&clock=0&foot=0&day=0&"
                "width={width}&"
                "height={height}&"
                "maxwidth={width}&"
                "maxheight={height}".format(
                    school_id=self.school_id,
                    width=self.width,
                    height=self.height
                )
            ),
        }
        self.session = None
        postdata = json.load(open('app/static/body.txt'))
        self.click_basedata = postdata['click'].format(school_id=self.school_id)
        self.elev_basedata = postdata['elev'].format(school_id=self.school_id)

    def make_session(self):
        log.info("Creating session...")
        self.session = Session()
        self.session.headers = json.load(open('app/static/headers.txt'))
        # Dummy variables for single use only
        p_id = "BFBA0FBE-9726-4BAF-A323-466C69AF51D5"
        s_id = ""
        # Dummy requests to get fresh session ids for urls and cookie in the session
        init_req_data = self.session.get(self.urls['schema']).text.encode('utf8')
        log.debug(init_req_data)
        s_id_match = re.search(r"S\((\w+)", init_req_data)
        if s_id_match:
            s_id = s_id_match.groups()[0]
            log.debug("Got session id {}".format(s_id))
        self.urls['schema'] = self.urls['schema'].replace('S())', 'S({}))'.format(s_id))
        self.urls['lesson'] = self.urls['lesson'].format(s_id)
        req = Request(
            "POST",
            self.urls['schema'],
            data=self.elev_basedata.format(p_id=p_id)
        )
        self.send(req, name="SESSION_CREATE")
        self.urls['img'] = self.urls['img'].format(
            p_id=p_id,
        )
        for key in self.urls.keys():
            log.info("URL for {}: {}".format(key, self.urls[key]))
        req = Request("GET", self.urls['img'])
        self.send(req, name="Image")
        return True

    def click(self, data):
        req = Request(
            "POST",
            self.urls['schema'],
            data=data,
            headers={"Content-Length": len(data)}
        )
        resp = self.send(req, name="Click")
        log.debug("Click response:\n{}".format(resp.text))
        if resp.history:
            req = Request(
                "GET",
                self.urls['lesson'],
                headers={'Referer': self.urls['schema']}
            )
            new_resp = self.send(req, name="Lesson")
            log.debug("Redirect response:\n{}".format(new_resp.text))
            return new_resp
        return None

    def scrape_lessons(self, resume=True, start_id=0):
        # TODO  Dela upp i scraper och schema
        # h]r ]r schemalogik
        if resume:
            #May give error
            last_id = db.session.query.max(Lesson.student_id).all()[0][0]
            if last_id:
                start_id = last_id

        for student in Student.query.filter(Student.id >= start_id).all():
            log.info(u"{} {} {} {}".format(
                student.id,
                student.first_name,
                student.last_name,
                student._class
                )
            )
            # H]r b[rjar ju sj]lva scrapern
            for day in range(5):
                day_width = self.width/5
                day_x_left = day*(day_width)
                subdivide_y = 20
                # TODO HT ELLER VT?? MAKE LOGIC MAN
                x_values = (
                    day_x_left + int(day_width/3.2),
                    day_x_left + int(day_width/2),
                    day_x_left + int(day_width/1.3)
                )
                log.info("Day {}".format(day))
                for x in x_values:
                    for i in range(subdivide_y):
                        y = i * (self.height/subdivide_y) + 23
                        click_data = self.click_basedata.format(
                            x=x,
                            y=y,
                            p_id=student.schedule_id
                        )
                        lesson = self.click(click_data)
                        if lesson:
                            # TODO Abstract away schema variable if feasible
                            self.schema.save_lesson(day, student, lesson.text)

    def send(self, req, name="", save=False):
        prep = self.session.prepare_request(req)
        #if (prep.body):
            #prep.headers['Content-Length']= len(prep.body)
        resp = self.session.send(prep, allow_redirects=True, timeout=10)
        html = resp.text.encode('utf8')
        if save:
            f = open("{}.html".format(name), "wb")
            f.write(html)
            f.close()

        log.debug((
            "\n"
            "###########################################################"
            "Request info for {}".format(name)
        ))
        info = {
            "cookies": self.session.cookies,
            "history": resp.history,
            "url": resp.url,
            "status": resp.status_code,
            "reason": resp.reason,
            "client-headers": prep.headers,
            "length": len(html),
        }
        for key, value in info.iteritems():
            log.debug("{}\t{}: {}".format(name, key, value))
        return resp

    def scrape_IDs(self):
        if Student.query.count() != 0:
            return
        req = Request(
            "POST",
            self.urls['schema'],
            data=self.elev_basedata.format(
                p_id="BFBA0FBE-9726-4BAF-A323-466C69AF51D5"
            )
        )
        resp = self.send(req, name="ID_SCRAPE")
        soup = BeautifulSoup(resp.text)
        for find in soup.findAll("option"):
            parts = re.match(
                r"(\w+)\s+(\w+\s?\w*)\,\s(\w+)",
                find.string,
                flags=re.U
            )
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
