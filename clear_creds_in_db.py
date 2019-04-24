from api import models

models.Credentials.objects.all().delete()
print(models.Credentials.objects.all().values())