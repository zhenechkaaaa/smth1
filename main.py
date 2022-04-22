import requests
from flask import Flask, url_for, request, render_template, redirect
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.users import User
from data.review import Review
from resources import note_res
from forms.review import ReviewForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.signup import RegisterForm
from forms.login import LoginForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

api.add_resource(note_res.ReviewResource, '/api/reviews/<int:review_id>')
# для списка объектов
api.add_resource(note_res.ReviewListResource, '/api/reviews')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/home")
def home():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        review = db_sess.query(Review).filter(
            (Note.user == current_user) | (Review.is_private != True))
    else:
        review = db_sess.query(Review).filter(Review.is_private != True)
    return render_template('map.html', title='*название от жени*', review=review)


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


@app.route('/review/add', methods=['GET', 'POST'])
@login_required
def add_reviews():
    form = ReviewForm()
    if form.validate_on_submit():
        requests.post('http://127.0.0.1:5000/api/review', {
            'content': form.content.data,
            'is_private': form.is_private.data,
            'user_id': current_user.id})
        return redirect('/smth')
    return render_template('review.html', title='Добавление отзыва',
                           form=form)


@app.route('/review/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_news(id):
    requests.delete('http://127.0.0.1:5000/api/review/' + str(id))
    return redirect('/home')


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


if __name__ == '__main__':
    main()
    app.run(port=8000, host='127.0.0.1')
