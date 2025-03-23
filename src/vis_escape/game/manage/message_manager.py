from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from vis_escape.game.manage.game_state import GameState


class ViewType(Enum):
    WALL = "WALL"
    RECEPTACLE = "RECEPTACLE"
    ITEM = "ITEM"


class ActionType(Enum):
    # Wall View Actions
    TURN = auto()  # WV->WV, OV->WV, IV->WV
    INSPECT = auto()  # WV->OV, OV->IV

    # Common Actions
    STEP_BACK = auto()  # OV->WV, IV->OV

    # Object/Item Interactions
    USE_VALID = auto()  # State changes within OV/IV
    USE_INVALID = auto()  # No state change
    PICK = auto()  # State changes within OV
    RECEPTACLE_ACTION = auto()  # Custom actions defined for receptacle


@dataclass
class ViewTransition:
    from_view: ViewType
    to_view: ViewType
    action_type: ActionType
    target_id: Optional[str] = None
    success: bool = True


class MessageManager:
    def get_transition_message(
        self,
        prev_state: GameState,
        current_state: GameState,
        action_type: ActionType,
        image_caption: Optional[str] = None,
        action: Optional[str] = None,
    ) -> dict:
        transition = ViewTransition(
            from_view=ViewType(prev_state.current_view),
            to_view=ViewType(current_state.current_view),
            action_type=action_type,
        )

        messages = {}

        if action_type == ActionType.TURN:
            transition.target_id = current_state.current_wall
            messages = self._get_turn_message(transition, action)
        elif action_type == ActionType.INSPECT:
            transition.target_id = action.split(" ")[1]
            messages = self._get_inspect_message(transition, action)
        elif action_type == ActionType.STEP_BACK:
            transition.target_id = None
            messages = self._get_step_back_message(transition, action)
        elif action_type == ActionType.USE_VALID:
            transition.target_id = action.split(" ")[1]
            messages = self._get_use_message(transition, valid=True, action=action)
        elif action_type == ActionType.USE_INVALID:
            transition.target_id = action.split(" ")[1]
            messages = self._get_use_message(transition, valid=False, action=action)
        elif action_type == ActionType.PICK:
            transition.target_id = action.split(" ")[1]
            messages = self._get_pick_message(transition, action)
        elif action_type == ActionType.RECEPTACLE_ACTION:
            transition.target_id = current_state.current_item
            messages = self._get_receptacle_action_message(transition, action)
        else:
            messages = {
                "action_message": "Action performed.",
                "after_state_message": "Observe current state.",
            }

        if image_caption:
            messages["after_state_message"] = image_caption

        return messages

    def _get_turn_message(
        self, transition: ViewTransition, action: Optional[str] = None
    ) -> dict:
        if transition.from_view == ViewType.WALL:
            return {
                "action_message": f"Turned to face the {transition.target_id} wall.",
                "after_state_message": "",
            }
        else:
            return {
                "action_message": f"Moved away from previous view to look at the {transition.target_id} wall.",
                "after_state_message": "",
            }

    def _get_inspect_message(
        self, transition: ViewTransition, action: Optional[str] = None
    ) -> dict:
        if transition.from_view == ViewType.WALL:
            return {
                "action_message": f"Taking a closer look at {transition.target_id}.",
                "after_state_message": "",
            }
        elif transition.from_view == ViewType.RECEPTACLE:
            return {
                "action_message": f"Examining {transition.target_id} in detail.",
                "after_state_message": "",
            }
        return {"action_message": "", "after_state_message": ""}

    def _get_step_back_message(
        self, transition: ViewTransition, action: Optional[str] = None
    ) -> dict:
        if transition.from_view == ViewType.ITEM:
            return {
                "action_message": "Stepping back to look more broadly.",
                "after_state_message": "",
            }
        elif transition.from_view == ViewType.RECEPTACLE:
            return {
                "action_message": "Stepping back to look more broadly.",
                "after_state_message": "",
            }
        return {"action_message": "", "after_state_message": ""}

    def _get_use_message(
        self, transition: ViewTransition, valid: bool, action: Optional[str] = None
    ) -> dict:
        if valid:
            return {
                "action_message": f"Successfully used the {transition.target_id}.",
                "after_state_message": "",
            }
        else:
            return {"action_message": f"Nothing happened.", "after_state_message": ""}

    def _get_pick_message(
        self, transition: ViewTransition, action: Optional[str] = None
    ) -> dict:
        return {
            "action_message": f"Picked up {transition.target_id}.",
            "after_state_message": "",
        }

    def _get_receptacle_action_message(
        self, transition: ViewTransition, action: Optional[str] = None
    ) -> dict:
        return {"action_message": action, "after_state_message": ""}
