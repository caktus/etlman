import random

from faker import Faker


class TestBackend:
    def execute_script(self, language: str, script: str) -> tuple[int, str, str]:
        fake = Faker()
        Faker.seed(0)
        return (
            random.randint(0, 10),
            "(stdout) " + fake.paragraph(nb_sentences=20),
            "(stderr) " + fake.paragraph(nb_sentences=20),
        )
