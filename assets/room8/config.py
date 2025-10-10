from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.refrigerator.refrigerator_locked import Refrigerator
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.wardrobe.wardrobe import Wardrobe
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.barcode.barcode import Barcode
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)
barcode = Barcode(item_type="barcode", item_name="Barcode", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_B = Puzzle(item_type="puzzle", item_name="Image2", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Refrigerator", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Wardrobe", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

numberlock = NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer="3571", 
                           appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
englishlock = NonKeyLock(item_type="lock", item_name="Englishlock", question_text="", answer="cold", 
                        appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")
sensorlock = KeyLock(item_type="lock", item_name="Sensorlock", question_text="", answer=f"use {barcode.item_name}",
                        appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

inspectable_items=[keylock_A, keylock_B, keylock_C, numberlock, englishlock, sensorlock, puzzle_A, puzzle_B]

refrigerator=Refrigerator(
    id="Refrigerator",
    interactable_states={
        keylock_A: {"locked"},
        puzzle_B:{"open"}
    }
)
wardrobe=Wardrobe(
    id="Wardrobe",
    interactable_states={
        keylock_B: {"locked"},
        key_C:{"open"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        sensorlock: {"locked"},
    }
)
lockbox=LockBox(
    id="Box",
    interactable_states={
        englishlock: {"locked"},
        key_B:{"open"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        keylock_C: {"locked"},
        barcode:{"open"}
    }
)
lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        numberlock: {"locked"},
        puzzle_A:{"open", "closed", "locked"},
        key_A:{"open"},
    }
)

lockdesk.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
refrigerator.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
lockbox.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
wardrobe.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
safe.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))
exitdoor.add_transition("locked", f"use {barcode.item_name}", "open", HasItemRule(barcode.item_name))

north_wall = WallState("NORTH", [refrigerator])
west_wall = WallState("WEST", [lockdesk])
south_wall = WallState("SOUTH", [wardrobe, exitdoor, lockbox])
east_wall = WallState("EAST", [safe])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="WEST")
game_state.set_clear_condition("Door", "open")

hint_messages={
    '': "Solve the Numberlock at the Desk at the west wall. The answer is '3571'",
    'solved_Numberlock': "Pick up key_A at the Desk at the west wall",
    'picked_key_A': "Use key_A to unlock the Refrigerator at the north wall",
    'used key_A': "Solve the Englishlock at the Locked Box at the south wall. The answer is 'cold'",
    'solved_Englishlock': "Pick up key_B at the Box at the south wall",
    'picked_key_B': "Use key_B to unlock the Wardrobe at the south wall",
    'used key_B': "Pick up key_C at the Wardrobe at the south wall",
    'picked_key_C': "Use key_C to unlock the Safe at the east wall",
    'used key_C': "Pick up Barcode at the Safe at the east wall",
    'picked_Barcode': "Use Barcode to unlock the Door at the south wall",
    'used Barcode': "Open the Door at the south wall"
}
game_state.set_hint_message(hint_messages)
