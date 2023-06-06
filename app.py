from flask import Flask, render_template, redirect, request, session
from flask_pymongo import pymongo 
from flask_paginate import Pagination, get_page_args
from bson import ObjectId
from datetime import datetime
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

 #pripojenie na databazu
CONNECTION_STRING = 'mongodb+srv://123:123@cluster0.phsvxda.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('blog') 
article_collection = pymongo.collection.Collection(db,'article')
user_collection = pymongo.collection.Collection(db,'user')

articles = []
for article in db.articles.find():
        articles.append(article)

def get_articles(offset=0,per_page=3):
    return articles[offset:offset+per_page]

def get_page_args(page_parameter="page", per_page_parameter="per_page", default_per_page=9):
    page = int(request.args.get(page_parameter, 1))
    per_page = int(request.args.get(per_page_parameter, default_per_page))
    offset = (page - 1) * per_page
    return page, per_page, offset

@app.route("/")
def index():
    return render_template("index.html") #aby sme si v šablone html definovali dane articles


@app.route('/info/<string:id>',methods=['GET']) #info(id) - id je article
def info(id):
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        obj = article_collection.find_one({'_id': ObjectId(id)})

        id_artcl = obj.get('_id')
        title_artcl = obj.get('title')
        content_artcl = obj.get('content')

        comments = []
        comments2 = []

        if obj and 'comments' in obj:
            comments = obj['comments']
            for comment in comments:
                text = comment['comment']
                author = comment['author']
                comments2.append({'text': str(text), 'user': str(author)})
        
        print(comments)

        if(session["who"]==0):
            returnPage="/main_page_user"
            data = {'id':id_artcl, 'title': title_artcl, 'content': content_artcl, 'comments': comments2, 'returnPage':returnPage}
        else:
            returnPage="/main_page_admin"
            data = {'id':id_artcl, 'title': title_artcl, 'content': content_artcl, 'comments': comments2, 'returnPage':returnPage}
        

        return render_template('info.html', data=data)

@app.route("/add_comment/<string:id>", methods=["POST"])
def add_comment(id):
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        if request.method == "POST":
            obj = article_collection.find_one({'_id': ObjectId(id)})
            comment = request.form.get("comment")

            date = datetime.now().date()
            date_str = date.strftime('%Y-%m-%d')

            if obj and 'comments' in obj:
                comments = obj['comments']
                comments.append({'comment': comment, 'author':session['name'],'date':date_str})
                article_collection.update_one({'_id': ObjectId(id)}, {'$set': {'comments': comments}})

            title_artcl = obj.get('title')
            content_artcl = obj.get('content')

            comments = []
            comments2 = []

            if obj and 'comments' in obj:
                comments = obj['comments']
                for comment1 in comments:
                    text = comment1['comment']
                    author = comment1['author']
                    comments2.append({'text': str(text), 'user': str(author)})
    
            if(session["who"]==0):
                returnPage="/main_page_user"
                data = {'id':id, 'title': title_artcl, 'content': content_artcl, 'comments': comments2, 'returnPage':returnPage}
            else:
                returnPage="/main_page_admin"
                data = {'id':id, 'title': title_artcl, 'content': content_artcl, 'comments': comments2, 'returnPage':returnPage}
    
            return render_template('info.html', data=data)
        
#@app.route("/add_comment/<string:id>", methods=["POST"])
#def add_comment(id):
#    if session["name"] is None and session["who"] is None:
#        return redirect("/")
#    else:
#        if request.method == "POST":
#            comment = request.form["comment"]
#            comment_data = {"article": id,"user": session["name"],"text": comment}
#            article_collection.insert_one(comment_data)
#            return render_template("info.html")
#        else:
#            return render_template("info.html")

@app.route('/delete/post/<string:id>',methods=['GET'])
def delete(id):
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        article_collection.delete_one({'_id': ObjectId(id)})
        return redirect("/main_page_admin")

@app.route('/update/post/<string:id>',methods=['GET'])
def update(id):
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        obj = article_collection.find_one({'_id': ObjectId(id)})
        title = obj.get('title')
        content = obj.get('content')
        data = {'id': id,'title': title, 'content': content}
        return render_template("update.html",data=data)

@app.route('/post_submit', methods=['POST'])
def post_submit():
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        title = request.form['exampleInputName']
        content = request.form['exampleInputText']
        id = request.form['id']
        
        filter = { '_id': ObjectId(id) }
    
        # Values to be updated.
        value_name = { "$set": { 'title': title } }
        value_text = { "$set": { 'content': content } }
        print(value_name)

        # Using update_one() method for single updation.
        article_collection.update_one(filter, value_name)
        article_collection.update_one(filter, value_text)

        obj = article_collection.find_one({'_id': ObjectId(id)})
        title = obj.get('title')
        content = obj.get('content')
        data = {'id': id,'title': title, 'content': content}
        return render_template("update.html",data=data)

#page_parameter aktualna stranka
#per_page_parameter pocet kolko na stranku
#"page" a "per_page" - premenne do ktorych sa ukladaju hodnoty

@app.route("/add_article", methods=["GET", "POST"])
def add_article():
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]
            value = request.form["value"]
            date = datetime.now().date()
            date_str = date.strftime('%Y-%m-%d')
            print(date)


            article = {"title": title, "content": content,"date":date_str,"author":session["name"],"comments": [], "value": [value]}
            result = article_collection.insert_one(article)
        
            return render_template("add_article.html")
        else:
            return render_template("add_article.html")

@app.route('/delete_item', methods=['POST'])
def delete_item():
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        item_id = request.form['item_id']
        article_collection.delete_one({'_id': ObjectId(item_id)})
        return 'Item deleted successfully'

@app.route('/main_page', methods=['POST','GET'])
def main_page():
    mail = request.form["title"]
    pswd = request.form["content"]
    key="invalid"
    
    obj = user_collection.find_one({'mail':mail})

    if obj is None:
        return redirect("/")

    if obj.get("pswd")==pswd:
        key="valid"
        session["name"] = obj.get("mail")
        session["who"] = obj.get("extra")
   
    if obj is None:
        return render_template("index_none.html")
    elif session["who"] == 1 and key=="valid":
        return redirect("/main_page_admin")
    elif session["who"] == 0 and key=="valid": 
        return redirect("/main_page_user")
    elif key=="invalid":
        return redirect("/")
        

@app.route('/sign_in')
def sign_in():
    return render_template("sign_in.html")

@app.route('/sign_in_confirm', methods=['POST'])
def sign_in_confirm():
    user_mail = request.form["user_mail"]
    pswd = request.form["pswd"]
    first_name = request.form["fn"]
    last_name = request.form["ln"]
    cnct = first_name + " " + last_name

    query = {'mail': user_mail}
    result = user_collection.count_documents(query)

    if result == 0:
        user = {"mail": user_mail, "pswd": pswd, "extra": 0, "name": cnct}
        user_collection.insert_one(user)

        return render_template("sign_in.html")
    else:
        return "The user already exists"


@app.route('/log_out')
def log_out():
    session["name"] = None
    session["who"] = None
    return redirect("/")

@app.route('/main_page_admin')
def main_page_admin():
    if session.get("name") is None and session.get("who") is None:
        return redirect("/")
    else:
        global articles #info ze articles pouzity nizsie odkazuje na globalnu premennu
        articles = []
        for article in db.article.find():
            articles.append(article)
        page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page", default_per_page=6)  # parameter from URL
        total = len(articles)
        pagination_articles = get_articles(offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
        return render_template("main_page_admin.html", articles=pagination_articles, page=page, per_page=per_page, pagination=pagination)

@app.route('/main_page_user')
def main_page_user():
    if session.get("name") is None and session.get("who") is None:
        return redirect("/")
    else:
        global articles #info ze articles pouzity nizsie odkazuje na globalnu premennu
        articles = []
        for article in db.article.find():
            articles.append(article)
        page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page", default_per_page=6)  # parameter from URL
        total = len(articles)
        pagination_articles = get_articles(offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
        return render_template("main_page_user.html", articles=pagination_articles, page=page, per_page=per_page, pagination=pagination)

@app.route('/chart')
def homepage():
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        labels = [
            'February',
            'March',
            'April',
            'May'
        ]
    
        date_values = []

        objects_comments = article_collection.find({'date': {'$exists': True}})
        for doc in objects_comments:
            date_values.append(doc['date'])

        counterFebruary=0
        counterMarch=0
        counterApril=0
        counterMay=0

        for doc in date_values:
            date_obj = datetime.strptime(doc, '%Y-%m-%d')
            month = date_obj.month
            if month == 5:
                counterMay += 1
            if month == 4:
                counterApril += 1
            if month == 3:
                counterMarch += 1
            if month == 2:
                counterFebruary += 1

        data = [counterFebruary,counterMarch,counterApril,counterMay]


        if(session["who"]==0):
            returnPage="/main_page_user"
            data2 = {'returnPage':returnPage}
        else:
            returnPage="/main_page_admin"
            data2 = {'returnPage':returnPage}
    
        # Return the components to the HTML template
        return render_template(
            template_name_or_list='chartjs-example.html',
            data=data,
            labels=labels,
            data2=data2
        )
    
@app.route('/users')
def users():
    if session.get("name") is None and session.get("who") is None:
        return redirect("/")
    else:
        users = []
        for user in db.user.find():
            if 'name' in user and user['mail'] != session['name']:
            #users.append(user['name'])

                if 'name' in user and user['extra'] == 0:
                    articles = []  # List to store the articles
                    for article in db.article.find({'author': user['mail']}):
                        articles.append(article['title'])
                    user_data = {
                    '_id': str(user['_id']),  # Convert ObjectId to string
                    'name': user['name'],
                    'mail': user['mail'],
                    'articles': articles,
                    'extra': 'USER' 
                    }
                    users.append(user_data)
                    print(articles)
                else:
                    articles = []  # List to store the articles
                    for article in db.article.find({'author': user['mail']}):
                        articles.append(article['title'])
                    user_data = {
                    '_id': str(user['_id']),  # Convert ObjectId to string
                    'name': user['name'],
                    'mail': user['mail'],
                    'articles': articles,
                    'extra': 'ADMIN' 
                    }
                    users.append(user_data)
    
        return render_template('users.html', data=users)

@app.route('/delete_user/post/<string:id>',methods=['GET'])
def delete_user(id):
    if session["name"] is None and session["who"] is None:
        return redirect("/")
    else:
        user_collection.delete_one({'_id': ObjectId(id)})
        return redirect("/users")

@app.route('/update_prsn/<string:id>', methods=['GET'])
def update_prsn(id):
     if session.get("name") is None and session.get("who") is None:
        return redirect("/")
     else:
        obj = user_collection.find_one({'_id': ObjectId(id)})
        filter = { '_id': ObjectId(id) }
 
        if obj['extra']==0:
            extra = { "$set": { 'extra': 1 } }
        else:
            extra = { "$set": { 'extra': 0 } }

        user_collection.update_one(filter, extra)

        return redirect("/users")