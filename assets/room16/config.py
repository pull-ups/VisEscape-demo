from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.oakbarrel.oakbarrel import OakBarrel
from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.entrancecard.entrancecard import EntranceCard
from vis_escape.objects.items.hammer.hammer import Hammer
from vis_escape.objects.items.lock.key_lock import KeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)

entrancecard = EntranceCard(item_type="entrancecard", item_name="EntranceCard", appliable_receptacle=None, appliable_state=None)
hammer = Hammer(item_type="hammer", item_name="Hammer", appliable_receptacle=None, appliable_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")

naillock=KeyLock(item_type="lock", item_name="Nail", question_text="", answer=f"use {hammer.item_name}", appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")
entrancecardlock=KeyLock(item_type="lock", item_name="Keycardlock", question_text="", answer=f"use {entrancecard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="closed")

inspectable_items=[keylock_A, keylock_B, naillock, entrancecardlock]

closet= ClosetLocked(
    id="Closet",
    interactable_states={
        key_B: {"open"},
        keylock_A: {"locked"}
    }
)

lockdesk= LockDesk(
    id="Desk",
    interactable_states={
        entrancecard: {"open"},
        keylock_B: {"locked"}
    }
)

oakbarrel= OakBarrel(
    id="OakBarrel",
    interactable_states={
        hammer: {"open"},
    }
)

lockbox=LockBox(
    id="Box",
    interactable_states={
        key_A: {"open"},
        naillock: {"locked"}
    }
)

exitdoor= LockDoor(
    id="Door",
    interactable_states={
        entrancecardlock: {"locked"}
    }
)

lockbox.add_transition("locked", f"use {hammer.item_name}", "open", HasItemRule(hammer.item_name))
closet.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
lockdesk.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
exitdoor.add_transition("locked", f"use {entrancecard.item_name}", "open", HasItemRule(entrancecard.item_name))

north_wall = WallState("NORTH", [closet])
west_wall = WallState("WEST", [exitdoor, lockbox])
south_wall = WallState("SOUTH", [lockdesk])
east_wall = WallState("EAST", [oakbarrel])

hint_messages = {
    '': "Pick up the Hammer from the OakBarrel at the east wall",
    'picked_Hammer': "Use the Hammer to open the Box at the west wall",
    'used Hammer': "Pick up Key_A from the Box at the west wall",
    'picked_Key_A': "Use Key_A to unlock the Closet at the north wall",
    'used Key_A': "Pick up Key_B from the Closet at the north wall",
    'picked_Key_B': "Use Key_B to unlock the Desk at the south wall",
    'used Key_B': "Pick up the EntranceCard from the Desk at the south wall",
    'picked_EntranceCard': "Use the EntranceCard to unlock the Door at the west wall",
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")
game_state.set_clear_condition("Door", "open")
game_state.set_hint_message(hint_messages)
