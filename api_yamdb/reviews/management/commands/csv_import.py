"""Иморт данных.

Для импорта данных выполните команду:
 python manage.py import
 --path "./api_yamdb/static/data/users.csv"
 --model_name "reviews.User"
"""
import csv

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help_cmd = 'Импорт данных из файлов CSV в БД'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='путь к файлу CSV')
        parser.add_argument('model', type=str, help='имя модели')

    def handle(self, *args, **options):
        file_path = options['path']
        model = apps.get_model(options['model'])

        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file, delimiter=',')
            header = reader.__next__()
            for row in reader:
                data = {key: value for key, value in zip(header, row)}
                try:
                    model.objects.create(**data)
                except IntegrityError as err:
                    line = ', '.join(row)
                    self.stdout.write(f'Error! {err}, "{line}"')
