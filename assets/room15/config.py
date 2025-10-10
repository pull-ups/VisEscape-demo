from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.box.non_lock_box import NonLockBox
from vis_escape.objects.receptacles.locker.single_locker import SingleLocker
from vis_escape.objects.receptacles.posmachine.posmachine import PosMachine
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.creditcard.creditcard import CreditCard
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="Key_C", appliable_receptacle=None, appliable_state=None)
creditcard = CreditCard(item_type="creditcard", item_name="CreditCard", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Locker", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="1592", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[keylock_A, keylock_B, keylock_C, numberlock, puzzle_A]

box=NonLockBox(
    id="Box",
    interactable_states={
        creditcard: {"open"}
    }
)
locker=SingleLocker(
    id="Locker",
    interactable_states={
        key_B: {"open"},
        keylock_A: {"locked"}
    }   
)

safe=Safe(
    id="Safe",
    interactable_states={
        key_A: {"open"},
        numberlock: {"locked"}
    }
)

posmachine=PosMachine(
    id="PosMachine",
    interactable_states={
        puzzle_A: {"on"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_C: {"locked"}
    }
)

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        key_C: {"open"},
        keylock_B: {"locked"}
    }
)

safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
locker.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
closet.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
exitdoor.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))

north_wall = WallState("NORTH", [locker])
west_wall = WallState("WEST", [exitdoor, closet])
south_wall = WallState("SOUTH", [safe])
east_wall = WallState("EAST", [posmachine])

hint_messages = {
    '': "Solve the NumberLock in the Safe at the south wall. The answer is 1592",
    'solved_NumberLock': "Pick up Key_A from the Safe at the south wall",
    'picked_Key_A': "Use Key_A to unlock the Locker at the north wall",
    'used Key_A': "Pick up Key_B from the Locker at the north wall",
    'picked_Key_B': "Use Key_B to unlock the Closet at the west wall",
    'used Key_B': "Pick up Key_C from the Closet at the west wall",
    'picked_Key_C': "Use Key_C to unlock the Door at the west wall",
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
