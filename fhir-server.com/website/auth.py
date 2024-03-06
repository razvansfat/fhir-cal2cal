from flask import Blueprint, render_template, request, flash, redirect, url_for
# from .models import User
from .models import Users, Users_roles, Nom_roles
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
import requests

auth = Blueprint('auth', __name__)
@auth.route('/login', methods=['GET', 'POST'])
def login():

    userAll = Users.query.all()
    email = 'test@test.com'
    password = '1234'

    user = Users.query.filter_by(username=email).first()
    if check_password_hash(user.password, password):
        #flash('Logged in success!', category='success')
        login_user(user)
        user2 = Users.query\
            .filter_by(username=email)\
            .join(Users_roles, Users.id_users == Users_roles.user_id)\
            .join(Nom_roles, Nom_roles.code == Users_roles.role)\
            .add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role, Nom_roles.role_name)\
            .first()

        return redirect(url_for('views.home'))
               
# @auth.route('/login', methods=['GET', 'POST'])
# def login():

#     userAll = Users.query.all()
#     if userAll:
#         if request.method == 'POST':
#             # email = request.form.get('email')
#             # password = request.form.get('password')
#             email = 'test@test.com'
#             password = '1234'

#             user = Users.query.filter_by(username=email).first()

#             # user = Users.query\
#             #     .filter_by(username=email)\
#             #     .join(Users_roles, Users.id_users == Users_roles.user_id)\
#             #     .join(Nom_roles, Nom_roles.code == Users_roles.role)\
#             #     .add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role, Nom_roles.role_name)\
#             #     .first()
        
#             # print(generate_password_hash(password, method='sha256'))
#             if user:


#                 #metatagsRez = ''
#                 #userRole = 'Admin'
#                 #userRight = 1
                
#                 #questionnaireAll = user.password
#                 #if check_password_hash(user.password, password):
#                 #    userRole = 'DA'
#                 #else:
#                 #    userRole = check_password_hash(user.password, '1234')
            
#                 #return render_template("home.html", user=current_user, formulare=questionnaireAll, metatags=metatagsRez, roles=userRole, right=userRight)

#                 #return redirect(url_for('views.home'))
                
#                 if check_password_hash(user.password, password):
#                     #flash('Logged in success!', category='success')
#                     login_user(user)
#                     user2 = Users.query\
#                         .filter_by(username=email)\
#                         .join(Users_roles, Users.id_users == Users_roles.user_id)\
#                         .join(Nom_roles, Nom_roles.code == Users_roles.role)\
#                         .add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role, Nom_roles.role_name)\
#                         .first()

#                     # if user2.role_name == 'Admin':
#                     #     return redirect(url_for('practitioner.view_practitioner'))
#                     # else:
#                     #     API_ENDPOINT = "http://localhost:8080/fhir/Practitioner?email=" + current_user.username + "&_pretty=true"
#                     #     r = requests.get(url = API_ENDPOINT) 
#                     #     content = r.json()

#                     #     if content['total'] == 0:
#                     #         return redirect(url_for('views.edit_practitioner'))
#                     #     else:
#                     #         return redirect(url_for('views.home'))
#                     return redirect(url_for('views.home'))
#                 else:
#                     flash('Incorect credentials pass', category='error')
#             else:
#                 flash('Incorect credentials user', category='error')

#         return redirect(url_for('views.public_page'))
#     else:
#         return redirect(url_for('views.public_page'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.public_page'))

