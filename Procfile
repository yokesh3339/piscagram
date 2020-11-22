web: daphne Database.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=Database.settings -v2