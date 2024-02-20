from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import requests
import json
from .models import Search
import random
from urllib.request import urlopen, Request
import urllib.parse as url_parse


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/'
}

def index(request):
    searchList = Search.objects.all()

    goodsList = []

    for obj in searchList:

        url = "https://search.shopping.naver.com/search/all"
        keyword = obj.keyword

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

        # proxy_server = random_us_proxy()
        # proxies = {"http": 'http://' + proxy_server, 'https': 'https://' + proxy_server}
        # res = requests.get(url, params=params, headers=headers, proxies=proxies)

        # res = requests.get(url, params=params, headers=headers, verify=False)
        # html = res.text

        url = url + "?" + url_parse.urlencode(params)

        # Request 객체를 생성하여 URL과 헤더를 전달
        req = Request(url, headers=headers)

        # urlopen() 함수에 Request 객체를 전달하여 요청을 보냄
        response = urlopen(req)

        # 응답 받기
        html = response.read()

        soup = BeautifulSoup(html, 'html.parser')

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

            goodsList.append(
                {"title": title, "link": link, "price": price, "dlv": dlv, "compImg": compImg, "compText": compText})

    context = {"success": "success", "goodsList": goodsList, "searchList": searchList}

    return render(request, 'search/index.html', context)


@csrf_exempt
def search(request):
    keyword = ""

    if request.method == "POST":
        keyword = request.POST.get("keyword")

    print("keyword {}".format(keyword))

    if keyword != "전체":
        searchList = Search.objects.filter(keyword=keyword)
    else:
        searchList = Search.objects.all()

    goodsList = []

    for obj in searchList:

        url = "https://search.shopping.naver.com/search/all"
        keyword = obj.keyword

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

        # proxy_server = random_us_proxy()
        # proxies = {"http": 'http://' + proxy_server, 'https': 'https://' + proxy_server}
        # res = requests.get(url, params=params, headers=headers, proxies=proxies)

        # res = requests.get(url, params=params, headers=headers)
        # html = res.text

        url = url + "?" + url_parse.urlencode(params)

        # Request 객체를 생성하여 URL과 헤더를 전달
        req = Request(url, headers=headers)

        # urlopen() 함수에 Request 객체를 전달하여 요청을 보냄
        response = urlopen(req)

        soup = BeautifulSoup(html, 'html.parser')

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

            goodsList.append(
                {"title": title, "link": link, "price": price, "dlv": dlv, "compImg": compImg, "compText": compText})

    context = {"success": "success", "goodsList": goodsList}

    return JsonResponse(context)


def random_us_proxy():
    proxy_url = "https://www.us-proxy.org/"

    res = requests.get(proxy_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.find('tbody')
    rows = table.find_all('tr')
    proxy_server_list = []

    for row in rows:
        https = row.find('td', attrs={'class': 'hx'})
        if https.text == 'yes':
            ip = row.find_all('td')[0].text
            port = row.find_all('td')[1].text
            server = f"{ip}:{port}"
            proxy_server_list.append(server)

    proxy_server = random.choices(proxy_server_list)[0]
    return proxy_server
