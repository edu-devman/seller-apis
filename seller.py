import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id, client_id, seller_token):
    """Получить список товаров магазина озон.

    Принимает на вход несколько переменных, позволет получить
    словарь, содержащий товары и их характеристики

    Example:
        >>> get_product_list("", s12542, s.XXXX)
        "items": [
          {
            "archived": true,
            "has_fbo_stocks": true,
            "has_fbs_stocks": true,
            "is_discounted": true,
            "offer_id": "136748",
            "product_id": 223681945,
            "quants": [
              {
                "quant_code": "string",
                "quant_size": 0
              }
            ]
          }
        ],
        "total": 1,
        "last_id": "bnVсbA=="

    Args:
        client_id: Идентификатор клиента
        seller_token: API-ключ
        last_id: идентификатор последнего значения на странице

    Returns:
        [result]: словарь, содержащий список тваров с их характеристиками

    Note:
        - Возвращает товары и их характеристикими;
        - в случае ошибки будет выброшено исключение.
    """
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def get_offer_ids(client_id, seller_token):
    """Получить артикулы товаров магазина озон, Пример: "offer_id": "136748"

    Принимает на вход несколько аргументов, в результете выполнения,
    позволяет получить артикулы товаров.

    Example:
        >>> get_offer_ids(s12542, s.XXXX)
        "items": [
          {
            ...
            "offer_id": "136748",
            ...
          }
        ],
        "total": 1,
        "last_id": "bnVсbA=="

    Args:
        client_id: Идентификатор клиента
        seller_token: API-ключ

    Returns:
        [offer_ids]: список артикулов товаров

    Note:
        - Возвращает список артикулов* товаров магазина озон,
          *offer_id - идентификатор товара в системе продавца — артикул.
    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids


def update_price(prices: list, client_id, seller_token):
    """Обновить цены товаров.

    Позволяет изменить цену одного или нескольких товаров,
    где prices: list - формируется в функции create_prices

    Example:
        >>> update_price(prices: list, s12542, s.XXXX)
        POST:
        {
          "prices": [
            {
              "auto_action_enabled": "UNKNOWN",
              "auto_add_to_ozon_actions_list_enabled": "UNKNOWN",
              "currency_code": "RUB",
              "manage_elastic_boosting_through_price": true,
              "min_price": "800",
              "min_price_for_auto_actions_enabled": true,
              "net_price": "650",
              "offer_id": "",
              "old_price": "0",
              "price": "1448",
              "price_strategy_enabled": "UNKNOWN",
              "product_id": 1386,
              "quant_size": 1,
              "vat": "0.1"
            }
          ]
        }
        --
        RESULT:
        {
          "result": [
            {
              "product_id": 1386,
              "offer_id": "PH8865",
              "updated": true,
              "errors": []
            }
          ]
        }

    Args:
        client_id: Идентификатор клиента
        seller_token: API-ключ
        prices: информация о ценах товаров.

    Returns:
        [result]: Изменение стоимости товара/ов

    Note:
        - Возвращает измененную стоимость товаров
        - в случае ошибки будет выброшено исключение.
    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_stocks(stocks: list, client_id, seller_token):
    """Обновить остатки

    Позволяет изменить информацию о количестве товара в наличии,
    где prices: list - формируется в функции create_stocks

    Важно: Метод будет отключён 27 мая 2025 года. Переключитесь
    на /v2/products/stocks

    Example:
        >>> update_stocks(stocks: list, s12542, s.XXXX)
        POST:
        {
          "stocks": [
            {
              "offer_id": "PH11042",
              "product_id": 313455276,
              "stock": 100,
              "warehouse_id": 22142605386000
            }
          ]
        }
        --
        RESULT:
        {
          "result": [
            {
              "warehouse_id": 22142605386000,
              "product_id": 118597312,
              "offer_id": "PH11042",
              "updated": true,
              "errors": []
            }
          ]
        }

    Args:
        client_id: Идентификатор клиента
        seller_token: API-ключ
        stocks: информация о товарах на складах.

    Returns:
        [result]: Изменение информации о количестве товара в наличии

    Note:
        - Изменяет информацию о количестве товара в наличии;
        - в случае ошибки будет выброшено исключение.
    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def download_stock():
    """Скачать файл ostatki с сайта casio

    Функция загружает zip-архив по указанному URL, извлекает из него
    файл "ostatki.xls", читает этот Excel-файл начиная
    с 18-й строки (header=17) и преобразует в список словарей.
    Затем удаляет extracted file и возвращает данные.

    Example:
        >>> download_stock()
    [
        {
            'Код': 'ABC123',
            'Наименование': 'CASIO G-SHOCK GA-100-1A1ER',
            'Количество': 5,
            'Цена': '15,990.00 руб.',
            'Склад': 'Москва'
        },
        {
            'Код': 'DEF456',
            'Наименование': 'CASIO BABY-G BGA-190-7BER',
            'Количество': 3,
            'Цена': '12,490.00 руб.',
            'Склад': 'СПб'
        },
        {
            'Код': 'GHI789',
            'Наименование': 'CASIO EDIFICE EF-527D-1AVER',
            'Количество': 0,
            'Цена': '18,790.00 руб.',
            'Склад': 'Москва'
        },
        # ...
    ]

    Args:
       []

    Returns:
        [watch_remnants]:  Возвращается список словарей,
                           содержашем данные о товарах Casio.

    Note:
        -  Список словарей, где каждый словарь представляет
           одну строку.
    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants


def create_stocks(watch_remnants, offer_ids):
    """Создадим остатки

    Функция формирует информацию о количестве товаров в наличии, 
    сверяя актуальную информацию от поставшика `watch_remnants`.
    Сверка формируется на основе артикулов товаров,
    которые уже есть на сайте озон  - `offer_ids`.
    Если товар на сайте отсутствует - он будет добавлен из `watch_remnants`.

    Example:
        >>> create_stocks(watch_remnants, offer_ids)
        {"offer_id": "136748",  "stock": 100}
        {"offer_id": "112348",  "stock": 4}
        {"offer_id": "112748",  "stock": 0}

    Args:
        offer_ids - список артикулов с сайта озон
        watch_remnants - список словарей, содержаших данные о товарах Casio

    Returns:
        [stocks]: Возвращается количество товаров

    Note:
        -  Словарь содержит количество товаров Cisco
    """
    # Уберем то, что не загружено в seller
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks


def create_prices(watch_remnants, offer_ids):
    """Создадим цены

    Функция формирует информацию о цене товаров в наличии, 
    сверяя актуальную информацию от поставшика `watch_remnants`.
    Сверка формируется на основе артикулов товаров,
    которые уже есть на сайте озон  - `offer_ids`.

    Example:
        >>> create_prices(watch_remnants, offer_ids)
        price = {
            "auto_action_enabled": "UNKNOWN",
            "currency_code": "RUB",
            "offer_id": "136748",
            "old_price": "0",
            "price": "1448",
        }

    Args:
        offer_ids - список артикулов с сайта озон
        watch_remnants - список словарей, содержаших данные о товарах Casio

    Returns:
        [stocks]: Возвращается стоимость товаров

    Note:
        -  Словарь содержит стоимость товаров Cisco
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices


def price_conversion(price: str) -> str:
    """Преобразовать цену. Пример: 5'990.00 руб. -> 5990

    Функция удаляет все нецифровые символы и дробную часть, возвращая
    только целые числа в виде строки.

    Example:
        >>> price_conversion("5'990.00 руб.")
        '5990'
        >>> price_conversion("1,299.99 $")
        '1299'
        >>> price_conversion("0.50 руб.")
        '0'
        >>> price_conversion(5990.00)
        'AttributeError: "float" object has no attribute "split"'
        >>> price_conversion(5990)
        'AttributeError: "int" object has no attribute "split"'


    Args:
        price (str): Строка с ценой, которая может содержать разделители
                     тысяч, дробную часть, валюту и другие нецифровые символы.

    Returns:
        str: Строка, содержащая только цифры целой части цены.

    Note:
        - Если цена содержит дробную часть, она отбрасывается;
        - все нецифровые символы (включая пробелы, валюту, разделители)
          удаляются;
        - возвращаемая строка может быть пустой, если в исходной строке нет
          цифр;
        - если на вход будет подано число, возникнет ошибка.
    """
    return re.sub("[^0-9]", "", price.split(".")[0])


def divide(lst: list, n: int):
    """Разделить список lst на части по n элементов

    Функция позволяет разделить список на части не более чем 100 элементов.
    Такое разделение связано с тем, что за один запрос можно изменить 
    наличие для 100 пар товар-склад. 
    (https://docs.ozon.ru/api/seller/#operation/ProductAPI_ProductsStocksV2)

    Args:
        lst list: Словарь элементов
        n int: Число константа - `100`

    Returns:
        lst: Возвращает скорректированный список элеметов
        
    Note:
        - В зависимости от места вызова функции в коде, на вход может принять,
          либо prices, либо stocks
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
