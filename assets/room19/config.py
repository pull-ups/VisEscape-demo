from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.cupboard.cupboard_locked import CupboardLocked
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.wifirouter.wifirouter import WifiRouter
from vis_escape.objects.receptacles.tablet.tablet import Tablet
from vis_escape.objects.receptacles.trashbin.trashbin_unlock import Trashbin

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.screwdriver.screwdriver import Screwdriver
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.wifiantenna.wifiantenna import WifiAntenna
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)
screwdriver = Screwdriver(item_type="screwdriver", item_name="Screwdriver", appliable_receptacle=None, appliable_state=None)
wifiantenna = WifiAntenna(item_type="wifiantenna", item_name="WifiAntenna", appliable_receptacle=None, appliable_state=None)

screen = Puzzle(item_type="puzzle", item_name="Screen", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Cupboard", appliable_state="locked", after_solve_state="open")
screwdriverlock=KeyLock(item_type="lock", item_name="Lock", question_text="", answer=f"use {screwdriver.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="3778", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

inspectable_items=[screen, keylock_A, keylock_B, numberlock, screwdriverlock]

tablet=Tablet(
    id="Tablet",
    interactable_states={
        screen: {"on"}
    }
)
wifirouter=WifiRouter(
    id="WifiRouter",
    interactable_states={
    }
)
trashbin=Trashbin(
    id="TrashBin",
    interactable_states={
        screwdriver: {"open"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        keylock_A: {"locked"},
        key_B: {"open"}
    }
)
closet=ClosetLocked(
    id="Closet",
    interactable_states={
        screwdriverlock: {"locked"},
        key_A: {"open"}
    }
)
cupboard=CupboardLocked(
    id="Cupboard",
    interactable_states={
        keylock_B: {"locked"},
        wifiantenna: {"open"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        numberlock: {"locked"}
    }
)

closet.add_transition("locked", f"use {screwdriver.item_name}", "open", HasItemRule(screwdriver.item_name))
safe.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))
cupboard.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
wifirouter.add_transition("before_connect", f"use {wifiantenna.item_name}", "after_connect", HasItemRule(wifiantenna.item_name))
tablet.add_transition("off", "connect_internet", "on", TriggerActiveRule(f"used {wifiantenna.item_name}"))
exitdoor.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))

north_wall = WallState("NORTH", [tablet, trashbin])
west_wall = WallState("WEST", [closet, wifirouter])
south_wall = WallState("SOUTH", [safe, cupboard])
east_wall = WallState("EAST", [exitdoor])

hint_messages = {
    '' : 'Pick up the Screwdriver from the TrashBin at the north wall',
    'picked_Screwdriver' : 'Use the Screwdriver to open the Closet at the west wall',
    'used Screwdriver' : 'Pick up Key_A from the Closet at the west wall',
    'picked_Key_A' : 'Use Key_A to unlock the Safe at the south wall',
    'used Key_A' : 'Pick up Key_B from the Safe at the south wall',
    'picked_Key_B' : 'Use Key_B to unlock the Cupboard at the south wall',
    'used Key_B' : 'Pick up the WifiAntenna from the Cupboard at the south wall',
    'picked_WifiAntenna' : 'Connect the WifiAntenna to the WifiRouter at the west wall',
    'used WifiAntenna' : 'See the quiz in the Tablet at the north wall, and solve the NumberLock on the Door at the east wall. The code is 3778'
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_hint_message(hint_messages)
game_state.set_clear_condition("Door", "open")
