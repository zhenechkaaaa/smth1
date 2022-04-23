import requests
from flask import Flask, url_for, request, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource

from forms.signup import RegisterForm
from forms.login import LoginForm
from forms.note import NoteForm
from data import db_session
from data.users import User
from data.notes import Note
from resources import user_res, note_res

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# для одного объекта
api.add_resource(note_res.NoteResource, '/api/notes/<int:note_id>')

# для списка объектов
api.add_resource(note_res.NoteListResource, '/api/notes')

# для одного объекта
api.add_resource(user_res.UserResource, '/api/users/<int:user_id>')

# для списка объектов
api.add_resource(user_res.UserListResource, '/api/users')


@app.route("/")
@app.route("/home")
def home():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        notes = db_sess.query(Note).filter(
            (Note.user == current_user) | (Note.is_private != True))
    else:
        notes = db_sess.query(Note).filter(Note.is_private != True)
    return render_template('map.html', notes=notes, title='*какое-то крутое название*')


@app.route('/signup', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('signup.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('signup.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('signup.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/note/add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NoteForm()
    if form.validate_on_submit():
        requests.post('http://127.0.0.1:8080/api/notes', {
            'title': form.title.data,
            'content': form.content.data,
            'is_private': form.is_private.data,
            'user_id': current_user.id
        })
        return redirect('/home')
    return render_template('news.html', title='Добавление отзыва',
                           form=form)


@app.route('/note/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_news(id):
    requests.delete('http://127.0.0.1:8080/api/notes/' + str(id))
    return redirect('/home')


@app.route('/note/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_news(note_id):
    form = NoteForm()
    if form.validate_on_submit():
        requests.put('http://127.0.0.1:8080/api/notes/' + str(note_id),
                     {
                         'title': form.title.data,
                         'content': form.content.data,
                         'is_private': form.is_private.data,
                         'user_id': current_user.id
                     }
                     )
        return redirect('/home')
    return render_template('news.html', title='Изменение отзыва',
                           form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/home")


@app.route("/smth")
def cool():
    return render_template('cool.html', title='Добро пожаловать!')


def main():
    db_session.global_init("db/spb.db")
    db_sess = db_session.create_session()
    db_sess.commit()

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
