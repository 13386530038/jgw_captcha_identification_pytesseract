import base64
import os
import random
import sys
import time
from io import BytesIO

import requests
from PIL import Image
import pytesseract

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def get_img(url):
    header = {
        "Host": "www.beian.gov.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.beian.gov.cn/portal/registerSystemInfo",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=099DF69FF3B7DA344F4F32C3A6DE1E12",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    response = requests.get(url=url, headers=header)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
    img.save("temp.png")
    img.show()

# 返回PIL.Image
# 说明：先获取了浏览器的包含导航栏的长宽，不同电脑可能不同，因此为了获得完整正确的验证码，可能需要修改下面的left、top等参数。
# 运行期间保持浏览器最大化，否则可能出错。
def get_img2(driver):
    driver.save_screenshot('fetch_date.png')  # 截取整个DOC

    width = 'return document.body.clientWidth'
    w = driver.execute_script(width)
    hight = 'return document.body.clientHeight'
    h = driver.execute_script(hight)

    im = Image.open("fetch_date.png")
    new_im = im.resize((w, h))
    # new_im.show()

    ce = driver.find_element(By.XPATH,'//*[@id="domainform"]/div/div[2]/div/img')
    left = ce.location['x'] - 10
    top = ce.location['y']
    right = ce.size['width'] + left
    height = ce.size['height'] + top


    img = new_im.crop((left, top, right, height))
    img.save('fetch_date.png')
    # img.show()
    return img

# 返回识别数字
def reg_num(img):
    return pytesseract.image_to_string(Image.open('fetch_date.png'), lang='eng')

if __name__ == '__main__':
    # 可以加一些设置
    url = input("请输入要识别URL：")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome('C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe', options=options)
    driver.maximize_window()

    # 访问百度验证码页面
    driver.get('https://www.beian.gov.cn/portal/registerSystemInfo')

    while True:
        try:
            WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'/html/body/div[1]/div[3]/div'))
        except:
            break

        try:
            # 找到网站域名选项
            driver.find_element(By.XPATH,'//*[@id="myTab"]/li[2]/a')
            driver.refresh()

            web = driver.find_element(By.XPATH, '//*[@id="myTab"]/li[2]/a').click()
            # 找到URL框
            url_input = driver.find_element(By.XPATH,'//*[@id="domain"]').send_keys(url)

            # 等待验证码出现
            WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'//*[@id="domainform"]/div/div[2]/div/img'))
            img_src = driver.find_element(By.XPATH,'//*[@id="domainform"]/div/div[2]/div/img').get_attribute('src')
            # img_base64 = get_img(img_src)
            img = get_img2(driver)
            num = reg_num(img)
            print(num)
            num_input = driver.find_element(By.XPATH,'//*[@id="ver2"]').send_keys(num)

            # 点击查询
            time.sleep(1)
            botton = driver.find_element(By.XPATH,'//*[@id="domainform"]/div/div[3]/div/button').click()
            # element = driver.find_element_by_xpath('//*[@id="domainform"]/div/div[3]/div/button').click()
            # element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="domainform"]/div/div[3]/div/button')))
            # element.click()

            time.sleep(3)
        except:
            break

    # 爬取table
    info = {}
    table_tr_list1 = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div[1]/table').find_elements(By.TAG_NAME,'tr')
    for tr in table_tr_list1:
        td_list = tr.find_elements(By.TAG_NAME,'td')
        info[td_list[0].text]=td_list[1].text

    table_tr_list2 = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div[2]/table').find_elements(By.TAG_NAME, 'tr')
    for tr in table_tr_list2:
        td_list = tr.find_elements(By.TAG_NAME, 'td')
        info[td_list[0].text] = td_list[1].text

    print(info)