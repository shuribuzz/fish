import sqlite3
from geolite2 import geolite2
from collections import Counter
from urllib import parse
from dateutil import parser
import operator

# Создаем соединение с нашей базой данных
tesdb = sqlite3.connect('database.sqlite')

# Создаем курсор
cursor = tesdb.cursor()

# Функция нахождения наиболее часто встречающегося объекта в списке
def freq(b):
    d = {}
    m, i = 0, 0 # Максимальная частота и индекс в словаре
    for x in b: # Пробегаем в цикле исходный массив
        d[x] = d[x] + 1 if x in d else 1 # Если ключ уже есть, прибавляем 1, если нет, записываем 1
        if d[x] > m:
            m, i = d[x], x # Запоминаем максимум и его индекс

    return {i:m}

# Функция преобразования списка кортежей в список строк
def to_arr(tulp):
    arr = []
    for row in tulp:
        for x in row:
            arr.append(str(x))
    return arr


# 1.Посетители из какой страны совершают больше всего действий на сайте?
# Функция определения страны по IP через библиотеку geolite2
def country(ip):
    try:
        reader = geolite2.reader()
        get_country = reader.get(ip)
        return get_country['country']['names']['ru']
    except TypeError:
        return None
    except KeyError:
        return get_country['registered_country']['names']['ru']

def visitors():
    country_arr = []

    cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'cart?goods%' ")
    result = cursor.fetchall()

    ip_arr = to_arr(result)

    for ip in ip_arr:
        country_arr.append(country(ip))

    print('Посетители этой страны совершают больше всего действий на сайте: ' + str(freq(country_arr)))
    geolite2.close()

# 2.Посетители из какой страны чаще всего интересуются товарами из категории “fresh_fish”?
def visitorsfresh():
    country_arr = []

    cursor.execute("SELECT IP FROM testtable WHERE Category = 'fresh_fish'")

    result = cursor.fetchall()

    ip_arr = to_arr(result)

    for ip in ip_arr:
        country_arr.append(country(ip))

    print('Посетители из этой страны чаще всего интересуются товарами из категории “fresh_fish: '+ str(freq(country_arr)))

# 3.В какое время суток чаще всего просматривают категорию “frozen_fish”?
def timesofday():
    dict_timesofday = {'утро': 0, 'день': 0, 'вечер': 0, 'ночь': 0}

    cursor.execute("SELECT DateTime FROM testtable WHERE Category = 'frozen_fish'")
    result3 = cursor.fetchall()
    times_arr = to_arr(result3)

    for i in times_arr:
        dt = parser.parse(i)

        if 6 <= dt.hour <= 12 and 0 <= dt.minute <= 59:
            dict_timesofday['утро'] += 1

        if 12 <= dt.hour <= 18 and 0 <= dt.minute <= 59:
            dict_timesofday['день'] += 1

        if 18 <= dt.hour <= 0 and 0 <= dt.minute <= 59:
            dict_timesofday['вечер'] += 1

        if 0 <= dt.hour <= 6 and 0 <= dt.minute <= 59:
            dict_timesofday['ночь'] += 1

    v = list(dict_timesofday.values())
    k = list(dict_timesofday.keys())
    max_timesofday = k[v.index(max(v))]
    print("Время суток, в которое чаще всего просматривают категорию “frozen_fish”: " + str(max_timesofday))

# 4.Какое максимальное число запросов на сайт за астрономический час?
def maxnumbrequesthour():
    dict_dh = {}
    cursor.execute("SELECT DateTime FROM testtable")
    result3 = cursor.fetchall()
    times_arr = to_arr(result3)

    for dh in times_arr:
        datetimes = parser.parse(dh)
        dh = datetimes.strftime('%d:%H')

        try:
            dict_dh[dh] += 1
        except KeyError:
            dict_dh[dh] = 1

    print('Максимальное число запросов на сайт за астрономический час: ' + str(max(dict_dh.values())))

# 5.Товары из какой категории чаще всего покупают совместно с товаром из категории “semi_manufactures”?
def semi():
    semi_list = []
    frozen_list = []
    fresh_list = []
    caviar_list = []
    canned_list = []

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'cart?goods%'")
    carts = cursor.fetchall()
    carts_arr = to_arr(carts)

    for i in carts_arr:
        query_goods_id = int(parse.parse_qs(parse.urlparse(i).query)['goods_id'][0])
        query_cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]

        if 14 <= query_goods_id <= 18:
            semi_list.append(query_cart_id)
        if 1 <= query_goods_id <= 7:
            fresh_list.append(query_cart_id)
        if 8 <= query_goods_id <= 13:
            frozen_list.append(query_cart_id)
        if 19 <= query_goods_id <= 21:
            canned_list.append(query_cart_id)
        if 22 <= query_goods_id <= 24:
            caviar_list.append(query_cart_id)

    dt = dict()
    dt['frozen fish'] = 0
    dt['fresh fish'] = 0
    dt['canned food'] = 0
    dt['caviar'] = 0
    for i in semi_list:
        if i in frozen_list:
            dt['frozen fish'] += 1
        if i in fresh_list:
            dt['fresh fish'] += 1
        if i in caviar_list:
            dt['caviar'] += 1
        if i in canned_list:
            dt['canned food'] += 1

    product = max(dt.items(), key=operator.itemgetter(1))[0]

    print('Товары этой категории чаще всего покупают совместно с товаром из категории “semi_manufactures”: ' + str(product))

# 6.Сколько брошенных (не оплаченных) корзин имеется?
def unpaidcarts():
    cartid_set = set()
    payid_arr = []
    count = 0

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'cart?goods%'")
    cart = cursor.fetchall()
    cart_arr = to_arr(cart)

    for i in cart_arr:
        cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]
        cartid_set.add(cart_id)

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'pay?user%'")
    pay = cursor.fetchall()
    pay_arr = to_arr(pay)

    for i in pay_arr:
        pay_cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]
        payid_arr.append(pay_cart_id)

    for i in cartid_set:
        if i not in payid_arr:
            count += 1
    print('Количество брошенных корзин: ' + str(count))

# 7.Какое количество пользователей совершали повторные покупки?
def doublesuccesspay():
    cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'success_pay_%'")
    success_pay = cursor.fetchall()
    c = Counter(success_pay)
    arr = []
    for i in c.values():
            if i > 1:
                arr.append(i)
    print('Количество пользователей, которые совершали повторные покупки: ' + str(len(arr)))



#tesdb.close()