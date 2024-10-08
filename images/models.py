from django.db import models


class GeneratedImage(models.Model):
    prompt = models.CharField(max_length=255)
    image = models.ImageField(upload_to='generated_images/')
    task_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prompt
