import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app.forms import LoginForm, RegistrationForm, MakeHomeworkForm, HomeworkLoadForm, CheckForm
from flask import render_template, redirect, request, url_for, send_from_directory
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.models import User
import os.path
from werkzeug.utils import secure_filename

from app.models import User, You_homework, Homeworks, Status

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = Homeworks.query.all()
    posts = [[i.number, i.lesson] for i in posts]
    status = ('admin' == current_user.status)
    return render_template('index.html', posts=posts, status=status)


#########################################LOGIN BLOCK###########################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    delete_users()
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
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
    import random
    import smtplib
    from email.mime.text import MIMEText  # Текст/HTML
    from email.mime.multipart import MIMEMultipart
    delete_users()
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

    if current_user.is_authenticated:
        return redirect('/index')
    a = random.randint(0, 99999)
    a_hash = generate_password_hash(str(a))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
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
        except:
            return redirect('/Registration')
    return render_template('Registration.html', form=form)

@app.route('/check_email/<kod>/<login>/', methods=['GET', 'POST'])
def check_email(kod, login):
    form = CheckForm()
    if form.validate_on_submit():
        if check_password_hash(str(kod), str(form.kod.data)):
            db.session.query(User).filter_by(username=login).update({User.delete_status: 'success'}, synchronize_session=False)
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


############################################################################################################

@app.route('/uploads/<filename>', methods=['GET', 'POST'])
@login_required
def uploads(filename):
    return send_from_directory('files', filename)


@app.route('/homework_load/<number>', methods=['GET', 'POST'])
@login_required
def homework_load(number):
    form = HomeworkLoadForm()
    if admin_check():
        if form.validate_on_submit():
            filename = secure_filename(form.files.data.filename)
            make_folders('./app/files/Users/{}/{}/'.format(str(current_user), str(number)))
            form.files.data.save(os.path.join('./app/files/Users/{}/{}/'.format(str(current_user), str(number)), filename))

            new_HW = You_homework(
                number=number,
                body=form.comments.data,
                timestamp=datetime.datetime.utcnow(),
                user_id=current_user.id,
                files=os.path.join('./app/files/Users/{}/{}/'.format(str(current_user), str(number)), filename)
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
        students = [[i, False if You_homework.query.filter_by(user_id=i.id).first() == None else True] for i in User.query.filter_by(status=None)]
        return render_template('homework_for_teacher.html', number=str(number), students=students)
    return render_template('homework.html', number=str(number), hw=Homeworks.query.filter_by(number=number).first())


@app.route('/make_homework', methods=['GET', 'POST'])
@login_required
def make_homework():
    if admin_check():
        return redirect('/login')
    form = MakeHomeworkForm()
    if form.validate_on_submit():
        filename = secure_filename(form.files.data.filename)

        form.files.data.save(os.path.join('./app/files/Homeworks/', filename))

        new_HW = Homeworks(
            number=form.number.data,
            lesson=current_user.lesson,
            comments=form.comments.data,
            files=os.path.join('./app/files/Homeworks/', filename)
        )
        db.session.add(new_HW)
        db.session.commit()
        return redirect('/index')
    return render_template('make_homework.html', form=form)

@app.route('/delete_homework/<number>', methods=['GET', 'POST'])
@login_required
def delete_homework(number):
    if admin_check():
        return redirect('/login')
    os.remove(Homeworks.query.filter_by(number=str(number)).first().files)
    a = db.session.query(Homeworks).filter_by(number=str(number))
    a.delete()
    db.session.commit()
    return redirect('/index')


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
                email=tmp_email,
            )
            new_user.set_password(tmp_pass)
            db.session.add(new_user)

        for i in posts:
            for q in i[1]:
                a = random.randint(18, 31)
                new_HW = Homeworks(
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

