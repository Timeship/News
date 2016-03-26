#!/usr/bin/env python
# coding=utf-8
import os 
import random 
from datetime import datetime
from flask import Flask,render_template,request,session,redirect,url_for,make_response
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbuser:rootpass@localhost:5432/exampledb'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

manager = Manager(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'hard to guess'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

@app.route('/',methods=['GET','POST'])
def index():
    #title = None
    form = EditForm()
    if form.validate_on_submit():
        news = News(title=form.title.data,content=form.content.data,flag=1)
        print(news)
        db.session.add(news)
        return redirect('index')
    return render_template('index.html',form=form,name=session.get('title'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@app.route('/ckupload',methods=['POST','OPTIONS','GET'])
def ckupload():
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """
<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>
"""%(callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response


class EditForm(Form):
    title = StringField('请输入新闻标题',validators=[Required()])
    content = TextAreaField('请输入新闻内容',validators=[Required()]) 
    submit = SubmitField('提交')

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    flag = db.Column(db.Integer)
    def __repr__(self):
        return '<News %r>'% self.title 






if __name__ == '__main__':
    manager.run()
