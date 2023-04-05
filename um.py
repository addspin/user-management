from flask import Flask, render_template, url_for, request, jsonify, session, flash, redirect
# from flask_sqlalchemy import SQLAlchemy
import os 
from os.path import join, dirname, realpath
import sqlite3
import pandas as pd
import json

path_db = 'db/um.db'
name_table_service = 'service'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some random string'

# Upload folder
UPLOAD_FOLDER = 'static/import_files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

# @app.route('/')
# def search():
#     return render_template('search.html', side_pos='active')

@app.route('/service')
def service():
    search_value = False
    search_value = search_service()
    return render_template('service.html', side_pos='active', search_value=search_value)

@app.route('/service_insert', methods=['GET', 'POST']) 
def service_insert():
    service_name = False
    search_value = False
    if request.method == 'POST':
        form = request.form
        service_name = insert_data_form_service(form)
        search_value = search_service()
    search_value = search_service()
    return render_template('service.html', side_pos='active', service_name=service_name, search_value=search_value)

# @app.route('/service_search', methods=['GET', 'POST'])
# def service_search():
#     service_search_data = False
#     service_name = False
#     if request.method == 'POST':
#         service_name_search = request.form['service_name_search']
#         if service_name_search != '':
#             service_search_data = service_name_search_data(service_name_search)
#             search_value = search_service()
#         else:
#             return redirect(url_for('service'))
#     return render_template('service_search.html', side_pos='active', service_name=service_name, search_value=search_value, service_name_search=service_name_search, service_search_data=service_search_data)

@app.route('/service_change', methods=['GET', 'POST'])
def service_change():
    if request.method == 'POST':
        form = request.form
        change_data_form_service(form)
    return redirect(url_for('service'))

def change_data_form_service(form):
    service_name = request.form['service_name']
    service_name_old = request.form['service_name_old']
    service_url = request.form['service_url']
    service_text = request.form['service_text']
    service_owner = request.form['service_owner']
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    if service_text == '':
        service_text = "Нет информации"
    if service_name != service_name_old:
        cursor.execute('DELETE FROM service WHERE service_name =?', (service_name_old, ))
        cursor.execute('INSERT INTO service values (?, ?, ?, ?)', (service_name, service_url, service_text, service_owner))
    cursor.execute('REPLACE INTO service values (?, ?, ?, ?)', (service_name, service_url, service_text, service_owner))    
    conn.commit()
    conn.close()
   

@app.route('/service_del', methods=['GET', 'POST'])
def service_del():
    service_name = False
    if request.method == 'POST':
        service_name = request.form.getlist('check_service')
        delete_data_form_service(service_name)
    return redirect(url_for('service'))

def delete_data_form_service(service_name):
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    for value in service_name:
        print(value)
        cursor.execute('DELETE FROM service WHERE service_name =?', (value, ))  
    conn.commit()
    conn.close()

def service_name_search_data(service_name_search):
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    cursor.execute('select * from service where service_name =?', (service_name_search, ))  
    results = cursor.fetchone()
    conn.close()
    return (results)

def search_service():
    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("create table if not exists service (service_name varchar(300) PRIMARY KEY, service_url varchar(300), service_text text, service_owner varchar(300));")  
    cursor.execute('SELECT * FROM service')  
    results = cursor.fetchall()
    conn.close()
    return (results)

def insert_data_form_service(form):
    service_name = request.form['service_name']
    service_url = request.form['service_url']
    service_text = request.form['service_text']
    service_owner = request.form['service_owner']
    if service_text == '':
        service_text = "Нет информации"
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
 

    # Проверка существует ли сервис
    service_name_test = cursor.execute('SELECT * FROM service WHERE service_name=?', (service_name, ))
    if service_name_test.fetchone() is None: 
        # Запись нового сервиса, если такого еще не существует
        cursor.execute("create table if not exists service (service_name varchar(300) PRIMARY KEY, service_url varchar(300), service_text text, service_owner varchar(300));")  
        cursor.execute("INSERT INTO service values (?, ?, ?, ?)", (service_name, service_url, service_text, service_owner))
        conn.commit()
        conn.close()
        flash(f"Сервис")
    else:
        flash(f"Сервис", 'error')
    return (service_name)

# @app.route('/service_search', methods=['GET', 'POST'])
# def service_search():
#     service_name = False
#     if request.method == 'POST':
#         form = request.form
#         service_name_search = insert_data_form_service_search(form)

#     # return render_template('service.html', side_pos='active', service_name=service_name)
#     # return()
#     return redirect(url_for('service_insert'))


# -------------------------------------Просмотр информации пользователя--------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        user_name = request.form['user_name']
        user = False
        user = search_users()
        display = "display: block;"
        service_data = search_service_name(form)
        object_data = search_object_name(form)
        return render_template('search.html', side_pos='active', object_data=object_data, service_data=service_data, user=user, user_name=user_name, display=display)

    else:
        user = False
        user = search_users()
        display = "display: none;"
        return render_template('search.html', side_pos='active', user=user, display=display)

def search_service_name(form):
    user_name = request.form['user_name']
    if user_name != ' ':
        conn = sqlite3.connect(path_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("select * from service_data where user_name = ?", (user_name, )) 
        result = cursor.fetchall()
        return(result)


def search_object_name(form):
    user_name = request.form['user_name']
    if user_name != ' ':
        conn = sqlite3.connect(path_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("select * from object_data where user_name = ?", (user_name, )) 
        results = cursor.fetchall()
        return(results)

@app.route('/remove_from_user', methods=['GET', 'POST'])
def remove_from_user():
    if request.method == 'POST':
        service_name = False
        data = request.form
        conn = sqlite3.connect(path_db)
        cursor = conn.cursor()
        if service_name != ' ':
            for value in data:
                # print (data[value])
                if "check_service_" in value:
                    service_name = data[value] 
                    cursor.execute('DELETE FROM service_data WHERE service_name = ?', (service_name, ))
                    conn.commit()
            # for value in data:        
                if "device_ident_" in value:
                    device_ident = data[value] 
                    cursor.execute('DELETE FROM object_data WHERE device_ident = ?', (device_ident, ))   
                    conn.commit()
            conn.close()
            return redirect(url_for('search'))



# -------------------------------------Пользователи --------------------------------------------------
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        form = request.form
        search_value = False
        device_value = False
        user = False
        search_value = search_service()
        device_value = search_device()
        user = search_users()
        user_name = insert_data_type_form_user(form)
        return render_template('users.html', side_pos='active', user_name=user_name, search_value=search_value, device_value=device_value, user=user)
    else:
        search_value = False
        device_value = False
        user = False
        search_value = search_service()
        device_value = search_device()
        user = search_users()
        return render_template('users.html', side_pos='active', search_value=search_value, device_value=device_value, user=user)


# @app.route('/users')
# def users():
#     search_value = False
#     device_value = False
#     user = False
#     search_value = search_service()
#     device_value = search_device()
#     user = search_users()
#     return render_template('users.html', side_pos='active', search_value=search_value, device_value=device_value, user=user)

# @app.route('/user_insert', methods=['GET', 'POST'])
# def user_insert():
#     if request.method == 'POST':
#         form = request.form
#         search_value = False
#         device_value = False
#         user = False
#         search_value = search_service()
#         device_value = search_device()
#         user = search_users()
#         user_name = insert_data_type_form_user(form)
#     return render_template('users.html', side_pos='active', user_name=user_name, search_value=search_value, device_value=device_value, user=user)


def insert_data_type_form_user(form):
    data = request.form
    # data = request.get_json()
    user_name = request.form['user_name']
    if user_name != ' ':
        conn = sqlite3.connect(path_db)
        cursor = conn.cursor()
        cursor.execute("create table if not exists service_data (user_name varchar(300), service_name varchar(300) PRIMARY KEY, service_url varchar(300), service_text varchar(1000), service_owner varchar(300));") 
        cursor.execute("create table if not exists object_data (user_name varchar(300), device_ident varchar(300) PRIMARY KEY, device_inv varchar(300), device_type varchar(1000), device_text varchar(300));") 
        service_name = False
        service_url = False
        service_text = False
        service_owner = False

        device_ident = False
        device_inv = False
        device_type = False
        device_text = False
        # test_data_service = False
        # service_name = ""
        # for value in data:
        for value in data:
            print (data)
            if 'service_name_' in value:
                service_name = data[value]
            if "service_url_" in value:
                service_url = data[value]
            if "service_text_" in value:
                service_text = data[value]
            if "service_owner_" in value:
                service_owner = data[value]
                cursor.execute("REPLACE INTO service_data (user_name, service_name, service_url, service_text, service_owner) values (?, ?, ?, ?, ?)", (user_name, service_name, service_url, service_text, service_owner))
                # cursor.execute('REPLACE INTO service_data values (?, ?, ?, ?, ?)', (user_name, service_name, service_url, service_text, service_owner))
        # conn.commit()
            # test_data_service = cursor.execute('SELECT * FROM service_data WHERE service_name=?', (service_name, ))
            # if test_data_service.fetchone() is None:
            
            # cursor.execute('REPLACE INTO service_data values (?, ?, ?, ?, ?)', (user_name, service_name, service_url, service_text, service_owner))
                # cursor.execute('INSERT INTO service_data values (?, ?, ?, ?, ?)', (user_name, service_name, service_url, service_text, service_owner))
            # conn.commit()

        # for value in data:
        #     if "device_ident_" in value:
        #         device_ident = data[value]
        #         # print(device_ident)
        #     if "device_inv_" in value:
        #         device_inv = data[value]
        #     if "device_type_" in value:
        #         device_type = data[value]
        #     if "device_text_" in value:
        #         device_text = data[value]

        #     cursor.execute('REPLACE INTO object_data values (?, ?, ?, ?, ?)', (user_name, device_ident, device_inv, device_type, device_text))
            # conn.commit() 
        # device_ident = ""
        device_ident = False
        device_inv = False
        device_type = False
        device_text = False
        for value in data: 
            if "device_ident_" in value:
                device_ident = data[value]
            if "device_inv_" in value:
                device_inv = data[value]
            if "device_type_" in value:
                device_type = data[value]
            if "device_text_" in value:
                device_text = data[value]
        #     # test_data_ident = cursor.execute('SELECT * FROM object_data WHERE device_ident=?', (device_ident, ))
        #     # if test_data_ident.fetchone() is None: 
        #         # cursor.execute('INSERT INTO object_data values (?, ?, ?, ?, ?)', (user_name, device_ident, device_inv, device_type, device_text))
                cursor.execute('REPLACE INTO object_data (user_name, device_ident, device_inv, device_type, device_text) values (?, ?, ?, ?, ?)', (user_name, device_ident, device_inv, device_type, device_text))
            # conn.commit() 

                
        # if device_ident == "" and service_name == "":
        #     flash("Сервисы и объекты не выбраны", 'user_error')
        # else:
        #     flash(f"Информация для пользователя ", 'info_add')
 
    conn.commit()
    conn.close()
    return(user_name)
    # else:
    #     flash("Имя пользователя небыло выбрано!", 'user_error')

def search_users():
    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # cursor.execute("create table if not exists device (id integer, device_type_name varchar(300), device_inv varchar(300), device_ident varchar(300) PRIMARY KEY, device_text varchar(300));")    
    cursor.execute('SELECT * FROM users')
    results = cursor.fetchall()
    conn.close()
    return (results)

@app.route('/device', methods=['GET', 'POST'])
def device():
    search_value = False
    device_value = False
    search_value = search_device_type()
    device_value = search_device()
    return render_template('device.html', side_pos='active', search_value=search_value, device_value=device_value)

@app.route('/device_insert', methods=['GET', 'POST']) 
def device_insert():
    device_ident = False
    search_value = False
    if request.method == 'POST':
        form = request.form
        insert_data_form_device(form)
        search_value = search_device_type()
        device_value = search_device()
    return render_template('device.html', side_pos='active', device_value=device_value, search_value=search_value)

@app.route('/device_insert_type', methods=['GET', 'POST']) # создать отдельный /service_insert и /service_search
def device_insert_type():
    device_type_name = False
    search_value = False
    if request.method == 'POST':
        form = request.form
        device_type_name = insert_data_type_form_device(form)
        search_value = search_device_type()
        device_value = search_device()
    return render_template('device.html', side_pos='active', device_value=device_value, device_type_name=device_type_name, search_value=search_value)

@app.route('/device_remove_type', methods=['GET', 'POST']) # создать отдельный /service_insert и /service_search
def device_remove_type():
    # device_type_name = False
    search_value = False
    if request.method == 'POST':
        form = request.form
        device_type_name = remove_type(form)
        search_value = search_device_type()
        device_value = search_device()
    return render_template('device.html', side_pos='active', device_value=device_value, device_type_name=device_type_name, search_value=search_value)

@app.route('/device_del', methods=['GET', 'POST'])
def device_del():
    device_ident = False
    if request.method == 'POST':
        device_ident = request.form.getlist('device_ident')
        delete_data_form_device(device_ident)
    return redirect(url_for('device'))

def delete_data_form_device(device_ident):
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    for value in device_ident:
        cursor.execute('DELETE FROM device WHERE device_ident =?', (value, ))  
    conn.commit()
    conn.close()

@app.route('/device_change', methods=['GET', 'POST'])
def device_change():
    if request.method == 'POST':
        form = request.form
        change_data_form_device(form)
    return redirect(url_for('device'))

def change_data_form_device(form):
    device_ident = request.form['device_ident']
    device_ident_old = request.form['device_ident_old']
    device_inv = request.form['device_inv']
    device_type_name = request.form['device_type_name']
    device_text = request.form['device_text']
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    if device_text == '':
        device_text = "Нет информации"
    if device_ident != device_ident_old:
        cursor.execute('DELETE FROM device WHERE device_ident =?', (device_ident_old, ))
        cursor.execute('INSERT INTO device values (?, ?, ?, ?)', (device_ident, device_inv, device_type_name, device_text))
    cursor.execute('REPLACE INTO device values (?, ?, ?, ?)', (device_ident, device_inv, device_type_name, device_text))    
    conn.commit()
    conn.close()

def remove_type(form):
    device_type_name = request.form['device_type_name']
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    if device_type_name == '':
        return redirect(url_for('device'))
    cursor.execute('DELETE FROM device_type WHERE device_type_name=?', (device_type_name, ))
    flash("Тип ", 'type_info')
    conn.commit()
    conn.close()
    return(device_type_name)

def insert_data_type_form_device(form):
    device_type_name = request.form['device_type_name']
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    # Проверка существует ли тип устройства
    device_type_name_test = cursor.execute('SELECT * FROM device_type WHERE device_type_name=?', (device_type_name, ))
    if device_type_name == '':
         return redirect(url_for('device'))
    if device_type_name_test.fetchone() is None: 
        # Запись нового типа устройства, если такого еще не существует
        cursor.execute('INSERT INTO device_type values (?)', (device_type_name, ))
        conn.commit()
        conn.close()
        flash(f"Новый тип ", 'insert_type')
    else:
        flash(f"Тип", 'type_exists')
    return (device_type_name)

def search_device_type():
    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("create table if not exists device_type (device_type_name varchar(300) PRIMARY KEY);")    
    cursor.execute('SELECT * FROM device_type')  
    results = cursor.fetchall()
    conn.close()
    return (results)

def search_device():
    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("create table if not exists device (id integer, device_type_name varchar(300), device_inv varchar(300), device_ident varchar(300) PRIMARY KEY, device_text varchar(300));")    
    cursor.execute('SELECT * FROM device')
    results = cursor.fetchall()
    conn.close()
    return (results)

def insert_data_form_device(form):
    device_type_name = request.form['device_type_name']
    device_inv = request.form['device_inv']
    device_ident = request.form['device_ident']
    device_text = request.form['device_text']
    if device_text == '':
        device_text = "Нет информации"
    if device_inv == '':
        device_inv = "Нет информации"
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    # Проверка существует ли тип устройства
    cursor.execute("create table if not exists device (device_ident varchar(300) PRIMARY KEY, device_inv varchar(300), device_type_name varchar(300), device_text varchar(300));")  
    device_ident_test = cursor.execute('SELECT * FROM device WHERE device_ident=?', (device_ident, ))
    if device_ident_test.fetchone() is None: 
        # Запись нового типа устройства, если такого еще не существует
        # cursor.execute("create table if not exists device (id integer, device_type_name varchar(300), device_inv varchar(300), device_ident varchar(300) PRIMARY KEY, device_text varchar(300));")  
        cursor.execute("INSERT INTO device values (?, ?, ?, ?)", (device_ident, device_inv, device_type_name, device_text))
        conn.commit()
        conn.close()
        flash(f"Устройство с идентификатором")
    else:
        flash(f"Устройство с идентификатором", 'error')
    return (device_ident)



@app.route('/imp_exp')
def imp_exp():
    return render_template('imp_exp.html', side_pos='active')

@app.route('/imp_exp', methods=['POST'])
def imp_exp_file_import():
    uploaded_file = request.files['file']
    
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        parseCSV(file_path)
        flash("Файл загружен")
    else:
        flash("Файл не загружен", 'error')
    return redirect(url_for('imp_exp'))

def parseCSV(filePath):
 
    col_names = ['Name']
    csvData = pd.read_csv(filePath,names=col_names, header=None)
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()
    cursor.execute("create table if not exists users (user_name varchar(300) PRIMARY KEY);")  
    cursor.execute("DELETE FROM users;")
    
    for id,user_name in csvData.iterrows():
        cursor.execute("INSERT INTO users values (?)", (user_name))    
    conn.commit()
    conn.close()

    # удлить фсе файлы в каталоге импорта
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))
    


# @app.route('/service_send_data', methods=['GET', 'POST'])
# def service_send_ajax():
#     if request.method == 'POST':
#         form = request.get_json()
#         #  print(qtc_data
#         # form = request.form
#         print(form)
#         insert_data_form_service(form)
        
  
#     # results = {'processed': 'true'}
#     # return jsonify(results)
#         # service_data = form
#     return render_template('service.html', side_pos='active')




def insert_data_form_service_search(form):
    service_name_search = request.form['service_name_search']
    # print(service_name_search)
    # if service_name == '':
    #     return redirect(url_for('service'))

    # conn = sqlite3.connect(path_db)
    # cursor = conn.cursor()
    # cursor.execute("create table if not exists service (id integer PRIMARY KEY, service_name varchar(300), service_url varchar(300), service_text text, service_owner varchar(300));")  
    # cursor.execute("INSERT INTO service values (null, ?, ?, ?, ?)", (service_name, service_url, service_text, service_owner))
    # conn.commit()
    # conn.close()

    return (service_name_search)



# def insert_data_form_device(form):
#     device_name = request.form['device_type_name']
#     device_inv = request.form['device_inv']
#     device_ident = request.form['device_ident']
#     conn = sqlite3.connect(path_db)
#     cursor = conn.cursor()
#     cursor.execute("create table if not exists device (id integer PRIMARY KEY, device_name varchar(300), device_inv varchar(300), device_ident varchar(300));")
#     cursor.execute("INSERT INTO device values (null, ?, ?, ?)", (device_name, device_inv, device_ident))
#     conn.commit()
#     conn.close()
#     flash(f"Устройство")
#     return (device_name)

## for POST ajax
# def insert_data_form_service(form):
#     service_name = form['service_name']
#     service_url = form['service_url']
#     if service_name == '':
#         print('HAHAH')
#         return()
#     # inv_number = int(request.form['inv_number'])
#     # print(service_name)
#     # print(inv_number)
#     conn = sqlite3.connect(path_db)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO service values (null, ?, ?)", (service_name, service_url))
#     conn.commit()
#     conn.close()
#     flash("This is a flashed message.")
    

# return (formated_QTc, prolonged)


if __name__ == '__main__':
    app.run(debug=True)
