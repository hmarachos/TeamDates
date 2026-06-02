# Миграции

Директория используется Flask-Migrate.

Инициализация:

```bash
flask --app wsgi:app db init
flask --app wsgi:app db migrate -m "initial schema"
flask --app wsgi:app db upgrade
```

