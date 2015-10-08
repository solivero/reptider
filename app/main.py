from scraper import NovaSchemScraper
from schema import Schema
from . import log
from requests import Timeout
import logging

def main(verbose=False, start_id=0):
    if verbose:
        log.setLevel(logging.DEBUG)
    schema = Schema()
    log.info("Starting main function")
    scraper = NovaSchemScraper(
        schema=schema,
        width=1820,
        height=573,
        school_id="L000575",
        code="826939"
    )
    scraper.make_session()
    scraper.scrape_IDs()
    try:
        scraper.scrape_lessons(resume=False, start_id=start_id)
        schema.remove_NP()
    except Timeout as timeout:
        print "Timeout error: " % timeout
        main()
