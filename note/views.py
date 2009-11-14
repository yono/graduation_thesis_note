# Create your views here.
from django.template import Context, loader
from graduate.note.models import MyUser,Note, Belong
from django.http import HttpResponse

def index(request):
    user_list = MyUser.objects.all()
    years = {}
    groups = {}
    for user in user_list:
        belongs = user.belong_set.all()
        for belong in belongs:
            print belong.start.year,belong.group.name
            years[belong.start.year] = 0
            groups[belong.group.name] = 0
    year_list = []
    for year in years:
        year_list.append(year)
    year_list.sort(reverse=True)
    belong_list = []
    user_table = []
    belong_list.insert(0, [''])
    for group in groups:
        belong_list.append([group])
    user_table.append(belong_list)
    for year in year_list:
        oneyear_list = Belong.objects.filter(start__year=year)
        oneyear_users = []
        for group_list in belong_list:
            group = group_list[0]
            oneyear_users.append([])
            for belong in oneyear_list:
                if belong.group.name == group:
                    oneyear_users[-1].append(belong.myuser)
                elif group == '' and len(oneyear_users[-1]) == 0:
                    oneyear_users[-1].append(year)

        user_table.append(oneyear_users)
    
    for i in user_table:
        print i

    
    t = loader.get_template('note/index.html')
    c = Context({
        'user_list': user_list,
        'year_list': year_list,
        'groups'   : groups,
        'user_table':user_table,
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

def note_form(request,user_nick):
    user = MyUser.objects.get(nick=user_nick)
    t = loader.get_template('note/note_form.html')
    c = Context({
        'user':user,
        })
    return HttpResponse(t.render(c))
