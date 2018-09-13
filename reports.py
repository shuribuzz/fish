import sqlite3
from collections import Counter

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

# 1.Посетители из какой страны совершают больше всего действий на сайте?
def visitors():
    cursor.execute("SELECT IP FROM testtable")
    result1 = cursor.fetchall()
    print('Посетители этой страны совершают больше всего действий на сайте: '+ str(freq(result1)))


# 2.Посетители из какой страны чаще всего интересуются товарами из категории “fresh_fish”?
def visitorsfresh():
    cursor.execute("SELECT IP FROM testtable WHERE Category = 'fresh_fish'")
    result2 = cursor.fetchall()
    print('Посетители из этой страны чаще всего интересуются товарами из категории “fresh_fish: '+ str(freq(result2)))


# 3.В какое время суток чаще всего просматривают категорию “frozen_fish”?
def timesofday():
    cursor.execute("SELECT Time FROM testtable WHERE Category = 'frozen_fish'")
    result3 = cursor.fetchall()
    print(freq(result3))


# 4.Какое максимальное число запросов на сайт за астрономический час
#  (c 00 минут 00 секунд до 59 минут 59 секунд)?

# 5.Товары из какой категории чаще всего покупают совместно с товаром из категории “semi_manufactures”?
'''
# 6.Сколько брошенных (не оплаченных) корзин имеется?
cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'cart?goods%'")
cart = cursor.fetchall()
cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'success_pay%'")
pay = cursor.fetchall()
unpaid = len(cart)-len(pay)
print('Количество брошенных корзин: '+ str(unpaid))
'''

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

'''
##################### 6
cartIP_arr = []
cartgoods_arr = []

cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'cart?goods%'")
cartIP_tulpe = cursor.fetchall()

for row in cartIP_tulpe:
    for x in row:
        cartIP_arr.append(str(x))

for i in cartIP_arr:
    cursor.execute("SELECT Category FROM testtable WHERE IP=:IP", {"IP": i})
    cartgoods = cursor.fetchall()
    cartgoods_arr.append(cartgoods)

counts = [sum(1 for a, in array if a.startswith("cart?goods")) for array in cartgoods_arr]

print(len(cartIP_arr))
print(Counter(cartIP_arr))
print(len(counts))


payIP_arr = []
paygoods_arr = []

cursor.execute("SELECT IP FROM testtable WHERE Category LIKE 'success_pay%'")
payIP_tulpe = cursor.fetchall()

for row in payIP_tulpe:
    for x in row:
        payIP_arr.append(str(x))

for i in payIP_arr:
    cursor.execute("SELECT Category FROM testtable WHERE IP=:IP", {"IP": i})
    paygoods = cursor.fetchall()
    paygoods_arr.append(paygoods)

counts = [sum(1 for a, in array if a.startswith("success_pay")) for array in paygoods_arr]

print(len(payIP_arr))
print(Counter(payIP_arr))
print(len(counts))
'''
################################
#tesdb.close()