import os
from typing import List

init_prompt = """You are an AI agent playing a room escape game. The room is surrounded by 4 walls, and you can explore other walls by "turn_to_[direction]". Each wall has objects that you can interact with, and you can inspect the object by "inspect [object]". Please read the given information and task description below carefully and respond accordingly."""


def get_prompt_next_action_withreason(direction: str, current_scene_desc: str, inventory: List[str], salient_action_history: List[str], action_history: List[str], previous_action: str, available_actions: List[str], ispuzzle: bool, hint_message: str) -> str:
    puzzle_text1="""<ANSWER> is an action to input the answer to open the lock you are facing. When you choose <ANSWER>, you should follow this format: "<ANSWER>your answer</ANSWER>".""" if ispuzzle else ""
    puzzle_text2="""or <ANSWER>your answer</ANSWER>""" if ispuzzle else ""

    action_history = "\n".join([f"{action['action']}" for action in action_history])
    salient_action_history = "\n".join([f"{action['action']}" for action in salient_action_history])

    salient_action_history_text = f"<Action Memory>\n{salient_action_history}</Action Memory>\n" if salient_action_history else ""
    action_history_text = f"<Recent actions(from oldest to latest)>\n{action_history}</Recent actions>\n" if action_history else ""
    inventory_text = "<Inventory>You have nothing.</Inventory>" if not inventory else f"<Inventory>You have {inventory}.</Inventory>"
    hint_message_text = f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    hint_guideline_text = "If there is a hint message, you should choose action to accomplish the guideline in hint message." if hint_message else ""
    available_actions=available_actions+["<ANSWER> [your answer]"] if ispuzzle else available_actions

    prompt = f"""{init_prompt}. 
{salient_action_history_text}{action_history_text}
<Current Observation>{direction} side of room - {current_scene_desc}</Current Observation>
{inventory_text}
<Your action before this turn>{previous_action}</Your action before this turn>
{hint_message_text}
Here is the task:
Based on these information, choose next action to progress in the game. You must choose one of the following actions:
{available_actions}
{puzzle_text1}
{hint_guideline_text} Your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action {puzzle_text2}, no other text.
[ACTION]"""
    return prompt


def get_prompt_next_action_withreason_vlm(direction: str, current_scene_desc: str, inventory: List[str], salient_action_history: List[str], action_history: List[str], previous_action: str, available_actions: List[str], ispuzzle: bool, hint_message: str) -> str:
    puzzle_text1="""<ANSWER> is an action to input the answer to open the lock you are facing. When you choose <ANSWER>, you should follow this format: "<ANSWER>your answer</ANSWER>".""" if ispuzzle else ""
    puzzle_text2="""or <ANSWER>your answer</ANSWER>""" if ispuzzle else ""


    action_history = "\n".join([f"{action['action']}" for action in action_history])
    salient_action_history = "\n".join([f"{action['action']}" for action in salient_action_history])

    salient_action_history_text = f"<Action Memory>\n{salient_action_history}</Action Memory>\n" if salient_action_history else ""
    action_history_text = f"<Recent actions(from oldest to latest)>\n{action_history}</Recent actions>\n" if action_history else ""
    inventory_text = "<Inventory>You have nothing.</Inventory>" if not inventory else f"<Inventory>You have {inventory}.</Inventory>"
    hint_message_text = f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    hint_guideline_text = "If there is a hint message, you should choose action to accomplish the guideline in hint message." if hint_message else ""
    available_actions=available_actions+["<ANSWER> [your answer]"] if ispuzzle else available_actions

    prompt = f"""{init_prompt}. 
{salient_action_history_text}{action_history_text}
<Current Observation>{direction} side of room - [IMAGE]</Current Observation>
{inventory_text}
<Your action before this turn>{previous_action}</Your action before this turn>
{hint_message_text}
Here is the task:
Based on these information, choose next action to progress in the game. You must choose one of the following actions:
{available_actions}
{puzzle_text1}
{hint_guideline_text} Your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action {puzzle_text2}, no other text.
[ACTION]"""
    return prompt


def get_prompt_next_action_first_turn(direction: str, current_scene_desc: str, inventory: List[str], available_actions: List[str]) -> str:
    prompt=f"""{init_prompt}. 
<Current Observation>{direction} side of room - {current_scene_desc}</Current Observation>

Based on these information, choose next action to progress in the game. You can do one of the following actions:
{available_actions}
Your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action, no other text.
[ACTION]"""
    return prompt


def get_prompt_next_action_first_turn_vlm(direction: str, current_scene_desc: str, inventory: List[str], available_actions: List[str]) -> str:
    prompt=f"""{init_prompt}. 
<Current Observation>{direction} side of room - [IMAGE]</Current Observation>

Based on these information, choose next action to progress in the game. You can do one of the following actions:
{available_actions}
Your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action, no other text.
[ACTION]"""
    return prompt





def get_prompt_next_action_withreason_retry(direction: str,  before_action: str, available_actions: List[str], hint_message: str) -> str:
    
    hint_message_text = f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    hint_guideline_text = "If there is a hint message, you should choose action to accomplish the guideline in hint message." if hint_message else ""
    prompt = f"""{init_prompt}. 
<Current Observation>{direction} side of room</Current Observation>
<Your Previous Action> {before_action}
{hint_message_text}
<Available Actions> {available_actions}
You just performed the <Your Previous Action>, but that action is not currently available in <Available Actions>. Referring to your memory, choose an action that is necessary to perform <Your Previous Action>.
{hint_guideline_text}
You should choose one of the following actions:
{available_actions}
Please respond following below format without any other text:
[ACTION]"""
    return prompt




