from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=80, unique=True)
    password_hash = fields.CharField(max_length=256)

class Questionnaire(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=120)
    user = fields.ForeignKeyField('models.User', related_name='questionnaires')
    created_at = fields.DatetimeField(auto_now_add=True)

class Question(models.Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    question_type = fields.CharField(max_length=20)  # 'yes_no' or 'dropdown'
    classification = fields.CharField(max_length=20)  # 'impact' or 'probability'
    yes_score = fields.IntField(null=True)
    no_score = fields.IntField(null=True)
    high_score = fields.IntField(null=True)
    medium_score = fields.IntField(null=True)
    low_score = fields.IntField(null=True)
    questionnaire = fields.ForeignKeyField('models.Questionnaire', related_name='questions')

class Assessment(models.Model):
    id = fields.IntField(pk=True)
    threat_actor = fields.CharField(max_length=120)
    questionnaire = fields.ForeignKeyField('models.Questionnaire', related_name='assessments')
    created_at = fields.DatetimeField(auto_now_add=True)

class AssessmentResponse(models.Model):
    id = fields.IntField(pk=True)
    assessment = fields.ForeignKeyField('models.Assessment', related_name='responses')
    question = fields.ForeignKeyField('models.Question', related_name='responses')
    response = fields.CharField(max_length=20)
    score = fields.IntField()
