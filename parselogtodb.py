import sqlite3


logs = open('./logs.txt')
list = [list.split() for list in logs]

for row in list:
    del row[0:2]
    datetime = row[0] + ' ' + row[1]
    row.insert(0, datetime)
    del row[1:5]
    url = row[2]
    cat = url.split('/')[3]
    row.append(cat)
    product = ''
    if len(url.split('/')) > 4:
        product = url.split('/')[4]
    row.append(product)

#print(list)

# Создаем соединение с нашей базой данных
tesdb = sqlite3.connect('database.sqlite')

# Создаем курсор
cursor = tesdb.cursor()

# Делаем SELECT запрос к базе данных
cursor.execute("SELECT link FROM testtable")

# Делаем INSERT запрос к базе данных
for i in list:
   cursor.execute('INSERT INTO testtable VALUES (?, ?, ?, ?, ?)', i)

#Cохраняем транзакцию и закрываем соединение с ДБ
tesdb.commit()
print('База данных создана')
tesdb.close()
