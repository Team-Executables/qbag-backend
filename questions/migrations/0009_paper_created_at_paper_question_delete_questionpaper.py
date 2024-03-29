# Generated by Django 4.0.3 on 2022-08-14 23:45

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0008_paper_name_question_medium'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paper',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='questions.question'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='QuestionPaper',
        ),
    ]
