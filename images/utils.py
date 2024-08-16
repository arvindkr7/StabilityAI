import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


def get_base_url(request):
    return request.build_absolute_uri('/')[:-1]


def create_image_from_base64(base64_data, file_name):
    # Decode the base64 image
    data = base64.b64decode(base64_data)

    # Create a ContentFile to be saved in Django's ImageField
    image_file = ContentFile(data, name=file_name)

    # Create an image from the data (optional: to validate or modify)
    image = Image.open(BytesIO(data))
    image.verify()  # Verify that it is indeed an image

    return image_file
