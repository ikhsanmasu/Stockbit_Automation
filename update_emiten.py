from stocbit import StockbitBase
from PyQt5.QtCore import QThread, pyqtSignal

from datetime import datetime


class UpdateEmiten(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)

    email = str()
    password = str()
    pin = str()

    def run(self):
        try:
            client = StockbitBase()

            self.progress.emit(f"{datetime.now()} - INFO - scapping data dari https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham/")
            all_saham = client.get_all_saham()
            self.progress.emit(f"{datetime.now()} - INFO - selesai mengambil data saham -> Mencoba Login ke stockbit")
            # login akun dan masuk ke mode trading
            self.__login(client)
            self.progress.emit(f"{datetime.now()} - INFO - Login Berhasil")
            # get watchlist data
            self.progress.emit(f"{datetime.now()} - INFO - Mengambil data eksisting watchlist saham")
            emitens = self.__get_watchlist(client)
            self.progress.emit(f"{datetime.now()} - INFO - Mengambil data eksisting watchlist saham selesai")

            add_new = list(set(all_saham) - set(emitens)) + list(set(all_saham))

            client.update_watchlist(add_new)
            client.close_driver()
        except:
            self.finished.emit(f"{datetime.now()} - WARNING - Window tertutup saat proses")

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

    def __get_watchlist(self, client):
        # get watchlist data
        summary = client.get_watchlist()
        result = [data['symbol'] for data in summary]
        return result