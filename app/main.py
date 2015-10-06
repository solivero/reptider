import logging
from scraper import NovaSchemScraper
from schema import Schema
log = logging.getLogger()
log.setLevel(logging.INFO)

out = logging.StreamHandler(stdout)
out.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
out.setFormatter(formatter)
log.addHandler(out)

def main(start_id=0):
    scraper = NovaSchemScraper(
        width=1820,
        height=573,
        school_id="L000575",
        code="826939"
    )
    scraper.scrape_IDs()
    try:
        scraper.scrape_lessons(resume=False, start_id=start_id)
        schema.remove_NP()
    except Timeout as timeout:
        print "Timeout error: " % timeout
        main()
