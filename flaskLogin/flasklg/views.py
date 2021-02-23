from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user
from flasklg.forms import LoginForm, RegisterForm
from flasklg.models import User

bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@bp.route('/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST' and form.validate():
        user = User.select_by_email(form.email.data)
        if user and user.validate_password(form.passwoord.data):
            login_user(user)
            next = request.args.get('next')
            if not next:
                next = url_for('app.welcome')
            return redirect(next)
    return render_template('login.html', form=form)


@bp.route('/register', method=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email = form.email.data,
            username = form.username.data,
            password = form.password.data
        )
        user.add_user()
        return redirect('register.html', form=form)


@bp.route('/user')
@login_required
def user():
    return render_template('user.html')
