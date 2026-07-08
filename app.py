from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

TABLECOLUMNS = ['Placement', 'Name', 'Length', 'Date', 'Victors', 'Records', 'Objects', 'Views', 'Likes', 'Comments']


@app.route('/')
def index():
    return render_template('index.html', tablecolumns=TABLECOLUMNS)


@app.route('/creategraph')
def creategraph():
    x = request.args['xvalue']
    print(x)

    y = request.args['yvalue']
    print(y)

    if x in TABLECOLUMNS and y in TABLECOLUMNS:
        conn = sqlite3.Connection('leveldata.db')
        cursor = conn.cursor()

        cursor.execute(f"SELECT {', '.join(['Name', x, y])} FROM leveldata")
        xydata = cursor.fetchall()

        conn.close()


        jsonobject = []
        for xytuple in xydata:
            leveldata = {}
            leveldata['Name'] = xytuple[0]
            leveldata[x] = xytuple[1]
            leveldata[y] = xytuple[2]
            jsonobject.append(leveldata)
            
        return jsonobject
    
    else:
        return 'INVALID INPUT'
    

#python -m flask --debug run