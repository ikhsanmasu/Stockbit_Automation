import math

from stocbit import StockbitBase
from datetime import datetime, time as datetimetime
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep


class StartTrading(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)
    update_saldo = pyqtSignal(str)
    update_timer = pyqtSignal(str)
    normalize_button = pyqtSignal()

    email = str()
    password = str()
    pin = str()

    jam_trading = str()
    saldo_trading = str()
    persentase_minimum = float()
    jumlah_emiten = int()
    range_value = str()
    range_harga = str()

    prioritas1 = str()
    prioritas2 = str()
    prioritas3 = str()
    prioritas4 = str()
    prioritas5 = str()
    prioritas6 = str()

    def run(self):
        try:
            # timer trading
            now = datetime.now()
            jt = self.jam_trading.split(":")
            start_hour = int(jt[0])
            start_minute = int(jt[1])
            start_second = int(jt[2])
            start_time = datetime.combine(now.date(), datetimetime(start_hour, start_minute, start_second))

            sisa_waktu = int((start_time - now).total_seconds() - 120)
            while sisa_waktu > 0:
                sisa_waktu = int((start_time - datetime.now()).total_seconds() - 120)
                self.update_timer.emit(f"Mencoba login dalam {sisa_waktu}s")
                sleep(1)
            self.update_timer.emit(f"Mencoba login")

            client = StockbitBase()
            # login akun dan masuk ke mode trading
            self.__login(client)

            self.update_timer.emit(f"login berhasil")

            client.get_watchlist_open_driver()

            sisa_waktu = int((start_time - now).total_seconds())
            while sisa_waktu > 0:
                sisa_waktu = int((start_time - datetime.now()).total_seconds())
                self.update_timer.emit(f"Mencoba trading dalam {sisa_waktu}s")
                sleep(1)
            self.update_timer.emit(f"Mencoba trading")

            self.progress.emit(f"{datetime.now()} - INFO - Mengambil data saham")
            summary = client.get_watchlist()
            self.progress.emit(f"{datetime.now()} - INFO - Filter saham")
            emitens = self.__get_potential_saham(summary)
            # . atau _ menggantikan ribuan
            saldo = self.saldo_trading.replace(".", "").replace("_", "")
            saldo = int(saldo)
            jumlah_emiten = int(self.jumlah_emiten)
            nilai_beli = int(saldo / jumlah_emiten)
            self.progress.emit(f"{datetime.now()} - INFO - Memulai order")

            try:
                for emiten in emitens[0:jumlah_emiten]:
                    lot = 100
                    harga_emiten = int(emiten['price'])
                    response = client.buy(symbol=emiten['symbol'], jumlah=nilai_beli // (harga_emiten * lot))
                    if response != True:
                        self.progress.emit(f"{datetime.now()} - WARNING - Gagal order {emiten['symbol']}")
            except:
                self.progress.emit(f"{datetime.now()} - INFO - Jumlah potensial saham kurang dari {jumlah_emiten}")

            self.finished.emit(f"{datetime.now()} - INFO - Proses Start Trading Selesai")

            client.close_driver()
        except Exception as e:
            self.finished.emit(f"{datetime.now()} - WARNING - Window tertutup saat proses")


    def __get_potential_saham(self, summary):
        summary = filter(lambda x:x['value'] != '-', summary)
        filtered_summary = list(self.__filter_emiten(summary))
        sorted_summary = self.__sorting_emiten(filtered_summary)

        if filtered_summary:
            self.progress.emit("Potential Emiten")
            self.progress.emit(''.join(
                [f" {data['symbol']} - {data['price']} - {data['percentage']} - value : {data['value']}\n" for data in
                 sorted_summary]))
        else:
            self.progress.emit("Tidak ada emiten yang cocok dibeli\n")

        return sorted_summary

    def __sorting_emiten(self, data):
        data = sorted(data, key=lambda x: int(x['price']))
        prioritas = [self.prioritas1, self.prioritas2, self.prioritas3, self.prioritas4, self.prioritas5, self.prioritas6]
        sorted_priority = list()

        for index in range(5):
            new_data = list(filter(
                lambda x: int(prioritas[index].split("-")[0]) <= int(x['price']) <= int(
                    prioritas[index].split("-")[1]),
                data))

            for dt in new_data:
                data.remove(dt)
                sorted_priority.append(dt)

        result = list()
        for sp in sorted_priority:
            result.append(sp)

        final = result + data
        return final

    def __filter_emiten(self, data):
        rp1 = int(self.range_harga.split("-")[0])
        rp2 = int(self.range_harga.split("-")[1])
        data = self.__filter_by_price(data, min=rp1, max=rp2)

        rv1 = int(self.range_value.split("-")[0])

        data = self.__filter_by_value(data, min=rv1)

        # mengubah format indonesia ke format luar menjadi . sebagai coma
        persentase = self.persentase_minimum
        data = self.__filter_by_minimum_percentage(data, persentase)
        return data

    def __filter_by_price(self, data, min: int = 0, max: int = 100000):
        data = filter(lambda x: min <= int(x['price']) <= max, data)
        return list(data)

    def __filter_by_value(self, data, min: int = 10000000):
        data = filter(lambda x: int(x['value']) >= min, data)
        return list(data)

    def __filter_by_minimum_percentage(self, data, min: float = 1):
        data = filter(lambda x: x['percentage'][x['percentage'].find("(") + 1] != "-" and float(
            x['percentage'][x['percentage'].find("(") + 1:x['percentage'].find(")") - 1].replace("-", "").replace("+",
                                                                                                                  "")) >= min,
                      data)
        return list(data)

    def __login(self, client):
        trying = True
        count = 0
        while trying:
            try:
                client.login(self.progress, email=self.email, password=self.password, pin=self.pin)
                trying = False
            except Exception as e:
                if count > 3:
                    self.progress.emit(
                        f"{datetime.now()} - WARNING - Proses Login Gagal sebanyak {count} berhenti mencoba login")
                    trying = False
                    continue
                self.progress.emit(
                    f"{datetime.now()} - WARNING - Proses Login Gagal, mencoba percobaan ke {count + 2} login kembali ")
                count += 1

        self.progress.emit(f"{datetime.now()} - INFO - Proses Login Selesai")
