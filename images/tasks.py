from celery import shared_task
from .stability_api import stability_ai
from .models import GeneratedImage
from django.urls import reverse


@shared_task(bind=True)
def generate_image_task(self, prompt):
    # Use the pre-instantiated stability_ai_instance
    success, data = stability_ai.generate_image(prompt)
    if success:
        image_url = stability_ai.save_image(prompt, data, self.request.id)
        return image_url
    else:
        print(f"Error generating image: {data}")
        return None


def check_or_create_task(prompt, base_url):
    try:
        result = GeneratedImage.objects.get(prompt=prompt)
        return prompt, f'{base_url}{reverse("task_result", args=[result.task_id])}'
    except GeneratedImage.DoesNotExist:
        # Launch Celery tasks for the prompt and store their id
        task_id = generate_image_task.delay(prompt).id
        return prompt, f'{base_url}{reverse("task_result", args=[task_id])}'