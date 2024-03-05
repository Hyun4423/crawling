import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome 드라이버 경로 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
custom_headers = {
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

for key, value in custom_headers.items():
    options.add_argument(f"--{key}={value}")

# Selenium 웹 드라이버 실행
driver = webdriver.Chrome(options=options)

req = requests.get("http://54.180.212.237/get_search_list")

search_list = json.loads(req.text)["search_list"]

goods_list = []

driver.get("http://54.180.212.237")

print("driver.page_source => {}".format(driver.page_source))

# 대기 설정
wait = WebDriverWait(driver, 30)

# iframe이 로드될 때까지 대기
wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

iframe = driver.find_element(By.TAG_NAME, "iframe")

driver.switch_to.frame(iframe)

print("driver.page_source => {}".format(driver.page_source))

# 모든 속성을 확인하려면 get_attribute() 메서드를 사용합니다.
attributes = iframe.get_property("attributes")
for attribute in attributes:
    attribute_name = attribute["name"]
    attribute_value = iframe.get_attribute(attribute_name)
    print(f"{attribute_name}: {attribute_value}")

# 원래의 상위 프레임으로 다시 전환
driver.switch_to.default_content()

for obj in search_list:

    url = "http://search.shopping.naver.com/search/all"
    keyword = obj["keyword"]

    # params = None
    # if url.find('naver'):
    params = (
        ('sort', 'price_asc'),
        ('pagingIndex', '1'),
        ('pagingSize', '3'),
        ('viewType', 'list'),
        ('productSet', 'total'),
        ('deliveryFee', ''),
        ('deliveryTypeValue', ''),
        ('frm', 'NVSHATC'),
        ('query', keyword),
        ('origQuery', keyword),
        ('freeDelivery', 'true'),
        ('iq', ''),
        ('eq', ''),
        ('xq', ''),
    )

    url = url + "?" + urlencode(params)

    # iframe의 src 속성 변경
    # iframe.__setattr__("src", url)
    driver.execute_script("arguments[0].setAttribute('src', arguments[1])", iframe, url)

    driver.switch_to.frame(iframe)

    iframe_content = driver.page_source

    print("iframe_content => {}".format(iframe_content))

    soup = BeautifulSoup(iframe_content, 'html.parser')

    content = soup.select_one("#content")

    items = content.select("div.basicList_list_basis__uNBZx > div > div")

    for item in items:
        title = item.select_one("div.product_title__Mmw2K > a").text
        link = item.select_one("div.product_title__Mmw2K > a").get("href")
        price = item.select_one("div.product_price_area__eTg7I span.price").text
        dlv = item.select_one("div.product_price_area__eTg7I span.price_delivery__yw_We").text
        comp = item.select_one("div.product_mall_title__Xer1m > a > img")
        compImg = ""
        compText = ""
        if comp:
            compImg = comp.get("src")
            compText = comp.get("alt")
        else:
            compText = item.select_one("div.product_mall_title__Xer1m > a").text

        goods_list.append(
            {"title": title, "link": link, "price": price, "dlv": dlv, "compImg": compImg, "compText": compText})

# 드라이버 종료
driver.quit()

print("goods_list => {}".format(goods_list))

requests.post("http://54.180.212.237/result", json={'goods_list': goods_list})
