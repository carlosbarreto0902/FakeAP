from django.http import HttpResponse

# Create your views here.

def hello(request, username):
    print(username)
    return HttpResponse("<h1>¡Segundo pull request!</h1>")
def about(request):
    return HttpResponse('about')
