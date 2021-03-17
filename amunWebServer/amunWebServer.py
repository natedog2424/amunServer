from flask import Flask, render_template
import serial

app = Flask(__name__)
light = False;
@app.route('/')
def hello_world():
    return render_template("home.html")

@app.route('/test', methods = ['POST'])
def test():
    global light
    if light:
        ser.write(b"A")
        light = False;
    else:
        ser.write(b"z")
        light = True;
    print("test")
    return render_template("home.html")

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()
    app.run(debug=True, host='0.0.0.0', port=80)
