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

def user(request,user_nick):
    user = MyUser.objects.get(nick=user_nick)
    notes = Note.objects.filter(user=user.id)
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes
        })
    return HttpResponse(t.render(c))

def note(request,user_nick,note_id):
    user = MyUser.objects.get(nick=user_nick)
    note = Note.objects.get(user=user.id)
    t = loader.get_template('note/note.html')
    c = Context({
        'user':user,
        'note':note
        })
    return HttpResponse(t.render(c))
