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
    #if len(notes) == 0:
    #    notes = Note.objects.all()
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
        belong_list.append(UserTableCell('belong',grade.formalname))
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
                if belong.grade.formalname == grade:
                    users.append(belong)
            yearcolumn.append(UserTableCell('users','',users))
        user_table.append(yearcolumn)

    notes = Note.objects.all()
    tags = make_tagcloud(notes)
    
    t = loader.get_template('note/index.html')
    c = RequestContext(request,{
        'user_table':user_table,
        'tags':tags,
        })

    return HttpResponse(t.render(c))

@login_required
def home(request):
    user = User.objects.get(username=request.user)
    notes = Note.objects.filter(user=user.id).order_by('-date')
    tags = make_tagcloud(notes)
    totaltime = sum([note.elapsed_time for note in notes])
    belongs = Belong.objects.filter(user=user)
    t = loader.get_template('note/home.html')
    c = RequestContext(request,{
        'theuser':user,
        'notes':notes,
        'tags':tags,
        'totaltime':totaltime,
        'belongs':belongs,
        })
    return HttpResponse(t.render(c))

class NoteDate(object):
    def __init__(self,year,month):
        self.year  = year
        self.month = month

def get_note_month(notes):
    dates_t = {}
    for note in notes:
        year = note.date.year
        month = note.date.month
        dates_t[(year,month)] = 0
    
    dates_t = dates_t.keys()
    dates_t.sort(cmp=lambda x,y:cmp(x[0]+x[1], y[0]+y[1]),reverse=True)
    
    dates = []
    for date in dates_t:
        dates.append(NoteDate(date[0],date[1]))
    return dates

def user(request,user_nick):
    user = User.objects.get(username=user_nick)

    
    resultdict = {}
    dates = []
    if ('year' in request.GET and 'month' in request.GET) or 'year-month' in request.GET:
        if ('year' in request.GET):
            year = request.GET['year']
            month = request.GET['month']
        else:
            year,month = request.GET['year-month'].split('-')

        resultdict['year'] = year
        resultdict['month'] = month
        belong = Belong.objects.get(user=user,start__year=year)
        notes = Note.objects.filter(user__username=user_nick,date__gt=belong.start,date__lt=belong.end,date__month=month).order_by('-date')
        notes_all = Note.objects.filter(user=user.id).order_by('-date')
        dates = get_note_month(notes_all)
    elif 'year' in request.GET:
        resultdict['year'] = request.GET['year']
        belong = Belong.objects.get(user=user,start__year=request.GET['year'])
        notes = Note.objects.filter(user__username=user_nick,date__gt=belong.start,date__lt=belong.end).order_by('-date')
        notes_all = Note.objects.filter(user=user.id).order_by('-date')
        dates = get_note_month(notes_all)
    else:
        notes = Note.objects.filter(user=user.id).order_by('-date')

    tags = make_tagcloud(notes)

    belongs = Belong.objects.filter(user=user)
    totaltime = sum([note.elapsed_time for note in notes])
    resultdict.update({
            'theuser':user,
            'notes':notes,
            'tags':tags,
            'totaltime':totaltime,
            'dates':dates,
            'belongs':belongs,
            })
    t = loader.get_template('note/user.html')
    c = RequestContext(request,resultdict)
    return HttpResponse(t.render(c))

@login_required
def note_new(request):
    if 'user' in request.GET:
        user = User.objects.get(pk=request.GET['user'])
        now = datetime.now()
        t = loader.get_template('note/note_new.html')
        c = RequestContext(request,{
            'theuser':user,
            'date_year' :create_select_year(now),
            'date_month':create_select_month(now),
            'date_day'  :create_select_day(now),
            'date_hour' :create_select_hour(now),
            'date_min'  :create_select_min(now),
            })
        return HttpResponse(t.render(c))
    else:
        return index(request)

@login_required
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
        content = content.replace('\n','<br />')
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
         
        t = loader.get_template('note/note.html')
        c = RequestContext(request,{
            'theuser':note.user,
            'note':note,
            })
        return HttpResponse(t.render(c))

def note_edit(request,note_id):
    note = Note.objects.get(pk=note_id)
    now = note.date
    start = note.start
    end = note.end

    elapsed_hour = note.elapsed_time / 60
    elapsed_min  = note.elapsed_time % 60

    t = loader.get_template('note/note_edit.html')
    c = RequestContext(request,{
        'note':note,
        'theuser':user,
        'date_year'  :create_select_year(now),
        'date_month' :create_select_month(now),
        'date_day'   :create_select_day(now),
        'start_year' :create_select_year(start),
        'start_month':create_select_month(start),
        'start_day'  :create_select_day(start),
        'start_hour' :create_select_hour(start),
        'start_min'  :create_select_min(start),
        'end_year'   :create_select_year(end),
        'end_month'  :create_select_month(end),
        'end_day'    :create_select_day(end),
        'end_hour'   :create_select_hour(end),
        'end_min'    :create_select_min(end),
        'elapsed_hour':elapsed_hour,
        'elapsed_min':elapsed_min,
        })
    return HttpResponse(t.render(c))

def note_update(request,note_id):
    note = Note.objects.get(pk=note_id)
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
    elapsed_min = int(request.POST['hour']*60) + int(request.POST['min'])
    content = content.replace('\n','<br />')
    note.title = title
    note.content = content
    note.locate = locate
    note.date = date
    note.start = start
    note.end = end
    print elapsed_min
    note.elapsed_time = elapsed_min
    note.save()

    note.tag.clear()
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
    
    return HttpResponseRedirect('/note/user/%s/%d/%d/%d' %
            (note.user.username,note.date.year,note.date.month,note.id))

def note(request,user_nick,year,month,note_id):
    user = User.objects.get(username=user_nick)
    note = Note.objects.get(pk=note_id)
    t = loader.get_template('note/note.html')
    c = RequestContext(request,{
        'theuser':user,
        'note':note,
        })
    return HttpResponse(t.render(c))

def tag(request,tag_name):
    tag = Tag.objects.get(name=tag_name)
    notes = tag.note_set.all()
    t = loader.get_template('note/tag.html')
    c = RequestContext(request,{
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
