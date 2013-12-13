#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PROG_NAME
# Short description


import web
from web import form
from config import *
from os import path


######################    CONFIGURATION   ###################### 


web.config.debug = True  # Set to "False" for production site

db = web.database(dbn='sqlite', db=LIBRARY_ROOT+'metadata.db')
ebooks = LIBRARY_ROOT + '(.*)'

urls = (
    '/', 'index', 
    '/authors', 'authors', 
    '/books', 'books', 
    '/recent', 'recent',
    '/booksbyauthor', 
    'booksbyauthor', 
    '/book', 'book',
    '/login', 'login',
    '/static', 'static', # not required on nginx server?) 
    ) 




######################    FORMS   ###################### 


searchForm = form.Form(form.Textbox('search'))

loginForm = web.form.Form( web.form.Textbox('username', web.form.notnull),
        web.form.Textbox('password', web.form.notnull),
        web.form.Button('Login'),
        )



######################    WEB.PY FRAMEWORK   ###################### 
# HTTP Authentication through NGINX


class index:
    def GET(self):
        form = searchForm()
        return render.index(form)

        
    def POST(self):
        form = searchForm()
        # FORM VALIDATION MUST BE CALLED (or even a fill?)
        # see: http://bit.ly/Yx5Abg
        if not form.validates(): 
            return render.index(form)
        else:
            raise web.seeother('/books?search=True&query=%s' % form.d.search)

        
class authors:
    def GET(self):
        return render.authors(fetch.authors())

        
class books:
    def GET(self):
        query = web.input(search=False)
        if query.search == 'True':
            searchBool = True
        else:
            searchBool = False
        if searchBool:
            return render.books(fetch.search(query.query))
        else:
            return render.books(fetch.books())


class recent:
    def GET(self):
        return render.recent(fetch.recent_books(limit=15))

      
class booksbyauthor:
    def GET(self):
        # browser input = http://0.0.0.0:8080/booksbyauthor?id=88&id=87&id=84
        author = web.input(id=[])
        author.name = fetch.author_name_by_id(author.id)
        bookIds = fetch.book_id_by_author_id(author.id)
        books = fetch.books_by_id(bookIds)
        return render.booksbyauthor(books, author)


class book:
    def GET(self):
        i = web.input(id=[])
        books = fetch.books_by_id(i.id)
        comments = fetch.comment_by_id(i.id)
        return render.book(books, comments)



######################    FUNCTIONS   ###################### 


# SQL doesn't order the results based on my search params! BOO!     
def authors_link_to_books(author_sort):  
    # get authors from author_sort
    authors = author_sort.split(' & ')
    authorIds = []
    for author in authors:
        sql = db.select('authors', where="sort = $author", vars=locals()).list()
        for item in sql:
            authorIds.append(item.id)
    link = []
    for author, authorId in zip(authors, authorIds):
        link.append('<a href="/booksbyauthor?id=' + str(authorId) + '">' 
                        + clean_authors(author) + '</a>')
    return ' & '.join(link)
  

def link_to_book(id):
    sql = fetch.books_by_id(id)
    data = []
    for book in sql:
        sqlBook = db.select('data', where='book = $book.id', vars=locals()).list()
        for item in sqlBook:
            dl_path = ( SITE_ROOT + 'static/' + book.path + '/'+ item.name \
            + '.' + item.format.lower() ) # nginx doesn't like capitalized filenames
            data.append(dl_path)
    return data


def link_file_format(link):
    fileName, fileExtension = path.splitext(link)
    return fileExtension.upper().lstrip('.')


def clean_authors(author_sort):
    '''Returns a cleanly formatted string of multiple authors from author_sort'''
    authors = author_sort.split(' & ')
    authorsClean = []
    for author in authors:
         authorsClean.append(' '.join(author.split(', ')[::-1]))
    return ' & '.join(authorsClean)



######################    CLASSES   ###################### 


"id IS LIST LIKE (list of integers!)"
class fetch:
    
    # FIXME: web.py error with Sqlite datetime columns; so we ignore them,
    # but what a brute workaround!
    _BOOK_COLUMNS = 'id, title, sort, series_index, author_sort, isbn, lccn, \
                    path, flags, uuid, has_cover'
    
    @staticmethod
    def authors():
        return db.select('authors', order='sort')
    
    @staticmethod
    def books():
        return db.select('books', what=fetch._BOOK_COLUMNS, order='sort')
    
    @staticmethod
    def books_by_id(id):
        return db.select('books', what=fetch._BOOK_COLUMNS, \
                where="id IN $id", vars=locals())
    
    @staticmethod
    def book_id_by_author_id(id):
        sql = db.select('books_authors_link', what='book', \
                where="author IN $id", vars=locals()).list()
        bookIds = []
        for item in sql:
            bookIds.append(item.book)
        return bookIds
        
    @staticmethod
    def recent_books(limit=15):
        return db.select('books', what='id, sort, title, author_sort', \
                limit='$limit',  order='timestamp DESC', vars=locals())
    
    @staticmethod
    def author_name_by_id(id):
        sql = db.select('authors', where="id IN $id", vars=locals())
        authorNames = []
        for item in sql:
            authorNames.append(item.name)
        return authorNames
    
    @staticmethod   
    def comment_by_id(id):
        """Gets comments for books from ids"""
        sql = db.select('comments', where="book in $id", vars=locals())
        comments = []
        for item in sql:
            comments.append(item)
        return comments
    
    @staticmethod
    def search(searchString):
        searchString = '%'+searchString+'%'
        sql = db.select('books', what=fetch._BOOK_COLUMNS, \
                where='title LIKE $searchString \
                OR author_sort LIKE $searchString', vars=locals())
        return sql



######################    APPLICATION   ###################### 


render = web.template.render('templates/', globals={'cleanAuth':clean_authors, \
            'zip':zip, 'type':type, 'authorLink':authors_link_to_books, \
            'ebookLink':link_to_book, 'fileExt':link_file_format})       



if __name__ == "__main__":
    # Uncomment below for NGINX + WSGI website
    # web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr) #wsgi setup
    app = web.application(urls, globals())
    app.run()
