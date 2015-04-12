from sys import argv
from app import app, schema

commands = ['run']
if len(argv) == 1:
    for command in commands:
        print command
else:
    if argv[1] == "run":
        app.run()
    elif argv[1] == "scrape":
        schema.main()
    else:
        print "Unknown command"
        for command in commands:
            print command
