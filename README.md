# Проект "YaMDb"

![example workflow](https://github.com/xjt85/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

>Учебный проект в рамках курса __Python-developer__ на платформе __Яндекс.Практикум__

Проект __YaMDb__ собирает отзывы (Review) пользователей о произведениях (Titles).

### О проекте:
Произведения в проекте не хранятся.
Нельзя посмотреть фильм или послушать музыку.

Произведения разделены на категории (Category):   
«Книги», «Фильмы», «Музыка».  

_Список категорий  может быть расширен администратором._

Произведению может быть присвоен жанр (Genre) из списка предустановленных:  
- «Сказка»,
- «Рок»
- «Артхаус».

_Новые жанры может создавать только администратор._

Пользователи могут оставлять к произведениям текстовые отзывы (Review) и  
ставить произведению оценку в диапазоне от одного до десяти (целое число).

На одно произведение пользователь может оставить только один отзыв.

Для аутентификации используются JWT-токены.  
У неаутентифицированных пользователей доступ к API только на чтение.  
Аутентифицированным пользователям разрешено создание, изменение и удаление своего отзыва;  
в остальных случаях доступ предоставляется только для чтения.

### Технологии:
- django 2.2.16

Модели: User, Category, Genre, Title, Review, Comment

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone ссылка на репозиторий
cd api_yamdb
```

### В папке /infra/ cоздать .env-файл по следующему шаблону:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=<имя базы данных>
POSTGRES_USER=<логин для подключения к базе данных>
POSTGRES_PASSWORD=<пароль для подключения к БД>
DB_HOST=<название сервиса (контейнера), например "db">
DB_PORT=<номер порта для подключения к БД>
```
### команды для запуска приложения в контейнерах:
```
cd infra
docker-compose up -d --build

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

### команды для заполнения базы данными.
```
dddd
```

### Примеры запросов к API

Запрос на получение списка категорий:

```
http://api/v1/categories/
```

Запрос на получение списка жанров
```
http://api/v1/genres/
```

### Разработчик проекта


Роман Чуклинов
