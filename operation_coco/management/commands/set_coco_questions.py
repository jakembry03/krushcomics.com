from getpass import getpass

from django.core.management.base import BaseCommand
from django.db import transaction

from operation_coco.answers import hash_answer, normalize_answer
from operation_coco.models import MAX_HINTS, QUESTION_COUNT, SecurityQuestion


class Command(BaseCommand):
    help = (
        "Interactively set Coco's security questions. Answers are typed "
        "hidden, normalized, and stored only as salted hashes."
    )

    def handle(self, *args, **options):
        if SecurityQuestion.objects.exists():
            reply = input("This replaces the existing security questions. Continue? [y/N] ")
            if reply.strip().lower() not in ("y", "yes"):
                self.stdout.write("Nothing changed.")
                return

        questions = [self.ask_question(order) for order in range(1, QUESTION_COUNT + 1)]

        with transaction.atomic():
            SecurityQuestion.objects.all().delete()
            for question in questions:
                question.full_clean()
                question.save()

        self.stdout.write(self.style.SUCCESS(f"Saved {len(questions)} questions."))

    def ask_question(self, order):
        self.stdout.write(f"\nQuestion {order} of {QUESTION_COUNT}")

        prompt = ""
        while not prompt:
            prompt = input("Question text: ").strip()

        self.stdout.write("Answers are hidden as you type. Each one is asked twice.")
        hashes = [self.ask_answer("Answer: ", required=True)]
        while True:
            extra = self.ask_answer("Another accepted answer (blank to finish): ", required=False)
            if extra is None:
                break
            hashes.append(extra)

        hints = []
        while len(hints) < MAX_HINTS:
            hint = input(f"Hint {len(hints) + 1} of {MAX_HINTS} (blank to finish): ").strip()
            if not hint:
                break
            hints.append(hint)

        return SecurityQuestion(order=order, prompt=prompt, answer_hashes=hashes, hints=hints)

    def ask_answer(self, label, required):
        """
        Ask for an answer twice, hidden, and return its hash. Returns None
        for a blank entry when the answer is optional.
        """
        while True:
            answer = getpass(label)
            if not answer.strip():
                if required:
                    continue
                return None
            if not normalize_answer(answer):
                self.stdout.write("That answer has no letters or numbers left after cleanup. Try again.")
                continue
            if getpass("Type it again to confirm: ") != answer:
                self.stdout.write("Those didn't match. Try again.")
                continue
            return hash_answer(answer)
