import sqlite3
from geolite2 import geolite2
from collections import Counter
from urllib import parse
from dateutil import parser

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
def to_list(tulp):
    list = []
    for row in tulp:
        for x in row:
            list.append(str(x))
    return list


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

def popularcountry():
    country_list = []

    cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'cart?goods%' ")
    ip_tulpe = cursor.fetchall()

    ip_list = to_list(ip_tulpe)

    for ip in ip_list:
        country_list.append(country(ip))

    print('Посетители этой страны совершают больше всего действий на сайте: ' + str(freq(country_list)))
    geolite2.close()

# 2.Посетители из какой страны чаще всего интересуются товарами из категории “fresh_fish”?
def popularcountryfresh():
    country_list = []

    cursor.execute("SELECT IP FROM testtable WHERE Category = 'fresh_fish'")

    ip_tulpe = cursor.fetchall()

    ip_list = to_list(ip_tulpe)

    for ip in ip_list:
        country_list.append(country(ip))

    print('Посетители из этой страны чаще всего интересуются товарами из категории “fresh_fish: '+ str(freq(country_list)))

# 3.В какое время суток чаще всего просматривают категорию “frozen_fish”?
def timesofday():
    timesofday_dict = {'утро': 0, 'день': 0, 'вечер': 0, 'ночь': 0}

    cursor.execute("SELECT DateTime FROM testtable WHERE Category = 'frozen_fish'")
    times_tulpe = cursor.fetchall()
    times_list = to_list(times_tulpe)

    for i in times_list:
        dt = parser.parse(i)

        if 6 <= dt.hour <= 12 and 0 <= dt.minute <= 59:
            timesofday_dict['утро'] += 1

        if 12 <= dt.hour <= 18 and 0 <= dt.minute <= 59:
            timesofday_dict['день'] += 1

        if 18 <= dt.hour <= 0 and 0 <= dt.minute <= 59:
            timesofday_dict['вечер'] += 1

        if 0 <= dt.hour <= 6 and 0 <= dt.minute <= 59:
            timesofday_dict['ночь'] += 1

    v = list(timesofday_dict.values())
    k = list(timesofday_dict.keys())
    max_timesofday = k[v.index(max(v))]
    print("Время суток, в которое чаще всего просматривают категорию “frozen_fish”: " + str(max_timesofday))

# 4.Какое максимальное число запросов на сайт за астрономический час?
def maxnumrequesthour():
    dayhour_dict = {}
    cursor.execute("SELECT DateTime FROM testtable")
    times_tulpe = cursor.fetchall()
    times_list = to_list(times_tulpe)

    for i in times_list:
        datetimes = parser.parse(i)
        i = datetimes.strftime('%d:%H')

        try:
            dayhour_dict[i] += 1
        except KeyError:
            dayhour_dict[i] = 1

    print('Максимальное число запросов на сайт за астрономический час: ' + str(max(dayhour_dict.values())))


# 5.Товары из какой категории чаще всего покупают совместно с товаром из категории “semi_manufactures”?
def semi():
    semi_manufactures_list = []
    frozen_fish_list = []
    fresh_fish_list = []
    caviar_list = []
    canned_food_list = []
    count_category_dict = {'frozen fish': 0, 'fresh fish': 0, 'canned food': 0, 'caviar': 0}

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'cart?goods%'")
    carts_tulpe = cursor.fetchall()
    carts_list = to_list(carts_tulpe)

    for i in carts_list:
        product_id = int(parse.parse_qs(parse.urlparse(i).query)['goods_id'][0])
        cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]

        if 1 <= product_id <= 7:
            fresh_fish_list.append(cart_id)
        if 8 <= product_id <= 13:
            frozen_fish_list.append(cart_id)
        if 14 <= product_id <= 18:
            semi_manufactures_list.append(cart_id)
        if 19 <= product_id <= 21:
            canned_food_list.append(cart_id)
        if 22 <= product_id <= 24:
            caviar_list.append(cart_id)

    for i in semi_manufactures_list:
        if i in frozen_fish_list:
            count_category_dict['frozen fish'] += 1
        if i in fresh_fish_list:
            count_category_dict['fresh fish'] += 1
        if i in caviar_list:
            count_category_dict['caviar'] += 1
        if i in canned_food_list:
            count_category_dict['canned food'] += 1

    v = list(count_category_dict.values())
    k = list(count_category_dict.keys())
    category = k[v.index(max(v))]

    print('Товары этой категории чаще всего покупают совместно с товаром из категории “semi_manufactures”: ' + str(
        category))

# 6.Сколько брошенных (не оплаченных) корзин имеется?
def unpaidcarts():
    cartid_set = set()
    payid_list = []
    count = 0

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'cart?goods%'")
    cart_tulpe = cursor.fetchall()
    cart_list = to_list(cart_tulpe)

    for i in cart_list:
        cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]
        cartid_set.add(cart_id)

    cursor.execute("SELECT Category FROM testtable WHERE Category LIKE 'pay?user%'")
    pay = cursor.fetchall()
    pay_list = to_list(pay)

    for i in pay_list:
        pay_cart_id = parse.parse_qs(parse.urlparse(i).query)['cart_id'][0]
        payid_list.append(pay_cart_id)

    for i in cartid_set:
        if i not in payid_list:
            count += 1
    print('Количество брошенных корзин: ' + str(count))

# 7.Какое количество пользователей совершали повторные покупки?
def doublesuccesspay():
    cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'success_pay_%'")
    successpay_tulpe = cursor.fetchall()
    c = Counter(successpay_tulpe)
    doublesuccesspay_list = []
    for i in c.values():
            if i > 1:
                doublesuccesspay_list.append(i)
    print('Количество пользователей, которые совершали повторные покупки: ' + str(len(doublesuccesspay_list)))



#tesdb.close()