from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.refrigerator.refrigerator_locked import Refrigerator
from vis_escape.objects.receptacles.coffeemachine.coffeemachine import CoffeeMachine
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.drawer.single_drawer_locked import SingleDrawerLocked

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.entrancecard.entrancecard import EntranceCard
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="key_B", appliable_receptacle=None, appliable_state=None)
key_C = Key(item_type="key", item_name="key_C", appliable_receptacle=None, appliable_state=None)

entrancecard = EntranceCard(item_type="entrancecard", item_name="EntranceCard", appliable_receptacle=None, appliable_state=None)

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Refrigerator", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
keylock_C=KeyLock(item_type="lock", item_name="Keylock_C", question_text="", answer=f"use {key_C.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
entrancecardlock_A=KeyLock(item_type="lock", item_name="Keycardlock_A", question_text="", answer=f"use {entrancecard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
numberlock_A=NonKeyLock(item_type="lock", item_name="Numberlock_A", question_text="", answer=f"3542", appliable_receptacle="2TierDrawer", appliable_state="locked", after_solve_state="open")

inspectable_items=[keylock_A, keylock_B, keylock_C, numberlock_A, entrancecardlock_A]

refrigerator=Refrigerator(
    id="Refrigerator",
    interactable_states={
        keylock_A: {"locked"}
    }
)

coffeemachine=CoffeeMachine(
    id="Coffeemachine",
    interactable_states={
        key_A: {"empty"},
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        entrancecardlock_A: {"locked"}
    }
)

lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        entrancecard: {"open"},
        keylock_C: {"locked"}
    }
)

safe=Safe(
    id="Safe",
    interactable_states={
        key_C: {"open"},
        keylock_B: {"locked"}
    }
)
doubledrawer=SingleDrawerLocked(
    id="2TierDrawer",
    interactable_states={
        key_B: {"open"},
        numberlock_A: {"locked"}
    }
)

doubledrawer.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock_A.item_name}"))
refrigerator.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
safe.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
lockdesk.add_transition("locked", f"use {key_C.item_name}", "open", HasItemRule(key_C.item_name))
exitdoor.add_transition("locked", f"use {entrancecard.item_name}", "open", HasItemRule(entrancecard.item_name))

north_wall = WallState("NORTH", [refrigerator])
east_wall = WallState("EAST", [coffeemachine, exitdoor])
south_wall = WallState("SOUTH", [lockdesk, safe])
west_wall = WallState("WEST", [doubledrawer])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")

hint_messages={
    '': "Pour coffee in the CoffeeMachine at the east wall",
    'pour coffee': "Pick up key_A in the CoffeeMachine at the east wall",
    "picked_key_A": "Use key_A to unlock the Refrigerator at the north wall",
    "used key_A": "Solve the Numberlock_A in the first tier of the 2TierDrawer at the west wall. The answer is 3542",
    "solved_Numberlock_A": "Pick up key_B in the first tier of the 2TierDrawer at the west wall.",
    "picked_key_B": "Use Keylock_B to unlock the safe at the south wall",
    "used key_B": "Pick up key_C in the safe at the south wall",
    "picked_key_C": "Use Keylock_C to unlock the desk at the south wall",
    "used key_C": "Pick up entrancecard in the desk at the south wall",
    "picked_EntranceCard": "Use entrancecard to unlock the door at the east wall"
}
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
