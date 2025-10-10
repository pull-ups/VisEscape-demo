from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.hourglass.hourglass import Hourglass
from vis_escape.objects.receptacles.suitcase.suitcase import Suitcase
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.idcard.idcard import IDCard
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)

idcard = IDCard(item_type="ID_card", item_name="IDcard", appliable_receptacle=None, appliable_state=None)

puzzle = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
idcardlock=KeyLock(item_type="lock", item_name="Idcardlock", question_text="", answer=f"use {idcard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer="1246", appliable_receptacle="Suitcase", appliable_state="locked", after_solve_state="open")
englishlock=NonKeyLock(item_type="lock", item_name="Englishlock", question_text="", answer="jobs", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle, keylock_A, idcardlock, numberlock, englishlock]

hourglass=Hourglass(
    id="Hourglass",
    interactable_states={
    }
)
lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        keylock_A:{"locked"},
        puzzle:{"open"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        englishlock:{"locked"},
        idcard:{"open"}
    }
)
suitcase=Suitcase(
    id="Suitcase",
    interactable_states={
        numberlock:{"locked"},
        key_A:{"open"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        idcardlock:{"locked"},
        
    }
)

suitcase.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
lockdesk.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
exitdoor.add_transition("locked", f"use {idcard.item_name}", "open", HasItemRule(idcard.item_name))

north_wall = WallState("NORTH", [hourglass])
west_wall = WallState("WEST", [suitcase])
south_wall = WallState("SOUTH", [lockdesk, safe])
east_wall = WallState("EAST", [exitdoor])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_clear_condition("Door", "open")

hint_messages={
    '': "Solve the Numberlock at the Suitcase at the west wall. The answer is '1246'",
    'solved_Numberlock': "Pick up key_A at the Suitcase at the west wall",
    'picked_key_A': "Use key_A to unlock the Desk at the south wall",
    'used key_A': "Solve the Englishlock at the Safe at the south wall. The answer is 'jobs'",
    'solved_Englishlock': "Pick up IDcard at the Safe at the south wall",
    'picked_IDcard': "Use IDcard to unlock the Door at the east wall",
    'used IDcard': "Open the Door at the east wall"
}
game_state.set_hint_message(hint_messages)
