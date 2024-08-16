
from django.http import JsonResponse
from celery.result import AsyncResult
from .utils import get_base_url
from concurrent.futures import ThreadPoolExecutor, as_completed
from .tasks import check_or_create_task


def generate_images(request):
    """
    View to generate images based on comma-separated prompts.
    :param request: The incoming HTTP request
    :return: JSON response with each prompt and its  URL task or an error message
    """
    # prompts: Comma-separated list of prompts from the URL
    prompts = request.GET.get('prompts', '').strip()

    # Check if prompts is empty
    if not prompts:
        return JsonResponse({'error': 'Please provide a prompts in query params'}, status=400)

    # Split the prompts by comma and strip any whitespace
    prompt_list = [prompt.strip() for prompt in prompts.split(',')]

    if not prompt_list:
        return JsonResponse({'error': 'No valid prompts provided'}, status=400)

    base_url = get_base_url(request)

    # Simplest way to run the celery tasks
    # results = {prompt: f'{base_url}/image/result/{generate.delay(prompt).id}' for prompt in prompt_list}

    # using below approach to check if prompt exists in the db
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Create a mapping of prompts to futures
        future_to_prompt = {executor.submit(check_or_create_task, prompt, base_url): prompt for prompt in prompt_list}

        for future in as_completed(future_to_prompt):
            prompt = future_to_prompt[future]
            try:
                prompt, url = future.result()
                results[prompt] = url
            except Exception as e:
                # Handle exceptions here
                results[prompt] = str(e)

    return JsonResponse(results)


def check_task_status(request, task_id=None):
    if not task_id:
        return JsonResponse({'error': 'Task ID not provided'}, status=400)

    result = AsyncResult(task_id)

    if result.state == 'SUCCESS':
        task_result = result.result
        if task_result:
            image_url = f'{get_base_url(request)}{task_result}'
            return JsonResponse({'status': 'Completed', 'image_url': image_url}, status=200)
        else:
            return JsonResponse({'status': 'Failed', 'error': 'No image URL returned'})
    else:
        return JsonResponse({'status': result.state, 'result': result.result})
