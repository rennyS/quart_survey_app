from quart import Quart, render_template, session, g
from tortoise.contrib.quart import register_tortoise
from auth import auth_bp, get_current_user
from questionnaire import questionnaire_bp
from assessment import assessment_bp
from admin import admin_bp

app = Quart(__name__)
app.secret_key = 'supersecretkey'

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(questionnaire_bp, url_prefix='/questionnaire')
app.register_blueprint(assessment_bp, url_prefix='/assessment')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.before_request
async def before_request():
    g.user = await get_current_user()

@app.context_processor
async def inject_user():
    return dict(user=g.user)

@app.route('/')
async def index():
    return await render_template('index.html')

register_tortoise(
    app,
    db_url='sqlite://site.db',
    modules={'models': ['models']},
    generate_schemas=True
)

if __name__ == '__main__':
    app.run()
