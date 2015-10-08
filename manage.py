from sys import argv
from app import app, main

commands = ['run']
if len(argv) == 1:
    for command in commands:
        print command
else:
    verbose = False
    if "-v" in argv:
        verbose = True
    if argv[1] == "run":
        app.run()
    elif argv[1] == "scrape":
        main.main(verbose=verbose)
    else:
        print "Unknown command"
        for command in commands:
            print command
