import os
import requests
from .utils import create_image_from_base64


class StabilityAI:
    def __init__(self):
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.api_key = os.getenv('API_KEY')
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt):
        """
        Generate an image based on the provided prompt using the Stability AI API.
        :param prompt: The text prompt for image generation
        :return: Tuple (status, data), where status is a boolean indicating success,
                 and data is the image content if successful, or the error message otherwise.
        """
        body = {
            "text_prompts": [{"text": prompt}],
            "width": 1024,
            "height": 1024,
        }

        print("Generating image", prompt)

        try:
            response = requests.post(self.api_url, headers=self.headers, json=body)
            # Raises an HTTPError if the response is an error
            response.raise_for_status()
            # Else, return the response
            return True, response.json()
        except requests.exceptions.RequestException as e:
            # Handle request exceptions such as timeouts or HTTP errors
            return False, str(e)

    def save_image(self, prompt, response_data, task_id):
        """
        Save the generated image data to the Django model.

        :param prompt: The text prompt associated with the generated image
        :param image_data: The binary content of the image
        :param task_id: The task id associated with the prompt
        :return: The URL of the saved image
        
        """
        # Importing here to avoid circular imports
        from .models import GeneratedImage
        base64_image = response_data['artifacts'][0]['base64']

        # Save image to Django model for future use case
        file_name = f'{prompt.replace(" ", "_")}.png'
        image_file = create_image_from_base64(base64_image, file_name)
        image_instance, created = GeneratedImage.objects.get_or_create(
            prompt=prompt,
            defaults={'image': image_file, 'task_id': task_id}
            )
        if not created:
            # If the object already exists, update the image and task_id
            image_instance.image = image_file
            image_instance.task_id = task_id
            image_instance.save()
        return image_instance.image.url


# Create a single instance of StabilityAI to be reused
stability_ai = StabilityAI()
