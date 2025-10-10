from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.bed.bed import Bed
from vis_escape.objects.receptacles.tv.tv import TV
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.remotecontrol.remotecontrol import RemoteControl
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)
remotecontrol = RemoteControl(item_type="remotecontrol", item_name="RemoteControl", appliable_receptacle=None, appliable_state=None)

screen = Puzzle(item_type="puzzle", item_name="Screen", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Briefcase", appliable_state="locked", after_solve_state="open")
remotecontrol_sensor=KeyLock(item_type="lock", item_name="RemoteControlSensor", question_text="", answer=f"use {remotecontrol.item_name}", appliable_receptacle="TV", appliable_state="off", after_solve_state="on")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="9732", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[screen, keylock_A, keylock_B, numberlock, remotecontrol_sensor]

bed=Bed(
    id="Bed",
    interactable_states={
        remotecontrol : {"bed_without_pillow"}
    }
)
tv=TV(
    id="TV",
    interactable_states={
        remotecontrol_sensor : {"off"},
        screen : {"on"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        numberlock: {"locked"},
        key_A: {"open"}
    }
)
closet=ClosetLocked(
    id="Closet",
    interactable_states={
        keylock_A: {"locked"},
        key_B: {"open"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        keylock_B: {"locked"}
    }
)

tv.add_transition("off", f"use {remotecontrol.item_name}", "on", HasItemRule(remotecontrol.item_name))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
closet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
exitdoor.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))

north_wall = WallState("NORTH", [closet])
west_wall = WallState("WEST", [exitdoor])
south_wall = WallState("SOUTH", [tv, safe])
east_wall = WallState("EAST", [bed])

hint_messages = {
    '': 'Pick up the RemoteControl under the pillow on the Bed at the east wall.',
    'picked_RemoteControl': 'Use the RemoteControl to turn on the TV at the south wall.',
    'used RemoteControl': 'Solve the NumberLock in the Safe at the south wall. The answer is 9732',
    'solved_NumberLock': 'Pick up Key_A from the Safe at the south wall',
    'picked_Key_A': 'Use Key_A to unlock the Closet at the north wall',
    'used Key_A': 'Pick up Key_B from the Closet at the north wall',
    'picked_Key_B': 'Use Key_B to unlock the Door at the west wall',
    'used Key_B': 'Open the Door at the west wall',
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
