from vis_escape.objects.item import PickableItem


class Ring(PickableItem):
    def __init__(
        self,
        item_type: str,
        item_name: str,
        pickable: bool = True,
        applicable: bool = True,
    ):
        super().__init__(
            item_type=item_type,
            item_name=item_name,
            pickable=pickable,
            applicable=applicable,
        )
