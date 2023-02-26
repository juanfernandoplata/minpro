from flask import Flask, request, make_response, redirect, render_template, abort, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

import smtplib
import email as emailib

import jwt

from random import randint

app = Flask( __name__ )
app.config[ "SECRET_KEY" ] = "$=?'!#=NdFnkDSfsJSO!W/(XcWI)R)U=WQSBZ?U'#e"

login_manager = LoginManager()
login_manager.init_app( app )
login_manager.login_view = "f1login"

db_params = {
    "dbname": "xyzpos",
    "user": "xyzdbm",
    "password": "xyzdbm",
    "host": "localhost",
    "port": 5432
}

class User( UserMixin ):
    def __init__( self, user_id, role, names, lastnames, email ):
        self.id = user_id
        self.role = role
        self.names = names
        self.lastnames = lastnames
        self.email = email

@login_manager.user_loader
def load_user( user_id ):
    conn = psycopg2.connect( **db_params )
    cur = conn.cursor()
    cur.execute( f"select id, role, names, lastnames, email from users where id = '{ user_id }'" )
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if( user_data ):
        return User( user_data[ 0 ], user_data[ 1 ], user_data[ 2 ], user_data[ 3 ], user_data[ 4 ] )

    return None

def send_verification_code( email ):
    """
    code = "".join( chr( randint( 48, 57 ) ) for _ in range( 6 ) )
    msg = emailib.message_from_string( f"Your verification code is: { code }" )
    msg[ "From" ] = "minpro.assist@outlook.com"
    msg[ "To" ] = email
    msg[ "Subject" ] = "XYZ POS Verification Code"

    s = smtplib.SMTP( "smtp-mail.outlook.com", 587 )
    s.set_debuglevel( 1 )

    s.ehlo( "[10.50.32.86]" )
    s.starttls()
    s.ehlo( "[10.50.32.86]" )
    s.login( "minpro.assist@outlook.com", "min.assist" )
    s.sendmail( "minpro.assist@outlook.com", email, msg.as_string() )
    s.quit()
    """
    code = "".join( chr( randint( 48, 57 ) ) for _ in range( 6 ) )
    print( "CODE IS:", code )

    return code

def send_default_password( email ):
    """
    password = "".join( chr( randint( 48, 57 ) ) for _ in range( 6 ) )
    msg = emailib.message_from_string( f"Your default password is: { password }\nWe suggest changing it immediately." )
    msg[ "From" ] = "minpro.assist@outlook.com"
    msg[ "To" ] = email
    msg[ "Subject" ] = "XYZ POS Account Default Password"

    s = smtplib.SMTP( "smtp-mail.outlook.com", 587 )
    s.set_debuglevel( 1 )

    s.ehlo( "[10.50.32.86]" )
    s.starttls()
    s.ehlo( "[10.50.32.86]" )
    s.login( "minpro.assist@outlook.com", "min.assist" )
    s.sendmail( "minpro.assist@outlook.com", email, msg.as_string() )
    s.quit()
    """
    password = "".join( chr( randint( 48, 57 ) ) for _ in range( 6 ) )
    print( "PASSWORD IS:", password )

    return password

@app.route( "/" )
@login_required
def index():
    return render_template( "index.html" )

@app.route( "/f1login", methods= [ "GET", "POST" ] )
def f1login():
    if( request.method == "POST" ):
        user_id = request.form[ "userid" ]
        password = request.form[ "password" ]

        conn = psycopg2.connect( **db_params )
        cur = conn.cursor()
        cur.execute( f"select id, role, names, lastnames, email, password from users where id = '{ user_id }'" )
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if( user_data and check_password_hash( user_data[ 5 ], password ) ):
            code = send_verification_code( user_data[ 4 ] )
            cookie = jwt.encode( {
                "CODE" : code,
                "USER_DATA" : ( user_data[ 0 ], user_data[ 1 ], user_data[ 2 ], user_data[ 3 ], user_data[ 4 ]
            ) }, app.config[ "SECRET_KEY" ] )

            res = make_response( redirect( "/f2login" ) )
            res.set_cookie( "f2token", cookie )

            return res

    return render_template( "f1login.html" )

@app.route( "/f2login", methods= [ "GET", "POST" ] )
def f2login():
    if( request.method == "POST" ):
        code = request.form[ "code" ]

        cookie = request.cookies.get( "f2token" )
        token = jwt.decode( cookie, app.config[ "SECRET_KEY" ], algorithms = "HS256" )

        if( code == token[ "CODE" ] ):
            login_user( User( *token[ "USER_DATA" ]  ) )
            return redirect( url_for( "index" ) )

    return render_template( "f2login.html" )

@app.route( "/logout" )
@login_required
def logout():
    logout_user()
    return redirect( url_for( "f1login" ) )

@app.route( "/create_user", methods = [ "GET", "POST" ] )
@login_required
def create_user():
    if( current_user.role == "SEL" ): abort( 403 )

    if( request.method == "POST" ):
        user_id = request.form[ "userid" ]
        names = request.form[ "names" ]
        lastnames = request.form[ "lastnames" ]
        email = request.form[ "email" ]

        role = None
        if( current_user.role == "DIR" ): role = "MAN"
        elif( current_user.role == "MAN" ): role = "SEL"

        password = send_default_password( email )

        conn = psycopg2.connect( **db_params )
        cur = conn.cursor()
        cur.execute( f"insert into users values( '{ user_id }', '{ names }', '{ lastnames }', '{ email }', '{ generate_password_hash( password ) }', '{ role }' )" )
        cur.close()
        conn.commit()
        conn.close()

        return redirect( url_for( "index" ) )

    return render_template( "create_user.html" )

