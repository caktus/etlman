import random

from faker import Faker


class TestBackend:
    STDOUT_MARKER = "(stdout)"
    STDERR_MARKER = "(stderr)"

    def execute_script(self, language: str, script: str) -> tuple[int, str, str]:
        fake = Faker()
        Faker.seed(0)
        fake_stdout = fake.paragraph(nb_sentences=20)
        fake_stderr = fake.paragraph(nb_sentences=20)
        return (
            random.randint(0, 10),
            " ".join([self.STDOUT_MARKER, fake_stdout]),
            " ".join([self.STDERR_MARKER, fake_stderr]),
        )
