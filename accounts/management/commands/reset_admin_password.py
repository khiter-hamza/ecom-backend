from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update an admin user with a secure password."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Admin email")
        parser.add_argument("--password", required=True, help="New admin password")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]

        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters long.")

        User = get_user_model()

        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_user(email=email, password=password)
            created = True
        else:
            created = False
            user.set_password(password)

        user.is_staff = True
        user.is_superuser = True

        # Optional project-level admin flag if present on custom user model.
        if hasattr(user, "is_admin"):
            user.is_admin = True

        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin user: {email}"))
