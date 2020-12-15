import sqlite3
import xml.etree.ElementTree as ET
import json
import socket


class MySQLite:
    def __init__(self):
        self.table_connect = sqlite3.connect('co2_emissions.db')
        self.json_response = ''
        self.xml_file = 'UNData.xml'
        self.tuple_list = []
        self.co2_dict = {}

    def read_xml_file(self):
        index = 0
        root = ET.parse(self.xml_file).getroot()
        datas = root.findall('data')
        for data in datas:
            records = data.findall('record')
            for record in records:
                year = record.find('Year').text
                country = record.find('Country').text
                val = record.find('Value').text
                data_tuple = (int(year), str(country), float(val))
                self.co2_dict[index] = data_tuple
                index += 1

    def build_sql_table(self):
        emissions_table_create_query = '''CREATE TABLE IF NOT EXISTS Database (id INTEGER PRIMARY KEY, year INTEGER, 
        country STRING, value REAL); '''
        self.table_connect.execute(emissions_table_create_query)

    def insert_data_sql_table(self):
        insert_data_query = '''INSERT OR IGNORE INTO Database (id, year, country, value) VALUES (?,?,?,?) '''
        for k, v in self.co2_dict.items():
            data_tuple = (int(k), int(v[0]), v[1], float(v[2]))
            self.table_connect.execute(insert_data_query, data_tuple)
        self.table_connect.commit()

    def send_country_and_year_list(self):
        data_query = "SELECT country FROM Database"
        cursor = self.table_connect.execute(data_query)
        myresult = cursor.fetchall()
        countries = []
        for x in myresult:
            countries.append(x[0])
        countries = list(set(countries))
        countries.sort()
        json_data = json.dumps({"countries": countries})
        return json_data

    def send_country_data(self, country):
        data_query = "SELECT year,value FROM Database WHERE country=?"
        cursor = self.table_connect.execute(data_query, (country,))
        myresult = cursor.fetchall()
        temp_dict = {}
        for x in myresult:
            temp_dict[x[0]] = x[1]
        json_obj = json.dumps(temp_dict)
        return json_obj


class ServerSocket:
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 9999
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)

mysql = MySQLite()
mysql.read_xml_file()
mysql.build_sql_table()
mysql.insert_data_sql_table()

se = ServerSocket()
while True:
    conn, address = se.server_socket.accept()
    while True:
        request = conn.recv(1024).decode()
        print(request)
        if request == "initialize":
            data = mysql.send_country_and_year_list()
            conn.sendall(data.encode("utf-8"))
        else:
            msg = mysql.send_country_data(request)
            conn.sendall(msg.encode("utf-8"))
    conn.close()


