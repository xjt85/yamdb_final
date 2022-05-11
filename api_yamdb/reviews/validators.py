from django.core import validators
from django.utils import timezone


def validate_title_year(year):
    if 0 > year > timezone.now().year:
        raise validators.ValidationError(
            'Дата создания не может быть меньше нуля '
            'или больше текущего года!'
        )
    return year
