# Create your views here.
# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from graduate.note.models import User,Note,Belong,Tag,Grade,Comment,Metadata,TagCloud,TagCloudNode,NoteList
from django.http import HttpResponseRedirect
from django.db.models.query import Q
from django.db import connection
from django.views.generic.simple import direct_to_template
from datetime import datetime
from math import fabs
import creole2html
import creole

# index のユーザー一覧表の各セルを表現
class UserTableCell(object):
    def __init__(self,category,content,users=[]):
        self.category = category # belong or year or user
        self.content = content # belong or year で使う
        self.users = users # user で使う。ユーザーリスト

def index(request):
    notes = Note.objects.all()
    print notes[0].date.year
    years = {}
    grades = Grade.objects.all().order_by('-priority')

    ## 年度と所属の一覧を集める
    for user in User.objects.all():
        for belong in user.belong_set.all():
            years[belong.start.year] = 0

    year_list = years.keys()
    year_list.sort(reverse=True)

    belongs = [UserTableCell('belong','年度')]
    belongs.extend([UserTableCell('belong',g.formalname) for g in grades])
    user_table = [belongs] # ユーザー一覧表

    # 年度・所属ごとにユーザーを探す
    for year in year_list:
        yearcolumn = [UserTableCell('year',year)]
        for i in xrange(1,len(belongs)):
            grade_name = belongs[i].content
            user_belongs = Belong.objects.filter(start__year=year,
                                    grade__formalname=grade_name)
            yearcolumn.append(UserTableCell('users','',user_belongs))
        user_table.append(yearcolumn)
    
    tc = TagCloud()

    dictionary = {'user_table': user_table, 'tags': tc.nodes,}

    return direct_to_template(request,'note/index.html',dictionary)

@login_required
def home(request):
    user = User.objects.get(username=request.user)
    notes = Note.objects.filter(user=user.id).order_by('-date')\
                                             .order_by('-start')
    tc = TagCloud(notes)
    dictionary = {
        'theuser': user,
        'notes': notes,
        'tags': tc.nodes,
        'belongs': Belong.objects.filter(user=user),
    }

    return direct_to_template(request,'note/home.html',dictionary)


def user_info(request,user_nick):
    user = User.objects.get(username=user_nick)
    dictionary = {
        'theuser': user,
        'belongs': Belong.objects.filter(user=user).order_by('-start'),
    }
    return direct_to_template(request,'note/user_info.html',dictionary)

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
    # 年度と月両方が指定されてる場合
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
        notes_year.query.group_by = ['date']
        for note in notes_year:
            print note.date.year, note.date.month
        notes_l = NoteList(notes_year)
        notes_l.sort_by_date()
        dates = notes_l.dates
    elif 'year' in request.GET: # 年度のみの指定
        year = request.GET['year']
        resultdict['year'] = year
        belong = Belong.objects.get(user=user,start__year=year)
        notes = Note.objects.filter(user__username=user_nick,
                date__gt=belong.start,
                date__lt=belong.end).order_by('-date').order_by('-start')
        notes_l = NoteList(notes)
        notes_l.sort_by_date()
        dates = notes_l.dates
    else: # 指定なし
        notes = Note.objects.filter(user=user.id).order_by('-date').\
                order_by('-start')
        notes_l = NoteList(notes)
        notes_l.sort_by_date()
        dates = notes_l.dates
        

    tc = TagCloud(notes)

    belongs = Belong.objects.filter(user=user)
    dictionary = {
        'theuser':user,
        'notes':notes,
        'tags':tc.nodes,
        'dates':dates,
        'belongs':belongs,
    }
    return direct_to_template(request,'note/user.html',dictionary)

@login_required
def note_new(request):
    if 'user' in request.GET:
        user = User.objects.get(pk=request.GET['user'])
        now = datetime.now()
        dictionary = {
            'theuser':user,
            'date_year' :create_select_year(now),
            'date_month':create_select_month(now),
            'date_day'  :create_select_day(now),
            'date_hour' :create_select_hour(now),
            'date_min'  :create_select_min(now),
        }
        return direct_to_template(request,'note/note_new.html',dictionary)
    else:
        return HttpResponseRedirect('/note/')

def check_time(ftime):
    if ftime.isdigit():
        time = int(ftime)
    else:
        time = 0
    return time

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
        ## 数字が入力されてるかチェック
        hour = check_time(request.POST['hour'])
        min = check_time(request.POST['min'])
        ## 入力されてたらそのまま保存
        if (hour > 0) or (min > 0):
            elapsed_min = (hour * 60) + min
        else: ## 入力されてない場合は開始時刻と終了時刻から計算
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
                atag = tag.lstrip().rstrip()
                tag_list = Tag.objects.filter(name=atag)
                tag_obj = None
                if len(tag_list) == 0:
                    tag_obj = Tag(name=atag)
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

    dictionary = {
        'note':note,
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
    }
    return direct_to_template(request,'note/note_edit.html',dictionary)

@login_required
def note_update(request):
    note_id = request.POST['note_id']
    note = Note.objects.get(pk=note_id)
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
    ## 数字が入力されてるかチェック
    hour = check_time(request.POST['hour'])
    min = check_time(request.POST['min'])
    elapsed_min = (hour * 60) + min
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
            atag = tag.lstrip().rstrip()
            tag_list = Tag.objects.filter(name=atag)
            tag_obj = None
            if len(tag_list) == 0:
                tag_obj = Tag(name=atag)
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
    dictionary = {'note':note,}
    return direct_to_template(request,'note/note_delete.html',dictionary)

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
    comments = Comment.objects.filter(note=note)
    if note.text_type == 2: # wiki形式の場合
        p = creole.Parser(note.content)
        note.content = creole2html.HtmlEmitter(p.parse()).emit()
    else:
        note.content = note.content.replace('\n','<br />')
    dictionary = {'theuser':note.user, 'note':note, 'comments':comments,}
    return direct_to_template(request,'note/note.html',dictionary)

def tag(request):
    notes = Note.objects.all()
    tag = ''
    if 'tag' in request.GET:
        tag = Tag.objects.get(name=request.GET['tag'])
        notes = tag.note_set.all().order_by('-date')
        dictionary = {'tag':tag, 'notes':notes,}
        return direct_to_template(request,'note/tag_detail.html',dictionary)
    else:
        tc = TagCloud(notes)
        dictionary = {'tags':tc.nodes,}
        return direct_to_template(request,'note/tag.html',dictionary)


# 関連語による検索結果を表現
class RelatedWord(object):
    def __init__(self,word,ids):
        self.word = word
        self.ids = ids # ノートのリスト

"""
通常の検索と関連語検索の両方を行う
通常の検索: AND検索とNOT検索に対応
関連語検索: AND検索に対応
"""
def search(request):
    ## 通常の検索
    keywords = request.GET['keywords']
    exc = []
    fil_c = []
    fil_t = []
    ## AND検索 & NOT検索に対応
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
    fil = []
    ## AND検索に対応
    for keyword in keywords.split():
        if not keywords.startswith('-'):
            fil.append(Q(word__name=keyword))
    tmp_meta = Metadata.objects.filter(*fil).order_by('-weight')
    meta = [m for m in tmp_meta if m.note.id not in exist_notes]
    
    # メタデータ生成元の単語ごとにまとめる
    related_words_dict = {}
    for m in meta:
        if m.org.name in related_words_dict:
            related_words_dict[m.org.name].append(m)
        else:
            related_words_dict[m.org.name] = [m]
    
    related_words = [RelatedWord(k,v) for k,v in related_words_dict.items()]
    # 関連度順に降順ソート
    for i in xrange(len(related_words)):
        related_words[i].ids.sort(lambda x,y:cmp(x.weight,y.weight),reverse=True)
    related_words.sort(lambda x,y:cmp(len(x.ids),len(y.ids)),reverse=True)

    dictionary = {
        'notes':notes,
        'keywords':keywords.split(),
        'related_words':related_words,
    }
    return direct_to_template(request,'note/search.html',dictionary)

## option タグに渡す値と選択されてるかどうかのフラグ
class DateOption(object):
    def __init__(self,num,selected):
        self.num = num
        self.selected = selected

## ノート作成フォームの日付などのオプションを作成する
def create_select_year(now):
    years_num = 11
    years = []
    for i in xrange(years_num):
        years.append(DateOption(now.year - 5 + i,''))
        if years[i].num == now.year:
            years[i].selected = 'selected="selected"'
    return years

def create_select_month(now):
    month_num = 12
    months = []
    for i in xrange(month_num):
        months.append(DateOption(i+1,''))
        if months[i].num == now.month:
            months[i].selected = 'selected'
    return months

def create_select_day(now):
    day_num = 31
    days = []
    for i in xrange(day_num):
        days.append(DateOption(i+1,False))
        if days[i].num == now.day:
            days[i].selected = 'selected'
    return days

def create_select_hour(now):
    hour_num = 24
    hours = []
    for i in xrange(hour_num):
        hours.append(DateOption(i,False))
        if hours[i].num == now.hour:
            hours[i].selected = 'selected'
    return hours

def create_select_min(now):
    min_num = 60
    mins = []
    smallest = 1000
    select_min = 0
    count = 0
    for i in xrange(0,min_num,5):
        mins.append(DateOption(i,''))
        if fabs(i-now.minute) < smallest:
            smallest = fabs(i-now.minute)
            select_min = count
        count += 1
    mins[select_min].selected = 'selected'
    return mins

