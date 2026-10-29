from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Lists all registered users in the SQLite database."

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all().order_by("id")

        if not users.exists():
            self.stdout.write(self.style.WARNING("No users found in the database."))
            return

        self.stdout.write(self.style.SUCCESS(f"\nFound {users.count()} user(s) in db.sqlite3:\n"))
        header = f"{'ID':<5} | {'Username':<20} | {'Email':<30} | {'Role':<12} | {'Staff/Admin':<12} | {'Status':<10}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))

        for u in users:
            staff_flag = "Yes" if (u.is_staff or u.is_superuser) else "No"
            self.stdout.write(
                f"{u.id:<5} | {(u.username or '(none)'):<20} | {u.email:<30} | {u.role:<12} | {staff_flag:<12} | {u.status:<10}"
            )
        self.stdout.write("")
