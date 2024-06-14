from quart import Blueprint, render_template, redirect, url_for, request
from models import Team
from utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/teams', methods=['GET', 'POST'])
@admin_required
async def manage_teams():
    if request.method == 'POST':
        data = await request.form
        team_name = data['team_name']

        # Create a new team
        await Team.get_or_create(name=team_name)

        return redirect(url_for('admin.manage_teams'))

    teams = await Team.all()
    return await render_template('manage_teams.html', teams=teams)
