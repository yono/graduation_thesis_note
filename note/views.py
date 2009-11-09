# Create your views here.
from django.template import Context, loader
from graduate.note.models import MyUser,Note
from django.http import HttpResponse

def index(request):
    user_list = MyUser.objects.all()
    t = loader.get_template('note/index.html')
    c = Context({
        'user_list': user_list,
        })
    return HttpResponse(t.render(c))
