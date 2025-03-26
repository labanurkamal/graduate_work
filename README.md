# Проект Ассистент


## Стек Технология

[![FastAPI Version](https://img.shields.io/badge/FastAPI-v0.115.0-blue?logo=fastapi)](https://fastapi.tiangolo.com/release-notes/#01150)
[![Elasticsearch Version](https://img.shields.io/badge/Elasticsearch-v8.15.1-orange?logo=elasticsearch)](https://www.elastic.co/guide/en/elasticsearch/reference/current/release-notes-8.15.1.html)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-v16-blue?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/docs/release/16.0/)
[![nginx](https://img.shields.io/badge/NGINX-v1.27.4-blue?style=flat-square&logo=nginx)](https://nginx.org/ru/)
[![redis](https://img.shields.io/docker/v/_/redis?sort=semver&label=Redis&logo=Redis)](https://redis.io)
[![uvicorn](https://img.shields.io/badge/uvicorn-v0.34.0-blue?style=flat-square&logo=uvicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/Docker-v25.0.3-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![docker compose](https://img.shields.io/badge/docker%20compose-v2.24.6-blue?style=flat-square&logo=docker)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-v3.2.5-blue?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)

**Ассистент** — это интеграция голосового помощника с сервисом поиска фильмов. Проект позволяет пользователю задавать вопросы о фильмах голосом, а помощник выполняет запрос к сервису, получает данные из Elasticsearch и зачитывает результат.

## Описание проекта Foodgram

Ассистент — это голосовой помощник, интегрированный с сервисом поиска фильмов, который позволяет получать информацию о фильмах, актёрах, режиссёрах и сценаристах через голосовые команды, работающие на платформе Яндекс.Алиса.

**🔹 Основной сценарий работы:**

Пользователь голосом задаёт вопрос помощнику (Алиса, Маруся, Сири и др.).
Ассистент отправляет запрос в сервис поиска фильмов.
Сервис обращается к Elasticsearch и получает нужные данные.
Ответ возвращается помощнику, который зачитывает его пользователю.


# Голосовой помощник для поиска фильмов на платформе Яндекс.Алиса

Ассистент предоставляет информацию о фильмах, актёрах, режиссёрах и сценаристах через голосовое взаимодействие с интеграцией в сервис поиска фильмов.

## Основные возможности

### 1. Распознавание намерений и сущностей  
Проект использует машинное обучение для анализа пользовательских запросов:  
- **NER (Named Entity Recognition)** — извлечение сущностей, таких как названия фильмов и имена персон.  
- **Textcats (Text Classification)** — классификация запросов по категориям (описание фильма, рейтинг, фильмография и т. д.).  

### 2. Голосовое взаимодействие  
Процесс обработки голосовых команд:  
1. Получение запроса от пользователя в **Яндекс.Алисе**.  
2. Анализ и преобразование запроса с помощью моделей NER и Textcats.  
3. Формирование поискового запроса к **Elasticsearch**.  
4. Генерация ответа и его озвучивание голосовым движком Алисы. 

## Примеры взаимодействия

###  Описание фильма
**Запрос:**  
`«Расскажи краткое содержание фильма Интерстеллар»`

**Ответ:**  
```text
"Фильм, вдохновлённый идеями физика Кипа Торна, исследует темы выживания человечества..."
```

###  Рейтинг фильма
**Запрос:**  
`Какой рейтинг у фильма Интерстеллар?`

**Ответ:**  
```text
«Фильм Интерстеллар получил рейтинг 8.6 из 10»
```

###  Информация об актёрах
**Запрос:**
`Кто из актёров сыграл ключевого персонажа в Интерстеллар?»`

**Ответ:**  
```text
«Актеры, снявшиеся в фильме Интерстеллар, это Мэттью Макконахи, Энн Хэтэуэй: …»
```

###  Фильмография режиссёра
**Запрос:**  
`Какие фильмы снял Квентин Тарантино?`

**Ответ:**  
```text
«Режиссера Квентин Тарантино к фильмографии входит: Криминальное чтиво, Убить Билла, Бешеные псы: …»
```

###  Информация о сценаристах фильма
**Запрос:**  
`Кто сценарист фильма Интерстеллар??`

**Ответ:**  
```text
«Сценаристы, который написал сценарий фильма Интерстеллар: Кристофер Нолан: …»
```

## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```git
git clone https://github.com/labanurkamal/graduate_work
```
## Для работы с удаленным сервером:
**Выполните вход на свой удаленный сервер**
1. **Обновите репозиторий пакетов:**
   ```bash
   sudo apt update
   ```
**Установка Docker на Linux**

2. **Установите curl — консольную утилиту, которая умеет скачивать файлы по команде пользователя:**
   ```bash
   sudo apt install curl
   ```

3. **Скачайте скрипт для установки Docker с официального сайта:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh 
   ```

4. **Запустите сохранённый скрипт с правами суперпользователя:**
   ```bash
   sudo sh ./get-docker.sh 
   ```

5. **Установите Docker Compose:**
   ```bash
   sudo apt install docker-compose-plugin
   ```

6. **Проверьте, что Docker работает:**
   ```bash
   sudo systemctl status docker
   ```
## Запуск проекта в удаленном сервере:

**Скопируйте файлы docker-compose.yml и nginx.conf из директории deploy на сервер:**
   ```bash
   scp -r deploy <username>@<host>:/home/<username>/deploy
   ```
**Cоздайте .env файл и впишите:**
   ```bash
         # Postgres config
         POSTGRES_USER=<имя пользователя Postgres>
         POSTGRES_PASSWORD=<пароль для Postgres>
         POSTGRES_DB=<имя базы данных>
         POSTGRES_HOST=movies_db
         POSTGRES_PORT=<порт Postgres>
         POSTGRES_OPTIONS=<опции подключения к Postgres>
         DATABASE_TYPE=<тип базы данных>
         POSTGRES_URL=<postgresql://<имя пользователя Postgres>:<пароль для Postgres>@movies_db:<порт Postgres>/<имя базы данных>
         
         # Redis config
         REDIS_HOST=redis
         REDIS_PORT=<порт Redis>
         REDIS_PASSWORD=<пароль для Redis>
         REDIS_URL=<URL для подключения к Redis>
         
         # Elastic config
         ELASTIC_URL="http://elasticsearch:9200"
         
         # Assistant Service config
         PROJECT_NAME=<название проекта>
         PROJECT_DESCRIPTION=<описание проекта>
         CARD_TITLE=<заголовок карточки ассистента>
         CARD_DESCRIPTION=<описание ассистента>
         CARD_IMAGE_ID=<ID изображения для карточки от Яндекс Диалога>

   ```

## Сборка проекта на сервере:
   ```bash
    sudo docker compose up --build -d --remove-orphans
   ```

## Проект в интернете
Проект запущен и доступен по [адресу](https://practix.zapto.org/)