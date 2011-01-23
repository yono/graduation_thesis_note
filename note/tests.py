#! -*- coding: utf-8 -*-
import unittest
import datetime
from graduate.note.models import *
from django.contrib.auth.models import User as AuthUser

from growltestrunner import GrowlTestRunner


class GradeTest(unittest.TestCase):

    def setUp(self):
        self.grade1 = Grade.objects.create(name='grade1', formalname='Grade 1', priority=100)
        self.grade2 = Grade.objects.create(name='grade2', formalname='Grade 2', priority=10)
        
    def tearDown(self):
        pass

    def test_normal(self):
        before = Grade.objects.all()
        assert self.grade1 in before
        assert self.grade2 in before

    def test_delete(self):
        self.grade1.delete()
        after = Grade.objects.all()
        assert self.grade1 not in after


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user1 = User.objects.create(
                        username='hoge',
                        first_name='first',
                        last_name='last'
                    )

    def tearDown(self):
        user = AuthUser.objects.get(username='hoge')
        user.delete()

    def test_normal(self):
        users = User.objects.all()
        assert self.user1 in users

    def test_fullname(self):
        self.assertEqual(self.user1.fullname(), 'lastfirst')
         

class BelongTest(unittest.TestCase):
    pass


class TagTest(unittest.TestCase):
    pass


class NoteTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create(username='fuga')
        self.tag1 = Tag.objects.create(name='tag1')
        self.tag2 = Tag.objects.create(name='tag2')
        self.note1 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date.today(),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note1.tag.add(self.tag1)
        self.note1.tag.add(self.tag2)

    def tearDown(self):
        user = AuthUser.objects.get(username='fuga')
        user.delete()
        self.tag1.delete()
        self.tag2.delete()

    def test_normal(self):
        notes = Note.objects.all()
        assert self.note1 in notes
    
    def test_taglist(self):
        self.assertEqual(self.note1.taglist(), 'tag1, tag2')


class CommentTest(unittest.TestCase):
    pass


class WordTest(unittest.TestCase):
    pass


class MetadataTest(unittest.TestCase):
    pass


class NoteListTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create(username='fuga')
        self.note1 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date(2010, 4, 20),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note2 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date(2009, 4, 20),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note3 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date(2010, 5, 20),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note_dates = [NoteDate(2010, 5), NoteDate(2010, 4), NoteDate(2009, 4)] 
        self.note_list = NoteList(notes=[self.note1, self.note2, self.note3])

    def tearDown(self):
        user = AuthUser.objects.get(username='fuga')
        user.delete()

    def test_sort_by_date(self):
        self.note_list.sort_by_date()
        for i, node in enumerate(self.note_list.dates):
            self.assertEqual(self.note_list.dates[i].year, self.note_dates[i].year)

    def test_compare_by_year_month(self):
        date1 = (2010, 4)
        date2 = (2010, 5)
        self.assertEqual(self.note_list._compare_by_year_month(date2, date1), 1)
        self.assertEqual(self.note_list._compare_by_year_month(date1, date2), -1)
        self.assertEqual(self.note_list._compare_by_year_month(date1, date1), 0)


class TagCloudTest(unittest.TestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(name='tag1')
        self.tag2 = Tag.objects.create(name='tag2')
        self.user = User.objects.create(username='fuga')
        self.note1 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date(2010, 4, 20),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note2 = Note.objects.create(
                        title='タイトルテスト',
                        content='内容テスト',
                        locate='場所テスト',
                        date=datetime.date(2010, 4, 20),
                        start=datetime.datetime.now(),
                        end=datetime.datetime.now(),
                        elapsed_time=10,
                        user=self.user,
                        text_type=1
                    )
        self.note1.tag.add(self.tag1)
        self.note1.tag.add(self.tag2)
        self.note2.tag.add(self.tag1)


    def tearDown(self):
        user = AuthUser.objects.get(username='fuga')
        user.delete()

    def test_get_tagcount_from_notes(self):
        tagcloud = TagCloud()
        notes = Note.objects.all()
        tagcount = tagcloud.get_tagcount_from_notes(notes)
        assert self.tag1.name in tagcount
        assert self.tag2.name in tagcount


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(NoteTest)
    GrowlTestRunner().run(suite)
