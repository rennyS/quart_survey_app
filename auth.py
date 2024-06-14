from quart import Blueprint, render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Team

auth_bp = Blueprint('auth', __name__)

async def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = await User.get(id=user_id).select_related('team')
        return user
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        data = await request.form
        username = data['username']
        password = generate_password_hash(data['password'])
        team_id = data['team']

        # Get the team by ID
        team = await Team.get(id=team_id)
        
        user = await User.create(username=username, password_hash=password, team=team)
        
        return redirect(url_for('auth.login'))

    teams = await Team.all()
    return await render_template('register.html', teams=teams)

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
