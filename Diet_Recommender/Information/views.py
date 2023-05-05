from flask import redirect, render_template, Blueprint

Information = Blueprint('Information', __name__,
                        template_folder='templates/Information')


@Information.route('/')
def Index():
    return render_template('index.html')
