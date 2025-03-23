from typing import List

from vis_escape.objects.item import QuizItem


class NonKeyLock(QuizItem):
    def __init__(
        self,
        item_type: str,
        item_name: str,
        question_text: str,
        answer: str,
        appliable_receptacle: str,
        appliable_state: str,
        after_solve_state: str,
    ):
        super().__init__(
            item_type=item_type,
            item_name=item_name,
            question_text=question_text,
            answer=answer,
            appliable_receptacle=appliable_receptacle,
            appliable_state=appliable_state,
            after_solve_state=after_solve_state,
        )

    def get_actions(self) -> List[str]:
        return [f"inspect {self._item_name}"]
