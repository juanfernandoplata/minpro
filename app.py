from flask import Flask, request, make_response, redirect, render_template, url_for, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

import smtplib
import email as emailib

import jwt

import csv

from random import randint

#ITEMS_PER_PAGE = 2

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
    def __init__( self, user_id, role, rp_id, names, lastnames, email ):
        self.id = user_id
        self.role = role
        self.rp_id = rp_id
        self.names = names
        self.lastnames = lastnames
        self.email = email

@login_manager.user_loader
def load_user( user_id ):
    conn = psycopg2.connect( **db_params )
    cur = conn.cursor()
    cur.execute( f"select id, role, rp_id, names, lastnames, email from users where id = '{ user_id }'" )
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if( user_data ):
        return User( user_data[ 0 ], user_data[ 1 ], user_data[ 2 ], user_data[ 3 ], user_data[ 4 ], user_data[ 5 ] )

    return None

def transact( action, specs ):
    res = None

    conn = psycopg2.connect( **db_params )
    cur = conn.cursor()

    cur.execute( action + " " + specs )

    if( action == "select" ):
        res = cur.fetchall()

    if( action == "insert" or action == "update" or action == "delete" ):
        conn.commit()

    cur.close()
    conn.close()

    return res

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

@app.route( "/f1login", methods= [ "GET", "POST" ] )
def f1login():
    if( request.method == "POST" ):
        user_id = request.form[ "userid" ]
        password = request.form[ "password" ]

        conn = psycopg2.connect( **db_params )
        cur = conn.cursor()
        cur.execute( f"select id, role, rp_id, names, lastnames, email, password from users where id = '{ user_id }'" )
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if( user_data and check_password_hash( user_data[ 6 ], password ) ):
            code = send_verification_code( user_data[ 4 ] )
            cookie = jwt.encode( {
                "CODE" : code,
                "USER_DATA" : ( user_data[ 0 ], user_data[ 1 ], user_data[ 2 ], user_data[ 3 ], user_data[ 4 ], user_data[ 5 ] )
            }, app.config[ "SECRET_KEY" ] )

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

@app.route( "/" )
@login_required
def index():
    return render_template( "index.html", role = current_user.role )

@app.route( "/users" )
@login_required
def users():
    return render_template( "users.html", role = current_user.role )

@app.route( "/users/change_password", methods = [ "GET", "POST" ] )
@login_required
def users_change_password():
    if( request.method == "POST" ):
        ppw = request.form[ "ppw" ]
        npw = request.form[ "npw" ]
        rnpw = request.form[ "rnpw" ]

        if( npw == rnpw ):
            transact( "update", f"users set password = '{ generate_password_hash( npw ) }' where id = '{ current_user.id }'" )
            return redirect( url_for( "index" ) )

        else:
            print( "Flash al user para que sepa que las contras no coinciden" )
            return redirect( url_for( "users_change_password" ) )

    return render_template( "users_change_password.html", role = current_user.role )

@app.route( "/users/create", methods = [ "GET", "POST" ] )
@login_required
def users_create():
    if( current_user.role == "SEL" ): abort( 403 )

    if( request.method == "POST" ):
        user_id = request.form[ "userid" ]
        names = request.form[ "names" ]
        lastnames = request.form[ "lastnames" ]
        email = request.form[ "email" ]

        role = None
        rp_id = None
        if( current_user.role == "DIR" ):
            role = "MAN"
            rp_id = request.form[ "retail_point" ]

        elif( current_user.role == "MAN" ):
            role = "SEL"
            rp_id = current_user.rp_id

        password = send_default_password( email )

        conn = psycopg2.connect( **db_params )
        cur = conn.cursor()
        cur.execute( f"insert into users values( '{ user_id }', '{ names }', '{ lastnames }', '{ email }', '{ generate_password_hash( password ) }', '{ role }', { rp_id } )" )
        cur.close()
        conn.commit()
        conn.close()

        return redirect( url_for( "index" ) )

    else:
        RP = []

        if( current_user.role == "DIR" ):
            RP = transact( "select", "id, name from retail_points" )

        return render_template( "users_create.html", role = current_user.role, RP = RP )

@app.route( "/users/view", methods = [ "GET", "POST" ] )
@login_required
def users_view():
    ITEMS_PER_PAGE = 5

    if( current_user.role == "SEL" ): abort( 403 )

    page = int( request.args.get( "page", 1 ) )

    if( current_user.role == "DIR" ):
        total_items = transact( "select", "count( * ) from users where role = 'MAN'" )[ 0 ][ 0 ]

    elif( current_user.role == "MAN" ):
        total_items = transact( "select", f"count( * ) from users where role = 'SEL' and rp_id = { current_user.rp_id }" )[ 0 ][ 0 ]

    else: abort( 403 )

    total_pages = ( total_items + ITEMS_PER_PAGE - 1 ) // ITEMS_PER_PAGE

    if( request.method == "POST" ):
        user_id = request.form.get( "id" )

        transact( "delete", f"from users where id = '{ user_id }'" )

        return redirect( url_for( "users_view", page = page ) )

    else:
        role = None
        if( current_user.role == "DIR" ):
            items = transact( "select", f"id, names, lastnames, email from users where role = 'MAN' order by id offset { ( page - 1 ) * ITEMS_PER_PAGE } limit { ITEMS_PER_PAGE }" )

        elif( current_user.role == "MAN" ):
            items = transact( "select", f"id, names, lastnames, email from users where role = 'SEL' and rp_id = { current_user.rp_id } order by id offset { ( page - 1 ) * ITEMS_PER_PAGE } limit { ITEMS_PER_PAGE }" )

        return render_template( "users_view.html", role = current_user.role, items = items, page = page, total_pages = total_pages )

@app.route( "/products" )
@login_required
def products():
    if( current_user.role == "SEL" ): abort( 403 )

    return render_template( "products.html", role = current_user.role )

@app.route( "/products/add", methods=[ "GET", "POST" ] )
@login_required
def products_add():
    if( current_user.role == "SEL" ): abort( 403 )

    if( request.method == "POST" ):
        name = request.form.get( "name" )
        descr = request.form.get( "desc" )

        count = transact( "select", f"count( * ) from products where name = '{ name }'" )[ 0 ][ 0 ]

        if( not count ):
            transact( "insert", f"into products( name, descr ) values( '{ name }', '{ descr }' )" )

        else:
            print( "Aqui hay que hacer un flash (el producto ya hace parte del inventario local)" )

        return redirect( url_for( "products_add" ) )

    else:
        return render_template( "products_add.html", role = current_user.role )

@app.route( "/products/view", methods=[ "GET", "POST" ] )
@login_required
def products_view():
    ITEMS_PER_PAGE = 2

    if( current_user.role == "SEL" ): abort( 403 )

    fname = request.args.get( "fname", "" )
    fdesc = request.args.get( "fdesc", "" )
    page = int( request.args.get( "page", 1 ) )

    total_items = transact( "select", f"count( * ) from products where name like '%{ fname }%' and descr like '%{ fdesc }%'" )[ 0 ][ 0 ]
    total_pages = ( total_items + ITEMS_PER_PAGE - 1 ) // ITEMS_PER_PAGE

    if( request.method == "POST" ):
        prod_id = request.form.get( "prod_id" )
        name = request.form.get( "name" )
        descr = request.form.get( "desc" )

        count = transact( "select", f"count( * ) from inventory where prod_id = { prod_id } and rp_id = { current_user.rp_id }" )[ 0 ][ 0 ]

        if( "Add" in request.form ):
            if( not count ):
                transact( "insert", f"into inventory( rp_id, prod_id, price, quantity ) values( { current_user.rp_id }, { prod_id }, { 0.0 }, { 0 } )" )

            else:
                print( "Aqui hay que hacer un flash (el producto ya hace parte del inventario local)" )

        elif( "Remove" in request.form ):
            if( count ):
                transact( "delete", f"from inventory where rp_id = { current_user.rp_id } and prod_id = { prod_id }" )

            else:
                print( "Aqui hay que hacer un flash (el producto no hace parte del inventario local)" )

        return redirect( url_for( "products_view", fname = fname, fdesc = fdesc, page = page ) )

    else:
        items = transact( "select", f"* from products where name like '%{ fname }%' and descr like '%{ fdesc }%' order by id offset { ( page - 1 ) * ITEMS_PER_PAGE } limit { ITEMS_PER_PAGE }" )

        return render_template( "products_view.html", role = current_user.role, items = items, page = page, total_pages = total_pages )

@app.route( "/inventory" )
@login_required
def inventory():
    if( current_user.role == "DIR" or current_user.role == "SEL" ): abort( 403 )

    return render_template( "inventory.html", role = current_user.role )

@app.route( "/inventory/view", methods = [ "GET", "POST" ] )
def inventory_view():
    ITEMS_PER_PAGE = 5

    if( current_user.role == "DIR" or current_user.role == "SEL" ): abort( 403 )

    fname = request.args.get( "fname", "" )
    fdesc = request.args.get( "fdesc", "" )
    page = int( request.args.get( "page", 1 ) )

    total_items = transact( "select", f"count( * ) from products, inventory where id = prod_id and rp_id = { current_user.rp_id } and name like '%{ fname }%' and descr like '%{ fdesc }%'" )[ 0 ][ 0 ]
    total_pages = ( total_items + ITEMS_PER_PAGE - 1 ) // ITEMS_PER_PAGE

    if( request.method == "POST" ):
        prod_id = request.form.get( "id" )
        name = request.form.get( "name" )
        quantity = request.form.get( "quantity" )
        price = request.form.get( "price" )

        transact( "update", f"inventory set quantity = { quantity }, price = { price } where prod_id = { prod_id } and rp_id = { current_user.rp_id }" )

        return redirect( url_for( "inventory_view", fname = fname, fdesc = fdesc, page = page ) )

    else:
        items = transact( "select", f"prod_id, name, quantity, price from products, inventory where prod_id = id and rp_id = { current_user.rp_id } and name like '%{ fname }%' and descr like '%{ fdesc }%' order by prod_id offset { ( page - 1 ) * ITEMS_PER_PAGE } limit { ITEMS_PER_PAGE }" )

        return render_template( "inventory_view.html", role = current_user.role, items = items, fname = fname, fdesc = fdesc, page = page, total_pages = total_pages )

@app.route( "/inventory/update", methods = [ "GET", "POST" ] )
@login_required
def inventory_update():
    if( current_user.role == "DIR" or current_user.role == "SEL" ): abort( 403 )

    if( request.method == "POST" ):
        csv_file = request.files[ "csvfile" ]

        if( csv_file ):
            csv_string = csv_file.stream.read().decode( "utf-8" )
            csv_data = list( csv.reader( csv_string.splitlines(), delimiter = "," ) )

            if( [ "NOMBRE", "CANTIDAD", "PRECIO" ] == csv_data[ 0 ] ):
                conn = psycopg2.connect( **db_params )
                cur = conn.cursor()

                not_found = False
                for row in csv_data[ 1 : ]:
                    cur.execute( f"select count( * ) from products, inventory where id = prod_id and name = '{ row[ 0 ] }'" )
                    count = cur.fetchone()[ 0 ]

                    if( count ):
                        cur.execute( f"update inventory set quantity = { row[ 1 ] }, price = { row[ 2 ] } from products where id = prod_id and name = '{ row[ 0 ] }'" )

                    else:
                        print( "Indicar al usuario que se esta intentando modificar un registro que no existe" )
                        not_found = True
                        break

                if( not not_found ):
                    conn.commit()

                else:
                    conn.rollback()

                cur.close()
                conn.close()

            else:
                print( "Indicar que el formato es incorrecto" )

        else: print( "Indicar archivo no seleccionado" )

    return render_template( "inventory_update.html", role = current_user.role )

@app.route( "/logout" )
@login_required
def logout():
    logout_user()
    return redirect( url_for( "f1login" ) )
