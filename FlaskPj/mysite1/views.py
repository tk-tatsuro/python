# mysite1/Views.py
from flask import Blueprint, render_template

mysite1_bp: Blueprint = Blueprint('mysite1', __name__, url_prefix='/site1')


# https://www.myDmain/site1/hello
@mysite1_bp.route('/hello')
def hello():
    return render_template('mysite1/hello.html')

