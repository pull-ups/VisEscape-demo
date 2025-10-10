from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.bed.bed import Bed
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.locker.single_locker import SingleLocker
from vis_escape.objects.receptacles.bookshelf.moving_bookshelf import MovingBookshelf
from vis_escape.objects.receptacles.briefcase.briefcase import BriefCase
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.cabinet.cabinet import Cabinet

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.screwdriver.screwdriver import Screwdriver
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)
key_D = Key(item_type="key", item_name="key_D", appliable_receptacle=None, appliable_state=None)
screwdriver=Screwdriver(item_type="screwdriver", item_name="Screwdriver", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_B=Puzzle(item_type="puzzle", item_name="Image2", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Cabinet", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Locker", appliable_state="locked", after_solve_state="open")
keylock_D=KeyLock(item_type="lock", item_name="Keylock_D", question_text="", answer=f"use {key_D.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

numberlock=NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer="3225", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
englishlock=NonKeyLock(item_type="lock", item_name="Englishlock", question_text="", answer="john", appliable_receptacle="Briefcase", appliable_state="locked", after_solve_state="open")

screwdriverlock=KeyLock(item_type="lock", item_name="Lock", question_text="", answer=f"use {screwdriver.item_name}", appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, puzzle_B, keylock_A, keylock_B, keylock_C, keylock_D, numberlock, englishlock, screwdriverlock]

locker=SingleLocker(
    id="Locker",
    interactable_states={
        key_D: {"open"},
        keylock_C: {"locked"}
    }
)
briefcase=BriefCase(
    id="Briefcase",
    interactable_states={
        englishlock: {"locked"},
        puzzle_B: {"open"},
    }
)
bookshelf=MovingBookshelf(
    id="Bookshelf",
    interactable_states={
        key_A: {"moved"},
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_D: {"locked"},
    }
)
lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        keylock_B: {"locked"},
        key_C: {"open"},
    }
)
lockbox=LockBox(
    id="Box",
    interactable_states={
        puzzle_A: {"open"},
        screwdriverlock: {"locked"},
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        numberlock: {"locked"},
        key_B: {"open"},
    }
)
cabinet=Cabinet(
    id="Cabinet",
    interactable_states={
        keylock_A: {"locked"},
        screwdriver: {"open"},
    }
)
bed=Bed(
    id="Bed",
    interactable_states={
    }
)

cabinet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
lockbox.add_transition("locked", f"use {screwdriver.item_name}", "open", HasItemRule(screwdriver.item_name))
briefcase.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
lockdesk.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
locker.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))
exitdoor.add_transition("locked", f"use {key_D.item_name}", "open", HasItemRule(key_D.item_name))

north_wall = WallState("NORTH", [locker, briefcase])
east_wall = WallState("EAST", [safe, cabinet, bed])
south_wall = WallState("SOUTH", [bookshelf, exitdoor])
west_wall = WallState("WEST", [lockdesk, lockbox])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="SOUTH")
game_state.set_clear_condition("Door", "open")

hint_messages={
    "": "Pick up key_A at the Bookshelf at the south wall",
    "picked_key_A": "Use key_A to unlock the Cabinet at the east wall",
    "used key_A": "Pick up Screwdriver at the Cabinet at the east wall",
    "picked_Screwdriver": "Use Screwdriver to unlock the Box at the west wall",
    "used Screwdriver": "Solve the Englishlock at the Briefcase at the south wall. The answer is 'john'",
    "solved_Englishlock": "Solve the Numberlock at the Safe at the east wall. The answer is '3225'",
    "solved_Numberlock": "Pick up key_B at the Safe at the east wall",
    "picked_key_B": "Use key_B to unlock the Desk at the west wall",
    "used key_B": "Pick up key_C at the Desk at the west wall",
    "picked_key_C": "Use key_C to unlock the Locker at the north wall",
    "used key_C": "Pick up key_D at the Locker at the north wall",
    "picked_key_D": "Use key_D to unlock the Door at the south wall",
    "used key_D": "Open the Door at the south wall"
}
game_state.set_hint_message(hint_messages)
