from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule, AlwaysAllowRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.drawer.double_drawer_second_locked import DoubleDrawerSecondLocked
from vis_escape.objects.receptacles.cupboard.cupboard_locked import CupboardLocked
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.wardrobe.wardrobe import Wardrobe
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.idcard.idcard import IDCard
from vis_escape.objects.items.button.button import Button
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)

ID_card = IDCard(item_type="ID_card", item_name="IDcard", appliable_receptacle=None, appliable_state=None)

button = Button(item_type="button", item_name="Button", appliable_receptacle="2TierDrawer", appliable_state="first_open_second_locked", after_solve_state="first_open_second_open")

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Wardrobe", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Cupboard", appliable_state="locked", after_solve_state="open")
idcardlock_A=KeyLock(item_type="lock", item_name="Idcardlock_A", question_text="", answer=f"use {ID_card.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
numberlock_A=NonKeyLock(item_type="lock", item_name="Numberlock_A", question_text="", answer="8056", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, keylock_A, keylock_B, keylock_C, numberlock_A, idcardlock_A]

doubledrawer=DoubleDrawerSecondLocked(
    id="2TierDrawer",
    interactable_states={
        button: {"first_open_second_closed", "first_open_second_locked"},
        key_A: {"first_closed_second_open", "first_open_second_open"}
    }
)
cupboard=CupboardLocked(
    id="Cupboard",
    interactable_states={
        ID_card: {"open"},
        keylock_C: {"locked"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        key_C: {"open"},
        numberlock_A: {"locked"}
    }
)
wardrobe=Wardrobe(
    id="Wardrobe",
    interactable_states={
        key_B: {"open"},
        keylock_A: {"locked"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        idcardlock_A: {"locked"}
    }
)

lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        puzzle_A: {"open"},
        keylock_B: {"locked"}
    }
)

doubledrawer.add_transition("first_open_second_locked", f"press {button.item_name}", "first_open_second_open", AlwaysAllowRule())
wardrobe.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
lockdesk.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
cupboard.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock_A.item_name}"))
exitdoor.add_transition("locked", f"use {ID_card.item_name}", "open", HasItemRule(ID_card.item_name))

receptacles_position={
    "NORTH": [doubledrawer, cupboard],
    "EAST": [safe],
    "SOUTH": [wardrobe, exitdoor],
    "WEST": [lockdesk]
}

north_wall = WallState("NORTH", receptacles_position["NORTH"])
east_wall = WallState("EAST", receptacles_position["EAST"])
south_wall = WallState("SOUTH", receptacles_position["SOUTH"])
west_wall = WallState("WEST", receptacles_position["WEST"])

hint_messages={
    '': "Press the Button in the first tier of the 2TierDrawer at the north wall",
    'press Button': "Pick up key_A in the second tier of the 2TierDrawer at the north wall",
    'picked_key_A': "Use key_A to unlock the Wardrobe at the south wall",
    'used key_A': "Pick up key_B in the Wardrobe at the south wall",
    'picked_key_B': "Use key_B to unlock the Desk at the west wall",
    'used key_B': "Solve the Numberlock_A in the Safe at the east wall. The answer is 8056",
    'solved_Numberlock_A': "Pick up key_C in the Safe at the east wall",
    'picked_key_C': "Use key_C to unlock the Cupboard at the north wall",
    'used key_C': "Pick up IDcard in the Cupboard at the north wall",
    'picked_IDcard': "Use IDcard to unlock the Door at the south wall"
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
