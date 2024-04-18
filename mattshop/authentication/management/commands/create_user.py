from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from faker import Faker

class Command(BaseCommand):
    help = "Manually creates a user for simplifying testing and API interaction on a local environment."

    def handle(self, *args, **options):
        fake = Faker()
        username = fake.user_name()
        password = fake.word()
        User.objects.create_user(username=username, password=password)

        print("User created. Username: '{}', Password '{}'.".format(username, password))
