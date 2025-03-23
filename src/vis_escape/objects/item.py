from typing import List


class Item:
    def __init__(
        self,
        item_type: str,
        item_name: str = None,
        appliable_receptacle: str = None,
        appliable_state: str = None,
    ):
        self._item_type = item_type
        self._item_name = item_name or item_type
        self._appliable_receptacle = appliable_receptacle
        self._appliable_state = appliable_state

    @property
    def item_type(self) -> str:
        return self._item_type

    @property
    def item_name(self) -> str:
        return self._item_name


class PickableItem(Item):
    def __init__(
        self,
        item_type: str,
        item_name: str = None,
        appliable_receptacle: str = None,
        appliable_state: str = None,
        after_solve_state: str = None,
    ):
        super().__init__(item_type, item_name, appliable_receptacle, appliable_state)
        self._after_solve_state = after_solve_state

    @property
    def after_solve_state(self) -> str:
        return self._after_solve_state

    @property
    def in_inventory(self) -> bool:
        return self._in_inventory

    @property
    def appliable_receptacle(self) -> str:
        return self._appliable_receptacle

    @property
    def appliable_state(self) -> str:
        return self._appliable_state

    def get_actions(self) -> List[str]:
        actions = [f"pick {self._item_name}"]
        return actions


class StaticItem(Item):
    """Static object that only acts simple interctions (e.g. buttons)"""

    def __init__(
        self,
        item_type: str,
        item_name: str = None,
        appliable_receptacle: str = None,
        appliable_state: str = None,
        after_solve_state: str = None,
    ):
        super().__init__(item_type, item_name, appliable_receptacle, appliable_state)
        self._after_solve_state = after_solve_state

    @property
    def appliable_receptacle(self) -> str:
        return self._appliable_receptacle

    @property
    def appliable_state(self) -> str:
        return self._appliable_state

    @property
    def after_solve_state(self) -> str:
        return self._after_solve_state

    def get_actions(self) -> List[str]:
        return [f"inspect {self._item_name}"]


class QuizItem(Item):
    """Basic object needs to check answers(e.g. Quiz or Problems)"""

    def __init__(
        self,
        item_type: str,
        item_name: str,
        answer: str,
        question_text: str = None,
        appliable_receptacle: str = None,
        appliable_state: str = None,
        after_solve_state: str = None,
    ):
        super().__init__(item_type, item_name, appliable_receptacle, appliable_state)

        self._answer = answer
        self._question_text = question_text
        self._appliable_receptacle = appliable_receptacle
        self._appliable_state = appliable_state
        self._after_solve_state = after_solve_state

    @property
    def answer(self) -> str:
        return self._answer

    @property
    def question_text(self) -> str:
        return self._question_text

    @property
    def appliable_receptacle(self) -> str:
        return self._appliable_receptacle

    @property
    def appliable_state(self) -> str:
        return self._appliable_state

    @property
    def after_solve_state(self) -> str:
        return self._after_solve_state

    def get_actions(self) -> List[str]:
        return [f"inspect {self._item_name}"]

    def check_answer(self, try_answer: str) -> bool:
        print("Checking answer: ", try_answer)
        print("Answer: ", self._answer)
        return self._answer.lower() == try_answer.lower()

    def answer_correct(self):
        self._state = "solved"


class LockKeyItem(QuizItem):
    """Lockers opening with keys"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = "not_solved"
