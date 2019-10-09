"""
Test cases for backend project
"""

from django.http import HttpResponse, JsonResponse


def get_request(request):
    """
    @api {get} /get_request/ Test GET Method
    @apiName GetRequest
    @apiGroup Test
    @apiVersion 0.1.0

    @apiParam {String} q Message to be appended
    @apiSuccess {String} message Success response message
    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "message": "Congrats! You hit the backend."
    }
    """
    request.encoding = 'utf-8'
    message = 'Get Message: '
    if request.GET and 'q' in request.GET:
        message += request.GET['q']

    return JsonResponse({'message': 'Congrats! You hit the backend.'})


def post_request(request):
    """
    @api {post} /post_request/ Test POST Method
    @apiName PostRequest
    @apiGroup Test
    @apiVersion 0.1.0

    @apiParam {String} q Message to be appended
    @apiSuccess {String} message Success response message
    @apiSuccessExample {text} Success-Response:
    HTTP/1.1 200 OK
    Post Message: the message you posted
    """

    message = 'Post Message: '
    if request.POST and 'q' in request.POST:
        message += request.POST['q']

    return HttpResponse(message)
