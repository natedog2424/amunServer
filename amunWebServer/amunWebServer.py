from flask import Flask, render_template, request
import serial

app = Flask(__name__)
@app.route('/')
def hello_world():
    return render_template("home.html")

@app.route('/test', methods = ['POST'])
def test():
    color = request.form['color']
    ##color = color[1:]
    print(color)
    try:
        ser.write(color.encode('utf-8'))
    except:
        print("no serial connection")
    return render_template("home.html")

if __name__ == '__main__':
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.flush()
    except:
        print("no arduino connected")
    app.run(debug=True, host='0.0.0.0', port=80)
