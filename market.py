import datetime
import logging.config
from environs import Env
from seller import download_stock

import requests

from seller import divide, price_conversion

logger = logging.getLogger(__file__)


def get_product_list(page, campaign_id, access_token):
    """Получить список товаров магазина Яндекс Маркет.

    Для каждого товара, который вы размещаете на Маркете, функция возвращает
    информацию о карточках Маркета, к которым привязан этот товар.

    Example:
        Request:
            https://api.partner.market.yandex.ru/v2/campaigns/{campaignId}/offer-mapping-entries

        Responses [200 OK]:
            {
                "status": "OK",
                "result": {
                    "paging": {
                        "nextPageToken": "string",
                        "prevPageToken": "string"
                        ...
                    ...
            }
        Responses [400 Bad Request]:
            {
                "status": "OK",
                "errors": [
                    {
                        "code": "string",
                        "message": "string"
                    }
                ]
            }
        Responses [403 Forbidden]
        Responses [404 Not Found]   
        Responses [420 Method Failure]
        Responses [500 Internal Server Error]

    Args:
        page: Идентификатор страницы c результатами;
        campaign_id: идентификатор кампании;
        access_token: идентификатор клиента.

    Returns:
        [result]: словарь, содержащий список тваров с их характеристиками

    Note:
        - Информация о товарах в каталоге;
        - лимит: 10 000 товаров в минуту;
        - в случае ошибки будет выброшено исключение.
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {
        "page_token": page,
        "limit": 200,
    }
    url = endpoint_url + f"campaigns/{campaign_id}/offer-mapping-entries"
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def update_stocks(stocks, campaign_id, access_token):
    """Обновить остатки товаров магазина Яндекс Маркет.

    Функция фозвращает `остаток товара` — это число единиц,
    доступных для заказа на Маркете.

    Example:
        Request:
            https://api.partner.market.yandex.ru/v2/campaigns/{campaignId}/offers/stocks

        Responses [200 OK]:
            {
                "skus": [
                    {
                        "sku": "string",
                        "items": [
                            {
                                "count": 0,
                                "updatedAt": "2022-12-29T18:02:01Z"
                            }
                        ]
                    }
                ]
            }
        Responses [400 Bad Request]:
            {
                "status": "OK",
                "errors": [
                    {
                        "code": "string",
                        "message": "string"
                    }
                ]
            }
        Responses [401 Forbidden]
        Responses [404 Not Found]
        Responses [420 Method Failure]
        Responses [500 Internal Server Error]

    Args:
        page: Идентификатор страницы c результатами;
        campaign_id: идентификатор кампании;
        access_token: идентификатор клиента.

    Returns:
        [result]: словарь, содержащий обновленный список тваров

    Note:
        - Обновляет данные об остатках товаров на витрине;
        - лимит: 100 000 товаров в минуту;
        - в случае ошибки будет выброшено исключение.
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"skus": stocks}
    url = endpoint_url + f"campaigns/{campaign_id}/offers/stocks"
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def update_price(prices, campaign_id, access_token):
    """Обновить цены товаров магазина Яндекс Маркет.

    Example:
        Request:
            https://api.partner.market.yandex.ru/v2/campaigns/{campaignId}/offer-prices/updates

        Responses [200 OK]:
            {
                "offers": [
                    {
                        "offerId": "string",
                        "price": {
                            "value": 0,
                            "discountBase": 0,
                            "currencyId": "RUR",
                            "vat": 0
                        }
                    }
                ]
            }
        Responses [400 Bad Request]:
            {
                "status": "OK",
                "errors": [
                    {
                        "code": "string",
                        "message": "string"
                    }
                ]
            }
        Responses [401 Forbidden]
        Responses [403 Not Found]
        Responses [404 Not Found]
        Responses [420 Method Failure]
        Responses [423 Locked]
        Responses [500 Internal Server Error]

    Args:
        prices: Словарь, содержащий id товара и цену;
        campaign_id: идентификатор кампании;
        access_token: идентификатор клиента.

    Returns:
        [result]: словарь, содержащий обновленный список тваров

    Note:
        - Обновляет цену товаров на витрине;
        - лимит: 10 000 товаров в минуту;
        - в случае ошибки будет выброшено исключение.
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"offers": prices}
    url = endpoint_url + f"campaigns/{campaign_id}/offer-prices/updates"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def get_offer_ids(campaign_id, market_token):
    """Получить артикулы товаров Яндекс маркета

    Example:
        >>> get_offer_ids(s12542, s.XXXX)
                "skus": [
                    {
                        "sku": "string",
                    }
                    ...
                ]

    Args:
        campaign_id: Идентификатор кампании;
        access_token: идентификатор клиента.

    Returns:
        [SKU]: список артикулов товаров

    Note:
        - Возвращает список SKU* товаров Яндекс маркета,
          SKU* — идентификатор товара.
    """
    page = ""
    product_list = []
    while True:
        some_prod = get_product_list(page, campaign_id, market_token)
        product_list.extend(some_prod.get("offerMappingEntries"))
        page = some_prod.get("paging").get("nextPageToken")
        if not page:
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer").get("shopSku"))
    return offer_ids


def create_stocks(watch_remnants, offer_ids, warehouse_id):
    """Создает остатки.

    Функция формирует информацию о количестве товаров в наличии,
    сверяя актуальную информацию от поставшика -
    `watch_remnants` (формирует seller.py)
    Сверка формируется на основе артикулов товаров,
    которые уже есть на сайте озон  - `offer_ids`.
    Если товар на сайте отсутствует - он будет добавлен из `watch_remnants`.

    Example:
        >>> create_stocks(watch_remnants, offer_ids, warehouse_id)
        {"offer_id": "136748",  "stock": 100, "warehouseId": 0}
        {"offer_id": "112348",  "stock": 4, "warehouseId": 0}
        {"offer_id": "112748",  "stock": 0, "warehouseId": 0}

    Args:
        offer_ids: Cписок артикулов с сайта озон;
        watch_remnants: список словарей, содержаших данные о товарах Casio;
        warehouse_id: идентификатор склада.

    Returns:
        [stocks]: Возвращается количество товаров

    Note:
        -  Словарь содержит количество товаров Cisco
    """
    # Уберем то, что не загружено в market
    stocks = list()
    date = str(datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z")
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append(
                {
                    "sku": str(watch.get("Код")),
                    "warehouseId": warehouse_id,
                    "items": [
                        {
                            "count": stock,
                            "type": "FIT",
                            "updatedAt": date,
                        }
                    ],
                }
            )
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append(
            {
                "sku": offer_id,
                "warehouseId": warehouse_id,
                "items": [
                    {
                        "count": 0,
                        "type": "FIT",
                        "updatedAt": date,
                    }
                ],
            }
        )
    return stocks


def create_prices(watch_remnants, offer_ids):
    """Создает цены.

    Функция формирует информацию о цене товаров в наличии,
    сверяя актуальную информацию от поставшика `watch_remnants` -
    `watch_remnants` (формирует seller.py)
    Сверка формируется на основе артикулов товаров,
    которые уже есть на Яндекс маркете - `offer_ids`.

    Example:
        >>> create_prices(watch_remnants, offer_ids)
            "price": {
                "value": 1110,
                "discountBase": 0,
                "currencyId": "RUR",
                "vat": 0
            }

    Args:
        offer_ids: Cписок артикулов на Яндекс маркете;
        watch_remnants: cписок словарей, содержаших данные о товарах Casio.

    Returns:
        [stocks]: Возвращается стоимость товаров

    Note:
        -  Словарь содержит стоимость товаров Cisco
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "id": str(watch.get("Код")),
                # "feed": {"id": 0},
                "price": {
                    "value": int(price_conversion(watch.get("Цена"))),
                    # "discountBase": 0,
                    "currencyId": "RUR",
                    # "vat": 0,
                },
                # "marketSku": 0,
                # "shopSku": "string",
            }
            prices.append(price)
    return prices


async def upload_prices(watch_remnants, campaign_id, market_token):
    """Загрузить список цен.

    Функция позволяет загрузить список цен Cisco в Яндекс Маркет.

    Example:
        >>> upload_prices(watch_remnants, campaign_id, market_token)

    Args:
        watch_remnants: Список цен для товаров Casio;
        campaign_id: идентификатор кампании;
        market_token: API-ключ.

    Returns:
        [prices]: возвращает стоимость товаров Casio

    Note:
        - Стоимоть товаров с учетом обновления;
        - список разделен по 500 элеметов.
    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_prices in list(divide(prices, 500)):
        update_price(some_prices, campaign_id, market_token)
    return prices


async def upload_stocks(watch_remnants, campaign_id, market_token, warehouse_id):
    """Загрузить список товаров.

    Функция позволяет загрузить список товаров Cisco в Яндекс Маркет.

    Example:
        >>> upload_stocks(watch_remnants, client_id, seller_token)

    Args:
        watch_remnants: Список цен для товаров Casio;
        campaign_id: идентификатор кампании;
        market_token: API-ключ;
        warehouse_id: идентификатор склада.

    Returns:
        [stocks]: возвращает количество товаров Casio

    Note:
        - Количество товаров с учетом обновления;
        - только при условии, что количество товаров не равно 0;
        - список разделен по 2000 элеметов.
    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    stocks = create_stocks(watch_remnants, offer_ids, warehouse_id)
    for some_stock in list(divide(stocks, 2000)):
        update_stocks(some_stock, campaign_id, market_token)
    not_empty = list(
        filter(lambda stock: (stock.get("items")[0].get("count") != 0), stocks)
    )
    return not_empty, stocks


def main():
    """Запуск функций для обновления списка товаров и цен.

    1. Функция читает переменные окружения и передает в вызываемые функции:
        - market_token (API-ключ)
        - campaign_fbs_id (идентификатор fbs)
        - campaign_dbs_id (дентификатор dbs)
        - warehouse_fbs_id (идентификатор склада fbs)
        - warehouse_dbs_id (идентификатор склада dbs)
    2. Функция обрабатывает исключения, которые могут возникнуть в процессе
       работы вызываемых функций.

    Args:
        []

    Returns:
        []

    Note:
        []

    """
    env = Env()
    market_token = env.str("MARKET_TOKEN")
    campaign_fbs_id = env.str("FBS_ID")
    campaign_dbs_id = env.str("DBS_ID")
    warehouse_fbs_id = env.str("WAREHOUSE_FBS_ID")
    warehouse_dbs_id = env.str("WAREHOUSE_DBS_ID")

    watch_remnants = download_stock()
    try:
        # FBS
        offer_ids = get_offer_ids(campaign_fbs_id, market_token)
        # Обновить остатки FBS
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_fbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_fbs_id, market_token)
        # Поменять цены FBS
        upload_prices(watch_remnants, campaign_fbs_id, market_token)

        # DBS
        offer_ids = get_offer_ids(campaign_dbs_id, market_token)
        # Обновить остатки DBS
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_dbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_dbs_id, market_token)
        # Поменять цены DBS
        upload_prices(watch_remnants, campaign_dbs_id, market_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
