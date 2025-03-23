from vis_escape.objects.item import PickableItem


class Book(PickableItem):
    def __init__(
        self,
        item_type: str,
        item_name: str,
        appliable_receptacle: str = None,
        appliable_state: str = None,
    ):
        super().__init__(
            item_type=item_type,
            item_name=item_name,
            appliable_receptacle=appliable_receptacle,
            appliable_state=appliable_state,
        )
