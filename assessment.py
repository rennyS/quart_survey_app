import matplotlib.pyplot as plt
import os
from quart import Blueprint, render_template, redirect, url_for, request, g
from models import Assessment, AssessmentResponse, Questionnaire
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/list')
async def list_assessments():
    if not g.user:
        return redirect(url_for('auth.login'))

    if g.user.is_admin:
        assessments = await Assessment.all().prefetch_related('questionnaire')
    else:
        assessments = await Assessment.filter(team=g.user.team).prefetch_related('questionnaire')
    return await render_template('list_assessments.html', assessments=assessments)

@assessment_bp.route('/start/<int:questionnaire_id>', methods=['GET', 'POST'])
async def start_assessment(questionnaire_id):
    if not g.user:
        return redirect(url_for('auth.login'))

    questionnaire = await Questionnaire.get(id=questionnaire_id).prefetch_related('questions')
    if request.method == 'POST':
        data = await request.form
        threat_actor = data['threat_actor']
        assessment = await Assessment.create(threat_actor=threat_actor, questionnaire=questionnaire, team=g.user.team)
        
        for question in questionnaire.questions:
            response = data[f'question_{question.id}_response']
            if question.question_type == 'yes_no':
                score = question.yes_score if response == 'yes' else question.no_score
            elif question.question_type == 'dropdown':
                if response == 'high':
                    score = question.high_score
                elif response == 'medium':
                    score = question.medium_score
                elif response == 'low':
                    score = question.low_score
            await AssessmentResponse.create(assessment=assessment, question=question, response=response, score=score)
        
        return redirect(url_for('assessment.view_assessment', assessment_id=assessment.id))

    return await render_template('start_assessment.html', questionnaire=questionnaire)


def create_risk_matrix(total_impact, total_probability, assessment_id):
    # Normalize scores to a 1-5 scale
    normalized_impact_score = min(round(total_impact / 5), 5)
    normalized_probability_score = min(round(total_probability / 5), 5)

    # Define the risk colors for background grid
    colors = ['green', 'yellow', 'orange', 'red']
    cmap = mcolors.ListedColormap(colors)

    # Create the risk matrix with equal distribution of colored squares, inverted
    risk_matrix = np.array([
        [1, 1, 3, 3, 3],  # Row 5
        [1, 1, 1, 3, 3],  # Row 4
        [0, 1, 1, 1, 3],  # Row 3
        [0, 0, 1, 1, 1],  # Row 2
        [0, 0, 0, 1, 1]   # Row 1
    ])

    # Create a scatter plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw the background grid
    for i in range(5):
        for j in range(5):
            ax.fill_between([j + 0.5, j + 1.5], i + 0.5, i + 1.5, color=cmap(risk_matrix[4 - i, j]), edgecolor='black', linewidth=1)

    # Plot the person's scores
    ax.scatter(normalized_probability_score, normalized_impact_score, color='blue', edgecolor='black', s=100)
    ax.text(normalized_probability_score + 0.1, normalized_impact_score + 0.1, 'Score', fontsize=9)

    # Add labels, title, and grid
    ax.set_xticks(np.arange(1, 6))
    ax.set_xticklabels(['1', '2', '3', '4', '5'])
    ax.set_yticks(np.arange(1, 6))
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_xlabel('Probability')
    ax.set_ylabel('Impact')
    ax.set_title('Probability vs. Impact Matrix')
    ax.grid(which='both', color='grey', linestyle='-', linewidth=0.5)

    # Set the limits to align with the grid
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)

    # Save the plot
    plot_filename = f'assessment_{assessment_id}.png'
    plot_path = os.path.join('static', 'plots', plot_filename)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    fig.savefig(plot_path)
    plt.close(fig)

    return plot_filename



@assessment_bp.route('/view/<int:assessment_id>')
async def view_assessment(assessment_id):
    if not g.user:
        return redirect(url_for('auth.login'))

    print(f"Fetching assessment with ID: {assessment_id}")

    assessment = await Assessment.get_or_none(id=assessment_id).select_related('team', 'questionnaire__user').prefetch_related('responses__question')
    if not assessment:
        print(f"No assessment found with ID: {assessment_id}")
        return redirect(url_for('assessment.list_assessments'))

    if assessment.team_id != g.user.team_id:
        print(f"User not authorized to view this assessment. User's team: {g.user.team_id}, Assessment's team: {assessment.team_id}")
        return redirect(url_for('assessment.list_assessments'))

    impact_scores = [response.score for response in assessment.responses if response.question.classification == 'impact']
    probability_scores = [response.score for response in assessment.responses if response.question.classification == 'probability']
    
    if impact_scores:
        total_impact = sum(impact_scores)
    else:
        total_impact = 0
    
    if probability_scores:
        total_probability = sum(probability_scores)
    else:
        total_probability = 0
    
    # Create the risk matrix plot
    plot_filename = create_risk_matrix(total_impact, total_probability, assessment_id)

    return await render_template('view_assessment.html', assessment=assessment, impact_scores=impact_scores, probability_scores=probability_scores, total_impact=total_impact, total_probability=total_probability, plot_filename=plot_filename)