import time
import openai
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import AzureOpenAIResource

def test_openai_view(request):
    resources = AzureOpenAIResource.objects.all()
    return render(request, 'buddi/test_openai.html', {'resources': resources})

@csrf_exempt  # For testing; remove and use proper CSRF handling in production
def run_openai_test(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "output": "Invalid request method."}, status=405)

    resource_id = request.POST.get("resource_id")
    prompt = request.POST.get("prompt")

    if not resource_id or not prompt:
        return JsonResponse({"success": False, "output": "Missing resource or prompt."}, status=400)

    resource = get_object_or_404(AzureOpenAIResource, id=resource_id)

    try:
        # Set up OpenAI API configuration
        openai.api_type = "azure"
        openai.api_base = resource.endpoint
        openai.api_version = resource.api_version
        openai.api_key = resource.api_key

        start = time.time()

        # Call OpenAI API for chat completion
        response = openai.ChatCompletion.create(
            engine=resource.deployment_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )

        latency_ms = int((time.time() - start) * 1000)
        completion_text = response['choices'][0]['message']['content']

        # Success response
        return JsonResponse({
            "success": True,
            "http_status": 200,
            "latency_ms": latency_ms,
            "output": completion_text.replace("\n", "<br>"),
            "trace_id": None,  # No trace ID here since it's a successful request
            "retry_after": None,
            "internal_request_id": None,
        })

    except openai.error.OpenAIError as e:
        # Handle OpenAI-specific errors
        error_code = getattr(e, 'code', 'Unknown')
        error_message = str(e)
        http_status = getattr(e, 'http_status', 400)
        trace_id = e.headers.get('x-ms-request-id', 'N/A')  # Capture trace ID from headers
        internal_request_id = e.headers.get('x-ms-internal-request-id', 'N/A')  # Internal request ID
        retry_after = e.headers.get('Retry-After', None)  # Retry-After header in case of rate limit (429, 503)

        return JsonResponse({
            "success": False,
            "http_status": http_status,
            "error_code": error_code,
            "error_message": error_message,
            "trace_id": trace_id,
            "retry_after": retry_after,
            "internal_request_id": internal_request_id,
            "output": f"OpenAI Error: {error_message}",
        }, status=http_status)

    except requests.exceptions.RequestException as e:
        # Handle any requests-related errors
        return JsonResponse({
            "success": False,
            "output": f"Request Exception: {str(e)}",
            "http_status": 500,
            "trace_id": None,
            "retry_after": None,
            "internal_request_id": None,
        }, status=500)

    except Exception as e:
        # Catch any other unexpected errors
        return JsonResponse({
            "success": False,
            "output": f"Unexpected Error: {str(e)}",
            "http_status": 500,
            "trace_id": None,
            "retry_after": None,
            "internal_request_id": None,
        }, status=500)
