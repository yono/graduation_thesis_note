# Create your views here.
# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader, RequestContext
from graduate.note.models import User,Note,Belong,Tag,Grade,Comment
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.query import Q
from django.db import connection
from datetime import datetime,time,timedelta
from math import fabs
import re
import creole2html
import creole
import metadata

# タグクラウドを実現
class TagCloud(object):
    def __init__(self,tag,cssclass):
        self.tag = tag
        self.cssclass = cssclass

# タグクラウドを生成
def make_tagcloud(notes=[]):
    css_classes = ['nube1','nube2','nube3','nube4','nube5']
    tags = {}

    # O/Rマッパーを使わずSQLを直接実行して処理を高速化
    if len(notes) == 0:
        cursor = connection.cursor()
        cursor.execute('''
        select t.name,count(tg.id) from note_tag t,note_note_tag tg
        where t.id = tg.tag_id group by tg.tag_id
        ''')
        rows = cursor.fetchall()
        tags = dict(rows)

    # タグの出現回数を数える
    for note in notes:
        for tag in note.tag.all():
            tags[tag.name] = tags.get(tag.name, 0) + 1

    # タグの出現回数に応じてフォントの大きさを決定
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

# index のユーザー一覧表の各セルを表現
class UserTableCell(object):
    def __init__(self,category,content,users=[]):
        self.category = category # belong or year or user
        self.content = content # belong or year で使う
        self.users = users # user で使う。ユーザーリスト

def index(request):
    user_list = User.objects.all()
    years = {}
    grades = Grade.objects.all().order_by('-priority')

    ## 年度と所属の一覧を集める
    for user in user_list:
        belongs = user.belong_set.all()
        for belong in belongs:
            years[belong.start.year] = 0

    year_list = []
    for year in years:
        year_list.append(year)
    year_list.sort(reverse=True)

    user_table = [] # ユーザー一覧表
    belong_list = [UserTableCell('belong','年度')]
    for grade in grades:
        belong_list.append(UserTableCell('belong',grade.formalname))
    user_table.append(belong_list)

    for year in year_list: # 年度ごとに配列にまとめる
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

    tags = make_tagcloud()
    
    t = loader.get_template('note/index.html')
    c = RequestContext(request,{
        'user_table':user_table,
        'tags':tags,
        })

    return HttpResponse(t.render(c))

@login_required
def home(request):
    user = User.objects.get(username=request.user)
    notes = Note.objects.filter(user=user.id).order_by('-date').order_by('-start')
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

# Template に渡す用のクラス
class NoteDate(object):
    def __init__(self,year,month):
        self.year  = year
        self.month = month

# 年と月をソートする際の比較
def compare_year_month(x,y):
    if cmp(x[0],y[0]) != 0:
        return cmp(x[0],y[0])
    else:
        return cmp(x[1],y[1])

# ノートが存在する年と月をリスト化
def get_note_month(notes):
    dates_t = {}
    for note in notes:
        year = note.date.year
        month = note.date.month
        dates_t[(year,month)] = 0
    
    dates_t = dates_t.keys()
    dates_t.sort(compare_year_month,reverse=True)
    
    dates = []
    for date in dates_t:
        dates.append(NoteDate(date[0],date[1]))
    return dates

def user_info(request,user_nick):
    user = User.objects.get(username=user_nick)
    belongs = Belong.objects.filter(user=user).order_by('-start')
    t = loader.get_template('note/user_info.html')
    c = RequestContext(request,{
        'theuser':user,
        'belongs':belongs,
        })
    return HttpResponse(t.render(c))

"""
ユーザーごとのノートをリスト表示
年度ごとの表示
年/月ごとの表示
全てのノートの表示
に対応
"""
def user(request,user_nick):
    user = User.objects.get(username=user_nick)
    
    resultdict = {}
    dates = []
    if ('year' in request.GET and 'month' in request.GET) or\
            'year-month' in request.GET:
        if ('year' in request.GET):
            year = request.GET['year']
            month = request.GET['month']
        else:
            year,month = request.GET['year-month'].split('-')

        resultdict = {'year':year,'month':month}
        belong = Belong.objects.get(user=user,start__year=year)
        notes = Note.objects.filter(user__username=user_nick,
                date__gt=belong.start,date__lt=belong.end,
                date__month=month).order_by('-date').order_by('-start')
        notes_year = Note.objects.filter(user__username=user_nick,
                date__gt=belong.start,
                date__lt=belong.end).order_by('-date').order_by('-start')
        dates = get_note_month(notes_year)
    elif 'year' in request.GET:
        year = request.GET['year']
        resultdict['year'] = year
        belong = Belong.objects.get(user=user,start__year=year)
        notes = Note.objects.filter(user__username=user_nick,
                date__gt=belong.start,
                date__lt=belong.end).order_by('-date').order_by('-start')
        dates = get_note_month(notes)
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
        return HttpResponseRedirect('/note/')

@login_required
def note_create(request):
    if 'note_user_id' not in request.POST:
        return HttpResponseRedirect('/note/note_new/')
    else:
        user_id = request.POST['note_user_id']
        title = request.POST['note_title']
        content = request.POST['note_content']
        locate = request.POST['note_locate']
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
        hour = int(request.POST['hour'])
        min = int(request.POST['min'])
        ## 入力されてたらそのまま保存
        if (hour > 0) or (min > 0):
            elapsed_min = (hour * 60) + min
        else:
            elapsed_time = end - start
            elapsed_min = (elapsed_time.seconds)/60
        text_type = int(request.POST['note_text_type'])
        note = Note(title=title,content=content,locate=locate,date=date,
                start=start,end=end,elapsed_time=elapsed_min,user_id=user_id,
                text_type=text_type)
        note.save()

        # タグを登録
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
        
        return HttpResponseRedirect('/note/note_detail/%d/' % (note.id))

@login_required
def note_edit(request):
    note_id = request.GET['note_id']
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

@login_required
def note_update(request):
    note_id = request.POST['note_id']
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
    elapsed_min = (int(request.POST['hour'])*60) + int(request.POST['min'])
    text_type = int(request.POST['note_text_type'])
    note.title = title
    note.content = content
    note.locate = locate
    note.date = date
    note.start = start
    note.end = end
    note.elapsed_time = elapsed_min
    note.text_type = text_type
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
    
    return HttpResponseRedirect('/note/note_detail/%d/' % (note.id))

@login_required
def note_delete(request):
    note_id = request.GET['note_id']
    note = Note.objects.get(pk=note_id)
    t = loader.get_template('note/note_delete.html')
    c = RequestContext(request,{
        'theuser':user,
        'note':note,
        })
    return HttpResponse(t.render(c))

@login_required
def note_destroy(request):
    note_id = request.GET['note_id']
    note = Note.objects.get(pk=note_id)
    user = User.objects.get(pk=note.user.id)
    note.delete()

    return HttpResponseRedirect('/note/user/%s/' % (user.username))

def post_comment(request):
    if 'comment_note_id' in request.POST:
        note_id = int(request.POST['comment_note_id'])
        note = Note.objects.get(pk=note_id)
        user = note.user
        name = request.POST['comment_name']
        content = request.POST['comment_content']
        posted_date = datetime.now()
        comment = Comment(note=note,name=name,content=content,
                            posted_date=posted_date)
        comment.save()
        return HttpResponseRedirect('/note/note_detail/%d/' % (note_id))
    else:
        return HttpResponseRedirect('/note/')

def note(request,note_id):
    note = Note.objects.get(pk=note_id)
    user = note.user
    ## wiki形式の場合
    if note.text_type == 2:
        p = creole.Parser(note.content)
        note.content = creole2html.HtmlEmitter(p.parse()).emit()
    else:
        note.content = note.content.replace('\n','<br />')
    comments = Comment.objects.filter(note=note)
    t = loader.get_template('note/note.html')
    c = RequestContext(request,{
        'theuser':user,
        'note':note,
        'comments':comments,
        })
    return HttpResponse(t.render(c))

def tag(request):
    notes = Note.objects.all()
    tag = ''
    if 'tag' in request.GET:
        tag = Tag.objects.get(name=request.GET['tag'])
        notes = tag.note_set.all().order_by('-date')
        t = loader.get_template('note/tag_detail.html')
        c = RequestContext(request,{
            'tag':tag,
            'notes':notes,
            })
        return HttpResponse(t.render(c))
    else:
        tags = make_tagcloud(notes)
        t = loader.get_template('note/tag.html')
        c = RequestContext(request,{
            'tags':tags,
            })
        return HttpResponse(t.render(c))

# 関連語による検索結果を表現
class RelatedNote(object):
    def __init__(self,note,org_words):
        self.note = note
        self.org_words = org_words # 基になった単語

# 関連語による検索結果を表現
class RelatedWord(object):
    def __init__(self,word,ids):
        self.word = word
        self.ids = ids

def search(request):
    ## 通常の検索
    keywords = request.GET['keywords']
    exc = []
    fil_c = []
    fil_t = []
    for keyword in keywords.split():
        if keyword.startswith('-'):
            exc.append(Q(content__icontains=keyword[1:]))
            exc.append(Q(title__icontains=keyword[1:]))
        else:
            fil_c.append(Q(content__icontains=keyword))
            fil_t.append(Q(title__icontains=keyword))
    notes = Note.objects.filter(*fil_t) | Note.objects.filter(*fil_c)
    notes = notes.exclude(*exc).order_by('-date')
    exist_notes = dict([(note.id,0) for note in notes])

    ## 関連語検索
    m = metadata.MetaData()
    related_notes = {}
    related_note_set = set({})
    for keyword in keywords.split(): # 複数語での検索に対応(NOT検索は無視)
        related_words = m.search(keyword)
        tmp_related_notes = {}
        for id,src_word in related_words: # 基になった語をまとめる
            id = int(id)
            # 通常の検索でヒットしたページは無視
            if id not in exist_notes:
                if id in related_notes:
                    tmp_related_notes[id][src_word] = 0
                    related_notes[id][src_word] = 0
                else:
                    tmp_related_notes[id] = {src_word:0}
                    related_notes[id] = {src_word:0}
            
        # set を使ってAND演算を行う
        tmp_set = set(tmp_related_notes)
        if len(related_note_set) == 0:
            related_note_set = related_note_set.union(tmp_set)
        else:
            related_note_set = related_note_set.intersection(tmp_set)

    related_notes_list = []
    for i in related_note_set:
        note = Note.objects.get(pk=i)
        org_words = ','.join(related_notes[i].keys())
        related_notes_list.append(RelatedNote(note,org_words))

    # 基になった単語でまとめる
    related_words_dict = {}
    for i in related_note_set:
        note = Note.objects.get(pk=i)
        for word in related_notes[i].keys():
            if word in related_words_dict:
                related_words_dict[word].append(note)
            else:
                related_words_dict[word] = [note]
    
    related_words = []
    for word in related_words_dict:
        related_words.append(RelatedWord(word,related_words_dict[word]))

    related_words.sort(lambda x,y:cmp(len(x.ids),len(y.ids)),reverse=True)

    t = loader.get_template('note/search.html')
    c = RequestContext(request,{
        'notes':notes,
        'keywords':keywords.split(),
        'related_notes':related_notes_list,
        'related_words':related_words,
        })
    return HttpResponse(t.render(c))

## option タグに渡す値と選択されてるかどうかのフラグ
class DateOption(object):
    def __init__(self,num,selected):
        self.num = num
        self.selected = selected

## ノート作成用（日付など）の関数
def create_select_year(now):
    now_year = now.year
    years_num = 11
    years = []
    for i in xrange(years_num):
        years.append(DateOption(now_year - 5 + i,''))
        if years[i].num == now_year:
            years[i].selected = 'selected="selected"'
    return years

def create_select_month(now):
    now = datetime.now()
    now_month = now.month
    month_num = 12
    months = []
    for i in xrange(month_num):
        months.append(DateOption(i+1,''))
        if months[i].num == now_month:
            months[i].selected = 'selected'
    return months

def create_select_day(now):
    now_day = now.day
    day_num = 31
    days = []
    for i in xrange(day_num):
        days.append(DateOption(i+1,False))
        if days[i].num == now_day:
            days[i].selected = 'selected'
    return days

def create_select_hour(now):
    now_hour = now.hour
    hour_num = 24
    hours = []
    for i in xrange(hour_num):
        hours.append(DateOption(i,False))
        if hours[i].num == now_hour:
            hours[i].selected = 'selected'
    return hours

def create_select_min(now):
    now_min = now.minute
    min_num = 60
    mins = []
    smallest = 1000
    select_min = 0
    count = 0
    for i in xrange(0,min_num,5):
        mins.append(DateOption(i,''))
        if fabs(i-now_min) < smallest:
            smallest = fabs(i-now_min)
            select_min = count
        count += 1
    mins[select_min].selected = 'selected'
    return mins

