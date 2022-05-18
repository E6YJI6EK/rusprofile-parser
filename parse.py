from ast import pattern
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re


def init_driver():
    # init webdriver firefox
    options = webdriver.FirefoxOptions()
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
    )
    options.set_preference("dom.webdriver.enabled", False)
    options.headless = True
    return webdriver.Firefox(
        executable_path="driver/geckodriver",
        options=options
    )


def init_wait(driver):
    return WebDriverWait(driver, 3)


def element_is_exist(by, path, wait):
    try:
        # driver.find_element(by, path)
        wait.until(EC.presence_of_element_located((by, path)))
        return True
    except Exception:
        return False


def auth(driver, wait, mail, password):
    # Находим конпку для авторизации
    button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'login-tools__user')))
    button.click()
    # Находим поля мыла и пароля
    mail_field = wait.until(EC.presence_of_element_located((By.ID, "mw-l_mail")))
    password_field = driver.find_element(By.ID, 'mw-l_pass')

    mail_field.send_keys(mail)
    password_field.send_keys(password)
    # Кнопка заверешения авторизации
    login_button = driver.find_element(By.ID, "mw-l_entrance")
    login_button.click()

    # если появляется дурацкое окно
    if element_is_exist(By.XPATH, "/html/body/div[5]/div/div/div/div/div[6]", wait):
        skip_button = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div/div/div[6]")))
        skip_button.click()
        return True

    return True


def get_data(driver, wait, inn_code):
    data = {}

    #  Делаем query-запрос на руспрофайл с данным ИНН
    try:
        driver.get(url=f'https://www.rusprofile.ru/search?query={inn_code}&type=ul')
    except Exception as e:
        print(e)
        return None

    #  Проверяем страничку, выданную поиском

    # Поиск ОПФ, названия организации
    pattern = re.compile(r"(\S+?)\s*(\"*[\w\s\d-]*?\"*)")
    org_name = pattern.search(driver.find_element(By.CSS_SELECTOR, ".company-header>.company-header__row>h1").text)
    print(org_name.group())
    opf = org_name.group(1)
    data.update({"opf": opf})
    organization = org_name.group(2)
    data.update({"organization": organization})

    # Поиск мыла
    if element_is_exist(By.CSS_SELECTOR, ".mail>.light", wait):  # Если мыла нет вообще
        email = "-"
    else:
        email = driver.find_element(By.CSS_SELECTOR, ".mail>span>a").text

    data.update({"email": email})

    # Поиск директора
    director = driver.find_element(By.XPATH,
                                   "/html/body/div[2]/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/div[3]/span[3]").text
    data.update({"director": director})

    # Поиск адреса
    address = driver.find_element(By.XPATH, "//*[@id='anketa']/div[2]/div[1]/div[2]/address/span[2]").text
    data.update({"address": address})

    # Поиск телефона
    if element_is_exist(By.CSS_SELECTOR, ".phone>.light", wait):  # Если номероов нет вообще
        phones = None
    elif element_is_exist(By.XPATH,
                          "/html/body/div[2]/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/div[1]/div/span[4]/button", wait):  # Если есть кнопка "Ещё N номеров"
        phones = []

        more_button = driver.find_element(By.XPATH,
                                          "/html/body/div[2]/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[3]/div[1]/div/span[4]/button")
        more_button.click()

        first_phones = driver.find_elements(By.CSS_SELECTOR, ".phone>span>a")
        hidden_phones = driver.find_elements(By.CSS_SELECTOR, ".phone>.hidden-text>span>a")

        for item in first_phones:
            phones += [item.text]
        for item in hidden_phones:
            phones += [item.text]
    else:
        phones = []

        first_phones = driver.find_elements(By.CSS_SELECTOR, ".phone>span>a")

        for item in first_phones:
            phones += [item.text]

    data.update({"phones": phones})

    return data



