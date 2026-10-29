"""Management command to reset user IDs to sequential 1, 2, 3..."""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset all user IDs to sequential 1, 2, 3... and update all FK references."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get current users ordered by ID
            cursor.execute("SELECT id FROM accounts_user ORDER BY id")
            old_ids = [row[0] for row in cursor.fetchall()]

            if not old_ids:
                self.stdout.write(self.style.WARNING("No users found."))
                return

            # Build mapping: old_id -> new_id
            id_map = {}
            for new_id, old_id in enumerate(old_ids, start=1):
                id_map[old_id] = new_id

            self.stdout.write(f"Remapping {len(old_ids)} users: {list(id_map.items())}")

            # If all IDs are already 1..N, skip
            if all(old == new for old, new in id_map.items()):
                self.stdout.write(self.style.SUCCESS("IDs are already sequential. Nothing to do."))
                return

            # Disable FK checks
            cursor.execute("PRAGMA foreign_keys = OFF")

            try:
                # Step 1: Shift all IDs to temporary high values to avoid conflicts
                offset = max(old_ids) + 10000
                for old_id in old_ids:
                    temp_id = old_id + offset
                    self._update_user_id(cursor, old_id, temp_id)

                # Step 2: Shift from temp values to final sequential IDs
                for old_id, new_id in id_map.items():
                    temp_id = old_id + offset
                    self._update_user_id(cursor, temp_id, new_id)

                # Step 3: Reset the autoincrement counter
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = %s WHERE name = 'accounts_user'",
                    [len(old_ids)],
                )

                self.stdout.write(self.style.SUCCESS(
                    f"Successfully reset {len(old_ids)} user IDs to 1-{len(old_ids)}."
                ))

            finally:
                # Re-enable FK checks
                cursor.execute("PRAGMA foreign_keys = ON")

    def _update_user_id(self, cursor, old_id, new_id):
        """Update a user's ID and all foreign key references pointing to it."""
        # All tables that reference accounts_user.id
        fk_tables = [
            ("jobs_job", "employer_id"),
            ("applications_application", "applicant_id"),
            ("accounts_employerprofile", "user_id"),
            ("accounts_applicantprofile", "user_id"),
            ("core_notification", "user_id"),
            ("accounts_user_groups", "user_id"),
            ("accounts_user_user_permissions", "user_id"),
            ("moderation_flag", "reporter_id"),
            ("moderation_flag", "resolved_by_id"),
            ("moderation_auditlog", "actor_id"),
            ("moderation_auditlog", "admin_id"),
            ("django_admin_log", "user_id"),
        ]

        # Update FK references first
        for table, column in fk_tables:
            try:
                cursor.execute(
                    f"UPDATE {table} SET {column} = %s WHERE {column} = %s",
                    [new_id, old_id],
                )
            except Exception:
                pass  # Table might not exist yet

        # Update the user ID itself
        cursor.execute(
            "UPDATE accounts_user SET id = %s WHERE id = %s",
            [new_id, old_id],
        )
