import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app.forms import LoginForm, RegistrationForm, MakeHomeworkForm, HomeworkLoadForm, CheckForm, LoadAvatarForm
from flask import render_template, redirect, request, url_for, send_from_directory
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.models import User
import os.path
from werkzeug.utils import secure_filename
import random
import smtplib
from email.mime.text import MIMEText  # Текст/HTML
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app.models import User, You_homework, Homeworks, Status
from config import Configuration


@app.route('/')
@app.route('/index')
@login_required
def index():
    lessons = list(set([i.lesson for i in Homeworks.query.all()]))
    posts = [
        [lesson, sorted(Homeworks.query.filter_by(lesson=lesson).all(), key=lambda date: date.timestamp, reverse=True)]
        for lesson in lessons if len(Homeworks.query.filter_by(lesson=lesson).all()) != 0 and len(
            Homeworks.query.filter_by(type='message', lesson=lesson).all()) != 0]
    status = ('admin' == current_user.status)
    return render_template('index.html', posts=posts, status=status, user=current_user)


#########################################LOGIN BLOCK###########################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        if not User.query.filter_by(delete_status='delete').first() is None:
            if form.username == User.query.filter_by(delete_status='delete').first().username:
                delete_users()
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # flash('Invalid username or password')
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/index'
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/Registration', methods=['GET', 'POST'])
def Registration():
    if current_user.is_authenticated:
        return redirect('/index')
    a = random.randint(0, 99999)
    a_hash = generate_password_hash(str(a))
    form = RegistrationForm()
    if form.validate_on_submit():
        if not User.query.filter_by(delete_status='delete').first() is None:
            if form.email == User.query.filter_by(delete_status='delete').first().email:
                delete_users()
        if Status.query.filter_by(email=form.email.data).first().access != None:
            user = User(username=form.username.data,
                        status='admin',
                        lesson=str([i for i in Status.query.all() if i.email == form.email.data][0]),
                        delete_status='delete',
                        email=form.email.data)
            user.set_password(form.password.data)
        else:
            user = User(username=form.username.data,
                        delete_status='delete',
                        email=form.email.data)
            user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_email(form.email.data, 'Проверка email', 'Код - {}'.format(a))
        return redirect('/check_email/{}/{}'.format(a_hash, form.username.data))
    return render_template('Registration.html', form=form)


@app.route('/check_email/<code>/<login>', methods=['GET', 'POST'])
def check_email(code, login):
    form = CheckForm()
    if form.validate_on_submit():
        if check_password_hash(str(code), str(form.code.data)):
            db.session.query(User).filter_by(username=login).update({User.delete_status: 'success'},
                                                                    synchronize_session=False)
            db.session.commit()
            return redirect('/login')
        delete_users()
        return redirect('/Registration')
    return render_template('check.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


##########################################HOMEWORK BLOCK######################################################

@app.route('/uploads/<filename>/<directory>', methods=['GET', 'POST'])
@login_required
def uploads(filename, directory):
    if os.path.splitext(filename)[1] not in Configuration.ALLOWED_EXTENSIONS_PHOTO:
        return send_from_directory('static', str(os.path.splitext(filename)[1].split('.')[1]) + ".png" if os.path.exists(
            './app/static/' + str(os.path.splitext(filename)[1].split('.')[1]) + '.png') else 'unknown_file.png')
    return send_from_directory(directory, filename)


@app.route('/upload/<filename>/<directory>', methods=['GET', 'POST'])
@login_required
def upload(filename, directory):
    return send_from_directory(directory, filename)


@app.route('/homework_load/<number>', methods=['GET', 'POST'])
@login_required
def homework_load(number):
    form = HomeworkLoadForm()
    if admin_check():
        if form.validate_on_submit():
            try:
                filename = secure_filename(form.files.data.filename)
                try:
                    filex = max([os.path.splitext(i)[0] for i in os.listdir('./app/files/')])
                    form.files.data.save(
                        os.path.join('./app/files', str(int(filex) + 1) + os.path.splitext(filename)[1]))
                    f = str(int(filex) + 1) + os.path.splitext(filename)[1]
                except:
                    form.files.data.save(os.path.join('./app/files', '0' + os.path.splitext(filename)[1]))
                    f = '0' + os.path.splitext(filename)[1]
                new_HW = You_homework(
                    number=number,
                    body=form.comments.data,
                    user_id=current_user.id,
                    files=f
                )
            except:
                new_HW = You_homework(
                    number=number,
                    body=form.comments.data,
                    user_id=current_user.id,
                )
            db.session.add(new_HW)
            db.session.commit()
            return redirect('/homework/{}'.format(number))
        return render_template('homework_load.html', form=form)
    return redirect('/homework/{}'.format(number))


@app.route('/homework/<number>', methods=['GET', 'POST'])
@login_required
def homework(number):
    if not admin_check():
        students = [[i.username, False if You_homework.query.filter_by(user_id=i.id).first() == None else True] for i in
                    User.query.filter_by(status=None)]
        return render_template('homework_for_teacher.html', number=str(number), students=students)
    hws = sorted(You_homework.query.filter_by(number=number).all(), key=lambda date: date.timestamp, reverse=True)
    return render_template('homework.html', user_id=current_user.id, hws=hws,
                           yhw=Homeworks.query.filter_by(number=number).first())


@app.route('/homework_student/<number>', methods=['GET', 'POST'])
@login_required
def homework_student(number):
    return render_template('homework.html', number=str(number), hw=Homeworks.query.filter_by(number=number).first(),
                           a=True if not admin_check() else False)


@app.route('/make_homework/<homework>', methods=['GET', 'POST'])
@login_required
def make_homework(homework):
    if admin_check():
        return redirect('/login')
    form = MakeHomeworkForm()
    if form.validate_on_submit():
        try:
            filename = secure_filename(form.files.data.filename)
            try:
                filex = max([os.path.splitext(i)[0] for i in os.listdir('./app/files/')])
                form.files.data.save(os.path.join('./app/files', str(int(filex) + 1) + os.path.splitext(filename)[1]))
                f = str(int(filex) + 1) + os.path.splitext(filename)[1]
            except:
                form.files.data.save(os.path.join('./app/files', '0' + os.path.splitext(filename)[1]))
                f = '0' + os.path.splitext(filename)[1]
            new_HW = Homeworks(
                number=form.number.data,
                lesson=current_user.lesson,
                comments=form.comments.data,
                type='homework' if homework == 'homework' else 'message',
                files=f
            )
        except:
            new_HW = Homeworks(
                number=form.number.data,
                type='homework' if homework == 'homework' else 'message',
                lesson=current_user.lesson,
                comments=form.comments.data,
            )
        db.session.add(new_HW)
        db.session.commit()
        return redirect('/')
    return render_template('make_homework.html', form=form)


@app.route('/delete_homework/<number>', methods=['GET', 'POST'])
@login_required
def delete_homework(number):
    try:
        if admin_check() or current_user.lesson != Homeworks.query.filter_by(number=number).first().lesson:
            return redirect('/login')
    except:
        return redirect('/login')
    try:
        os.remove(os.path.join('./app/files/', Homeworks.query.filter_by(number=str(number)).first().files))
    except:
        pass
    db.session.query(Homeworks).filter_by(number=str(number)).delete()
    db.session.commit()
    return redirect('/index')


######################################USER BLOCK################################################################
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    photo = False
    avatar = None
    if current_user.avatar is not None:
        avatar = User.query.filter_by(username=current_user.username).first().avatar
        photo = True
    lessons = list(set([i.lesson for i in Homeworks.query.all()]))
    posts = [
        [lesson, sorted(Homeworks.query.filter_by(lesson=lesson).all(), key=lambda date: date.timestamp, reverse=True)]
        for lesson in lessons]
    status = ('admin' == current_user.status)
    return render_template('user.html', posts=posts, avatar=avatar, status=status, user=current_user, photo=photo)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Configuration.ALLOWED_EXTENSIONS


@app.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    form = LoadAvatarForm()
    if form.files.data and allowed_file(form.files.data.filename):
        filename = secure_filename(form.files.data.filename)
        try:
            os.remove('./app/files/{}'.format(current_user.avatar))
        except:
            pass
        try:
            filex = max([os.path.splitext(i)[0] for i in os.listdir('./app/files/')])
            form.files.data.save(os.path.join('./app/files', str(int(filex) + 1) + os.path.splitext(filename)[1]))
            f = str(int(filex) + 1) + os.path.splitext(filename)[1]
        except:
            form.files.data.save(os.path.join('./app/files', '0' + os.path.splitext(filename)[1]))
            f = '0' + os.path.splitext(filename)[1]
        db.session.query(User).filter_by(username=current_user.username).update({User.avatar: f},
                                                                                synchronize_session=False)
        db.session.commit()
        return redirect('/user')
    return render_template('change_avatar.html', form=form)


######################################Funck################################################################
def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        posts = [['Алгебра', ['№135', '№345', '№222']],
                 ['Геометрия', ['№335', '№545', '№112']],
                 ['Русский язык', ['Упражнение 200', 'Упражнение 195']],
                 ['Литература', ['Доклад', 'Сочинение по произведению Сенька', 'стр.52 №1,2,3']]]
        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + first_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            new_user = User(
                username=first_names[i],
                email=tmp_email
            )
            new_user.set_password(tmp_pass)
            db.session.add(new_user)

        for i in posts:
            for q in i[1]:
                a = random.randint(18, 31)
                new_HW = Homeworks(
                    type='homework',
                    number=q,
                    lesson=i[0],
                    comments='Сделать до {} мая'.format(a),
                )
                db.session.add(new_HW)

        db.session.commit()
    return


def admin_check():
    if current_user.status == 'admin':
        return False
    return True


def make_folders(path):
    if not os.path.exists(path):
        try:
            os.makedirs(os.path.dirname(path))
        except:
            return make_folders(os.path.dirname(path))
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass


def delete_users():
    User.query.filter_by(delete_status='delete').delete()
    db.session.commit()


def send_email(addr_to, msg_subj, msg_text):
    addr_from = "andreishahmatoff@yandex.ru"  # Отправитель
    password = "sau2006"  # Пароль

    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = addr_to  # Получатель
    msg['Subject'] = msg_subj  # Тема сообщения

    body = msg_text  # Текст сообщения
    msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)  # Создаем объект SMTP
    # server.starttls()                                  # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()  # Выходим
