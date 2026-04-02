from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_photo_troisieme_nom"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="matricule",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=64,
                null=True,
                unique=True,
                verbose_name="matricule",
            ),
        ),
    ]
