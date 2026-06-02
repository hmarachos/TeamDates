# Birthday Reminder

Корпоративное Flask-приложение для ведения справочника сотрудников и автоматической рассылки уведомлений о днях рождения.

## Возможности

- CRUD сотрудников с поиском, фильтрацией, сортировкой и пагинацией.
- CRUD получателей уведомлений с проверкой email и включением/отключением рассылки.
- Dashboard со статистикой и ближайшими днями рождения за 30 дней.
- Ежемесячная рассылка 25 числа о днях рождения следующего месяца.
- Ежедневная рассылка о днях рождения текущего дня.
- HTML и plain text письма, адаптированные для корпоративной почты и Outlook.
- Журнал отправленных уведомлений.
- Импорт и экспорт сотрудников через Excel `.xlsx`.
- Авторизация администратора через Flask-Login.
- CSRF-защита, валидация форм, безопасная загрузка файлов.
- Логирование в `logs/app.log` через `RotatingFileHandler`.
- Docker и Docker Compose.

## Установка

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env`: задайте `SECRET_KEY`, SMTP-параметры, `ADMIN_USERNAME` и `ADMIN_PASSWORD`.

## Инициализация базы

```bash
flask --app wsgi:app db init
flask --app wsgi:app db migrate -m "initial schema"
flask --app wsgi:app db upgrade
flask --app wsgi:app create-admin
```

Для локальной разработки можно создать таблицы напрямую:

```bash
flask --app wsgi:app init-db
flask --app wsgi:app create-admin
```

Команда `init-db` создает отсутствующие таблицы без удаления существующих данных.

## Запуск

```bash
flask --app wsgi:app run --host 0.0.0.0 --port 5002
```

Production-запуск:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app
```

Откройте `http://localhost:5000` и войдите под администратором.

## Docker

```bash
docker compose up --build -d
docker compose exec flask-app flask --app wsgi:app db upgrade
docker compose exec flask-app flask --app wsgi:app create-admin
```

SQLite хранится в volume `sqlite_data`, логи пишутся в `./logs`.

## Excel

Импорт поддерживает `.xlsx` со строго заданными колонками:

```text
Наименование предприятия
ФИО
Должность
Подразделение
Дата рождения
```

Дата рождения принимается как Excel-дата, `ДД.ММ.ГГГГ` или `ГГГГ-ММ-ДД`.

## Резервное копирование базы

Для локального запуска:

```bash
cp instance/birthdays.db backups/birthdays_$(date +%Y%m%d_%H%M).db
```

Для Docker:

```bash
docker run --rm -v birthday-reminder_sqlite_data:/data -v "$PWD/backups:/backups" alpine \
  cp /data/birthdays.db /backups/birthdays_$(date +%Y%m%d_%H%M).db
```

## Обновление приложения

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi:app db upgrade
sudo systemctl restart birthday-reminder
```

Для Docker:

```bash
git pull
docker compose up --build -d
docker compose exec flask-app flask --app wsgi:app db upgrade
```

## Тесты

```bash
pytest
```

`pytest.ini` включает отчет покрытия для слоев `services`, `repositories`, `models`.
