# Продаем рыбу

![alt text](fish.png)

### Описание
Телеграм бот, который предназначен для продажи продукции, в данном случае рыбы.
Бот делает следующее:
- Отображает список имеющихся продуктов
- Отображает информацию по конкретному продукту:
   - Название
   - Описание 
   - Изображение
   - Стоимость за кг продукции
   - Объем общей имеющейся продукции в кг
- Позволяет добавить конкретный товар в корзину
- Отображает корзину с подробной информацией по каждому товару

![alt text](bot.gif)


### Как запустить
Для запуска на своем компьютере вам потребуется:

1. Свежая версия [Python](https://www.python.org).
2. Сохранить библиотеку на свой компьютер:
```
git clone https://github.com/inkvizitor1991/fish-shop.git
``` 
3. Установить зависимости:
```
pip install -r requirements.txt
``` 
4. Создать аккаунт на [moltin](https://www.elasticpath.com/). 
5. Добавить продукты в [catalog](https://euwest.cm.elasticpath.com/legacy-catalog).
6. Заполнить переменные окружения.
7. Запустить телеграмм бот:
```
python tg_shop.py
```
### Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны следующие переменные:
- `TG_BOT_TOKEN` — токен телеграм бота. Создать бота и получить токен можно у [BotFather](https://telegram.me/BotFather), для этого необходимо ввести `/start` и следовать инструкции.
- `REDIS_DATABASE_PASSWORD` — пароль от вашей базы данных, заведите базу данных на [redis](https://redis.com/).
- `REDIS_PORT` — порт от вашей базы данных [redis](https://redis.com/).
- `REDIS_HOST` — адрес от вашей базы данных [redis](https://redis.com/).
- `CLIENT_ID` — находится на главной странице [moltin](https://euwest.cm.elasticpath.com/), необходим единожды для создания `ACCESS_TOKEN`.
- `ACCESS_TOKEN` — токен автоверификации. В файле: `requests_to_moltin.py`, вызовите функцию create_token, она сгенерирует вам токен. Убедитесь что `CLIENT_ID` заполнен.
