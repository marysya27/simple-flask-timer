from flask import Flask, request, render_template, url_for, g, jsonify, redirect, session
import os
import sqlite3
from FDataBase import FDataBase
import random


DATABASE = '/tmp/flblog.db'
SECRET_KEY = "c289e5ace89efcecbb6be9f17eaa4045ad359444"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'fltimer.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().execute(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()



@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('receive_timer_data'))
    return render_template('login.html')

full_arr_scramble_txt = [
                        'F', 'F2', "F'",
                        'B', 'B2', "B'",
                        'L', 'L2', "L'",
                        'R', 'R2', "R'",
                        'U', 'U2', "U'",
                        'D', 'D2', "D'",  
                    ]

number_of_elements = 20

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        if dbase.is_name_in_db(request.form['name']):
            session['username'] = username
        else:
            res = dbase.add_user(request.form['name'])
            if res:
                session['username'] = username
        return redirect(url_for('receive_timer_data'))

    return render_template('main.html', scramble = get_scramble())
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('login.html')

def calc(el):
    res = el / 100
    part1_res = abs(res) // 60
    part2_res = str(abs(res) - (part1_res * 60))
    if len(str(int(float(part2_res)))) == 1:
        part2_res = '0'+part2_res
    part2_res =  part2_res[:2] + ':' + part2_res[3:]
    final_res = str(int(part1_res)) + ':' + part2_res[:5]    
        
    if final_res[0] == '0':
        final_res = final_res[2:]

    return final_res


def get_final_time_list(all_time):
    final_time_list = []
    final_time_list_for_calc = []

    count = 1

    for i in all_time:
        parts = i.split(':')
        
        hours = parts[0]
        minutes = parts[1]
        seconds = parts[2] if len(parts[2]) == 2 else '0' + parts[2]
        milliseconds = parts[3] if len(parts[3]) == 2 else '0' + parts[3]
        min = minutes if len(minutes) == 2 else '0' + minutes

        r = ''

        if int(hours) == 0 and int(minutes) == 0:
            r = seconds + ':' + milliseconds

        elif int(hours) == 0 and int(minutes) != 0:
            r = min + ':' + seconds + ':' + milliseconds

        else:
            r = hours + ':' + min + ':' + seconds + ':' + milliseconds

        final_time_list_for_calc.append(r)

        r = f'<span class="each-time"><span class="each-time-count">{count}. </span>{r}</span>'

        final_time_list.append(r)
        count += 1
    return [final_time_list_for_calc, final_time_list]

def get_scramble():
    scramble_array = [] 
    el_index = 0

    for _ in range(number_of_elements):
        elem = random.choice(full_arr_scramble_txt)
        index_current_elem = full_arr_scramble_txt.index(elem)
        range_index = [ i for i in range(el_index-2, el_index+3)]
        while index_current_elem in range_index:
            elem = random.choice(full_arr_scramble_txt)
            index_current_elem = full_arr_scramble_txt.index(elem)

        el_index = index_current_elem
            

        scramble_array.append(elem)

    return scramble_array

def get_best_time(times):
    min_el = 0

    for el in times:
        if len(el) == 8:
            time_in_mll = (int(el[:2]) * 6000) + int(el[3:5]) * 100 +int(el[6:])
        else:
            time_in_mll = int(el[:2]) * 100 +int(el[3:])

        if times.index(el) == 0:
            min_el = time_in_mll

        if time_in_mll < min_el:
            min_el = time_in_mll

    return calc(min_el)

def get_full_average_time(times):
    sum = 0

    for el in times:
        if len(el) == 8:
            time_in_mll = (int(el[:2]) * 6000) + int(el[3:5]) * 100 +int(el[6:])
        else:
            time_in_mll = int(el[:2]) * 100 +int(el[3:])

        sum += time_in_mll

    avr = sum / len(times)
    return calc(round(avr, 2))


@app.route('/send_timer_data', methods=['POST', 'GET'])
def receive_timer_data():
    username = session['username']
    if request.method == 'GET':
        data_by_nick = dbase.get_data_by_nick(username)
        arr_current_time = [i['time'] + ':' +str(i['milli']) for i in data_by_nick]

        res_arr = get_final_time_list(arr_current_time)[1]

        return render_template('main.html', arr_current_time = res_arr[::-1], scramble = get_scramble())


    if request.method == 'POST':
        timer_data = request.json['timerData']

        components = timer_data.split(":") 

        time_obj = ':'.join(timer_data.split(':')[:-1])
        id_by_nick = dbase.get_id_by_nick(username)

        res_for_db = dbase.add_time(id_by_nick['user_id'], time_obj, int(components[3]) )

        get_all_time = dbase.get_data_by_nick(username)
        all_time = [i['time'] + ':' +str(i['milli']) for i in get_all_time]
        times = get_final_time_list(all_time)[1]
        times_for_calc = get_final_time_list(all_time)[0]
        
        if len(times_for_calc) > 1:
            try:
                t1 = times_for_calc[-1]
                t2 = times_for_calc[-2]
                if len(t1) == 8:
                    time1inm = (int(t1[:2]) * 6000) + int(t1[3:5]) * 100 +int(t1[6:])
                else:
                    time1inm = int(t1[:2]) * 100 +int(t1[3:])


                if len(t2) == 8:
                    time2inm = (int(t2[:2]) * 6000) + int(t2[3:5]) * 100 +int(t2[6:])
                else:
                    time2inm = int(t2[:2]) * 100 +int(t2[3:])

                diff = time1inm - time2inm
                difference = calc(diff)

                if diff < 0:
                    difference = '-'+difference
                else:
                    difference = '+'+difference

            except Exception:
                difference = ''

        else:
            difference = ''

        average_last_5 = '-'
        average_last_10 = '-'
        if len(times_for_calc) >= 5:
           average_last_5 =  get_full_average_time(times_for_calc[-5:])
        if len(times_for_calc) >= 10:
           average_last_10 =  get_full_average_time(times_for_calc[-10:])

        try:
            f_avr_time = get_full_average_time(times_for_calc)
        except Exception:
            f_avr_time = '-'


        return {'times' : times, 'scramble_arr' : get_scramble(), 'difference' : difference,
                 'best_time' : get_best_time(times_for_calc), 'full_average_time' : f_avr_time,
                 'average_last_5' : average_last_5, 'average_last_10' : average_last_10}, 200
    
@app.route('/delete_attempt', methods=['POST'])
def delete_attempt():
    if request.method == 'POST':
        count = request.json['countDelete']

        res = dbase.delete_last_n_entries_by_nick(dbase.get_id_by_nick(session['username'])['user_id'], int(count))

        return 'success', 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
