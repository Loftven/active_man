from xkcdpass import xkcd_password as xp
from faker import Faker
import uuid
import hashlib


fake = Faker('ru_RU')


def gen_pass():
    delim = '!@$%^&*-_+=:|~?/.;'
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(
        wordfile=wordfile,
        min_length=5,
        max_length=10
    )
    return xp.generate_xkcdpassword(
        mywords,
        numwords=7,
        random_delimiters=True
    )


def gen_users(num=100):
    users = []
    for i in range(num):
        if i % 2:
            user = {
                'username': fake.user_name(),
                'password': hashlib.sha256(gen_pass().encode()).hexdigest(),
                'first_name': fake.first_name_male(),
                'last_name': fake.last_name_male(),
                'cityzen_id': f'CIT{fake.random_int(min=24565, max=56908778)}',
                'token': uuid.uuid4().hex,
                'privileges': 0
            }
        else:
            user = {
                'username': fake.user_name(),
                'password': hashlib.sha256(gen_pass().encode()).hexdigest(),
                'first_name': fake.first_name_female(),
                'last_name': fake.last_name_female(),
                'cityzen_id': f"CIT{fake.random_int(min=24565, max=56908778)}",
                'token': uuid.uuid4().hex,
                'privileges': 0
            }

        users.append(user)
    return users
