# Generated migration for InterviewAnalysis model

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_add_ai_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recording_filename', models.CharField(blank=True, max_length=255, null=True)),
                ('recording_duration_seconds', models.IntegerField(default=0)),
                ('emotion_trend', models.TextField(blank=True, help_text='Emotional pattern observed throughout the interview', null=True)),
                ('confidence_score', models.IntegerField(default=0, help_text='Confidence level 0-100')),
                ('communication_analysis', models.TextField(blank=True, help_text='Analysis of communication clarity and style', null=True)),
                ('strengths', models.JSONField(blank=True, default=list, help_text='List of observed strengths')),
                ('improvements', models.JSONField(blank=True, default=list, help_text='List of suggested improvements')),
                ('eye_movement_pattern', models.TextField(blank=True, help_text='Observed eye movement behavior', null=True)),
                ('attention_level', models.CharField(blank=True, help_text='low, moderate, or high', max_length=50, null=True)),
                ('suspicion_risk', models.CharField(blank=True, help_text='low, medium, or high', max_length=50, null=True)),
                ('integrity_notes', models.TextField(blank=True, help_text='Behavioral observations', null=True)),
                ('ranking_position', models.IntegerField(default=0, help_text='Position among participants')),
                ('total_participants', models.IntegerField(default=1, help_text='Total participants analyzed')),
                ('percentile_band', models.CharField(blank=True, help_text='Performance percentile', max_length=50, null=True)),
                ('raw_ai_response', models.JSONField(blank=True, default=dict)),
                ('analyzed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_analyses', to='profiles.userprofile')),
            ],
            options={
                'verbose_name_plural': 'Interview Analyses',
                'db_table': 'interview_analyses',
                'ordering': ['-analyzed_at'],
            },
        ),
    ]
