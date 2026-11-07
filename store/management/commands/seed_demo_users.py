from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

DEMO_USER = {
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo12345",
}

DEMO_ADMIN = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin12345",
}


class Command(BaseCommand):
    help = "Create a demo customer and a demo superuser for local development"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Refusing to run with DEBUG=False. These accounts use published "
                "passwords and are for local development only."
            )

        customer = self.create_user(DEMO_USER, is_superuser=False)
        admin = self.create_user(DEMO_ADMIN, is_superuser=True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo accounts ready"))
        self.stdout.write("")
        self.stdout.write(f"  Customer   {customer['username']} / {DEMO_USER['password']}")
        self.stdout.write(f"  Admin      {admin['username']} / {DEMO_ADMIN['password']}")
        self.stdout.write("")
        self.stdout.write("  Storefront http://127.0.0.1:8000/accounts/login/")
        self.stdout.write("  Admin      http://127.0.0.1:8000/admin/")
        self.stdout.write("")

    def create_user(self, details, is_superuser):
        user, created = User.objects.get_or_create(
            username=details["username"],
            defaults={"email": details["email"]},
        )

        user.email = details["email"]
        user.is_staff = is_superuser
        user.is_superuser = is_superuser
        user.set_password(details["password"])
        user.save()

        action = "created" if created else "password reset"
        self.stdout.write(f"{details['username']}: {action}")

        return {"username": user.username}
