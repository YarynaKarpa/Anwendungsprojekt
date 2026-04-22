from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('learner', '0003_studynote_selbstbewertung'),
    ]

    operations = [
        migrations.AddField(
            model_name='studynote',
            name='count_correct',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='studynote',
            name='count_wrong',
            field=models.IntegerField(default=0),
        ),
    ]