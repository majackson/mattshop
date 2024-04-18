from django.http import HttpResponse


def heartbeat(request):
    """Just a simple view that returns an HTTP response"""
    return HttpResponse()

