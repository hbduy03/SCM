# Trong views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.ai_models.vision_models import GlobalImageClassifier

# Khởi tạo model (Toàn cục)
ai_classifier = GlobalImageClassifier()


@csrf_exempt  # Hoặc bạn có thể gửi CSRF token từ JS (khuyên dùng cách có Token bên dưới)
def api_auto_fill_product(request):
    """API nhận file ảnh và trả về tên sản phẩm"""
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']

        result = ai_classifier.predict_from_file_object(uploaded_file)

        return JsonResponse(result)

    return JsonResponse({'success': False, 'error': 'No image provided'})