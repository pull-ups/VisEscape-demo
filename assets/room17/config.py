from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.windowblind.windowblind import WindowBlind
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.briefcase.briefcase import BriefCase
from vis_escape.objects.receptacles.computer.computer import Computer
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.usb.usb import USB
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)
usb = USB(item_type="usb", item_name="USB", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
monitor = Puzzle(item_type="puzzle", item_name="Monitor", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Briefcase", appliable_state="locked", after_solve_state="open")
usbslot=KeyLock(item_type="lock", item_name="USBSlot", question_text="", answer=f"use {usb.item_name}", appliable_receptacle="Computer", appliable_state="locked", after_solve_state="unlock")
englishlock=NonKeyLock(item_type="lock", item_name="EnglishLock", question_text="", answer="love", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="203", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, monitor, keylock_A, keylock_B, englishlock, numberlock, usbslot]

windowblind=WindowBlind(
    id="WindowBlinds",
    interactable_states={
        puzzle_A: {"up"}
    }
)

safe=Safe(
    id="Safe",
    interactable_states={
        key_A: {"open"},
        englishlock: {"locked"}
    }
)

lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        key_B: {"open"},
        keylock_A: {"locked"}
    }   
)
briefcase=BriefCase(
    id="Briefcase",
    interactable_states={
        keylock_B: {"locked"},
        usb: {"open"}
    }
)

computer=Computer(
    id="Computer",
    interactable_states={
        usbslot :{"locked"},
        monitor : {"unlock"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        numberlock: {"locked"}
    }
)

safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
lockdesk.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
briefcase.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
computer.add_transition("locked", f"use {usb.item_name}", "unlock", HasItemRule(usb.item_name))
exitdoor.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))

north_wall = WallState("NORTH", [windowblind, safe])
west_wall = WallState("WEST", [exitdoor])
south_wall = WallState("SOUTH", [briefcase, lockdesk])
east_wall = WallState("EAST", [computer])

hint_messages = {
    '': "Raise the WindowBlinds at the north wall to reveal a hint for the Safe. The code is 'love'",
    'solved_EnglishLock': "Pick up Key_A from the Safe at the north wall",
    'picked_Key_A': "Use Key_A to unlock the Desk at the south wall",
    'used Key_A': "Pick up Key_B from the Desk at the south wall",
    'picked_Key_B': "Use Key_B to unlock the Briefcase at the south wall",
    'used Key_B': "Pick up the USB from the Briefcase at the south wall",
    'picked_USB': "Use the USB to unlock the Computer at the east wall",
    'used USB': "Solve the NumberLock on the Door at the west wall. The code is '203'",
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_clear_condition("Door", "open")
game_state.set_hint_message(hint_messages)
