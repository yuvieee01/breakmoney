from django.db import migrations, models


def cleanup_null_token_hash(apps, schema_editor):
    EmailVerificationToken = apps.get_model("accounts", "EmailVerificationToken")
    EmailVerificationToken.objects.filter(token_hash__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounts",
            "0005_remove_emailverificationtoken_accounts_em_token_5f2b37_idx_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            cleanup_null_token_hash,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="emailverificationtoken",
            name="token_hash",
            field=models.CharField(max_length=64, unique=True, db_index=True),
        ),
    ]