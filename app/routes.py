from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, redirect
#from flask_security.utils import encrypt_password


from app.models import User


@app.route('/')
@app.route('/index')
def index():
    posts = [['Алгебра', ['№135', '№345', '№222']],
             ['Геометрия', ['№335', '№545', '№112']],
             ['Русский язык', ['Упражнение 200', 'Упражнение 195']],
             ['Литература', ['Доклад', 'Сочинение по произведению Сенька', 'стр.52 №1,2,3']]]
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and form.password.data == 'password' and form.username.data == 'login':
        return redirect('/index')
    return render_template('login.html', form=form)


@app.route('/homework')
def homework():
    return render_template('homework.html')


@app.route('/Registration', methods=['GET', 'POST'])
def Registration():
    form = RegistrationForm()
    if form.validate_on_submit() and form.password.data == form.password2.data:
        return redirect('/login')
    return render_template('Registration.html', form=form)

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random


    db.drop_all()
    db.create_all()

    with app.app_context():



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

        db.session.commit()
    return

