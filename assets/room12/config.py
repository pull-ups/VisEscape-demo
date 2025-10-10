from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.cupboard.cupboard import Cupboard
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.entrancecard.entrancecard import EntranceCard
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)

entrancecard = EntranceCard(item_type="entrancecard", item_name="EntranceCard", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
englishlock=NonKeyLock(item_type="lock", item_name="Englishlock", question_text="", answer="BWRB", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
entrancecardlock_A=KeyLock(item_type="lock", item_name="Keycardlock_A", question_text="", answer=f"use {entrancecard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, keylock_A, keylock_B, englishlock, entrancecardlock_A]

cupboard=Cupboard(
    id="Cupboard",
    interactable_states={
        key_A: {"open"},
    }
)
lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        puzzle_A: {"open"},
        keylock_A: {"locked"}
    }
)

safe=Safe(
    id="Safe",
    interactable_states={
        englishlock: {"locked"},
        key_B: {"open"}
    }
)

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        entrancecard: {"open"},
        keylock_B: {"locked"},
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        entrancecardlock_A: {"locked"}
    }
)

lockdesk.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
closet.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
exitdoor.add_transition("locked", f"use {entrancecard.item_name}", "open", HasItemRule(entrancecard.item_name))

north_wall = WallState("NORTH", [cupboard])
west_wall = WallState("WEST", [exitdoor, closet])
south_wall = WallState("SOUTH", [lockdesk])
east_wall = WallState("EAST", [safe])

hint_messages = {
    '': "Open the Cupboard at the north wall to pick up Key_A",
    'picked_Key_A': "Use Key_A to unlock the Desk at the south wall",
    'used Key_A': "Solve the English lock in the Safe at the east wall. The answer is BWRB",
    'solved_Englishlock': "Pick up Key_B in the Safe at the east wall",
    'picked_Key_B': "Use Key_B to unlock the Closet at the west wall",
    'used Key_B': "Pick up EntranceCard in the Closet at the west wall",
    'picked_EntranceCard': "Use EntranceCard to unlock the Door at the west wall"
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_clear_condition("Door", "open")
game_state.set_hint_message(hint_messages)
