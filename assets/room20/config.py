from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.tv.tv import TV
from vis_escape.objects.receptacles.kiosk.kiosk_locked import KioskLocked
from vis_escape.objects.receptacles.refrigerator.refrigerator import Refrigerator
from vis_escape.objects.receptacles.table.foodtable import Table
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
knife = Key(item_type="key", item_name="Knife", appliable_receptacle=None, appliable_state=None)
idcard = Key(item_type="key", item_name="IDCard", appliable_receptacle=None, appliable_state=None)
remotecontrol = Key(item_type="key", item_name="RemoteControl", appliable_receptacle=None, appliable_state=None)

screen1 = Puzzle(item_type="puzzle", item_name="TVScreen", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
screen2 = Puzzle(item_type="puzzle", item_name="KioskScreen", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
remotecontrol_sensor=KeyLock(item_type="lock", item_name="RemoteControlSensor", question_text="", answer=f"use {remotecontrol.item_name}", appliable_receptacle="TV", appliable_state="off", after_solve_state="on")

sensorlock=KeyLock(item_type="lock", item_name="Sensorlock", question_text="", answer=f"use {idcard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
bread=KeyLock(item_type="lock", item_name="Bread", question_text="", answer=f"use {knife.item_name}", appliable_receptacle="Table", appliable_state="food_original", after_solve_state="food_cut")
englishlock=NonKeyLock(item_type="lock", item_name="EnglishLock", question_text="", answer="NESW", appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="28", appliable_receptacle="Kiosk", appliable_state="locked", after_solve_state="unlock")

inspectable_items=[screen1, screen2, keylock_A, sensorlock, englishlock, numberlock]

lockbox=LockBox(
    id="Box",
    interactable_states={
        englishlock : {"locked"},
        idcard : {"open"},
    }
)
TV = TV(
    id="TV",
    interactable_states={
        screen1 : {"on"},
        remotecontrol_sensor : {"off"},
    }
)
kiosk = KioskLocked(
    id="Kiosk",
    interactable_states={
        screen2 : {"unlock"},
        numberlock : {"locked"},
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        keylock_A : {"locked"},
        remotecontrol : {"open"},
    }
)
refrigerator=Refrigerator(
    id="Refrigerator",
    interactable_states={
        knife : {"open"},
    }
)
table=Table(
    id="Table",
    interactable_states={
        key_A: {"food_cut"},
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        sensorlock: {"locked"}
    }
)

table.add_transition("food_original", f"use {knife.item_name}", "food_cut", HasItemRule(knife.item_name))
safe.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
TV.add_transition("off", f"use {remotecontrol.item_name}", "on", HasItemRule(remotecontrol.item_name))
kiosk.add_transition("locked", "unlock", "unlock", TriggerActiveRule(f"solved_{numberlock.item_name}"))
lockbox.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
exitdoor.add_transition("locked", f"use {idcard.item_name}", "open", HasItemRule(idcard.item_name))

north_wall = WallState("NORTH", [lockbox, exitdoor])
west_wall = WallState("WEST", [refrigerator, table])
south_wall = WallState("SOUTH", [TV])
east_wall = WallState("EAST", [kiosk, safe])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="WEST")

hint_messages = {
'': 'Pick up the Knife from the Refrigerator at the west wall.',
'picked_Knife' : 'Use the Knife to cut the Bread on the table at the west wall.',
'used Knife' : 'Pick up the Key_A on the table at the west wall.',
'picked_Key_A' : 'Use the Key_A to unlock the Safe at the east wall.',
'used Key_A' : 'Pick up the RemoteControl from the Safe at the east wall.',
'picked_RemoteControl' : 'Use the RemoteControl to turn on the TV at the south wall.',
'used RemoteControl' : 'Solve the NumberLock on the Kiosk at the east wall. The code is 28.',
'solved_NumberLock' : 'Solve the EnglishLock on the Lock Box at the north wall. The code is "NESW".',
'solved_EnglishLock' : 'Pick up the IDCard from the Lock Box at the north wall.',
'picked_IDCard' : 'Use the IDCard to unlock the Door at the north wall.',
}

game_state.set_hint_message(hint_messages)
game_state.set_clear_condition("Door", "open")
