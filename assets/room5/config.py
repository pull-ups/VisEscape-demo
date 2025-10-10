from vis_escape.game.core.rules import HasItemRule, TriggerActiveRule
from vis_escape.game.manage.game_state import GameState, WallState

from vis_escape.objects.receptacles.drawer.double_drawer_second_locked import DoubleDrawerSecondLocked
from vis_escape.objects.receptacles.microwave.microwave import Microwave
from vis_escape.objects.receptacles.coffeemachine.coffeemachine import CoffeeMachine
from vis_escape.objects.receptacles.closet.closet_locked import ClosetLocked
from vis_escape.objects.receptacles.desk.lock_desk import LockDesk
from vis_escape.objects.receptacles.box.lock_box import LockBox
from vis_escape.objects.receptacles.safe.safe import Safe
from vis_escape.objects.receptacles.door.lock_door import LockDoor

from vis_escape.objects.items.key.key import Key
from vis_escape.objects.items.nipper.nipper import Nipper
from vis_escape.objects.items.button.button import Button
from vis_escape.objects.items.puzzle.puzzle import Puzzle
from vis_escape.objects.items.lock.key_lock import KeyLock
from vis_escape.objects.items.lock.non_key_lock import NonKeyLock

key_A = Key(item_type="key", item_name="Key_A", appliable_receptacle=None, appliable_state=None)
key_B = Key(item_type="key", item_name="Key_B", appliable_receptacle=None, appliable_state=None)

nipper=Nipper(item_type="nipper", item_name="Nipper", appliable_receptacle=None, appliable_state=None)

puzzle_A = Puzzle(item_type="puzzle", item_name="Image1", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_B = Puzzle(item_type="puzzle", item_name="Image2", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_C = Puzzle(item_type="puzzle", item_name="Image3", appliable_receptacle=None, appliable_state=None, after_solve_state=None)
puzzle_D = Puzzle(item_type="puzzle", item_name="Image4", appliable_receptacle=None, appliable_state=None, after_solve_state=None)

button = Button(item_type="button", item_name="Button", appliable_receptacle="2TierDrawer", appliable_state="first_open_second_locked", after_solve_state="first_open_second_open")

keylock_A=KeyLock(item_type="lock", item_name="Keylock_A", question_text="", answer=f"use {key_A.item_name}", appliable_receptacle="Safe", appliable_state="locked", after_solve_state="open")
keylock_B=KeyLock(item_type="lock", item_name="Keylock_B", question_text="", answer=f"use {key_B.item_name}", appliable_receptacle="Box", appliable_state="locked", after_solve_state="open")

chains=KeyLock(item_type="lock", item_name="Chains", question_text="", answer=f"use {nipper.item_name}", appliable_receptacle="Closet", appliable_state="locked", after_solve_state="open")

numberlock_A=NonKeyLock(item_type="lock", item_name="Numberlock_A", question_text="", answer="4321", appliable_receptacle="Desk", appliable_state="locked", after_solve_state="open")
numberlock_B=NonKeyLock(item_type="lock", item_name="Numberlock_B", question_text="", answer="4127", appliable_receptacle="Door", appliable_state="locked", after_solve_state="open")

inspectable_items=[puzzle_A, puzzle_B, puzzle_C, puzzle_D, keylock_A, keylock_B, numberlock_A, numberlock_B]

microwave=Microwave(
    id="Microwave",
    interactable_states={
        nipper: {"open"}
    }
)
doubledrawer=DoubleDrawerSecondLocked(
    id="2TierDrawer",
    interactable_states={
        puzzle_A: {"first_open_second_closed", "first_open_second_locked"},
        puzzle_B: {"first_closed_second_open", "first_open_second_open"},
    }
)
lockdesk=LockDesk(
    id="Desk",
    interactable_states={
        numberlock_A: {"locked"},
        key_A: {"open"}
    }
)
closet=ClosetLocked(
    id="Closet",
    interactable_states={
        chains : {"locked"},
        puzzle_D: {"open"}
    }
)
safe=Safe(
    id="Safe",
    interactable_states={
        keylock_A: {"locked"},
        button: {"open"}
    }
)

lockbox=LockBox(
    id="Box",
    interactable_states={
        keylock_B: {"locked"},
        puzzle_C: {"open"}
    }
)
exitdoor=LockDoor(
    id="Door",
    interactable_states={
        numberlock_B: {"locked"},
    }
)
coffeemachine=CoffeeMachine(
    id="CoffeeMachine",
    interactable_states={
        key_B: {"empty"},
    }
)

lockdesk.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock_A.item_name}"))
safe.add_transition("locked", f"use {key_A.item_name}", "open", HasItemRule(key_A.item_name))

lockbox.add_transition("locked", f"use {key_B.item_name}", "open", HasItemRule(key_B.item_name))
closet.add_transition("locked", f"use {nipper.item_name}", "open", HasItemRule(nipper.item_name))
exitdoor.add_transition("locked", "unlock", "open", TriggerActiveRule(f"solved_{numberlock_B.item_name}"))

north_wall = WallState("NORTH", [microwave, doubledrawer])
west_wall = WallState("WEST", [lockdesk])
south_wall = WallState("SOUTH", [closet, safe, lockbox])
east_wall = WallState("EAST", [coffeemachine, exitdoor])

game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
game_state.set_clear_condition("Door", "open")

def hint_message(game_state):
    
    track1 = {'goal': 'press Button'}
    track2 = {'goal': 'used Key_B'}
    track3 = {'goal': 'used Nipper'}
    
    
    track1_complete = track1['goal'] in game_state.context.get_triggers()
    track2_complete = track2['goal'] in game_state.context.get_triggers()
    track3_complete = track3['goal'] in game_state.context.get_triggers()
    
    
    if all([track1_complete, track2_complete, track3_complete]):
        return "Solve NumberLock at the Door at the east wall. The answer is '4127'"
    
    
    hints = []
    triggers = game_state.context.get_triggers()
    
    
    if not track1_complete:
        if 'solved_Numberlock_A' not in triggers:
            hints.append("Solve the Numberlock at the Desk at the west wall. The answer is '4321'")
        elif 'picked_Key_A' not in triggers:
            hints.append("Pick up Key_A at the Desk at the west wall")
        elif 'used Key_A' not in triggers:
            hints.append("Use Key_A to unlock the Safe at the south wall")
        else:
            hints.append("Press Button at the Safe at the south wall")
    
    
    if not track2_complete:
        if 'picked_Key_B' not in triggers:
            hints.append("Pick up Key_B at the CoffeeMachine at the east wall")
        elif 'used Key_B' not in triggers:
            hints.append("Use Key_B to unlock the Box at the south wall")
    
    
    if not track3_complete:
        if 'picked_Nipper' not in triggers:
            hints.append("Find the Nipper at the Microwave at the north wall")
        elif 'used Nipper' not in triggers:
            hints.append("Use Nipper to cut the chain at the Closet at the south wall")
    
    
    return hints[0] if hints else "Solve the NumberLock at the Door"

game_state.set_hint_message(hint_message)

if __name__ == "__main__":
    game_state = GameState([north_wall, east_wall, south_wall, west_wall], initial_direction="NORTH")
    game_state.context.triggers = {}
    
    print(hint_message(game_state))
