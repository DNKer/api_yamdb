import csv
import os
import sqlite3

from django.conf import settings
from django.core.management import BaseCommand


prj_dir = os.path.abspath(os.path.curdir)
a = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base_name = 'db.sqlite3'
connect = sqlite3.connect(prj_dir + '/' + base_name)
cursor = connect.cursor()

cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_category (id int, name text, slug text)')#категория
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_genre (id int, name text, slug text)') #жанр
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_title_genre (id int, title_id int, genre_id int)') #жанртитул
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_review (id int, title_id int, text text, author int, score int, pub_date datetime)') #ревью
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_title (id int, name text, year int, category int)') #произведение
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_user (id int, username text, email text, role text, bio text, first_name text, last_name text)') #пользоват
cursor.execute(f'CREATE TABLE IF NOT EXISTS reviews_comment(id int, review_id int, text text, author int, pub_date datetime)') #комментарии


class Command(BaseCommand):
    def handle(self, *args, **options):
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        script_dir = settings.BASE_DIR
        with open(
                os.path.join(script_dir, 'static/data/users.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin, delimiter=',')
            to_db = [(
                i['id'],
                i['username'],
                i['email'],
                i['role'],
                i['bio'],
                i['first_name'],
                i['last_name']) for i in dr]
        cur.executemany('INSERT INTO reviews_user'
                        '(id, username, email, role,'
                        'bio, first_name, last_name)'
                        'VALUES (?, ?, ?, ?, ?, ?, ?);', to_db)
        con.commit()
        print('Запись успешно вставлена в таблицу reviews_user ', cur.rowcount)

        with open(
                os.path.join(script_dir, 'static/data/category.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['name'],
                 i['slug']) for i in dr]
        cur.executemany('INSERT INTO reviews_category'
                        '(id, name, slug)'
                        'VALUES (?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_category ',
            cur.rowcount
        )

        with open(
                os.path.join(script_dir, 'static/data/genre.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['name'],
                 i['slug']) for i in dr]
        cur.executemany('INSERT INTO reviews_genre'
                        '(id, name, slug)'
                        'VALUES (?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_genre ', cur.rowcount
        )

        with open(
                os.path.join(script_dir, 'static/data/titles.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['name'],
                 i['year']) for i in dr]
        cur.executemany('INSERT INTO reviews_title'
                        '(id, name, year)'
                        'VALUES (?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_title ', cur.rowcount
        )

        with open(
                os.path.join(script_dir, 'static/data/review.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['title_id'],
                 i['text'],
                 i['author'],
                 i['score'],
                 i['pub_date']) for i in dr]
        cur.executemany('INSERT INTO reviews_review'
                        '(id, title_id, text, author, score, pub_date)'
                        'VALUES (?, ?, ?, ?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_review ', cur.rowcount
        )

        with open(
                os.path.join(script_dir, 'static/data/comments.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['review_id'],
                 i['text'],
                 i['author'],
                 i['pub_date']) for i in dr]
        cur.executemany('INSERT INTO reviews_comment'
                        '(id, review_id, text, author, pub_date)'
                        'VALUES (?, ?, ?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_comment ', cur.rowcount
        )

        with open(
                os.path.join(script_dir, 'static/data/genre_title.csv'),
                'r',
                encoding='utf-8'
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i['id'],
                 i['title_id'],
                 i['genre_id']) for i in dr]
        cur.executemany('INSERT INTO reviews_title_genre'
                        '(id, title_id, genre_id)'
                        'VALUES (?, ?, ?);', to_db)
        con.commit()
        print(
            'Запись успешно вставлена в таблицу reviews_title_genre ',
            cur.rowcount
        )

        con.close()