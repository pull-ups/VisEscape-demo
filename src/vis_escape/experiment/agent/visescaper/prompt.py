import os
from typing import List

init_prompt = """You are an AI agent playing a room escape game. The room is surrounded by 4 walls, and you can explore other walls by "turn_to_[direction]". Each wall has objects that you can interact with, and you can inspect the object by "inspect [object]". Please read the given information and task description below carefully and respond accordingly."""


def get_prompt_short_term_planning(
    previous_plan: str,
    inventory: List[str],
    spatial_memory: str,
    action_history: List[str],
) -> str:
    plan_text = (
        f"<Your previous plan>{previous_plan}</Your previous plan>\n"
        if previous_plan
        else ""
    )
    inventory_text = "You have nothing." if not inventory else f"You have {inventory}."
    action_history_str = "\n".join(action_history)
    prompt = f"""{init_prompt}.
{plan_text}
<Inventory>{inventory_text}</Inventory>
<Spatial Memory>{spatial_memory}</Spatial Memory>
<Recent actions(from oldest to latest)>
{action_history_str}</Recent actions>

Here is the definition of each information:
<Your previous plan>: A plan that you have followed until now.
<Inventory>: A list of items that you have in your inventory.
<Spatial Memory>: A memory that tracks and stores information about the state, position, and visual information of objects in your surroundings.
<Recent actions>: Sequence of actions you have performed under your previous plan.

Here is the task:
Analyzing your <Spatial Memory> and <Recent actions>, Make a new plan to progress in the game. Please respond following below format without any other text:
[PLAN]"""
    return prompt


def get_prompt_action_memory_construct(action_history: List[str]) -> str:
    last10history_str = "\n".join(
        [
            f"Observation: [{log['scene']}]\n Action: [{log['action']}]-{log['analysis']}"
            for log in action_history
        ]
    )
    prompt = f"""{init_prompt}.
<Last 10 logs(from oldest to latest)>
{last10history_str}</Last 10 logs>
Here is the definition of each information:
<Last 10 logs>: Sequence of observation, action-effect, next observation, next action-effect for each turn.

Here is the task:
Based on the information that can be derived from the given sequence of logs, extract and remember noteworthy information. 
You should list your memories in a numbered format (e.g., 1., 2., 3.). Please respond following below format without any other text:
[MEMORY]"""
    return prompt


def get_prompt_spatial_memory_construct(action_history: List[str]) -> str:
    spatial_json_format = """{"direction 1" : {
    "objects":["object1", "object2", ...]
},
...}"""
    inspected_objects_json_format = """[{"object 1" : {
    "state":"",
    "characteristics":"",
    "additional info":""
},
...}]"""
    uninspected_objects_json_format = """[]"""
    additional_memory_json_format = (
        """[1. additional memory1, 2. additional memory2, ...]"""
    )

    last10history_str = "\n".join(
        [
            (
                f"Observation: [{log['scene']}]\n Action: [{log['action']}]"
                if log["analysis"] == "-"
                else f"Observation: [{log['scene']}]\n Action: [{log['action']}] - {log['analysis']}"
            )
            for log in action_history
        ]
    )
    prompt = f"""{init_prompt}. 
<Last 10 logs(from oldest to latest)>
{last10history_str}</Last 10 logs>
Here is the definition of information:
<Last 10 logs>: Sequence of observation, action-effect, next observation, next action-effect for each turn.

Here is the task:
Construct your memory about the room, based on the last 10 logs. Follow below guidelines:
1. Identify which objects exist on each directional wall, and add the information to "[SPATIAL MEMORY]" section.
2. If you have inspected an object via "inspect [object]", you should add the information to "[INSPECTED OBJECTS]" section.
3. The objects that you have not inspected via "inspect [object]" should be added to "[UNINSPECTED OBJECTS]" section.
4. Add any information from observations which is not included in [SPATIAL MEMORY] and [INSPECTED OBJECTS] that you think is necessary for solving other problems to the "[Additional Memory]" section. 

Please respond following below format without any other text:
[SPATIAL MEMORY]{spatial_json_format}
[INSPECTED OBJECTS]{inspected_objects_json_format}
[UNINSPECTED OBJECTS]{uninspected_objects_json_format}
[ADDITIONAL MEMORY]{additional_memory_json_format}"""
    return prompt


def get_prompt_spatial_memory_update(
    spatial_memory: str, action_history: List[str]
) -> str:
    spatial_json_format = """{"direction 1" : {
    "objects":["object1", "object2", ...]
},
...}"""
    inspected_objects_json_format = """[{"object 1" : {
    "state":"",
    "characteristics":"",
    "additional info":""
},
...}]"""
    uninspected_objects_json_format = """[]"""
    additional_memory_json_format = (
        """[1. additional memory1, 2. additional memory2, ...]"""
    )

    last10history_str = "\n".join(
        [
            (
                f"Observation: [{log['scene']}]\n Action: [{log['action']}]"
                if log["analysis"] == "-"
                else f"Observation: [{log['scene']}]\n Action: [{log['action']}] - {log['analysis']}"
            )
            for log in action_history
        ]
    )
    prompt = f"""{init_prompt}. 
<Current Memory>
{spatial_memory}</Current Memory>
<Last 10 logs(from oldest to latest)>
{last10history_str}</Last 10 logs>
Here is the definition of each information:
<Last 10 logs>: Sequence of observation, action-effect, next observation, next action-effect for each turn.

Here is the task:
Update your memory about the room, based on the last 10 logs. Follow below guidelines:
1. If you newly inspected an object via "inspect [object]" among objects in "[UNINSPECTED OBJECTS]" section, you should add the information to "[INSPECTED OBJECTS]" section.
2. Based on the information that you can obtain from last 10 logs, update <Current Memory> if there exists any information that you can obtain from <Last 10 logs> but not in <Current Memory>.
3. Add any information not included in spatial memory and inspected objects that you think is necessary for solving other problems to the "[ADDITIONAL MEMORY]" section.
Please respond following below format without any other text:
[SPATIAL MEMORY]{spatial_json_format}
[INSPECTED OBJECTS]{inspected_objects_json_format}
[UNINSPECTED OBJECTS]{uninspected_objects_json_format}
[ADDITIONAL MEMORY]{additional_memory_json_format}"""
    return prompt


def get_prompt_action_feedback(
    previous_scene_desc: str, current_scene_desc: str, previous_action: str
) -> str:
    prompt = f"""{init_prompt}. 
<Previous Observation> : {previous_scene_desc}
<Previous Action> : {previous_action}
<Current Observation> : {current_scene_desc}

Here is the definition of each information:
<Previous Observation> is a description of a scene before your action, and <Current Observation> is a description of a scene after your action. 

Here is the task:
Analyze the effect of your action by comparing <Previous Observation> and <Current Observation>. The analysis should be concise and definitive, not descriptive. Keep it under 10 words.
[ANALYSIS]"""
    return prompt


def get_prompt_next_action_first_turn(
    direction: str,
    current_scene_desc: str,
    inventory: List[str],
    available_actions: List[str],
) -> str:
    prompt = f"""{init_prompt}. 
<Current Observation>{direction} side of room - {current_scene_desc}</Current Observation>

Based on these information, choose next action to progress in the game. You can do one of the following actions:
{available_actions}
Before you act, think first, and then act. Your thought should be in section [THINK], and your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action, no other text.
[THINK]
[ACTION]"""
    return prompt


def get_prompt_next_action_first_turn_vlm(
    direction: str,
    current_scene_desc: str,
    inventory: List[str],
    available_actions: List[str],
) -> str:
    prompt = f"""{init_prompt}. 
<Current Observation>{direction} side of room - [IMAGE]</Current Observation>

Based on these information, choose next action to progress in the game. You can do one of the following actions:
{available_actions}
Before you act, think first, and then act. Your thought should be in section [THINK], and your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action, no other text.
[THINK]
[ACTION]"""
    return prompt


def get_prompt_next_action_withreason(
    direction: str,
    current_scene_desc: str,
    inventory: List[str],
    spatial_memory: str,
    salient_action_history: List[str],
    action_history: List[str],
    previous_react: str,
    available_actions: List[str],
    ispuzzle: bool,
    hint_message: str,
) -> str:
    puzzle_text1 = (
        """<ANSWER> is an action to input the answer to open the lock you are facing. When you choose <ANSWER>, you should follow this format: "<ANSWER>your answer</ANSWER>"."""
        if ispuzzle
        else ""
    )
    puzzle_text2 = """or <ANSWER>your answer</ANSWER>""" if ispuzzle else ""
    action_history = "\n".join(
        [
            (
                f"{action['action']}"
                if action["analysis"] == "-"
                else f"{action['action']} - {action['analysis']}"
            )
            for action in action_history
        ]
    )
    salient_action_history = "\n".join(
        list(
            dict.fromkeys(
                [
                    (
                        f"{action['action']}"
                        if action["analysis"] == "-"
                        else f"{action['action']} - {action['analysis']}"
                    )
                    for action in salient_action_history
                ]
            )
        )
    )

    salient_action_history_text = (
        f"<Action Memory>\n{salient_action_history}</Action Memory>\n"
        if salient_action_history
        else ""
    )
    action_history_text = (
        f"<Recent actions(from oldest to latest)>\n{action_history}</Recent actions>\n"
        if action_history
        else ""
    )
    inventory_text = (
        "<Inventory>You have nothing.</Inventory>"
        if not inventory
        else f"<Inventory>You have {inventory}.</Inventory>"
    )
    memory_text = f"<Memory>\n{spatial_memory}</Memory>\n" if spatial_memory else ""
    hint_message_text = (
        f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    )
    hint_guideline_text = (
        "If there is a hint message, you should choose action to accomplish the guideline in hint message."
        if hint_message
        else ""
    )
    available_actions = (
        available_actions + ["<ANSWER> [your answer]"]
        if ispuzzle
        else available_actions
    )

    prompt = f"""{init_prompt}. 
{memory_text}{salient_action_history_text}{action_history_text}
<Current Observation>{direction} side of room - {current_scene_desc}</Current Observation>
{inventory_text}
<Your Thought and Action before this turn>{previous_react}</Your Thought and Action before this turn>
{hint_message_text}
Here is the task:
Based on these information, choose next action to progress in the game. You must choose one of the following actions:
{available_actions}
{puzzle_text1}
Before you act, think first, and then act. {hint_guideline_text} Your thought should be in section [THINK], and your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action {puzzle_text2}, no other text.
[THINK]
[ACTION]"""
    return prompt


def get_prompt_next_action_withreason_vlm(
    direction: str,
    current_scene_desc: str,
    inventory: List[str],
    spatial_memory: str,
    salient_action_history: List[str],
    action_history: List[str],
    previous_react: str,
    available_actions: List[str],
    ispuzzle: bool,
    hint_message: str,
) -> str:
    puzzle_text1 = (
        """<ANSWER> is an action to input the answer to open the lock you are facing. When you choose <ANSWER>, you should follow this format: "<ANSWER>your answer</ANSWER>"."""
        if ispuzzle
        else ""
    )
    puzzle_text2 = """or <ANSWER>your answer</ANSWER>""" if ispuzzle else ""
    action_history = "\n".join(
        [
            (
                f"{action['action']}"
                if action["analysis"] == "-"
                else f"{action['action']} - {action['analysis']}"
            )
            for action in action_history
        ]
    )
    salient_action_history = "\n".join(
        list(
            dict.fromkeys(
                [
                    (
                        f"{action['action']}"
                        if action["analysis"] == "-"
                        else f"{action['action']} - {action['analysis']}"
                    )
                    for action in salient_action_history
                ]
            )
        )
    )

    salient_action_history_text = (
        f"<Action Memory>\n{salient_action_history}</Action Memory>\n"
        if salient_action_history
        else ""
    )
    action_history_text = (
        f"<Recent actions(from oldest to latest)>\n{action_history}</Recent actions>\n"
        if action_history
        else ""
    )
    inventory_text = (
        "<Inventory>You have nothing.</Inventory>"
        if not inventory
        else f"<Inventory>You have {inventory}.</Inventory>"
    )
    memory_text = f"<Memory>\n{spatial_memory}</Memory>\n" if spatial_memory else ""
    hint_message_text = (
        f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    )
    hint_guideline_text = (
        "If there is a hint message, you should choose action to accomplish the guideline in hint message."
        if hint_message
        else ""
    )
    available_actions = (
        available_actions + ["<ANSWER> [your answer]"]
        if ispuzzle
        else available_actions
    )

    prompt = f"""{init_prompt}. 
{memory_text}{salient_action_history_text}{action_history_text}
<Current Observation>{direction} side of room - [IMAGE]</Current Observation>
{inventory_text}
<Your Thought and Action before this turn>{previous_react}</Your Thought and Action before this turn>
{hint_message_text}
Here is the task:
Based on these information, choose next action to progress in the game. You must choose one of the following actions:
{available_actions}
{puzzle_text1}
Before you act, think first, and then act. {hint_guideline_text} Your thought should be in section [THINK], and your action should be in section [ACTION]. In [ACTION], respond ONLY with the chosen action {puzzle_text2}, no other text.
[THINK]
[ACTION]"""
    return prompt


def get_prompt_next_action_withreason_retry(
    direction: str,
    spatial_memory: str,
    before_action: str,
    available_actions: List[str],
    hint_message: str,
) -> str:
    memory_text = f"<Memory>{spatial_memory}</Memory>\n" if spatial_memory else ""
    hint_message_text = (
        f"<Hint Message>\n{hint_message}</Hint Message>\n" if hint_message else ""
    )
    hint_guideline_text = (
        "If there is a hint message, you should choose action to accomplish the guideline in hint message."
        if hint_message
        else ""
    )
    prompt = f"""{init_prompt}. 
<Current Observation>{direction} side of room</Current Observation>
{memory_text}
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
