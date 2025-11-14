from selenium import webdriver
import time

navegador = webdriver.Chrome()
navegador.get("https://ts-plusx1.kblcontabilidade.com.br/html5/login.aspx")

time.sleep(5)
