from flask import Flask, render_template, request, jsonify
import serial

##skyColors = ["fe9e4b" , "cc675f" , "99788b" , "4f5474" , "000000" ]
##skyColors = ["ff0000" , "00ff00" , "0000ff" , "ff00ff" , "000000" ]
skyColors = ["eeebe3" , "ffc284" , "fcd485" , "b8eff0" , "000000" ]

gradientTime = 0

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
    ser.write(color.encode('utf-8'))
    return render_template("home.html")

@app.route('/inc', methods = ['POST'])
def inc():
    updateSky(0.02)
    return jsonify(success=True) 

@app.route('/dec', methods = ['POST'])
def dec():
    updateSky(-0.02)
    return jsonify(success=True)

#300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, and 115200
BAUD_RATE = 19200 
if __name__ == '__main__':
    try:
        ser = serial.Serial('/dev/ttyACM0', 19200, timeout=1)
    except:
        try:
            ser = serial.Serial('/dev/ttyACM1', 19200, timeout=1)
        except:
            print("error connecting to serial")
    
    ser.flush()
    app.run(debug=True, host='0.0.0.0', port=80)
