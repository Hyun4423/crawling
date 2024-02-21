from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver

from .models import Search


def index(request):
    search_list = Search.objects.all()

    goods_list = []
    # goods_list = get_goods_list(search_list)
    # goods_list = get_goods_list_by_api(search_list)
    # goods_list = get_goods_list_by_webdriver(request, search_list)

    context = {"success": "success", "goods_list": goods_list, "search_list": search_list}

    return render(request, 'search/index.html', context)


@csrf_exempt
def search(request):
    keyword = ""

    if request.method == "POST":
        keyword = request.POST.get("keyword")

    print("keyword {}".format(keyword))

    if keyword != "전체":
        search_list = Search.objects.filter(keyword=keyword)
    else:
        search_list = Search.objects.all()

    # goods_list = get_goods_list(search_list)
    # goods_list = get_goods_list_by_api(search_list)
    goods_list = get_goods_list_by_webdriver(request,search_list)

    context = {"success": "success", "goods_list": goods_list}

    return JsonResponse(context)


def get_goods_list(search_list):
    goods_list = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for obj in search_list:

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

        res = requests.get(url, params=params, headers=headers)
        html = res.text

        print("html {} ".format(html))

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

            goods_list.append(
                {"title": title, "link": link, "price": price, "dlv": dlv, "compImg": compImg, "compText": compText})

    return goods_list


def get_goods_list_by_api(search_list):
    goods_list = []

    headers = {
        'X-Naver-Client-Id': 'WYdzqfyzZbAGjLV653ZH',
        'X-Naver-Client-Secret': 'C7XOh2cboZ'
    }

    for obj in search_list:

        url = "https://openapi.naver.com/v1/search/shop.json"
        keyword = obj.keyword

        params = {
            'query': keyword,
            'display': 3,
            'sort': "asc"
        }

        res = requests.get(url, params=params, headers=headers)
        data = res.json()

        for item in data['items']:
            goods_list.append(
                {'title': item['title'], "link": item['link'], "price": item['lprice'], "compText": item['mallName'],
                 "dlv": "", "compImg": ""}
            )

    return goods_list


def get_goods_list_by_webdriver(request, search_list):
    goods_list = []

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)

    for obj in search_list:

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

        url = url + "?" + urlencode(params)

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

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

    driver.quit()

    return goods_list

