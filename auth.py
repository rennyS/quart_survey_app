from quart import Blueprint, render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        data = await request.form
        username = data['username']
        password = generate_password_hash(data['password'])
        
        user = await User.create(username=username, password_hash=password)
        
        return redirect(url_for('auth.login'))
    return await render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        data = await request.form
        user = await User.get_or_none(username=data['username'])
        
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return await render_template('login.html')

@auth_bp.route('/logout')
async def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

async def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return await User.get(id=user_id)
    return None
