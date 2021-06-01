import os, ast, requests, datetime, time, threading, webbrowser, sys, collections
from bs4 import BeautifulSoup
from tkinter import ttk, font as tkFont, messagebox, filedialog
from tkinter import *
from infi.systray import SysTrayIcon
from plyer import notification
from playsound import playsound


class App:
    def __init__(self, js_app):
        self.js_app = js_app
        self.js_app.title("SolatApp")
        self.js_app.geometry("940x680")
        self.js_app.resizable(False, False)

        # WINDOW & TRAY MANAGER
        def open_window(systray):
            self.js_app.after(0, self.js_app.deiconify)

        menu = (("Buka Aplikasi", None, open_window),)
        systray = SysTrayIcon("data/faviconmosque.ico", "SolatApp", menu_options=menu)
        systray.start()

        def minimize():
            pil = messagebox.askyesnocancel(title="Keluar",
                                            message="Aplikasi Keluar?\n\nPilih \"No\" untuk minimize tray")
            if pil:
                systray.shutdown()
                sys.exit()
            elif not pil:
                self.js_app.withdraw()

        self.js_app.protocol("WM_DELETE_WINDOW", minimize)

        # TITLE APP
        font_style = tkFont.Font(family="Calibri", size=21)
        title_app = Label(self.js_app, text="SolatApp", font=font_style)
        title_app.place(x=510, y=35)

        # TITLE MONTH
        font_style2 = tkFont.Font(family="Calibri", size=13)
        title_month = Label(self.js_app, text="********", font=font_style2)
        title_month.place(x=825, y=46)

        # TABLE
        style = ttk.Style()
        style.map('Treeview', background=[('selected', 'green')])
        self.table = ttk.Treeview(self.js_app, height=31)
        self.table["columns"] = ('Tanggal', 'Imsyak', 'Shubuh', 'Terbit',
                                 'Dhuha', 'Dzuhur', 'Ashr', 'Maghrib', 'Isya')
        self.table.tag_configure('even_row', background='lavender')
        self.table.tag_configure('odd_row', background='lightcyan')
        self.table.tag_configure('target_row', background='lightgreen')

        self.table.column("#0", width=0, stretch=NO)
        self.table.column("Tanggal", anchor=CENTER, width=50)
        self.table.column("Imsyak", anchor=CENTER, width=50)
        self.table.column("Shubuh", anchor=CENTER, width=50)
        self.table.column("Terbit", anchor=CENTER, width=50)
        self.table.column("Dhuha", anchor=CENTER, width=50)
        self.table.column("Dzuhur", anchor=CENTER, width=50)
        self.table.column("Ashr", anchor=CENTER, width=40)
        self.table.column("Maghrib", anchor=CENTER, width=55)
        self.table.column('Isya', anchor=CENTER, width=45)

        self.table.heading("#0", text="")
        self.table.heading("Tanggal", text="Tanggal", anchor=CENTER)
        self.table.heading("Imsyak", text="Imsyak", anchor=CENTER)
        self.table.heading("Shubuh", text="Shubuh", anchor=CENTER)
        self.table.heading("Terbit", text="Terbit", anchor=CENTER)
        self.table.heading("Dhuha", text="Dhuha", anchor=CENTER)
        self.table.heading("Dzuhur", text="Dzuhur", anchor=CENTER)
        self.table.heading("Ashr", text="Ashr", anchor=CENTER)
        self.table.heading("Maghrib", text="Maghrib", anchor=CENTER)
        self.table.heading("Isya", text="Isya", anchor=CENTER)

        self.table.place(x=30, y=15)

        # LABEL KOTA
        font_label_kota = tkFont.Font(family="Calibri", size=12, weight='bold')
        label_kota = Label(self.js_app, text="Kota", font=font_label_kota)
        label_kota.place(x=510, y=87)

        # COMBOBOX
        self.city = self.get_city()
        self.list_city = ttk.Combobox(self.js_app, state='readonly',
                                      values=self.city, width=35)
        if os.path.exists('data/temp'):
            with open('data/temp', 'r') as f, open('data/data_kota.cfg', 'r') as f2:
                data_kota_temp = f.readline().split(";")[1]
                for data in f2:
                    id, data_kota = data.split(":")
                    if data_kota_temp == data_kota.strip():
                        self.list_city.current(int(id) - 1)
                        break
        else:
            self.list_city.current(0)
        self.list_city.place(x=660, y=90)

        # LABEL SOUND
        font_label_sound = tkFont.Font(family="Calibri", size=12, weight='bold')
        label_sound = Label(self.js_app, text="Suara Notifikasi", font=font_label_sound)
        label_sound.place(x=510, y=127)

        # SOUND PATH
        self.sound_path = Entry(self.js_app, width=27)
        self.sound_path.place(x=660, y=130)
        self.get_sound()

        # BUTTON SOUND PATH
        button_sound_path = Button(self.js_app, text="Pilih File", command=lambda: App.sound_set(self))
        button_sound_path.place(x=839, y=127)

        # PARAMETER & TABLE
        info = self.get_schedule_info_city()
        city_info, route, distance, inf1, inf2, inf3, inf4, inf5 = info
        self.city_info_str = StringVar()
        self.city_info_str.set(city_info)
        parameter_city = Label(self.js_app, textvariable=self.city_info_str)

        self.route_str = StringVar()
        self.route_str.set(route)
        route_city = Label(self.js_app, textvariable=self.route_str)

        self.distance_str = StringVar()
        self.distance_str.set(distance)
        distance_city = Label(self.js_app, textvariable=self.distance_str)

        parameter_city.place(x=510, y=200)
        route_city.place(x=510, y=220)
        distance_city.place(x=510, y=240)

        # COMPASS IMAGE
        img_file = PhotoImage(file='data/compass.png')
        self.compass_image = Label(self.js_app, image=img_file)
        self.compass_image.place(x=830, y=205)
        self.compass_image.photo = img_file

        # LABEL FIQH
        penetapan_subuh = Label(self.js_app, text=f'Penetapan Waktu Shubuh {inf1}')
        penetapan_ashr = Label(self.js_app, text=f'Penetapan Waktu Ashr {inf2}')
        penetapan_isya = Label(self.js_app, text=f'Penetapan Waktu Isya {inf3}')
        penetapan_imsyak = Label(self.js_app, text=f'Penetapan Waktu Imsyak {inf4}')
        jadwal = Label(self.js_app, text=f'Jadwal sudah diberi {inf5}')
        penetapan_subuh.place(x=510, y=320)
        penetapan_ashr.place(x=510, y=340)
        penetapan_isya.place(x=510, y=360)
        penetapan_imsyak.place(x=510, y=380)
        jadwal.place(x=510, y=400)

        # BUTTON UPDATE
        update = Button(self.js_app, text="Update", width=12, command=lambda: App.update_loc(self))
        update.place(x=800, y=165)
        self.js_app.bind("<Return>", lambda: App.update_loc(self))

        # LABEL CLOCK
        clock = Label(self.js_app, font=('calibri', 12, 'bold'))
        clock.place(x=510, y=167)

        def time_label():
            current_time = datetime.datetime.now()
            time_now = current_time.strftime("%d %B %Y %H:%M:%S")
            clock.config(text=time_now)
            clock.after(50, time_label)

        time_label()

        # LABEL BOTTOM
        info_label = Label(self.js_app, text="INFO: Update secara berkala tiap bulan!",
                           font=('calibri', 11))
        info_label.place(x=510, y=270)
        bottom_label2 = Label(self.js_app, text="Data diambil dari")
        bottom_label2.place(x=510, y=600)

        def callback(url):
            webbrowser.open_new(url)

        link2 = Label(self.js_app, text="jadwalsholat.org", fg="blue", cursor="hand2")
        link2.place(x=610, y=600)
        link2.bind("<Button-1>", lambda e: callback("http://www.jadwalsholat.org"))

        # get_city, get_schedule, get_sound once update

    def get_city(self):
        # Cek Kota Config
        if os.path.exists('data/data_kota.cfg'):
            if os.stat('data/data_kota.cfg').st_size != 0:
                with open('data/data_kota.cfg', 'r') as f:
                    list_kota = [data.split(":")[1].strip() for data in f]
        else:
            Schedule = Schedule_App(1)
            Schedule.update_kota()
            with open('data/data_kota.cfg', 'r') as f:
                list_kota = [data.split(":")[1].strip() for data in f]

        return list_kota

    def get_schedule_info_city(self):
        # Cek Jadwal Config
        if os.path.exists('data/data_jadwal.cfg'):
            if os.stat('data/data_jadwal.cfg').st_size != 0:
                info = self.update_insert_table(self.list_city.get())
        else:
            Schedule = Schedule_App(1)
            Schedule.update_tanggal()
            Schedule.info_city()
            info = self.update_insert_table(self.list_city.get())

        return info

    def get_sound(self):
        if os.path.exists('data/sound_temp'):
            with open('data/sound_temp', 'r') as f:
                data = f.readlines()
                self.sound_path.insert(0, str(data).strip('][').strip('\''))
        else:
            with open('data/sound_temp', 'w') as f:
                f.write('sound/beep.wav')
                self.sound_path.insert(0, 'sound/beep.wav')

    def update_insert_table(self, city_target):
        with open('data/data_jadwal.cfg', 'r') as f:
            count_tag = 0
            # Insert Table
            date_now = datetime.datetime.now().date()
            date_now = str(date_now).split('-')[2]
            target_time = [2, 5, 6, 7, 8]
            for line in f:
                data_per_tgl_list = ast.literal_eval(line.strip())
                if data_per_tgl_list[0] == date_now:
                    self.table.insert(parent='', index='end', values=data_per_tgl_list, tags=('target_row',))
                    target_this_day = [data_per_tgl_list[x] for x in target_time]
                    with open('data/temp', 'w') as z:
                        z.write(f'{target_this_day};{city_target}')
                elif count_tag % 2 == 0:
                    self.table.insert(parent='', index='end', values=data_per_tgl_list, tags=('even_row',))
                else:
                    self.table.insert(parent='', index='end', values=data_per_tgl_list, tags=('odd_row',))
                count_tag += 1
        # Parameter & Info City
        with open('data/params.cfg', 'r') as f_2:
            info = [line for line in f_2]

        return info

    def update_loc(self):
        target_city = self.list_city.get()
        # Cek Equals
        find = False
        with open('data/data_kota.cfg', 'r') as f:
            for data in f:
                target_from_list = data.split(":")[1].strip()
                if target_city == target_from_list:
                    id = data.split(":")[0].strip()
                    find = True
        if not find:
            dialog = messagebox.showwarning(title="Kesalahan",
                                            message="Pilih kota terlebih dahulu")
        else:
            # Update Data from Web
            Update = Schedule_App(int(id))
            Update.update_kota()
            Update.update_tanggal()
            Update.info_city()
            # Delete & Update Table
            for i in self.table.get_children():
                self.table.delete(i)
            GET = App.update_insert_table(self, target_city)
            # Update Param
            city_info, route, distance, inf1, inf2, inf3, inf4, inf5 = GET
            self.city_info_str.set(city_info)
            self.route_str.set(route)
            self.distance_str.set(distance)
            # Update Compass Image 
            img_file2 = PhotoImage(file='data/compass.png')
            self.compass_image.configure(image=img_file2)
            self.compass_image.image = img_file2

    def sound_set(self):
        sound_file = filedialog.askopenfilename(
            filetypes=(("File MP3", "*.mp3"),
                       ("File WAV", "*.wav"))
        )
        with open('data/sound_temp', 'w') as f:
            f.write(str(sound_file))
        self.sound_path.insert(0, sound_file)


class Schedule_App:
    def __init__(self, id):
        try:
            URL = "https://jadwalsholat.org/adzan/monthly.php"
            URL_CALENDAR = 'https://www.jadwalsholat.org/hijri/hijri.php'

            parameter = {
                'id': id,
            }

            self.php = requests.get(URL, params=parameter, timeout=10).text
            self.bs = BeautifulSoup(self.php, 'lxml')
        except (requests.ConnectionError, requests.Timeout) as e:
            dialog = messagebox.showerror(title="Kesalahan", message="No Internet Connection\n\n")

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
        table = self.bs.find('table')
        rows = table.find_all('tr', align="center")

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
        info_city_list = [cityinfo, arah, jarak, info1, info2, info3, info4, info5]

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
                print(time_now)
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

def main():
    main_app = Tk()
    main_app.iconbitmap('data/faviconmosque.ico')
    App(main_app)

    main_app.mainloop()

if __name__ == '__main__':
    app_ui = threading.Thread(target=main)
    app_ui.start()

    time.sleep(7)
    alarm = threading.Thread(target=Alarm.time_clock)
    alarm.daemon = True
    alarm.start()
