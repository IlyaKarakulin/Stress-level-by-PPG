import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel, QSlider, QLineEdit, QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QTableWidget, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt
from bleak import BleakScanner, BleakClient
import asyncio
import qasync
import functools
import sqlite3
import pandas as pd
import os
import requests
import json
import datetime
import matplotlib.pyplot as plt 
import matplotlib.backends.backend_qt5agg as figure_canvas
import matplotlib.path as mpath
import matplotlib.patches as patches
import matplotlib.colors as colors
import matplotlib.dates as mdates
import matplotlib as mpl
import numpy as np
from PyQt5.QtCore import QTimer
from scipy import signal

MY_UUID = "DEC01455-CEB1-CEC0-DEC0-FF0123456789"
WRITE_UUID = "DEC01444-CEB1-CEC0-DEC0-FF0123456789"
READ_UUID = "DEC01433-CEB1-CEC0-DEC0-FF0123456789"
mChildName = "None"
MAX_DATA_SIZE = 3500
MAX_DATA_SIZE_PLOT = 3500
SIZE_FILTER = 10
FREQUENCY = 250

array_plot = np.array([])
array_plot_axel = np.array([])

hex_values = [format(i, '02X') for i in range(36)]
# print(hex_values)

def plot(_start=0, _end=-1, _type="afe_LED1ABSVAL"):
    file_path = "dataframe/" + mChildName + ".csv"

    save_to_csv()

    df = pd.read_csv(file_path, delimiter=",")
    data = df[_type]
    plt.figure(figsize=(24, 6))
    print(_start, _end)
    plt.plot(data[_start:_end])
    plt.grid(axis='y')

    plot_path = "img/" + _type + "_" + mChildName
    i = 1
    while True:
        if not os.path.exists(plot_path + str(i) + ".png"):
            plt.savefig(plot_path + str(i) + ".png")
            break
        else:
            i += 1

def save_to_csv():
    features = 'device_name, comment, package_number, time, eda, accel_X, accel_Y, accel_Z, afe_LED1ABSVAL, battery, temperature, package_num'
    columns = ['device_name', 'comment', 'package_number', 'time', 'eda', 'accel_X', 'accel_Y', 'accel_Z', 'afe_LED1ABSVAL', 'battery', 'temperature', 'package_num']
    path_to_db = 'test_2.db'
    path_to_save = 'dataframe/'
    with sqlite3.connect(path_to_db) as conn:
        cur = conn.cursor()
        name = mChildName
        print(name)
        file_path = path_to_save + f'{name}.csv'
        if not os.path.exists(file_path):
            cur.execute(f'SELECT {features} FROM device_measurements WHERE device_name == "{name}"')
            res = cur.fetchall()
            df = pd.DataFrame(res, columns=columns)
            df.to_csv(file_path, index=False)
            print(f"File '{name}.csv' saved successfully.")
        else:
            print(f"File '{name}.csv' already exists. Skipped saving.")

def send_data(data):
    url = "http://157.230.95.209:30002"
    payload = {'List': data}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print('Данные успешно отправлены!')
    else:
        print('Ошибка отправки данных:', response.text)

def init_db():
    conn = sqlite3.connect('test_2.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_measurements 
                    (device_name text, comment text, package_number text, time text,
                    device_id text, eda text, accel_X text, accel_Y text, accel_Z text,
                    afe_LED1ABSVAL text, battery text, temperature text, package_num text);''')
    return conn

def store_data_in_db(conn, data):
    try:
        with conn:
            cursor = conn.cursor()
            for elem in data:
                name = elem['name']
                comment = elem['comment']
                package_number = elem['package_number']
                time = elem['time']
                device_name = elem['id']
                state = json.loads(elem['state'])
                eda = state[0]
                accel_X = state[1]
                accel_Y = state[2]
                accel_Z = state[3]
                afe_LED1ABSVAL = state[4]
                battery = state[5]
                temperature = state[6]
                package_num = state[7]

                params = (name, comment, package_number, time, device_name, eda, accel_X, accel_Y, accel_Z, afe_LED1ABSVAL, battery, temperature, package_num)
                cursor.execute("INSERT INTO device_measurements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)

    except Exception as e:
        print(f"An error occurred: {e}")

def check(data):
    current = data[0]
    list_error = []
    k = 7
    while k < len(data):
        current += 1
        if current == 256:
            current = 0
        while data[k] != current:
            list_error.append(current)
            current += 1
            if current == 256:
                current = 0
        k += 7
    return list_error

class Device:
    def __init__(self, bleak_app, loop=None, address=None):
        self.client = BleakClient(address, loop=loop)
        self.list_count = []
        self.dictionary = {}
        self.data_send = []
        self.address = address
        self.connected = False
        self.collecting = False
        self.bleak_app = bleak_app

    async def start_data_collection(self):
        
        self.bleak_app.update_device_status(self.address, "Connecting...")
        def callback(sender: int, data: bytearray):
            global array_plot
            global array_plot_axel
            size_package = 15
            data_list = [data[i:i + size_package] for i in range(0, len(data), size_package)]
            for _data in data_list:
                eda = int.from_bytes(_data[:2], byteorder='little')
                accel_X = int.from_bytes(_data[2:4], byteorder='little')
                accel_Y = int.from_bytes(_data[4:6], byteorder='little')
                accel_Z = int.from_bytes(_data[6:8], byteorder='little')
                afe_LED1ABSVAL = int.from_bytes(_data[8:11], byteorder='little')
                battery = int.from_bytes(_data[11:13], byteorder='little')
                temperature = int.from_bytes(_data[13:14], byteorder='little')
                package_num = int.from_bytes(_data[14:15], byteorder='little')

                info = [eda, accel_X, accel_Y, accel_Z, afe_LED1ABSVAL, battery, self.bleak_app.current_value_r22, package_num]
                self.list_count.append(package_num)
                if len(self.list_count) == 700:
                    res = check(self.list_count)
                    completion_percentage = ((len(self.list_count)/5)*100)/(len(res)+len(self.list_count)/5)

                    # print("Процент: ", completion_percentage)
                    self.bleak_app.update_completion_percentage(self.address, int(completion_percentage))
                    self.list_count = []

                self.dictionary['name'] = mChildName
                deviceName = self.address
                self.dictionary['id'] = deviceName
                self.dictionary['comment'] = 'device'
                self.dictionary['package_number'] = str(temperature)
                self.dictionary['state'] = str(info)
                self.dictionary['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                
                if len(array_plot) >= MAX_DATA_SIZE_PLOT + SIZE_FILTER:
                    array_plot = np.append(array_plot, afe_LED1ABSVAL)
                    # Удаление первого элемента
                    n = len(array_plot) - MAX_DATA_SIZE_PLOT + SIZE_FILTER
                    array_plot = array_plot[n:]
                else:
                    array_plot = np.append(array_plot, afe_LED1ABSVAL)

                self.data_send.append(self.dictionary.copy())

                self.dictionary.clear()

                if len(self.data_send) == MAX_DATA_SIZE:
                    print('CHILD', mChildName)
                    store_data_in_db(conn, self.data_send)
                    self.data_send.clear()

        print(f"Connecting to {self.address}")
        await self.client.connect()
        self.connected = self.client.is_connected
        self.bleak_app.update_device_status(self.address, "Connected" if self.connected else "Disconnected")
        print(f"Connected: {self.client.is_connected}")

        while self.connected and self.collecting:
            self.bleak_app.update_device_status(self.address, "Collecting data...")
            await self.client.start_notify(MY_UUID, callback)
            await asyncio.sleep(5.0)
            await self.client.stop_notify(MY_UUID)

        await self.client.disconnect()
        self.bleak_app.update_device_status(self.address, "Disconnected")
        self.connected = False

    async def write_gatt_value(self, value):
        # await self.client.connect()
        global array_plot
        try:
            if not self.client.is_connected:
                await self.client.connect()
                await self.client.write_gatt_char(WRITE_UUID, value, response=False)
                await self.client.disconnect()
            else:
                await self.client.write_gatt_char(WRITE_UUID, value, response=False)
            print("Успешно записано")
            #array_plot = np.array([])
        except Exception as e:
            print(f"An error occurred: {e}")
        # await self.client.disconnect()

    # async def read_gatt_value(self):
    #     # Assuming the response arrives as a variable named `response_value`
    #     await self.client.connect()
        
    #     header = bytes.fromhex('A5A5')                  # A5A5 - заголовок
    #     register_address = bytes.fromhex('08') 

    #     value_to_write = header + register_address

    #     # await self.client.write_gatt_char(READ_UUID, value_to_write, response=True)

    #     # print(response_value)
    #     response_value = await self.client.read_gatt_char(READ_UUID)

    #     parsed_response = response_value.hex()
    #     # parsed_value = bytes.fromhex(parsed_response)

    #     # response_value = await self.client.write_gatt_char(READ_UUID)  # Read the response value
    #     # Parse the response value into its components
    #     # Combine the bytes objects into the complete response_value
    #     # parsed_response = response_value.hex()
    #     print(parsed_response)
    #     print("Response успешно")
    #     await self.client.disconnect()
    #     # return header, register_address, register_value

    

class BleakApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.devices = {}
        self.initUI()
        self.plot_window = None
        self.current_value_r22 = 0

    def initUI(self):
        self.setGeometry(100, 100, 2500, 1600)
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        vbox = QVBoxLayout()

        self.label_child_name = QLabel("Enter mChildName:", self)
        vbox.addWidget(self.label_child_name)

        self.input_child_name = QLineEdit(self)
        vbox.addWidget(self.input_child_name)

        self.name_button = QPushButton("Save", self)
        self.name_button.clicked.connect(self.change_name)
        vbox.addWidget(self.name_button)

        self.connect_button = QPushButton("Scan", self)
        self.connect_button.clicked.connect(self.scan_devices)
        vbox.addWidget(self.connect_button)

        self.devices_table = QTableWidget(0, 4, self)
        self.devices_table.setHorizontalHeaderLabels(["Device", "Status", "Collect Data", "Completion %"])
        vbox.addWidget(self.devices_table)

        self.devices_table.setColumnWidth(0, 700)
        self.devices_table.setColumnWidth(1, 400)
        self.devices_table.setColumnWidth(2, 600)
        self.devices_table.setColumnWidth(3, 300)

        self.plot_button = QPushButton("Plot", self)
        self.plot_button.clicked.connect(self.show_plot_window)
        vbox.addWidget(self.plot_button)

        # Добавление элементов для ввода названия и значения регистра
        hbox_register = QHBoxLayout()
        self.combo_device_register = QComboBox(self)
        # print(self.devices)
        # self.combo_device_register.addItems(self.devices.keys()) 
        # self.combo_register_name.setFixedSize(200, 60) 
        self.combo_device_register.setFixedWidth(500) 
        hbox_register.addWidget(self.combo_device_register)

        # hbox_register = QHBoxLayout()
        self.combo_register_name = QComboBox(self)
        self.combo_register_name.addItems(hex_values) 
        # self.combo_register_name.setFixedSize(200, 60) 
        hbox_register.addWidget(self.combo_register_name)

        self.input_register_value = QLineEdit(self)
        self.input_register_value.setPlaceholderText("00000f9d")
        # self.input_register_value.setFixedSize(200, 60)
        hbox_register.addWidget(self.input_register_value)
        
        self.write_button = QPushButton("Write", self)
        self.write_button.clicked.connect(self.write_to_register)
        hbox_register.addWidget(self.write_button)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 255)  # установите минимальное и максимальное значения
        self.slider.setSingleStep(1)  # установите размер шага
        self.slider.setTickPosition(QSlider.TicksBelow)  # показать метки под слайдером
        self.slider.setTickInterval(4)  # задать длину между метками

        self.slider.valueChanged.connect(self.write_to_register_slider)  # подключите функцию к слайдеру
        hbox_register.addWidget(self.slider) 

        vbox.addLayout(hbox_register)

        # self.input_read_value = QLineEdit(self)
        # self.input_read_value.setPlaceholderText("Read Value")  # Установить текст-подсказку для поля чтения
        # # self.input_read_value.setText(current_value)  # Установить значение из переменной current_value
        # self.input_read_value.setReadOnly(True)  # Сделать поле только для чтения
        # hbox_register.addWidget(self.input_read_value)

        # self.read_button = QPushButton("Read", self)
        # self.read_button.clicked.connect(self.read_register)
        # hbox_register.addWidget(self.read_button)

        # vbox.addStretch(1)
        self.centralwidget.setLayout(vbox)

    def write_to_register_slider(self):
        selected_device_address = self.combo_device_register.currentText()

        a = self.slider.value()
        # self.current_value_r22 = hex(a)[2:].zfill(2)
        print(a)
        self.current_value_r22 = a

        
        register_value = hex(a)[2:].zfill(2)
        register_value = bytes.fromhex(register_value)
        print(register_value)
        header = bytes.fromhex('A5A5220000') 
        value_to_write = header + register_value + register_value
        print(value_to_write)    

        if selected_device_address in self.devices:
            device = self.devices[selected_device_address]['device']
            asyncio.ensure_future(device.write_gatt_value(value_to_write))
        else:
            print(f"Device {selected_device_address} not found in the list of devices.")

    def write_to_register_plus(self):
        selected_device_address = self.combo_device_register.currentText()


        a = int(self.current_value_r22, 16) + 1
        self.current_value_r22 = hex(a)[2:].zfill(2)
        print(self.current_value_r22)

        
        register_value = bytes.fromhex(self.current_value_r22)
        header = bytes.fromhex('A5A5220000') 
        value_to_write = header + register_value + register_value
        print(value_to_write)    

        if selected_device_address in self.devices:
            device = self.devices[selected_device_address]['device']
            asyncio.ensure_future(device.write_gatt_value(value_to_write))
        else:
            print(f"Device {selected_device_address} not found in the list of devices.")
    
    def write_to_register_minus(self):
        selected_device_address = self.combo_device_register.currentText()

        a = int(self.current_value_r22, 16) - 1
        self.current_value_r22 = hex(a)[2:].zfill(2)
        print(self.current_value_r22)

        register_value = bytes.fromhex(self.current_value_r22) 
        header = bytes.fromhex('A5A5220000') 
        value_to_write = header + register_value + register_value
        print(value_to_write)    
        if selected_device_address in self.devices:
            device = self.devices[selected_device_address]['device']
            asyncio.ensure_future(device.write_gatt_value(value_to_write))
        else:
            print(f"Device {selected_device_address} not found in the list of devices.")


    def write_to_register(self):
        # device = self.devices[self.devices_table.item(self.devices_table.currentRow(), 0).text()]['device']
        selected_device_address = self.combo_device_register.currentText()

        header = bytes.fromhex('A5A5')                  # A5A5 - заголовок
        selected_item_text = self.combo_register_name.currentText()
        register_address = bytes.fromhex(selected_item_text)           # 08 - адрес регистра

        input_register_value = self.input_register_value.text()
        register_value = bytes.fromhex(input_register_value)       # 00000f9d - значение регистра
        value_to_write = header + register_address + bytes.fromhex("00") + register_value
        # print(value_to_write)
        if selected_device_address in self.devices:
            device = self.devices[selected_device_address]['device']
            asyncio.ensure_future(device.write_gatt_value(value_to_write))
        else:
            print(f"Device {selected_device_address} not found in the list of devices.")
        
        

        # print(register_name, register_value)

    # def read_register(self):
    #     selected_device_address = self.combo_device_register.currentText()
    #     if selected_device_address in self.devices:
    #         device = self.devices[selected_device_address]['device']
    #         asyncio.ensure_future(device.read_gatt_value())
    #     else:
    #         print(f"Device {selected_device_address} not found in the list of devices.")

    def update_device_combo_box(self):
        self.combo_device_register.clear()  # Очищаем текущий список устройств
        devices_list = [device for device in self.devices.keys()]  # Получаем список адресов устройств
        self.combo_device_register.addItems(devices_list)
        # self.combo_device_register.adjustSize()

    def update_device_status(self, address, status):
        row_index = [self.devices[device].get('row') for device in self.devices if device == address][0]
        self.devices_table.item(row_index, 1).setText(status)

    def change_name(self):
        global mChildName
        mChildName = self.input_child_name.text()

    def update_completion_percentage(self, address, percentage):
        row_index = [self.devices[device].get('row') for device in self.devices if device == address][0]
        item = QTableWidgetItem(str(percentage) + "%")
        self.devices_table.setItem(row_index, 3, item)

    def handle_device_button(self, device_address):
        device = self.devices[device_address]['device']
        if device.connected:
            device.collecting = False
            self.update_device_status(device_address, "Stopping data collection...")
            self.devices[device_address]['button'].setText('Start Data Collection')
        else:
            device.collecting = True
            self.devices[device_address]['button'].setText('Stop Data Collection')
            asyncio.ensure_future(device.start_data_collection())

    def scan_devices(self):
        global mChildName
        self.devices = {}
        self.devices_table.setRowCount(0)
        mChildName = self.input_child_name.text()
        asyncio.ensure_future(self.scan())

    async def scan(self):
        scanner = BleakScanner()
        devices = await scanner.discover()
        for device in devices:
            if 'abrace' in str(device).lower() or 'swaid' in str(device).lower():
                dev = Device(self, loop=asyncio.get_event_loop(), address=device.address)
                button = QPushButton('Start Data Collection')
                button.clicked.connect(functools.partial(self.handle_device_button, device.address))

                row = self.devices_table.rowCount()
                self.devices_table.insertRow(row)
                self.devices_table.setItem(row, 0, QTableWidgetItem(str(device)))
                self.devices_table.setItem(row, 1, QTableWidgetItem("Disconnected"))
                self.devices_table.setCellWidget(row, 2, button)

                self.devices[device.address] = {'device': dev, 'button': button, 'row': row}
                self.update_device_combo_box()

    def show_plot_window(self):
        self.plot_window = PlotWindow(self.input_child_name.text())
        self.plot_window.show()

class PlotWindow(QWidget):
    def __init__(self, mChildName):
        super().__init__()
        self.mChildName = mChildName
        self.last_plot_idx = 0
        self.resize(2500, 1600)
        self.fig = plt.figure(figsize=(12, 6), dpi=100)
        self.canvas = figure_canvas.FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(3,1,1)
        self.ax2 = self.fig.add_subplot(3,1,2)
        self.ax3 = self.fig.add_subplot(3,1,3)

        self.low = 0.5
        self.high = 3


        layout = QtWidgets.QVBoxLayout(self)

        hbox_lowhigh = QHBoxLayout()
        hbox_lowhigh.heightForWidth

        self.label_input_low = QLabel("От", self)
        hbox_lowhigh.addWidget(self.label_input_low)

        self.input_low = QLineEdit(self)
        self.input_low.setText(str(self.low))
        self.input_low.setFixedWidth(150)
        hbox_lowhigh.addWidget(self.input_low)

        self.label_input_high = QLabel("До:", self)
        hbox_lowhigh.addWidget(self.label_input_high)

        self.input_high = QLineEdit(self)
        self.input_high.setText(str(self.high))
        self.input_high.setFixedWidth(150)
        hbox_lowhigh.addWidget(self.input_high)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_parameters)
        hbox_lowhigh.addWidget(self.save_button)

        self.label_input_size_filter = QLabel("SIZE_FILTER:", self)
        hbox_lowhigh.addWidget(self.label_input_size_filter)

        self.input_size_filter = QLineEdit(self)
        self.input_size_filter.setText(str(SIZE_FILTER))
        self.input_size_filter.setFixedWidth(150)
        hbox_lowhigh.addWidget(self.input_size_filter)

        self.save_button_filter = QPushButton("Save", self)
        self.save_button_filter.clicked.connect(self.save_size_plot)
        hbox_lowhigh.addWidget(self.save_button_filter)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(500, 10000)  # установите минимальное и максимальное значения
        self.slider.setSingleStep(100)  # установите размер шага
        self.slider.setTickPosition(QSlider.TicksBelow)  # показать метки под слайдером
        self.slider.setTickInterval(100)  # задать длину между метками
        self.slider.setValue(MAX_DATA_SIZE_PLOT)
        self.slider.valueChanged.connect(self.change_size_plot)  # подключите функцию к слайдеру


        self.slider_value = QLabel(str(self.slider.value()), self)
        hbox_lowhigh.addWidget(self.slider_value)

        hbox_lowhigh.addWidget(self.slider) 



        # hbox_lowhigh.addStretch()

        layout.addLayout(hbox_lowhigh)

        layout.addWidget(self.canvas)


        self.init_plot()
        self.show()

        # Setup a QTimer to periodically update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(300) 

    def save_parameters(self):
        self.low = float(self.input_low.text())
        self.high = float(self.input_high.text())
        if self.high > FREQUENCY//2:
            self.high = FREQUENCY//2 - 1
            self.input_high.setText(str(self.high))


    def save_size_plot(self):
        global SIZE_FILTER
        SIZE_FILTER = int(self.input_size_filter.text())
    
    def change_size_plot(self):
        global MAX_DATA_SIZE_PLOT
        MAX_DATA_SIZE_PLOT = self.slider.value()
        self.slider_value.setText(str(self.slider.value()))

    def hampel(self, data, window_size=250, n_sigmas=3): #обнаружение выбросов
        k = 1 
        MAD = lambda x: np.median(np.abs(x - np.median(x)))
        output = np.copy(np.asarray(data))
        onesided_filt = window_size // 2
        for i in range(onesided_filt, len(data) - onesided_filt - 1):
            dataslice = output[i - onesided_filt : i + onesided_filt]
            mad = MAD(dataslice)
            median = np.median(dataslice)
            if output[i] > median + (n_sigmas * mad):
                output[i] = median
        return output

    def filter(self, array, window_size = 100):
        smoothed_arr = []
        for i in range(len(array)):
            start = max(0, i - window_size // 2)
            end = min(len(array), i + window_size // 2 + 1)
            window = array[start:end]
            smoothed_arr.append(sum(window) / len(window))
        return np.array(smoothed_arr)
    
    def butter_bandpass(self, ys, f, low, high, N = 4):
        nyq = f/2
        b, a  = signal.butter(N, [low/nyq, high/nyq], btype="bandpass")
        res = signal.lfilter(b, a, ys)
        return res[SIZE_FILTER:]

    def init_plot(self):
        self.x = []
        self.y = []

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(range(len(array_plot)- SIZE_FILTER), array_plot[SIZE_FILTER:])
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("afe_LED1ABSVAL")
        self.ax.get_yaxis().set_visible(True)
        self.ax.grid(True)

        
        res = self.butter_bandpass(array_plot, 250, self.low, self.high)
        self.ax2.clear()
        self.ax2.plot(range(len(res)), res)
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("afe_LED1ABSVAL")
        self.ax2.get_yaxis().set_visible(True)
        self.ax2.grid(True)

        res_hampel = self.hampel(res)
        res_hampel = res - res_hampel
        # res = self.butter_bandpass(array_plot, 250, self.low, self.high)
        self.ax3.clear()
        self.ax3.plot(range(len(res_hampel)), res_hampel)
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("afe_LED1ABSVAL")
        self.ax3.get_yaxis().set_visible(True)
        self.ax3.grid(True)        

        self.canvas.draw()
        self.last_plot_idx += 1
        self.show()


    # def showEvent(self, event):
    #     self.update_plot()
    
    def closeEvent(self, event):
        self.timer.stop() 

if __name__ == "__main__":
    conn = init_db()
    app = QApplication(sys.argv)
    devices = []
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        ex = BleakApp()
        ex.show()
        loop.run_forever()
        
    conn.close()
    save_to_csv()
    sys.exit()