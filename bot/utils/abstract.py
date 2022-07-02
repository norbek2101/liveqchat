from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    
    @classmethod
    def get(self, *args, **kwargs):
        try:
            return self.objects.get(*args, **kwargs)
        except self.DoesNotExist:
            return False

    @classmethod
    def all(self):
        return self.objects.all()

    def get_created_at(self):
        return self.created_at.strftime("%d.%m.%Y %H:%M:%S")

    class Meta:
        abstract = True
