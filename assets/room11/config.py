from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.sink.sink import Sink
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.button.button import Button
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(
    item_type="puzzle",
    item_name="Image1",
    appliable_receptacle=None,
    appliable_state=None,
    after_solve_state=None
)

button = Button(
    item_type="button",
    item_name="Button",
    appliable_receptacle="Door",
    appliable_state="locked",
    after_solve_state="closed"
)

keylock_A = KeyLock(
    item_type="lock",
    item_name="Keylock_A",
    question_text="",
    answer=f"use {key_A.item_name}",
    appliable_receptacle="Closet",
    appliable_state="locked",
    after_solve_state="open"
)

keylock_B = KeyLock(
    item_type="lock",
    item_name="Keylock_B",
    question_text="",
    answer=f"use {key_B.item_name}",
    appliable_receptacle="Desk",
    appliable_state="locked",
    after_solve_state="open"
)

numberlock = NonKeyLock(
    item_type="lock",
    item_name="Numberlock",
    question_text="",
    answer="4331",
    appliable_receptacle="Safe",
    appliable_state="locked",
    after_solve_state="open"
)

inspectable_items=[puzzle_A, keylock_A, keylock_B, numberlock]

sink=Sink(
    id="Sink",
    interactable_states={
        puzzle_A: {"open"},
    }
)

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        key_B: {"open"},
        keylock_A: {"locked"},
    }
)

safe=Safe(
    id="Safe",
    interactable_states={
        key_A: {"open"},
        numberlock: {"locked"}
    }
)

desk=LockDesk(
    id="Desk",
    interactable_states={
        button: {"open"},
        keylock_B: {"locked"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        
    }
)

closet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
desk.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))

north_wall = WallState("NORTH", [sink])
south_wall = WallState("SOUTH", [closet])
east_wall = WallState("EAST", [safe])
west_wall = WallState("WEST", [exitdoor, desk])

hint_messages = {
    '': "Solve the Numberlock of the Safe at the east wall. The answer is 4331",
    'solved_Numberlock': "Pick up Key_A in the Safe at the east wall",
    'picked_Key_A': "Use Key_A to unlock the Closet at the south wall",
    'used Key_A': "Pick up Key_B in the Closet at the south wall",
    'picked_Key_B': "Use Key_B to unlock the Desk at the west wall",
    'used Key_B': "Press the Button in the Desk at the west wall",
    'press Button': "Open the Door at the west wall",
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_clear_condition("Door", "open")
game_state.set_hint_message(hint_messages)
