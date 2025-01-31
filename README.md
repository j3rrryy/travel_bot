# Aiogram [@Travel Agent Bot](https://t.me/TravelAgent3Bot)

<p align="center">
  <a href="https://github.com/j3rrryy/travel_bot/actions/workflows/main.yml">
    <img src="https://github.com/j3rrryy/travel_bot/actions/workflows/main.yml/badge.svg" alt="СI/CD">
  </a>
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/Python-3.12-FFD64E.svg" alt="Python 3.12">
  </a>
  <a href="https://github.com/j3rrryy/travel_bot/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
</p>

## :scroll: О боте

Бот, облегчающий планирование путешествий с друзьями. Он может помочь: не потерять важные документы, построить маршрут, найти новых друзей, поделить расходы, увидеть достопримечательности и узнать прогноз погоды на протяжении маршрута.

Бот построен на основе асинхронной библиотеки **[Aiogram](https://aiogram.dev)** для создания Telegram ботов на языке Python. При его создании был сделан упор на хорошую производительность, поэтому все операции с внешними сервисами (PostgreSQL, Redis, различные API) и файловой системой выполняются асинхронно, а все синхронные операции, которые могут быть выполнены только локально, например: отрисовка маршрута на карте и сохранение в формате фото, выполняются в отдельном процессе.

- **Обязательные функциональные возможности**

  - [x] :bust_in_silhouette: Добавление данных пользователя

  - [x] :earth_africa: Управлением путешествием

  - [x] :notebook: Заметки к путешествию

  - [x] :busts_in_silhouette: Путешествия с друзьями

  - [x] :car: Прокладывание маршрута путешествия

- **Опциональные функциональные возможности**

  - [x] :partly_sunny: Прогноз погоды в промежуточных точках

  - [x] :european_castle: Рекомендация местных достопримечательностей

  - [x] :busts_in_silhouette: Поиск пользователей для совместного путешествия

  - [x] :money_with_wings: Общие траты в путешествии

  - [x] :bulb: Ваши собственные идеи (Конвертер валют; Возврат долга в выбранной валюте; Случайный выбор участника путешествия, который платит за всех)

## :computer: Зависимости

- :whale2: Docker

## :page_facing_up: docker-compose.yml

docker-compose.yml содержит в себе:

- :file_folder: **Тома**

```yml
volumes:
  files: # том с фотографиями маршрутов и файлами пользователей
  pg_data: # том PostgreSQL
  redis_data: # том Redis
```

- :satellite: **Сервисы**

  - Бот

    ```yml
    bot:
      # сборка на основе Dockerfile
      build: .
      # перезагрузка в случае ошибки
      restart: always
      # применение миграций и запуск бота
      command: bash -c "alembic upgrade head && python bot.py"
      # открытие портов
      ports:
        - 8080:8080
      # использование файла для установки переменных окружения
      env_file:
        - .env
      # том с файлами
      volumes:
        - files:/files
      # ожидание запуска необходимых для работы контейнеров
      depends_on:
        - postgres
        - redis
      # установка имени контейнера
      container_name: travel_bot
    ```

  - PostgreSQL

    ```yml
    postgres:
      # сборка на основе легковесного alpine образа
      image: postgres:alpine
      # перезагрузка в случае ошибки
      restart: always
      # использование файла для установки переменных окружения
      env_file:
        - .env
      # том с данными
      volumes:
      - pg_data:/var/lib/postgresql/data/
      # установка имени контейнера
      container_name: postgres_bot
    ```

  - Redis

    ```yml
    redis:
      # сборка на основе легковесного alpine образа
      image: redis:alpine
      # перезагрузка в случае ошибки
      restart: always
      # запуск Redis
      command:
        - redis-server
      # использование файла для установки переменных окружения
      env_file:
        - .env
      # том с данными
      volumes:
        - redis_data:/data
      # установка имени контейнера
      container_name: redis_bot
    ```

- :hammer_and_wrench: **Начало работы**

  - Создайте Telegram бота с помощью [@BotFather](https://t.me/BotFather) и получите токен
  - Зарегистрируйтесь в [Openrouteservice](https://openrouteservice.org) и получите токен
  - Зарегистрируйтесь в [Geoapify](https://www.geoapify.com) и получите токен
  - Создайте `.env` файл с использованием шаблона `examples/.env.example`

- :rocket: **Запуск бота**

  ```shell
  docker compose up --build -d
  ```

- :x: **Остановка**

  ```shell
  docker compose stop
  ```

## :globe_with_meridians: Сервисы и внешние интеграции

- **[PostgreSQL](https://www.postgresql.org)** — надежная SQL СУБД с отличной производительностью и масштабируемостью. Все эти качества делают ее отличным выбором для высоконагруженных проектов. В боте используется в качестве основной БД. Также в проекте используется **[Alembic](https://alembic.sqlalchemy.org)** — удобный инструмент для проведения операций с миграциями и контроля их версий. В БД содержатся следующие таблицы:

  - alembic_version (служебная таблица)

  |version_num|
  |:-:|
  |pk, character varying(32), not null|

  - users

  |id|username|age|sex|latitude|longitude|city|country|currency|bio|
  |:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
  |pk, bigint, not null|character varying, not null|integer, not null|character varying, not null|double precision|double precision|character varying|character varying, not null|character varying, not null|character varying|

  - trips

  |id|username|name|description|locations|friends|
  |:-:|:-:|:-:|:-:|:-:|:-:|
  |pk, integer, not null|fk (users.username), character varying, not null|character varying, not null|character varying|json[]|character varying[]|

  - notes

  |id|user_id|trip_id|name|path|file_type|width|height|is_private|
  |:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
  |pk, integer, not null|fk (users.id), bigint, not null|fk (trips.id), integer, not null|character varying, not null|character varying, not null|character varying, not null|integer|integer|boolean|

  - expenses

  |id|username|trip_id|name|cost|currency|date|debtors|
  |:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
  |pk, integer, not null|fk (users.username), character varying, not null|fk (trips.id), integer, not null|character varying, not null|double precision|character varying, not null|timestamp without time zone, default now()|character varying[]|

- **[Redis](https://redis.io)** — масштабируемая NoSQL СУБД с потрясающей производительностью, которая хранит данные в виде пар «ключ — значение» прямо в оперативной памяти сервера, что и позволяет их быстро получать. В моем проекте используется для сохранения состояний пользователей и их промежуточных данных, кэширования.

> [!NOTE]
> **Интересный факт:** до настройки кэширования с использованием Redis среднее время ответа бота составляло около 300-350 мс, после настройки оно снизилось до 200-250 мс. Кэширование данных пользователя, а также результатов запросов к внешним сервсиам сделало бота более отзывчивым.

- **[OpenStreetMap](https://www.openstreetmap.org)** — открытая карта мира, которую могут редактировать обычные люди. В моем проекте используется для обратного геокодирования (получения города и страны из координат).

- **[Openrouteservice](https://openrouteservice.org)** — сервис для произведения различных действий с картой OpenStreetMap. В проекте используется для получения маршрута путешествия, он поддерживает построение маршрута на расстояния до 6 тыс. км, что является его огромным плюсом.

- **[Geoapify](https://www.geoapify.com)** — тоже сервис для произведения различных действий с картой OpenStreetMap. В проекте используется для нахождения достопримечательностей рядом, был выбран за удобство использования.

- **[Open-Meteo](https://open-meteo.com)** — сервис для получения прогнозов погоды с учетом множества параметров запроса. Для проекта был выбран именно он, ведь данный сервис позволяет получить погоду на целых 16 дней вперед, чего не могут вам предложить другие сервисы.

- **[Calcus.ru](https://calcus.ru)** — сервис, предоставляющий огромный набор различных калькуляторов и инструментов. В проекте используется для конвертации валют.

## :speech_balloon: Взаимодействие с ботом

> [!WARNING]
> Перед началом необходимо убедиться, что у вас в Telegram профиле указано имя пользователя в формате `@example`

- По нажатию на кнопку `/start` начинается процедура регистрации пользователя

- У бота есть боковое меню, которое содержит команды `/menu`, `/profile`, `/help`, они являются основными для взаимодействия с ботом

- `/profile` позволяет просмотреть ваш профиль и, по желанию, отредактировать его

- `/menu` бота позволяет просмотреть путешествия как созданные вами, так и те, в которые вас пригласили, они будут со значком :link:; создать новое путешествие; конвертировать валюту, которую вы указали в профиле

- В процессе создания нового путешествия вы указываете только одну локацию и даты, после создания путешествия вы сможете расширить список локаций

> [!IMPORTANT]
> Редактировать/удалять путешествия могут только их организаторы

- В разделе `Друзья` можно пригласить своих друзей, либо найти новых друзей с учетом возраста и интересов

> [!IMPORTANT]
> Добавлять/находить друзей для путешествия/удалять могут только организаторы путешествия

> [!NOTE]
> Поиск по интересам производится на основе полей `О себе` путем их сравнения и определения коэффициента подобия

- В разделе `Заметки` можно создать свою заметку, которая будет прикреплена к данному путешествию. Можно просматривать не только свои заметки, но и открытые чужие, они будут со значком :link:

> [!IMPORTANT]
> Удалять заметки могут только их создатели

- В разделе `Локации` можно создать просмотреть все локации путешествию, построить маршрут или добавить новую локацию

> [!IMPORTANT]
> Добавлять/удалять локации может только организатор путешествия

> [!NOTE]
> Первоначальная отрисовка карты с маршрутом может занимать некоторое время, после чего она будет сохранена на диск и будет загружаться оттуда. После обновления списка локаций старая карта удаляется

- В разделе `Траты` можно просмотреть, кому ты должен (со значком :heavy_exclamation_mark:)/кто тебе; можно записать новые траты и указать всех должников

> [!IMPORTANT]
> Редактировать/использовать команду с игрой/удалять траты могут только их создатели

> [!NOTE]
> Бот разделит общую сумму траты поровну на всех участников с учетом валют, указанных в их профилях. Также траты сами удаляются, когда последний должник выплачивает свою часть

> [!CAUTION]
> Использование далее описанных инструкций может сильно ударить по вашему кошельку! В выбранной трате можно сыграть в мини игру: случайным образом выбирается человек, который связан с этой тратой, это может быть как один из должников, так и тот, кто за всех заплатил, на него будут списаны все долги

## :blush: Желаю интересных и захватывающих путешествий

## :sparkling_heart: PROD contest 2024
