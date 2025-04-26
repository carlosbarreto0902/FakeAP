from django.http import HttpResponse

# Create your views here.

def hello(request, username):
    print(username)
    return HttpResponse("<h1>¡C logró!</h1>")
def about(request):
    return HttpResponse('about')
