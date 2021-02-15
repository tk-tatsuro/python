from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, session, jsonify, json
)
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from flaskr.models.base import (
    User, PasswordResetToken, UserConnect
)
from flaskr.forms.login import (
    LoginForm, RegisterForm, ResetPasswordForm,
    ForgotPasswordForm, UserForm, ChangePasswordForm,
    UserSearchForm, ConnectForm
)
from flaskr.models.message import Message
from flaskr.models.job import Job
from flaskr.forms.message import MessageForm
from flaskr.forms.post import GetPostForm
from flaskr.forms.job import (
    GetJobForm, OutputHtmlForm
)
from flaskr.utils.message_format import make_message_format, make_old_message_format

from flaskr import db
from datetime import datetime
import requests
import logging
import constants
import settings

logger = logging.getLogger(__name__)
bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    # friends, requested_friends, requesting_friends all None
    friends = requested_friends = requesting_friends = None
    connect_form = ConnectForm()
    session['url'] = 'app.home'
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
        requesting_friends = User.select_requesting_friends()
    return render_template(
        'home.html',
        friends=friends,
        requested_friends=requested_friends,
        requesting_friends=requesting_friends,
        connect_form=connect_form
    )


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.home'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user=User.select_user_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next_link = request.args.get('next')
            if not next_link:
                next_link = url_for('app.home')
            return redirect(next_link)
        elif not user:
            flash('That user does not exist')
        elif not user.is_active:
            flash('Invalid user. Please reset your password')
        elif not user.validate_password(form.password.data):
            flash('The email address and password are incorrect')
    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ''
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        # TODO(tokume) I want to send an email.
        print(
            f'URL for password setting: http://{settings.ip}:{settings.port}/reset_password/{token}'
        )
        flash('The URL for setting the password has been sent. please confirm.')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)


@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('The password has been updated.')
        return redirect(url_for('app.login'))
    return render_template('reset_password.html', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.select_user_by_email(email)
        if user:
            with db.session.begin(subtransactions=True):
                token = PasswordResetToken.publish_token(user)
            db.session.commit()
            reset_url = f'http://{settings.ip}:{settings.port}/reset_password/{token}'
            print(reset_url)
            flash('URL for password re-registration has been issued.')
        else:
            flash('That user does not exist.')
    return render_template('forgot_password.html', form=form)


@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = user_id + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        flash('Successful update of user information!!')
    return render_template('user.html', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            db.session.commit()
        flash('Successful update of your password')
        return redirect(url_for('app.user'))
    return render_template('change_password.html', form=form)


@bp.route('/user_search', methods=['GET'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    session['url'] = 'app.user_search'
    users = None
    user_name = request.args.get('username', None, type=str)
    next_url = prev_url = None
    if user_name:
        page = request.args.get('page', 1, type=int)
        posts = User.search_by_name(user_name, page)
        next_url = url_for('app.user_search', page=posts.next_num, username=user_name) if posts.has_next else None
        prev_url = url_for('app.user_search', page=posts.prev_num, username=user_name) if posts.has_prev else None
        users = posts.items
        # check status in UserConnect table
        # from_user_id = 'MyID',　to_user_id = 'PartnerID'、status=1, I'm requesting friendship
        # to_user_id = 'MyID', from_user_id = 'PartnerID'、status=1,  The Partner is requesting friendship
        # status = 2 (friendship)
    return render_template(
        'user_search.html', form=form, connect_form=connect_form,
        users=users, next_url=next_url, prev_url=prev_url
    )


@bp.route('/connect_user', methods=['POST'])
@login_required
def connect_user():
    form = ConnectForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.connect_condition.data == 'connect':
            new_connect = UserConnect(current_user.get_id(), form.to_user_id.data)
            with db.session.begin(subtransactions=True):
                new_connect.create_new_connect()
            db.session.commit()
        elif form.connect_condition.data == 'accept':
            connect = UserConnect.select_by_from_user_id(form.to_user_id.data)
            # get UserConnect(from friend to me)
            if connect:
                with db.session.begin(subtransactions=True):
                    connect.update_status() # status 1 => 2
                db.session.commit()
    next_url = session.pop('url', 'app:home')
    return redirect(url_for(next_url))


@bp.route('/message/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    if not UserConnect.is_friend(id):
        return redirect(url_for('app.home'))
    form = MessageForm(request.form)
    # get all messages
    messages = Message.get_friend_messages(current_user.get_id(), id)
    user = User.select_user_by_id(id)
    # judge new read messages
    read_message_ids = [message.id for message in messages if (not message.is_read) and (message.from_user_id == int(id))]
    # Message check(already read and no check)
    not_checked_message_ids = [message.id for message in messages if message.is_read and (not message.is_checked) and (message.from_user_id == int(current_user.get_id()))]
    if not_checked_message_ids:
        # create transaction
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    # read_message_ids.is_read change(from False to True)
    if read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(read_message_ids)
        db.session.commit()
    if request.method == 'POST' and form.validate():
        new_message = Message(current_user.get_id(), id, form.message.data)
        with db.session.begin(subtransactions=True):
            new_message.create_message()
        db.session.commit()
        return redirect(url_for('app.message', id=id))
    # data format(to %H:%M:%S)
    for message in messages:
        message.create_at = datetime.time(message.create_at).strftime('%H:%M:%S')
    return render_template(
        'message.html', form=form,
        messages=messages, to_user_id=id,
        user=user
    )


@bp.route('/message_ajax', methods=['GET'])
@login_required
def message_ajax():
    user_id = request.args.get('user_id', -1, type=int)

    # get unread messages
    user = User.select_user_by_id(user_id)
    not_read_messages = Message.select_not_read_messages(user_id, current_user.get_id())
    not_read_message_ids = [message.id for message in not_read_messages]
    if not_read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(not_read_message_ids)
        db.session.commit()

    # get my messages that it is read and unchecked.
    not_checked_messages = Message.select_not_checked_messages(current_user.get_id(), user_id)
    not_checked_message_ids = [not_checked_message.id for not_checked_message in not_checked_messages]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    return jsonify(data=make_message_format(user, not_read_messages), checked_message_ids=not_checked_message_ids)


@bp.route('/load_old_messages', methods=['GET'])
@login_required
def load_old_messages():
    user_id = request.args.get('user_id', -1, type=int)
    offset_value = request.args.get('offset_value', -1, type=int)
    if user_id == -1 or offset_value == -1:
        return
    messages = Message.get_friend_messages(current_user.get_id(), user_id, offset_value * 100)
    user = User.select_user_by_id(user_id)
    return jsonify(data=make_old_message_format(user, messages))


@bp.route('/get_posts', methods=['GET'])
@login_required
def get_posts():
    form = GetPostForm(request.form)
    tag = request.args.get('tag', None, type=str)
    posts = None
    if tag:
        headers = {
            "Authorization": "Bearer " + settings.access_token
        }
        params = {
            "first_post_num": constants.FIRST_POST_NUM,
            "end_post_num": constants.END_POST_NUM,
        }
        try:
            # ex. https://qiita.com/api/v2/tags/python/items?page=1&per_page=50
            response = requests.get(f'https://qiita.com/api/v2/tags/{tag}/items', params=params, headers=headers)
        except requests.exceptions.RequestException as e:
            logger.error(f'action=get error={e}')
            raise
        if response.status_code == constants.STATUS_NOT_FOUND:
            posts = constants.GET_FLG['not_found']
        else:
            posts = json.loads(response.text)
    return render_template(
        'qiita.html', form=form, posts=posts
    )


@bp.route('/get_job_offers', methods=['GET'])
@login_required
def get_job_offers():
    form = GetJobForm(request.form)
    tag = request.args.get('tag', None, type=str)
    job_offers = None
    if tag:
        skill_count = Job.get_job_offers(tag)
        if skill_count:
            job_offers = json.dumps(Job.get_skill_count(skill_count), default=str)
            Job.output_html(skill_count)
            # job_offers = Job.get_graph(count_dict)
        else:
            job_offers = constants.GET_FLG['not_found']

    return render_template(
        'job_search.html', job_offers=job_offers, form=form
    )


# @bp.route('/output_html', methods=['POST'])
# @login_required
# def output_html():
#     if request.method == "POST":
#         form = GetJobForm(request.form)
#         job_offers = request.args.get('tag', None, type=str)
#     return render_template(
#         'job_search.html', job_offers=job_offers, form=form
#     )


@bp.route('/output_score', methods=['GET'])
@login_required
def output_score(job_offers):
    print(job_offers)
    form = None
    return render_template(
        'job_search.html', job_offers=job_offers, form=form
    )


@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.home'))


@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
