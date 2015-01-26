from sys import argv
from app import app

commands = ['run']
if len(argv) == 1:
    for command in commands:
        print command
else:
    if argv[1] == "run":
        app.run()
    else:
        print "Unknown command"
        for command in commands:
            print command
