from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from functools import wraps
from datetime import datetime

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

def _continue_on_failure(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return f" WARNING - function {func} gagal di eksekusi"
    return wraper


class StockbitBase():
    def __init__(self):
        self.STOCKBIT_EMAIL = None
        self.STOCKBIT_PASSWORD = None
        self.STOCKBIT_PIN = None
        self.progress = None

        self.__login_url = "https://stockbit.com/login"
        self.__portofolio_url = "https://stockbit.com/securities/portfolio"
        self.__wathlist_url = "https://stockbit.com/watchlist"
        self.__buy_url = "https://stockbit.com/symbol/"

        self.__chrome_option = webdriver.ChromeOptions()
        self.__chrome_option.add_experimental_option("detach", True)

        try:
            self.__driver = webdriver.Chrome()
        except:
            # Install Webdriver
            service = Service(ChromeDriverManager().install())
            self.__driver = webdriver.Chrome(service=service)

        self.__actions = ActionChains(self.__driver)

    def get_all_saham(self):
        url = "https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham/"
        self.__driver.get(url)
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//label[text()="Baris:"]')))

        all_saham = self.__driver.find_element(By.XPATH, '//option[text()="All"]')
        all_saham.click()

        all_saham = self.__driver.find_elements(By.XPATH, '//table[@id="vgt-table"]/tbody/tr/td[1]/span')
        list_saham = []
        for saham in all_saham:
            list_saham.append(saham.text)
        return list_saham

    def update_watchlist(self, add_saham):
        input = self.__driver.find_elements(By.XPATH, value='//input')
        input = input[1]
        for saham in add_saham:
            input.send_keys(Keys.CONTROL + "a")
            input.send_keys(saham)
            input.send_keys(Keys.ENTER)
            sleep(2)

    def close_driver(self):
        self.__driver.close()

    @_continue_on_failure
    def buy(self, symbol: str, jumlah: int):
        self.__driver.maximize_window()
        url = self.__buy_url + symbol
        self.__driver.get(url)
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//h3[text()="{symbol}"]')))
        # buy_button = self.__driver.find_element(By.XPATH, '//*[@id="main-container"]/div[2]/section[1]/div[1]/div[2]/button[2]')
        # buy_button.click()
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//option[text()="Good For Day"]')))
        lot_input = self.__driver.find_element(By.XPATH, '//option[text()="Good For Day"]/preceding::input[1]')

        lot_input.send_keys(str(jumlah))

        place_order_button = self.__driver.find_element(By.XPATH, '//p[text()="Place Order"]/parent::button')
        place_order_button.click()
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//p[text()="Confirm"]')))
        confirm_button = self.__driver.find_element(By.XPATH, '//p[text()="Confirm"]//parent::button')
        confirm_button.click()
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//p[text()="Order is Now Placed"]')))
        self.progress.emit(f"INFO - Berhasil order {symbol} sebanyak {jumlah} lot")
        return True


    def login(self, progress, email: str, password: str, pin: str):
        self.progress = progress

        self.STOCKBIT_EMAIL = email
        self.STOCKBIT_PASSWORD = password
        self.STOCKBIT_PIN = pin

        self.progress.emit(f"{datetime.now()} - INFO - Membuka Halaman Login")
        self.__driver.get(self.__login_url)

        # self.progress.emit(f"{datetime.now()} - INFO - Mencoba Reject Cookies")
        # log = self.__reject_cookies()
        # self.progress.emit(f"{datetime.now()} - INFO - {log}")

        self.progress.emit(f"{datetime.now()} - INFO - Mencoba Sign In ke akun UpdateSaldo")
        log = self.__sign_in()
        self.progress.emit(f"{datetime.now()} - INFO - {log}")

        self.progress.emit(f"{datetime.now()} - INFO - Mencoba menutup menu pilih avatar")
        log = self.__close_avatar_choosing()
        self.progress.emit(f"{datetime.now()} - INFO - {log}")

        self.progress.emit(f"{datetime.now()} - INFO - Mencoba Memasukan Pin Start Trading")
        log = self.__start_trading()
        self.progress.emit(f"{datetime.now()} - INFO - {log}")

        return log

    def get_data_saldo(self):
        self.__driver.get(self.__portofolio_url)
        trading_balance = self.__driver.find_element(By.XPATH,
                                                     value='//*[@id="main-container"]/div[2]/div[2]/div[1]/p[1]')
        return trading_balance.text

    def get_watchlist_open_driver(self):
        self.__driver.get(self.__wathlist_url)

    def get_watchlist(self):
        # self.__driver.get(self.__wathlist_url)
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[text()='Symbol']")))
        list_emiten = self.__driver.find_elements(By.CSS_SELECTOR, value=".ant-spin-container tbody tr p")
        values_emiten = self.__driver.find_elements(By.CSS_SELECTOR, value=".ant-spin-container tbody tr td")
        summary_emiten = list()
        symbol = list()
        abrivation = list()
        price = list()
        percentage = list()
        value = list()

        for index, emiten in enumerate(values_emiten):
            if index % 3 == 2:
                value.append(emiten.text)

        for index, emiten in enumerate(list_emiten):
            if index % 5 == 0:
                symbol.append(emiten.text)
            elif index % 5 == 1:
                abrivation.append(emiten.text)
            elif index % 5 == 3:
                price.append(emiten.text)
            elif index % 5 == 4:
                percentage.append(emiten.text)

        for index in range(len(symbol)):
            s_e = {
                "symbol": symbol[index],
                "abrivation": abrivation[index],
                "price": price[index].replace(",", ""),
                "percentage": percentage[index],
                "value": value[index].replace(".00", "").replace(",", "")
            }
            summary_emiten.append(s_e)

        self.progress.emit(f"{datetime.now()} - INFO - Berhasil Scraping emiten")
        self.progress.emit(f"\n Summary Watchlist")
        self.progress.emit(''.join(
            [f" {data['symbol']} - {data['price']} - {data['percentage']} - value : {data['value']}\n" for data in
             summary_emiten]))

        return summary_emiten

    @_continue_on_failure
    def __reject_cookies(self):
        # Click Reject Cookies Button
        reject_button = self.__driver.find_element(by=By.CSS_SELECTOR, value='button[action-type="DENY"]')
        reject_button.click()
        return "Cookies Berhasil di Deny"

    @_continue_on_failure
    def __sign_in(self):
        # Sign in
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        email_field = self.__driver.find_element(by=By.ID, value="username")
        email_field.send_keys(self.STOCKBIT_EMAIL)
        password_field = self.__driver.find_element(by=By.ID, value="password")
        password_field.send_keys(self.STOCKBIT_PASSWORD)
        password_field.send_keys(Keys.ENTER)
        return "Percobaan Sign In Selesai"

    @_continue_on_failure
    def __close_avatar_choosing(self):
        # Close Avatar choosing
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, "modalnewavatar-button-skip")))
        skip_avatar = self.__driver.find_element(by=By.ID, value="modalnewavatar-button-skip")
        skip_avatar.click()
        return "Berhasil Menutup Window Pilih Avatar"

    # @_continue_on_failure
    def __start_trading(self):
        start_trading = self.__driver.find_element(by=By.XPATH, value='//*[@id="stockbit-header-web"]/div[2]')
        start_trading.click()
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[text()='Masukkan PIN Trading']")))
        actions = ActionChains(self.__driver)
        for index in range(0, 6):
            sleep(0.1)
            actions.send_keys(self.STOCKBIT_PIN[index])
            actions.perform()
        WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[text()='Trading Area']")))
        return "Berhasil Login Trading"
