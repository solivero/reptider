from scraper import NovaSchemScraper
from schema import Schema
from models import Student, Lesson
from . import log, db
from requests import Timeout
import logging

def main(resume=True, verbose=False, start_id=0, delay=0):
    if verbose:
        log.setLevel(logging.DEBUG)
    schema = Schema()
    log.info("Starting main function")
    scraper = NovaSchemScraper(
        delay=delay,
        width=1820,
        height=573,
        school_id="L000575",
        code="826939"
    )
    scraper.make_session()
    scraper.scrape_IDs()

    if resume:
        #May give error
        last_id = db.session.query(db.func.max(Lesson.student_id)).all()[0][0]
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
        try:
            lessons = scraper.scrape_lessons(student)
            for day_index, lessons in enumerate(lessons):
                for lesson_html in lessons:
                    schema.save_lesson(day_index, student, lesson_html)
        except Timeout as timeout:
            print "Timeout error: " % timeout

    schema.remove_NP()
    print "Finished"
