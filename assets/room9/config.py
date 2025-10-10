from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule, AlwaysAllowRule, NotRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.refrigerator.refrigerator_room9 import Refrigerator
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.computer.computer import Computer
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.table.table import Table
from vis_escape.objects.receptacles.briefcase.briefcase import BriefCase

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.hairdryer.hairdryer import HairDryer
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)
hairdryer = HairDryer(item_type="hairdryer", item_name="HairDryer", appliable_receptacle=None, appliable_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Briefcase", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
ice = KeyLock(item_type="lock", item_name="Icelock", question_text="", answer=f"use {hairdryer.item_name}", appliable_receptacle="Refrigerator", appliable_state="open_with_ice", after_solve_state="open")

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
keyboard=NonKeyLock(item_type="lock", item_name="Keyboard", question_text="", answer=f"APRIL", appliable_receptacle="Computer", appliable_state="locked", after_solve_state="unlock")
numberlock=NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer=f"9015", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[keylock_A, keylock_B, keylock_C, numberlock, keyboard, puzzle_A]

briefcase=BriefCase(
    id="Briefcase",
    interactable_states={
        keylock_B:{"locked"},
        puzzle_A:{"open"}
    }
)

computer=Computer(
    id="Computer",
    interactable_states={
        keyboard:{"locked"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        numberlock:{"locked"},
        key_C:{"open"}
    }
)

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        keylock_A:{"locked"},
        key_B: {"open"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_C:{"locked"}
    }
)
refrigerator=Refrigerator(
    id="Refrigerator",
    interactable_states={
        key_A:{"open"},
        ice:{"open_with_ice"}
    }
)
table=Table(
    id="Table",
    interactable_states={
        hairdryer:{"default"}
    }
)

refrigerator.add_transition("open_with_ice", "close", "closed", AlwaysAllowRule())
refrigerator.add_transition("open", "close", "closed", AlwaysAllowRule())

refrigerator.add_transition("open_with_ice", f"use {hairdryer.item_name}", "open", HasItemRule(hairdryer.item_name))
refrigerator.add_transition("closed", "open", "open", TriggerActiveRule(f"picked_{key_A.item_name}"))
refrigerator.add_transition("closed", "open", "open_with_ice", NotRule(TriggerActiveRule(f"picked_{key_A.item_name}")))
computer.add_transition("locked", "unlock", "unlock", TriggerActiveRule(f"solved_{keyboard.item_name}"))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
closet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(f"{key_A.item_name}"))
briefcase.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(f"{key_B.item_name}"))
exitdoor.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(f"{key_C.item_name}"))

north_wall = WallState("NORTH", [briefcase, computer])
east_wall = WallState("EAST", [safe])
south_wall = WallState("SOUTH", [closet, exitdoor])
west_wall = WallState("WEST", [refrigerator, table])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="WEST")
game_state.set_clear_condition("Door", "open")

hint_messages={
    '' : "Pick up HairDryer at the Table at the west wall",
    'picked_HairDryer': "Use HairDryer at the Refrigerator at the west wall",
    'used HairDryer':"Pick up key_A at the Refrigerator at the west wall",
    'picked_key_A': "Use key_A to unlock the Closet at the south wall",
    'used key_A': "Pick up key_B at the Closet at the south wall",
    'picked_key_B': "Use key_B to unlock the Briefcase at the north wall",
    'used key_B': "Solve the Question in the Computer at the north wall. The answer is 'APRIL'",
    'solved_Keyboard': "Solve the Numberlock at the Safe at the east wall. The answer is '9015'",
    'solved_Numberlock': "Pick up key_C at the Safe at the east wall",
    'picked_key_C': "Use key_C to unlock the Door at the south wall",
    'used key_C': "Open the Door at the south wall"
}
game_state.set_hint_message(hint_messages)
