from django.contrib.postgres import fields as postgres_fields
from django.db import models


class Contract(models.Model):
    period = postgres_fields.DateRangeField(help_text='N.B.: End date is the day after the actual end date')
