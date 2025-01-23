import socketio  # https://python-socketio.readthedocs.io/en/latest/client.html
import random
import time
import schedule
global do_work


def sendmsg(themessage):
    sio.emit('chatMsg', {'msg': themessage, 'meta': {}})


def sendmsglong(themessage):
    if len(themessage) > 250:
        print(len(themessage))
        new_line_string = '\n\n\n'
        messages = [themessage[i:i+250] for i in range(0, len(themessage), 250)]
        for i in messages:
            sio.emit('chatMsg', {'msg': i.replace('\n\n', new_line_string), 'meta': {}})
            time.sleep(2)

    else:
        sio.emit('chatMsg', {'msg': themessage, 'meta': {}})


C = "!"  # you connect, you disconnect, and you listen, and emit.
sio = socketio.Client()
openpw = open("pw.txt", "r")
pw = (openpw.read()).strip()
startdate = time.time()


def shutdown():
    global do_work
    do_work = False
    sio.disconnect()


def save():
    print("Saving")


def bgtask():
    schedule.every(1).hour.do(save)
    while do_work:
        schedule.run_pending()
        sio.sleep(1)


@sio.event  # on event "connect", run this code
def connect():
    print('connection established')
    sio.emit('joinChannel', {'name': ''})
    sio.emit('login', {'name': '', 'pw': pw})
    time.sleep(1)
    sio.start_background_task(bgtask)

    @sio.on('chatMsg')
    def on_message(data):
        user = data['username']

        if data['msg'].startswith('!flip'):
            coins = ["heads", "tails"]
            flip = random.choice(coins)
            if flip == "heads":
                sendmsg("The coin landed on Heads " + user + ".")
            if flip == "tails":
                sendmsg("The coin landed on Tails " + user + ".")

        if data['msg'].startswith('!ping'):
            start_date = startdate
            minutes = "minutes"
            seconds = "seconds"
            hours = "hours"
            days2 = "days"
            time_difference = int(time.time() - start_date)

            if time_difference < 60:
                sendmsg(f"PONG! Uptime = {time_difference} seconds")
            else:
                if 60 <= time_difference <= 3600:
                    mins, secs = divmod(time.time() - start_date, 60)
                    if int(mins) < 2: minutes = "minute"
                    if int(secs) < 2: seconds = "second"
                    sendmsg(f"PONG! Uptime = {int(mins)} {minutes}, {int(secs)} {seconds}")
                elif 3600 <= time_difference <= 86400:
                    hrs, mins = divmod(time.time() - start_date, 3600)
                    if int(mins) < 2: minutes = "minute"
                    if int(hrs) < 2: hours = "hour"
                    sendmsg(f"PONG! Uptime = {int(hrs)} {hours}, {int(mins / 60)} {minutes}")
                elif time_difference >= 86400:
                    days, hrs = divmod(time.time() - start_date, 86400)
                    if int(hrs) < 2: hours = "hour"
                    if int(days) < 2: days2 = "day"
                    sendmsg(f"PONG! Uptime = {int(days)} {days2}, {int(hrs / 3600)} {hours}")

        if data['msg'].startswith('!commands') or data['msg'].startswith('!help'):
            sendmsg("Current commands are ping, flip")


@sio.event
def connect_error():
    shutdown()
    print("The connection failed!")


@sio.on('addUser')
def on_user_connect(data):
    user = data['name']
    print(user + "has connected.")


@sio.event
def disconnect():
    shutdown()
    print('Disconnected from server.')


sio.connect('') # server ip goes here
sio.wait()
