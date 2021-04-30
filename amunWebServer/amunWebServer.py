from flask import Flask, render_template, request, jsonify
import serial
import datetime
import time
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Value, Array
import subprocess

##skyColors = ["fe9e4b" , "cc675f" , "99788b" , "4f5474" , "000000" ]
##skyColors = ["ff0000" , "00ff00" , "0000ff" , "ff00ff" , "000000" ]
skyColors = ["eeebe3" , "ffc284" , "fcd485" , "b8eff0" , "000000" ]

gradientTime = 0
alarmHour = Value('i', 0)
alarmMin = Value('i', 0)
alarmSet = Value('i', 0)
alarmSky = Array('c', "000000000000000000000000000000000000000000000000000000000000")
alarmSound = Array('c', "birds.wav")
wakeDuration = Value('d',1)

def linearGradient(colors, keys):
    if (len(colors) != len(keys)):
        return
    string = "~LV"
    string += str(len(colors))
    string += "{"

    for index in range(len(colors)):
        string += str(keys[index])
        string += "#"
        string += colors[index]
    string += "}"
    ser.write(string.encode('utf-8'))
    print(string.encode('utf-8'))


def updateSky(offset):
    global gradientTime
    gradientTime += offset
    gradientTime = max(min(gradientTime, 1), 0)
    print(gradientTime)
    keyValues = [0,0,0,0,0]
    for key in range(len(keyValues)):
        keyValues[key] = ((key) * 0.25) * gradientTime
    linearGradient(skyColors, keyValues)

app = Flask(__name__)
@app.route('/')
def hello_world():
    return render_template("home.html")

@app.route('/test', methods = ['POST'])
def test():
    color = request.form['color']
    
    print(color)
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    ser.write(color.encode('utf-8'))
    return render_template("home.html")

@app.route('/alarm', methods = ['POST'])
def alarm():
    global alarmHour
    global alarmMin
    global alarmSet
    global alarmSky
    global alarmSound
    global wakeDuration

    time = request.form['time']
    alarmSky.value = request.form['sky']
    alarmSound.value = request.form['sound']
    wakeDuration.value = float(request.form['duration'])
    print(alarmSky)
    print(wakeDuration)

    alarmHour.value = int(time[:2])
    alarmMin.value = int(time[-2:])
    alarmSet.value = int(True)
    
    print(time)
    return render_template("home.html")

@app.route('/inc', methods = ['POST'])
def inc():
    updateSky(0.02)
    return jsonify(success=True) 

@app.route('/dec', methods = ['POST'])
def dec():
    updateSky(-0.02)
    return jsonify(success=True)

def alarmRing():
    player = subprocess.Popen(["mplayer", "amunServer/amunWebServer/" + alarmSound.value, "-volume", "100"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    string = "~s"
    string += str(wakeDuration.value*60)
    string += "#"
    string += alarmSky.value
    ser.write(string.encode('utf-8'))
    ser.flush()
    ##for vol in range(1):
    ##    player.stdin.write("q")
    ##    time.sleep((wakeDuration.value*60)/33)

def alarmCheck(alarmHour, alarmMin, alarmSet):
    while(True):    
        now = datetime.datetime.now()
        print(now.hour)
        print(now.minute)

        print(alarmHour.value)
        print(alarmMin.value)
        print(alarmSet.value)
        if (alarmSet.value):
            if (((now.hour >= alarmHour.value) and (now.minute >= alarmMin.value)) or (now.hour > alarmHour.value)):
                alarmSet.value = False
                alarmRing()
        time.sleep(5)

#300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, and 115200
BAUD_RATE = 19200 
if __name__ == '__main__':
    alarmHour = Value('i', 0)
    alarmMin = Value('i', 0)
    alarmSet = Value('i', 0)
    try:
        ser = serial.Serial('/dev/ttyACM0', 19200, timeout=1)
    except:
        try:
            ser = serial.Serial('/dev/ttyACM1', 19200, timeout=1)
        except:
            print("error connecting to serial")
    
    ser.flush()
    p = Process(target=alarmCheck, args=(alarmHour, alarmMin, alarmSet))
    p.start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)
    p.join()
