import time
import openai
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
        openai.api_type = "azure"
        openai.api_base = resource.endpoint
        openai.api_version = resource.api_version
        openai.api_key = resource.api_key

        start = time.time()

        response = openai.ChatCompletion.create(
            engine=resource.deployment_id,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        latency_ms = int((time.time() - start) * 1000)
        completion_text = response['choices'][0]['message']['content']

        return JsonResponse({
            "success": True,
            "http_status": 200,
            "latency_ms": latency_ms,
            "output": completion_text.replace("\n", "<br>")
        })

    except openai.error.OpenAIError as e:
        return JsonResponse({
            "success": False,
            "http_status": getattr(e, 'http_status', 'Unknown'),
            "output": f"OpenAI Error: {str(e)}"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "output": f"Unexpected Error: {str(e)}"
        }, status=500)
