# -.- coding=utf8 -.-
from bs4 import BeautifulSoup
from . import db, log
from models import Student, Lesson
from math import floor


class Schema:

    def save_lesson(self, day, student, html):
        soup = BeautifulSoup(html)
        data = [unicode(info.text) for info in soup.find_all('td')]
        log.debug(data)
        existing = student.lessons.filter_by(
            day=day,
            start_min=self.to_timestamp(data[0][:5])
        ).first()
        if existing is not None:
            return
        if len(data) < 6:
            data.append('')

        lesson = Lesson(
            day=day,
            start_min=self.to_timestamp(data[0][:5]),
            end_min=self.to_timestamp(data[0][-5:]),
            subject=data[1],
            info=data[2].strip(),
            teachers=data[3],
            _class=data[4],
            rooms=data[5],
            student=student
        )
        db.session.add(lesson)
        db.session.commit()
        log.info("Lektion sparad dag {}:".format(day))
        for info in data:
            log.info(info.encode('utf8'))
            log.info("\n")


    def get_available(self, selected, day_index, start, end):
        start = self.get_start(selected, day_index, start, end)
        log.info("Hål börjar %s" % self.to_timestring(start))
        end = self.get_end(selected, day_index, start, end)
        log.info("Hål slutar %s" % self.to_timestring(end))
        return (start, end)

    def get_start(self, selected, day_index, start, end):
        log.debug("Search start, {} {} dag {}".format(
            self.to_timestring(start),
            self.to_timestring(end),
            self.day_index)
        )
        for stud in selected:
            lessons = stud.lessons.filter_by(day=day_index).order_by(Lesson.start_min).all()
            for lesson in lessons:
                log.debug(u"Testar tid {} lektion {} - {}".format(
                    self.to_timestring(start),
                    self.to_timestring(lesson.start_min),
                    self.to_timestring(lesson.end_min))
                )
                if lesson.start_min <= start and lesson.end_min > start:
                    start = lesson.end_min
                    log.debug("Ny utgångstid %s" % self.to_timestring(start))
                    return self.get_start(selected, day_index, start, end)
        return start

    def get_end(self, selected, day_index, start, end):
        log.debug("Search end, {} {} dag {}".format(
            self.to_timestring(start),
            self.to_timestring(end),
            day_index)
        )
        for stud in selected:
            lessons = stud.lessons.filter_by(day=day_index).order_by(Lesson.start_min).all()
            for lesson in lessons:
                log.debug("Testar tid {} lektion {} - {}".format(
                    self.to_timestring(start),
                    self.to_timestring(lesson.start_min),
                    self.to_timestring(lesson.end_min))
                )
                if lesson.start_min > start and lesson.start_min < end:
                    end = lesson.start_min
                    log.debug("Ny sluttid för hål %s" % self.to_timestring(end))
                    break
        return end

    def to_timestamp(self, timestring):
        return int(timestring[:2])*60+int(timestring[3:5])

    def to_timestring(self, timestamp):
        h = int(floor(timestamp/60))
        m = timestamp % 60
        return "{0:02d}:{1:02d}".format(h, m)

    def remove_NP(self):
        for student in Student.query.all():
            for lesson in student.lessons:
                if lesson.subject[:2] == "NP":
                    log.info(u"Removed {} for {}".format(
                        lesson.subject,
                        student.last_name)
                    )
                    db.session.delete(lesson)
        db.session.commit()
