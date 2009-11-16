# Create your views here.
# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader, RequestContext
from graduate.note.models import User,Note,Belong,Tag,Grade
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime,time,timedelta
from math import fabs

class TagCloud(object):
    def __init__(self,tag,cssclass):
        self.tag = tag
        self.cssclass = cssclass

def make_tagcloud(notes=[]):
    css_classes = ['nube1','nube2','nube3','nube4','nube5']
    tags = {}
    if len(notes) == 0:
        notes = Note.objects.all()
    for note in notes:
        for tag in note.tag.all():
            tags[tag.name] = tags.get(tag.name, 0) + 1

    fontmax = -1000
    fontmin = 1000
    for tag_num in tags.values():
        fontmax = max(fontmax, tag_num)
        fontmin = min(fontmin, tag_num)
    
    divisor = ((fontmax-fontmin) / len(css_classes)) + 1

    result = []
    for tag,num in tags.items():
        result.append(TagCloud(tag,css_classes[(num-fontmin)/divisor]))
    return result

class UserTableCell(object):
    def __init__(self,category,content,users=[]):
        self.category = category
        self.content = content
        self.users = users

def index(request):
    user_list = User.objects.all()
    years = {}
    grades = Grade.objects.all().order_by('-priority')

    ## 年度と所属の一覧を集める
    for user in user_list:
        belongs = user.belong_set.all()
        for belong in belongs:
            years[belong.start.year] = 0
            #grades[belong.grade.name] = 0

    year_list = []
    for year in years:
        year_list.append(year)
    year_list.sort(reverse=True)

    user_table = []
    belong_list = [UserTableCell('belong','年度')]
    for grade in grades:
        belong_list.append(UserTableCell('belong',grade.name))
    user_table.append(belong_list)

    for year in year_list:
        oneyear_list = Belong.objects.filter(start__year=year)
        yearcolumn = [UserTableCell('year',year)]
        for grade_list in belong_list:
            grade = grade_list.content
            if grade == '年度':
                continue
            users = []
            for belong in oneyear_list:
                if belong.grade.name == grade:
                    users.append(belong)
            yearcolumn.append(UserTableCell('users','',users))
        user_table.append(yearcolumn)

    notes = Note.objects.all()
    tags = make_tagcloud(notes)
    
    t = loader.get_template('note/index.html')
    c = Context({
        'user_table':user_table,
        'tags':tags,
        })

    return HttpResponse(t.render(c))

@login_required
def profile(request):
    user = User.objects.get(username=request.user)
    notes = Note.objects.filter(user=user.id).order_by('-date')
    tags = make_tagcloud(notes)
    totaltime = sum([note.elapsed_time for note in notes])
    t = loader.get_template('note/profile.html')
    c = Context({
        'user':user,
        'notes':notes,
        'tags':tags,
        'totaltime':totaltime,
        })
    return HttpResponse(t.render(c))

def user(request,user_nick):
    user = User.objects.get(username=user_nick)
    notes = Note.objects.filter(user=user.id).order_by('-date')
    tags = make_tagcloud(notes)
    totaltime = sum([note.elapsed_time for note in notes])
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes,
        'tags':tags,
        'totaltime':totaltime,
        })
    return HttpResponse(t.render(c))

def user_year(request,user_nick,year):
    user = User.objects.get(username=user_nick)
    notes = Note.objects.filter(user__username=user_nick,date__year=year)
    tags = make_tagcloud(notes)
    totaltime = sum([note.elapsed_time for note in notes])
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes,
        'tags':tags,
        'totaltime':totaltime,
        'year':year,
        })
    return HttpResponse(t.render(c))

def user_month(request,user_nick,year,month):
    user = User.objects.get(username=user_nick)
    notes = Note.objects.filter(user__username=user_nick,
            date__year=year,date__month=month)
    tags = make_tagcloud(notes)
    totaltime = sum([note.elapsed_time for note in notes])
    t = loader.get_template('note/user.html')
    c = Context({
        'user':user,
        'notes':notes,
        'tags':tags,
        'totaltime':totaltime,
        })
    return HttpResponse(t.render(c))

def note_new(request):
    if 'user' in request.GET:
        user = User.objects.get(pk=request.GET['user'])
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
        note = Note(title=title,content=content,locate=locate,date=date,
                start=start,end=end,elapsed_time=elapsed_min,user_id=user_id)
        note.save()

        if request.POST['note_tag_list'] != '':
            tags = request.POST['note_tag_list'].split(',')
            for tag in tags:
                tag_list = Tag.objects.filter(name=tag)
                tag_obj = None
                if len(tag_list) == 0:
                    tag_obj = Tag(name=tag)
                    tag_obj.save()
                else:
                    tag_obj = tag_list[0]
                note.tag.add(tag_obj) 
            note.save()

        return index(request)

def note(request,user_nick,note_id,year,month):
    user = User.objects.get(username=user_nick)
    note = Note.objects.get(pk=note_id)
    t = loader.get_template('note/note.html')
    c = Context({
        'user':user,
        'note':note,
        })
    return HttpResponse(t.render(c))

def tag(request,tag_name):
    tag = Tag.objects.get(name=tag_name)
    notes = tag.note_set.all()
    t = loader.get_template('note/tag.html')
    c = Context({
        'tag':tag,
        'notes':notes,
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
