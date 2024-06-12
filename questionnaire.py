from quart import Blueprint, render_template, redirect, url_for, request, g
from models import Questionnaire, Question

questionnaire_bp = Blueprint('questionnaire', __name__)

@questionnaire_bp.route('/create', methods=['GET', 'POST'])
async def create_questionnaire():
    if not g.user:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        data = await request.form
        name = data['name']
        questionnaire = await Questionnaire.create(name=name, user=g.user)
        
        for i in range(int(data['num_questions'])):
            question_text = data[f'question_{i}_text']
            question_type = data[f'question_{i}_type']
            classification = data[f'question_{i}_classification']
            yes_score = data.get(f'question_{i}_yes_score')
            no_score = data.get(f'question_{i}_no_score', 0)  # Default no_score to 0
            high_score = data.get(f'question_{i}_high_score')
            medium_score = data.get(f'question_{i}_medium_score')
            low_score = data.get(f'question_{i}_low_score')
            await Question.create(text=question_text, question_type=question_type, classification=classification, 
                                  yes_score=yes_score, no_score=no_score, high_score=high_score, medium_score=medium_score, low_score=low_score, 
                                  questionnaire=questionnaire)
        
        return redirect(url_for('index'))
    return await render_template('create_questionnaire.html')

@questionnaire_bp.route('/list')
async def list_questionnaires():
    if not g.user:
        return redirect(url_for('auth.login'))
        
    questionnaires = await Questionnaire.filter(user=g.user).all()
    return await render_template('list_questionnaires.html', questionnaires=questionnaires)

@questionnaire_bp.route('/view/<int:questionnaire_id>')
async def view_questionnaire(questionnaire_id):
    if not g.user:
        return redirect(url_for('auth.login'))
        
    questionnaire = await Questionnaire.get_or_none(id=questionnaire_id).prefetch_related('questions')
    if not questionnaire or questionnaire.user_id != g.user.id:
        return redirect(url_for('questionnaire.list_questionnaires'))
        
    return await render_template('view_questionnaire.html', questionnaire=questionnaire)
