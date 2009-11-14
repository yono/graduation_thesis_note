# Create your views here.
# -*- coding:utf-8 -*-
from django.contrib.auth import authenticate, login
from django.template import Context, loader
from graduate.note.models import MyUser,Note, Belong
from django.http import HttpResponse
from datetime import datetime,time,timedelta
from math import fabs

def index(request):
    user_list = MyUser.objects.all()
    years = {}
    groups = {}
    for user in user_list:
        belongs = user.belong_set.all()
        for belong in belongs:
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
                    oneyear_users[-1].append(belong)
                elif group == '' and len(oneyear_users[-1]) == 0:
                    oneyear_users[-1].append(year)

        user_table.append(oneyear_users)
    
    
    t = loader.get_template('note/index.html')
    c = Context({
        'user_list': user_list,
        'year_list': year_list,
        'groups'   : groups,
        'user_table':user_table,
        })
    return HttpResponse(t.render(c))

def mylogin(request):
    if 'login_nick' in request.POST and 'login_password' in request.POST:
        username = request.POST['login_nick']
        password = request.POST['login_password']
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print '--------- login ----------'
        t = loader.get_template('note/login.html')
        c = Context({
            })
    else:
        t = loader.get_template('note/login.html')
        c = Context({
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

def user_year(request,user_nick,year):
    user = MyUser.objects.get(nick=user_nick)
    notes = Note.objects.filter(date__year=year)
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes
        })
    return HttpResponse(t.render(c))

def user_month(request,user_nick,year,month):
    user = MyUser.objects.get(nick=user_nick)
    notes = Note.objects.filter(date__year=year,date__month=month)
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes
        })
    return HttpResponse(t.render(c))

def note_new(request):
    if 'user' in request.GET:
        user = MyUser.objects.get(pk=request.GET['user'])
        now = datetime.now()
        t = loader.get_template('note/note_new.html')
        c = Context({
            'user':user,
            'date_year' :create_select_year(now),
            'date_month':create_select_month(now),
            'date_day'  :create_select_day(now),
            'date_hour' :create_select_hour(now),
            'date_min'  :create_select_min(now),
            })
        return HttpResponse(t.render(c))
    else:
        return index(request)

def note_create(request):
    if 'note_user_id' not in request.POST:
        return note_new(request) 
    else:
        user_id = request.POST['note_user_id']
        title = request.POST['note_title']
        content = request.POST['note_content']
        locate = int(request.POST['note_locate'])
        date_y = int(request.POST['note_date_y'])
        date_m = int(request.POST['note_date_m'])
        date_d = int(request.POST['note_date_d'])
        date = datetime(date_y,date_m,date_d)
        start_y = int(request.POST['note_start_y'])
        start_m = int(request.POST['note_start_m'])
        start_d = int(request.POST['note_start_d'])
        start_h = int(request.POST['note_start_h'])
        start_mi = int(request.POST['note_start_mi'])
        start = datetime(start_y,start_m,start_d,start_h,start_mi)
        end_y = int(request.POST['note_end_y'])
        end_m = int(request.POST['note_end_m'])
        end_d = int(request.POST['note_end_d'])
        end_h = int(request.POST['note_end_h'])
        end_mi = int(request.POST['note_end_mi'])
        end = datetime(end_y,end_m,end_d,end_h,end_mi)
        elapsed_time = end - start
        elapsed_min = (elapsed_time.seconds)/60
        print end, start
        print type(elapsed_min),elapsed_min
        note = Note(title=title,content=content,locate=locate,date=date,
                start=start,end=end,elapsed_time=elapsed_min,user_id=user_id)
        note.save()
        return index(request)

def note(request,user_nick,note_id,year,month):
    user = MyUser.objects.get(nick=user_nick)
    note = Note.objects.get(user=user.id)
    t = loader.get_template('note/note.html')
    c = Context({
        'user':user,
        'note':note
        })
    return HttpResponse(t.render(c))

## ノート作成用（日付など）の関数
def create_select_year(now):
    now_year = now.year
    years_num = 11
    years = []
    for i in xrange(years_num):
        years.append([now_year - 5 + i, False])
        if years[i][0] == now_year:
            years[i][1] = True
    return years

def create_select_month(now):
    now = datetime.now()
    now_month = now.month
    month_num = 12
    months = []
    for i in xrange(month_num):
        months.append([i+1, False])
        if months[i][0] == now_month:
            months[i][1] = True
    return months

def create_select_day(now):
    now_day = now.day
    day_num = 31
    days = []
    for i in xrange(day_num):
        days.append([i+1, False])
        if days[i][0] == now_day:
            days[i][1] = True
    return days

def create_select_hour(now):
    now_hour = now.hour
    hour_num = 24
    hours = []
    for i in xrange(hour_num):
        hours.append([i, False])
        if hours[i][0] == now_hour:
            hours[i][1] = True
    return hours

def create_select_min(now):
    now_min = now.minute
    min_num = 60
    mins = []
    smallest = 1000
    select_min = 0
    count = 0
    for i in xrange(0,min_num,5):
        mins.append([i, False])
        if fabs(i-now_min) < smallest:
            smallest = fabs(i-now_min)
            select_min = count
        count += 1
    mins[select_min][1] = True
    return mins
