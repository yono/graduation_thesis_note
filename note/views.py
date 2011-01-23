# Create your views here.
# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from graduate.note.models import User,Note,Belong,Tag,Grade,Comment,Metadata,TagCloud,TagCloudNode,NoteList
from django.http import HttpResponseRedirect
from django.db.models.query import Q
from django.db import connection
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.simple import direct_to_template
from datetime import datetime
from math import fabs
import creole2html
import creole
from graduate.note.forms import NoteForm, CommentForm

# index のユーザー一覧表の各セルを表現
class UserTableCell(object):
    def __init__(self,category,content,users=[]):
        self.category = category # belong or year or user
        self.content = content # belong or year で使う
        self.users = users # user で使う。ユーザーリスト

def index(request):
    notes = Note.objects.all()
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
        form = NoteForm(initial={'user':user})
        dictionary = {
            'theuser':user,
            'form': form
        }
        return direct_to_template(request,'note/note_new.html',dictionary)
    else:
        return HttpResponseRedirect('/note/')

@login_required
@require_POST
def note_create(request):
    if 'user' not in request.POST:
        return HttpResponseRedirect('/note/note_new/')
    else:
        form = NoteForm(request.POST)
        note = form.save()
        return HttpResponseRedirect('/note/note_detail/%d/' % (note.id))

@login_required
def note_edit(request):
    note_id = request.GET['note_id']
    note = Note.objects.get(pk=note_id)
    form = NoteForm(instance=note)
    dictionary = {
        'note':note,
        'form': form,
    }
    return direct_to_template(request,'note/note_edit.html',dictionary)

@login_required
@require_POST
def note_update(request):
    note_id = request.POST['note_id']
    note = Note.objects.get(pk=note_id)
    form = NoteForm(request.POST, instance=note)
    form.save()
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

@require_POST
def post_comment(request):
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/note/note_detail/%s/' % (form.data['note']))
    else:
        return HttpResponseRedirect('/note/')

def note(request,note_id):
    note = Note.objects.get(pk=note_id)
    comments = Comment.objects.filter(note=note)
    comment_form = CommentForm(initial={'note':note.id})
    if note.text_type == 2: # wiki形式の場合
        p = creole.Parser(note.content)
        note.content = creole2html.HtmlEmitter(p.parse()).emit()
    else:
        note.content = note.content.replace('\n','<br />')
    dictionary = {'theuser':note.user, 'note':note, 'comments':comments, 'comment_form':comment_form}
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

