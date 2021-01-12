from django.db import models

# Create your models here.

class DeviceSoftware(models.Model):
    typ_choices = [
        ('FM', 'Firmware'),
        ('AP', 'Application Software'),
        ('MN', 'Monitoring Software'),
        ('OS', 'Operating System')
    ]
    typ = models.CharField(max_length = 10, verbose_name = 'Type', choices = typ_choices)
    major_version = models.CharField(max_length = 5, verbose_name = 'Major Version')
    minor_version = models.CharField(max_length = 5, verbose_name = 'Minor Version')
    

class Device(models.Model):
    device_id = models.CharField(max_length = 50, primary_key = True, verbose_name = 'Device Id', help_text = 'The unique id by which this device would be identified')
    make = models.CharField(max_length = 30)
    model = models.CharField(max_length = 50)
    online = models.BooleanField()
