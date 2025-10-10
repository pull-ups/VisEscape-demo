from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.laptop.laptop import Laptop
from vis_escape.objects.receptacles.poster.poster import Poster
from vis_escape.objects.receptacles.wifirouter.wifirouter import WifiRouter
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.monitor.monitor import Monitor
from vis_escape.objects.items.entrancecard.entrancecard import EntranceCard
from vis_escape.objects.items.wifiantenna.wifiantenna import WifiAntenna
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

entrancecard = EntranceCard(item_type="entrancecard", item_name="EntranceCard", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
monitor = Monitor(item_type="monitor", item_name="Monitor", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
wifiantenna = WifiAntenna(item_type="wifiantenna", item_name="WifiAntenna", appliable_receptacle=None, appliable_state=None)

numberlock=NonKeyLock(item_type="lock", item_name="Numberlock", question_text="", answer="2375", appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")
englishlock=NonKeyLock(item_type="lock", item_name="Englishlock", question_text="", answer="bat", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
entrancecardlock=KeyLock(item_type="lock", item_name="Keycardlock", question_text="", answer=f"use {entrancecard.item_name}", appliable_receptacle="Door", appliable_state="locked", after_solve_state="closed")

inspectable_items=[englishlock, numberlock, entrancecardlock, puzzle_A, monitor]

lockbox=LockBox(
    id="Box",
    interactable_states={
        numberlock:{"locked"},
        wifiantenna:{"open"},   
    }
)
laptop=Laptop(
    id="Laptop",
    interactable_states={
        monitor:{"on"}
    }
)
poster=Poster(
    id="Poster",
    interactable_states={
        puzzle_A:{"default"},
    }
)
wifirouter=WifiRouter(
    id="WifiRouter",
    interactable_states={
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        englishlock:{"locked"},
        entrancecard:{"open"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        entrancecardlock:{"locked"},
        
    }
)

lockbox.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock.item_name}"))
wifirouter.add_transition("before_connect", f"use {wifiantenna.item_name}", "after_connect", HasItemRule(wifiantenna.item_name))
laptop.add_transition("off", "connect_internet", "on", TriggerActiveRule(f"used {wifiantenna.item_name}"))
safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
exitdoor.add_transition("locked", f"use {entrancecard.item_name}", "open", HasItemRule(entrancecard.item_name))

north_wall = WallState("NORTH", [lockbox])
west_wall = WallState("WEST", [wifirouter])
south_wall = WallState("SOUTH", [safe, exitdoor])
east_wall = WallState("EAST", [laptop, poster])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="EAST")
game_state.set_clear_condition("Door", "open")

hint_messages={
    '': "Solve the Numberlock at the Locked Box at the north wall. The answer is '2375'",
    'solved_Numberlock': "Pick up WifiAntenna at the Locked Box at the north wall",
    'picked_WifiAntenna': "Use WifiAntenna to connect to the internet at the Wifi Router at the west wall",
    'used WifiAntenna': "Connect to the internet at the Laptop at the east wall, and get the password for the Englishlock at the Safe at the south wall. The answer is 'bat'",
    'solved_Englishlock': "Pick up EntranceCard at the Safe at the south wall",
    'picked_EntranceCard': "Use EntranceCard to unlock the Door at the south wall",
    'used EntranceCard': "Open the Door at the south wall"
}
game_state.set_hint_message(hint_messages)
