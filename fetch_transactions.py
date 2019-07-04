import hashlib
import os
import sys
from time import sleep

import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from sqlalchemy.exc import IntegrityError

from app.models import Transaction
from config import Config

load_dotenv()


def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in directory:
            if fname.endswith(".crdownload"):
                dl_wait = True

        seconds += 1
    return seconds


def download_transactions(date_range="Last 7 Days"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = "_downloads"
    download_path = os.path.join(base_dir, download_dir)
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    for f in os.listdir(download_path):
        os.remove(os.path.join(download_path, f))

    options = Options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    options.add_argument("--headless")
    options.add_argument("--allow-scripts")
    options.add_argument("--no-sandbox")
    options.add_argument("log-level=1")

    WINDOW_SIZE = "1200,900"
    options.add_argument("--window-size=%s" % WINDOW_SIZE)

    user = os.getenv("PAN")
    pwd = os.getenv("SECURE_CODE")
    driver = webdriver.Chrome(options=options)

    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    command_result = driver.execute("send_command", params)

    driver.get("https://ibs.bankwest.com.au/BWLogin/bib.aspx")

    # elem = driver.find_element_by_id("AuthUC_txtUserID")
    elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "AuthUC_txtUserID"))
    )
    print(f"before: {elem.get_attribute('value')}")
    elem.send_keys(user)
    print(f"after: {elem.get_attribute('value')}")
    # assert elem.get_attribute("value") == user
    # WebDriverWait(driver, 5).until(lambda browser: elem.get_attribute("value") == user)

    # elem = driver.find_element_by_id("AuthUC_txtData")
    elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "AuthUC_txtData"))
    )
    print(f"before: {elem.get_attribute('value')}")
    elem.send_keys(pwd)
    print(f"after: {elem.get_attribute('value')}")
    # assert elem.get_attribute("value") == pwd
    # WebDriverWait(driver, 5).until(lambda browser: elem.get_attribute("value") == pwd)

    # elem = driver.find_element_by_id("AuthUC_btnLogin")
    elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "AuthUC_btnLogin"))
    )
    elem.click()

    # elem = driver.find_element_by_link_text("Transaction search")
    try:
        elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Transaction search"))
        )
        print("Login successful.")
    except TimeoutException as e:
        print(driver.page_source)
    elem.click()

    elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "_ctl0_ContentMain_ddlRangeOptions"))
    )
    s1 = Select(elem)
    s1.select_by_visible_text(date_range)

    driver.execute_script(
        'javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("_ctl0:ContentButtonsLeft:btnExport", "", true, "", "", false, true))'
    )
    download_wait(download_path, 20, nfiles=1)
    driver.close()

    downloaded_file = os.path.join(download_path, os.listdir(download_path)[0])
    df = pd.read_csv(downloaded_file, dayfirst=True)
    df["Amount"] = df["Credit"].fillna(0.0) + df["Debit"].fillna(
        0.0
    )  # combine credit and debit columns
    df = df[
        ~df.Narration.str.contains("AUTHORISATION ONLY")
    ]  # drop authorisation only entries
    for f in os.listdir(download_path):
        os.remove(os.path.join(download_path, f))

    return df


def submit_transactions(df):
    n = 0
    for i, row in df.iterrows():
        try:
            h = hashlib.md5(
                "{0}{1}{2}".format(
                    row["Transaction Date"], row["Narration"], row["Balance"]
                ).encode("utf-8")
            ).hexdigest()
            db.session.add(
                Transaction(
                    id=h,
                    account=row["Account Number"],
                    date=pd.to_datetime(row["Transaction Date"]),
                    narration=row["Narration"],
                    amount=row["Amount"],
                    balance=row["Balance"],
                )
            )
            db.session.flush()
            n += 1
        except IntegrityError as e:
            db.session.rollback()
        finally:
            db.session.commit()
    print(f"Added {n} new transactions.")


if __name__ == "__main__":

    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)

    if len(sys.argv) == 2:
        date_range = sys.argv[1]
        submit_transactions(download_transactions(date_range=date_range))
    else:
        submit_transactions(download_transactions())
