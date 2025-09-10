from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

options = webdriver.ChromeOptions()
options.add_experimental_option("detach",True)
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
driver.get("https://www.instagram.com/")
time.sleep(5)
username_field = driver.find_element(By.NAME,"username")
password_field = driver.find_element(By.NAME,"password")
login_btn = driver.find_element(By.XPATH,"//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1']")
username_field.send_keys("icanmakebotsnow")
password_field.send_keys("kulkul123")
login_btn.click()
time.sleep(10)


dm_btn = driver.find_element(By.XPATH,"//a[@aria-label='Direct messaging - 0 new notifications link']//div[@class='x9f619 x3nfvp2 xr9ek0c xjpr12u xo237n4 x6pnmvc x7nr27j x12dmmrz xz9dl7a xn6708d xsag5q8 x1ye3gou x80pfx3 x159b3zp x1dn74xm xif99yt x172qv1o x10djquj x1lhsz42 xzauu7c xdoji71 x1dejxi8 x9k3k5o xs3sg5q x11hdxyr x12ldp4w x1wj20lx x1lq5wgf xgqcy7u x30kzoy x9jhf4c']")
dm_btn.click()

wait = WebDriverWait(driver,30)
turn_off = wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"/html[1]/body[1]/div[7]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[3]/button[2]")))
#turn_off = driver.find_element(By.XPATH,"/html[1]/body[1]/div[7]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[3]/button[2]")
turn_off.click()
time.sleep(2)

dm = driver.find_element(By.XPATH,"//div[@class='x78zum5 x2lah0s xn6708d']")
dm.click()

chatbox = driver.find_element(By.XPATH,"//div[@aria-label='Message']")
i=20
while i>0:
    chatbox.send_keys("hehe")
    time.sleep(2)
    send = driver.find_element(By.XPATH, "//div[normalize-space()='Send']")
    send.click()
    i=i-1
