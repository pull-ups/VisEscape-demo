from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule, AlwaysAllowRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.drawer.double_drawer_second_locked import DoubleDrawerSecondLocked
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.locker.single_locker import SingleLocker
from vis_escape.objects.receptacles.bookshelf.moving_bookshelf_fixed import MovingBookshelfFixed
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.screwdriver.screwdriver import Screwdriver
from vis_escape.objects.items.button.button import Button
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="Key_C", appliable_receptacle=None, appliable_state=None)
screwdriver=Screwdriver(item_type="screwdriver", item_name="Screwdriver", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

button = Button(item_type="button", item_name="Button", appliable_receptacle="Bookshelf", appliable_state="fixed", after_solve_state="moved")

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Locker", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
screwdriverlock=KeyLock(item_type="lock", item_name="Lock", question_text="", answer=f"use {screwdriver.item_name}", appliable_receptacle="Bookshelf", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer="2739", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, keylock_A, keylock_B, keylock_C, numberlock, screwdriverlock]

doubledrawer=DoubleDrawerSecondLocked(
    id="2TierDrawer",
    interactable_states={
        screwdriverlock: {"first_closed_second_locked", "first_open_second_locked"},
        button: {"first_closed_second_open", "first_open_second_open"},
        key_A: {"first_open_second_locked", "first_open_second_closed"}
    }
)
locker=SingleLocker(
    id="Locker",
    interactable_states={
        keylock_A: {"locked"},
        puzzle_A: {"open"},
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        screwdriver: {"open"},
        numberlock: {"locked"}
    }
)

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        keylock_B: {"locked"},
        key_C: {"open"}
    }
)
bookshelf=MovingBookshelfFixed(
    id="Bookshelf",
    interactable_states={
        key_B: {"moved"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_C: {"locked"}
    }
)

locker.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
closet.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
exitdoor.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))
doubledrawer.add_transition("first_open_second_locked", f"use {screwdriver.item_name}", "first_open_second_open", HasItemRule(screwdriver.item_name))
doubledrawer.add_transition("first_closed_second_locked", f"use {screwdriver.item_name}", "first_closed_second_open", HasItemRule(screwdriver.item_name))

north_wall = WallState("NORTH", [locker])
west_wall = WallState("WEST", [bookshelf, exitdoor])
south_wall = WallState("SOUTH", [safe, closet])
east_wall = WallState("EAST", [doubledrawer])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")

hint_messages={
    '': "Pick up key_A in the first tier of the 2TierDrawer at the east wall",
    'picked_Key_A': "Use key_A to unlock the Locker at the north wall",
    'used Key_A': "Solve the Numberlock in the Safe at the south wall. The answer is 2739",
    'solved_Numberlock': "Pick up Screwdriver in the Safe at the south wall",
    'picked_Screwdriver': "Use Screwdriver to unlock the second tier of the 2TierDrawer at the east wall",
    'used Screwdriver': "Press Button in the second tier of the 2TierDrawer at the east wall",
    'press Button': "Pick up key_B in the Bookshelf at the west wall",
    'picked_Key_B': "Use key_B to unlock the Closet at the south wall",
    'used Key_B': "Pick up key_C in the Closet at the south wall",
    'picked_Key_C': "Use key_C to unlock the Door at the west wall",
}
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
