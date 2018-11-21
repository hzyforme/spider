from selenium import webdriver
from time import sleep
import pickle
def getcookie():
    driver=webdriver.PhantomJs()
    driver.get('https://accounts.douban.com/login')
    driver.find_element_by_xpath('//*[@id="email"]').send_keys('username')
    driver.find_element_by_xpath('//*[@id="password"]').send_keys('pwd')
    driver.find_element_by_xpath('//*[@id="lzform"]/div[6]/input').click()
    sleep(5)
    cookie=driver.get_cookies()
    cookie_dict={}
    for c in cookie:
        cookie_dict[c['name']]=c['value']
    pickle.dump(cookie_dict,open('/home/fang/Documents/douban/douban/cookies.ini','wb'))
    driver.close()

if __name__ == '__main__':
    getcookie()
