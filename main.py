from bs4 import BeautifulSoup
import requests
import sqlite3
import time
import telebot

# підключення до бази даних
conn = sqlite3.connect('users.db') # write path for database
main_acc = "Your account" # write id your main account

# отримання списку користувачів
users = []
cursor = conn.execute('SELECT * FROM users')
for row in cursor:
    user_chat_id = row[1]
    users.append(user_chat_id)
# закриття підключення до бази даних
conn.close()

# ініціалізація бота
bot = telebot.TeleBot(token='Your bot token') # write your bot token

sent_to_users = set()


# Функція для очищення юзерів в списку вище, якщо потрібно розпочати розсилку спочатку
@bot.message_handler(commands=['clear'])
def handle_message(message):
    global sent_to_users
    sent_to_users = set()
    return sent_to_users


# Функція для розсилки
@bot.message_handler()
def handle_message(message):
    total_messages = 0
    delivered_messages = 0
    start_time = time.time()

    # відправлення повідомлення користувачу
    for user in users:
        if delivered_messages == 1000:
            break
        if user in sent_to_users:
            continue
        try:
            bot.send_message(chat_id=user, text=message.text)
            sent_to_users.add(user)
            delivered_messages += 1
        except Exception as f:
            print(f)
        total_messages += 1
        time.sleep(0.1)

    # генерація HTML звіту
    execution_time = time.time() - start_time
    template = '''
    <html>
    <head>
      <title>Результати розсилки</title>
    </head>
    <body>
      <p>Кількість відправлених повідомлень: {total_messages}</p>
      <p>Кількість успішно доставлених повідомлень: {delivered_messages}</p>
      <p>Час виконання: {execution_time}</p>
    </body>
    </html>
    '''.format(
        total_messages=total_messages,
        delivered_messages=delivered_messages,
        execution_time=execution_time
    )
    soup = BeautifulSoup(template, 'html.parser')
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    # відправлення звіту з результатами розсилки до головного облікового запису
    url = 'https://api.telegram.org/bot{}/sendDocument'.format(bot.token)
    files = {'document': open('report.html', 'rb')}
    data = {'chat_id': main_acc}
    response = requests.post(url, files=files, data=data)


bot.polling(none_stop=True)
