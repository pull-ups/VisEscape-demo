from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.kiosk.kiosk import Kiosk
from vis_escape.objects.receptacles.refrigerator.refrigerator_locked import Refrigerator
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.entrancecard.entrancecard import EntranceCard
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key = Key(item_type="key", item_name="Key", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_B = Puzzle(item_type="puzzle", item_name="Image2", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

entrancecard = EntranceCard(item_type="entrancecard", item_name="EntranceCard", appliable_receptacle=None, appliable_state=None)

keylock=KeyLock(item_type="lock", item_name="Keylock", question_text="", answer=f"use {key.item_name}", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
entrancecardlock=KeyLock(item_type="lock", item_name="Keycardlock_A", question_text="", answer=f"use {entrancecard.item_name}", appliable_receptacle="Refrigerator", appliable_state="locked", after_solve_state="closed")
numberlock=NonKeyLock(item_type="lock", item_name="NumberLock", question_text="", answer="2739", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")
englishlock=NonKeyLock(item_type="lock", item_name="EnglishLock", question_text="", answer="mars", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, puzzle_B, keylock, numberlock, englishlock, entrancecardlock]

kiosk=Kiosk(
    id="Kiosk",
    interactable_states={
        puzzle_A: {"on"},
    }
)

safe=Safe(
    id="Safe",
    interactable_states={
        entrancecard: {"open"},
        englishlock: {"locked"}
    }
)

lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        puzzle_B: {"open"},
        keylock: {"locked"},
    }
)

refrigerator=Refrigerator(
    id="Refrigerator",
    interactable_states={
        key: {"open"},
        entrancecardlock: {"locked"}
    }
)

exitdoor=LockDoor(
    id="Door",
    interactable_states={
        numberlock: {"locked"},
    }
)

safe.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{englishlock.item_name}"))
refrigerator.add_transition("locked", f"use {entrancecard.item_name}", "open", HasItemRule(entrancecard.item_name))
lockdesk.add_transition("locked", f"use {key.item_name}", "open", HasItemRule(key.item_name))
exitdoor.add_transition("locked", "unlock", "closed", TriggerActiveRule(f"solved_{numberlock.item_name}"))

north_wall = WallState("NORTH", [kiosk])
west_wall = WallState("WEST", [exitdoor, refrigerator])
south_wall = WallState("SOUTH", [safe])
east_wall = WallState("EAST", [lockdesk])

hint_messages = {
    '': "Solve the EnglishLock in the Safe at the south wall. The answer is 'mars'",
    'solved_EnglishLock': "Pick up the EntranceCard from the Safe at the south wall",
    'picked_EntranceCard': "Use EntranceCard to unlock the Refrigerator at the west wall",
    'used EntranceCard': "Pick up the Key from the Refrigerator at the west wall",
    'picked_Key': "Use Key to unlock the Desk at the east wall",
    'used Key': "Solve the NumberLock on the Door at the west wall. The answer is '2739'",
}

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_hint_message(hint_messages)

game_state.set_clear_condition("Door", "open")
