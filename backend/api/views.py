"""
Test cases for backend project
"""

from django.http import HttpResponse, JsonResponse


def get_request(request):
    """get request"""

    request.encoding = 'utf-8'
    message = 'Get Message: '
    if request.GET and 'q' in request.GET:
        message += request.GET['q']

    return JsonResponse({'message': 'Congrats! You hit the backend.'})


def post_request(request):
    """post request"""

    message = 'Post Message: '
    if request.POST and 'q' in request.POST:
        message += request.POST['q']

    return HttpResponse(message)
