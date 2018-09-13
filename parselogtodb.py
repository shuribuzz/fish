import sqlite3


logs = open('./logs.txt')
list = [list.split() for list in logs]

for row in list:
    row.pop(0)
    row.pop(0)
    row.pop(2)
    row.pop(2)
    url = row[3]
    cat = url.split('/')[3]
    row.append(cat)
    product = ''
    if len(url.split('/')) > 4:
        product = url.split('/')[4]
    row.append(product)

# Создаем соединение с нашей базой данных
tesdb = sqlite3.connect('database.sqlite')

# Создаем курсор
cursor = tesdb.cursor()

# Делаем SELECT запрос к базе данных
cursor.execute("SELECT link FROM testtable")

# Делаем INSERT запрос к базе данных
for i in list:
   cursor.execute('INSERT INTO testtable VALUES (?, ?, ?, ?, ?, ?)', i)

#Cохраняем транзакцию и закрываем соединение с ДБ
tesdb.commit()
print('База данных создана')
tesdb.close()
