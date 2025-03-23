from typing import List

from vis_escape.objects.item import StaticItem


class Monitor(StaticItem):
    def __init__(
        self,
        item_type: str,
        item_name: str,
        appliable_receptacle: str,
        appliable_state: str,
        after_solve_state: str,
    ):
        super().__init__(
            item_type=item_type,
            item_name=item_name,
            appliable_receptacle=appliable_receptacle,
            appliable_state=appliable_state,
            after_solve_state=after_solve_state,
        )

    def get_actions(self) -> List[str]:
        return [f"inspect {self._item_name}"]
