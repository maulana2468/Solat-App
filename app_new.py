from PyQt6 import uic
import sys, os, datetime, ast, requests, collections, time, threading
from bs4 import BeautifulSoup
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QIcon, QColor, QAction
from PyQt6.QtWidgets import (
    QTableWidgetItem, QMainWindow, QFileDialog, QMessageBox,
    QApplication, QSystemTrayIcon, QMenu, QWidget
)
from plyer import notification
from playsound import playsound


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('SolatApp.ui', self)
        self.setWindowIcon(QIcon('data/faviconmosque.ico'))
        self.setWindowTitle("SolatApp")
        self.setFixedSize(940, 680)

        # COMBOBOX
        # GETCITY & CHECK CONNECTION IF FIRST
        self.city = self.get_city()
        self.list_city.addItems(self.city)
        if os.path.exists('data/temp'):
            with open('data/temp', 'r') as f, open('data/data_kota.cfg', 'r') as f2:
                data_kota_temp = f.readline().split(";")[1]
                for data in f2:
                    id, data_kota = data.split(":")
                    if data_kota_temp == data_kota.strip():
                        self.list_city.setCurrentIndex(int(id) - 1)
        else:
            self.list_city.setCurrentIndex(0)

        # PARAMETER & TABLE
        # GETSCHEDULEINFOCITY --> UPDATEINSERTTABLE --> RETURN INFO
        info = self.get_schedule_info_city()
        city_info, route, distance, inf1, inf2, inf3, inf4, inf5, last_up = info
        self.parameter_city.setText(city_info)
        self.route_city.setText(route)
        self.distance_city.setText(distance)

        # LABEL FIQH
        self.penetapan_shubuh.setText(f'Penetapan Waktu Shubuh{inf1}')
        self.penetapan_ashr.setText(f'Penetapan Waktu Ashr{inf2}')
        self.penetapan_isya.setText(f'Penetapan Waktu Isya{inf3}')
        self.penetapan_imsyak.setText(f'Penetapan Waktu Imsyak{inf4}')
        self.jadwal.setText(f'Jadwal sudah diberi{inf5}')
        self.last_update.setText(f'Update terakhir: {last_up}')

        # COMPASS IMAGE
        pixmap = QPixmap('data/compass.png')
        self.compass_image.setPixmap(pixmap)

        # CLOCK
        timer = QTimer(self)
        timer.timeout.connect(self.display_time)
        timer.start(50)

        # BUTTON UPDATE
        self.update_button.clicked.connect(self.check_conn)

        # BUTTON SOUND & PATH
        # GETSOUND
        self.button_sound_path.clicked.connect(self.sound_set)
        self.get_sound()

        self.show()

        # GET_CITY, GET_SCHEDULE_INFO_CITY, GET_SOUND CALL FIRST

    def display_time(self):
        current_time = datetime.datetime.now()
        display = current_time.strftime("%d %B %Y %H:%M:%S")
        self.clock.setText(display)

    def get_city(self):
        # Cek Kota Config
        if os.path.exists('data/data_kota.cfg'):
            if os.stat('data/data_kota.cfg').st_size != 0:
                with open('data/data_kota.cfg', 'r') as f:
                    list_kota = [data.split(":")[1].strip() for data in f]
        else:
            self.check_conn(1, 0)
            schedule = ScheduleApp(1)
            schedule.update_kota()
            with open('data/data_kota.cfg', 'r') as f:
                list_kota = [data.split(":")[1].strip() for data in f]

        return list_kota

    def get_schedule_info_city(self):
        # Cek Jadwal Config
        info = ''
        if os.path.exists('data/data_jadwal.cfg'):
            if os.stat('data/data_jadwal.cfg').st_size != 0:
                info = self.update_insert_table(self.list_city.currentText())
        else:
            # Update + Save
            schedule = ScheduleApp(1)
            schedule.update_tanggal()
            schedule.info_city()
            info = self.update_insert_table(self.list_city.currentText())

        return info

    def get_sound(self):
        if os.path.exists('data/sound_temp'):
            with open('data/sound_temp', 'r') as f:
                data = f.readlines()
                self.sound_path.setText(str(data).strip('][').strip('\''))
        else:
            with open('data/sound_temp', 'w') as f:
                f.write('sound/beep.wav')
                self.sound_path.setText('sound/beep.wav')

    def update_insert_table(self, city_target):
        with open('data/data_jadwal.cfg', 'r') as f:
            # Insert Table
            date_now = datetime.datetime.now().date()
            date_now = str(date_now).split('-')[2]
            target_time = [1, 4, 5, 6, 7]
            row_count = 0
            for row in f:
                self.table.insertRow(row_count)
                data_per_tgl_list = ast.literal_eval(row.strip())
                target_date = data_per_tgl_list[0]
                data_per_tgl_list = data_per_tgl_list[1:]
                for col, data in enumerate(data_per_tgl_list):
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if target_date == date_now:
                        item.setBackground(QColor(153, 255, 153))
                        self.table.setItem(row_count, col, item)
                        target_this_day = [data_per_tgl_list[x] for x in target_time]
                        with open('data/temp', 'w') as z:
                            z.write(f'{target_this_day};{city_target}')
                    elif row_count % 2 == 0:
                        item.setBackground(QColor(230, 230, 250))
                        self.table.setItem(row_count, col, item)
                    else:
                        item.setBackground(QColor(224, 255, 255))
                        self.table.setItem(row_count, col, item)
                row_count = row_count + 1
        # Parameter & Info City
        with open('data/params.cfg', 'r') as f_2:
            info = [line for line in f_2]

        return info

    def update_loc(self):
        target_city = self.list_city.currentText()
        # Cek Equals
        find = False
        with open('data/data_kota.cfg', 'r') as f:
            for data in f:
                target_from_list = data.split(":")[1].strip()
                if target_city == target_from_list:
                    id = data.split(":")[0].strip()
                    find = True
        # Update Data from Web + Save
        Update = ScheduleApp(int(id))
        Update.update_kota()
        Update.update_tanggal()
        Update.info_city()
        # Delete & Update Table
        self.table.setRowCount(0)
        GET = self.update_insert_table(target_city)
        # Update Param & Info
        city_info, route, distance, inf1, inf2, inf3, inf4, inf5, last_up = GET
        self.parameter_city.setText(city_info)
        self.route_city.setText(route)
        self.distance_city.setText(distance)
        self.penetapan_shubuh.setText(f'Penetapan Waktu Shubuh{inf1}')
        self.penetapan_ashr.setText(f'Penetapan Waktu Ashr{inf2}')
        self.penetapan_isya.setText(f'Penetapan Waktu Isya{inf3}')
        self.penetapan_imsyak.setText(f'Penetapan Waktu Imsyak{inf4}')
        self.jadwal.setText(f'Jadwal sudah diberi{inf5}')
        self.last_update.setText(f'Update terakhir: {last_up}')
        # Update Compass Image
        pixmap = QPixmap('data/compass.png')
        self.compass_image.setPixmap(pixmap)

    def sound_set(self):
        sound_file, _ = QFileDialog.getOpenFileName(self, "Pilih Suara",
                                                    r"C:\\Users\\", "Sound files (*.mp3 *.wav)")
        if sound_file:
            with open('data/sound_temp', 'w') as f:
                f.write(sound_file)
            self.sound_path.setText(sound_file)

    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     'Keluar ',
                                     'Keluar dari Aplikasi ?\n\nKlik "No" atau tombol Close untuk minimize',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply is QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            self.setVisible(False)
            event.ignore()

    def check_conn(self, first=None, up_loc=1):
        try:
            URL = "https://jadwalsholat.org/adzan/monthly.php"
            php = requests.get(URL)
            if up_loc == 1:
                self.update_loc()
        except (requests.ConnectionError, requests.Timeout) as e:
            error = QMessageBox.warning(self,
                                        "Kesalahan",
                                        "Tidak ada Koneksi Internet\n\nKoneksikan terlebih dahulu",
                                        QMessageBox.StandardButton.Ok)
            if first == 1:
                sys.exit()


class ScheduleApp:
    def __init__(self, id):
        URL = "https://jadwalsholat.org/adzan/monthly.php"
        URL_CALENDAR = 'https://www.jadwalsholat.org/hijri/hijri.php'

        parameter = {
            'id': id,
        }

        self.php = requests.get(URL, params=parameter, timeout=10).text
        self.bs = BeautifulSoup(self.php, 'lxml')

    def update_kota(self):
        kota_dict = {}
        kota = self.bs.find_all('option')
        for val in kota:
            key = val['value']
            city = val.text
            kota_dict[int(key)] = city

        kota_dict = collections.OrderedDict(sorted(kota_dict.items()))

        with open('data/data_kota.cfg', 'w') as f:
            for k, v in kota_dict.items():
                f.write(f'{k}:{v}\n')

    def update_tanggal(self):
        table_list = self.bs.find('table')
        rows = table_list.find_all('tr', align="center")

        list_tgl = []
        for row in rows:
            data = row.find_all('td')
            data_tgl = [jadwal.text for jadwal in data]
            list_tgl.append(data_tgl)

        del list_tgl[0]
        del list_tgl[-1]

        with open('data/data_jadwal.cfg', 'w') as f:
            for list in list_tgl:
                f.write(f'{str(list)}\n')

    def info_city(self):
        current_time = datetime.datetime.now()
        last_up = current_time.strftime("%d %B %Y %H:%M:%S")
        cityinfo = ''
        nama_kota = self.bs.find_all('tr', class_="table_block_content")
        routelist = []
        infofiqh = []
        for nama in nama_kota:
            city = nama.find_all('td', colspan='7')
            for city_info in city:
                cityinfo = city_info.text
            route = nama.find_all('td', colspan='5')
            for route_info in route:
                routelist.append(route_info.text)
            fiqh = nama.find_all('td', colspan='6')
            for info_fiqh in fiqh:
                infofiqh.append(info_fiqh.text)

        arah, jarak = routelist
        info1, info2, info3, info4, info5 = infofiqh
        info_city_list = [cityinfo, arah, jarak, info1, info2, info3, info4, info5, last_up]

        with open('data/params.cfg', 'w') as f:
            for i_city in info_city_list:
                f.write(f'{i_city}\n')

        get_level = arah.split()[0]
        GET_LEVEL_URL = f"https://jadwalsholat.org/adzan/images/circle.php?s={get_level}"
        get_request_img = requests.get(GET_LEVEL_URL)
        images = open("data/compass.png", 'wb')
        images.write(get_request_img.content)
        images.close()


class Alarm:
    def time_clock():
        pray = {0: "Shubuh", 1: "Dzuhur", 2: "Ashr", 3: "Maghrib", 4: "Isya"}
        while True:
            time.sleep(0.25)
            with open('data/temp', 'r') as time_target, open('data/sound_temp', 'r') as sound_play:
                current_time = datetime.datetime.now()
                time_now = current_time.strftime("%H:%M")
                #print(time_now)
                time_target, city_target = time_target.readline().split(";")
                time_list_target = ast.literal_eval(time_target.strip())
                if time_now in time_list_target:
                    index = time_list_target.index(time_now)
                    for key, target_pray in pray.items():
                        if index == key: pray_time = target_pray
                    notification.notify(title=f'Waktu Salat {pray_time} Tiba',
                                        message=f'Untuk Wilayah {city_target} dan Sekitarnya',
                                        app_name="SolatApp",
                                        app_icon="data/faviconmosque.ico",
                                        timeout=60,
                                        ticker="SolatApp",
                                        toast=False)
                    sound_start = sound_play.readlines()
                    playsound(str(sound_start).strip('][').strip('\''), block=True)


def main_app():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Ui()

    # SYSTEM TRAY
    def open_app():
        window.setVisible(True)

    def close_event():
        window.close()

    icon = QSystemTrayIcon(QIcon('data/faviconmosque.ico'))
    icon.show()
    menu_tray = QMenu()

    open_action = QAction("Buka Aplikasi")
    open_action.triggered.connect(open_app)
    menu_tray.addAction(open_action)

    exit_action = QAction("Keluar")
    exit_action.triggered.connect(close_event)
    menu_tray.addAction(exit_action)

    icon.setContextMenu(menu_tray)

    # ALARM THREAD
    alarm = threading.Thread(target=Alarm.time_clock)
    alarm.daemon = True
    alarm.start()

    app.exec()


if __name__ == '__main__':
    main_app()
