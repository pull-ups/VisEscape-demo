from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.box.non_lock_box import NonLockBox
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.bookshelf.moving_bookshelf_fixed import MovingBookshelfFixed
from vis_escape.objects.receptacles.safe.safe import Safe

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.book.book import Book
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)
book = Book(item_type="book", item_name="Book", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

cabinet=KeyLock(item_type="lock", item_name="Cabinet", question_text="", answer=f"use {book.item_name}", appliable_receptacle="Bookshelf", appliable_state="fixed", after_solve_state="moved")
phone = NonKeyLock(item_type="lock", item_name="Telephone", question_text="", answer="911", 
                           appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, keylock_A, keylock_B, keylock_C, phone, cabinet]

closet=ClosetLocked(
    id="Closet",
    interactable_states={
        keylock_A:{"locked"},
        puzzle_A:{"open"},
    }
)
desk=LockDesk(
    id="Desk",
    interactable_states={
        phone:{"locked", "closed", "open"},
        key_B:{"open"},
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        keylock_B:{"locked"},
        book:{"open"},
    }
)
box=NonLockBox(
    id="Box",
    interactable_states={
        key_A:{"open"},
    }
)
bookshelf=MovingBookshelfFixed(
    id="Bookshelf",
    interactable_states={
        cabinet:{"fixed"},
        key_C:{"moved"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_C:{"locked"},
    }
)

closet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
desk.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{phone.item_name}"))
desk.add_transition("open", "unlock", "open", TriggerActiveRule(f"solved_{phone.item_name}"))
desk.add_transition("closed", "unlock", "open", TriggerActiveRule(f"solved_{phone.item_name}"))
bookshelf.add_transition("fixed", f"use {book.item_name}", "original", HasItemRule(book.item_name))
bookshelf.add_transition("fixed", "push_bookshelf_to_right", "moved", TriggerActiveRule(f"used_{book.item_name}"))
safe.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
exitdoor.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))

north_wall = WallState("NORTH", [closet])
west_wall = WallState("WEST", [bookshelf, exitdoor])
south_wall = WallState("SOUTH", [safe, box])
east_wall = WallState("EAST", [desk])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="SOUTH")

hint_messages={
    '': "Open the Box at the south wall and pick up key_A",
    'picked_key_A': "Use key_A to unlock the Closet at the north wall",
    'used key_A': "Call '911' with the Telephone at the Desk at the east wall",
    'solved_Telephone': 'Pick up key_B at the Bottom of the Desk at the east wall',
    'picked_key_B': "Use key_B to unlock the Safe at the south wall",
    'used key_B': "Pick up Book at the Safe at the south wall",
    'picked_Book': "Put down the Book at the Bookshelf at the west wall",
    'used Book': "Pick up key_C at the Bookshelf at the west wall",
    'picked_key_C': "Use key_C to unlock the Door at the west wall",
    'used key_C' : "Open the Door at the west wall"
}

game_state.set_hint_message(hint_messages)
game_state.set_clear_condition("Door", "open")
