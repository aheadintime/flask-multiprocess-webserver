
Multiprocess python flask webserver

To start it use

    flask --app app run

To change commands to be executed look for 

    commands = [
        ["ping 8.8.8.8", #COMMAND TITLE
            ['ping','-t', '8.8.8.8']], #COMMAND

To change html refresh rate look for

    refresh_time = 5 #HTML PAGE REFRESH TIME (in seconds)

How it looks like in web browser

![Html Page in web browser](/asset/ui.png)

