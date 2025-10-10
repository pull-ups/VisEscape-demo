import os
from typing import List, Optional

from openai import OpenAI

from vis_escape.config.models import get_config
from vis_escape.experiment.agent.inference import (
    run_inference_text,
    run_inference_vision,
)

from .prompt import *


class Agent:
    def __init__(self, model_cfg=None):
        self.config = get_config(model_cfg)
        self.clients = self._get_client()

    def get_next_action_first_turn(
        self,
        model: str,
        direction: str,
        current_scene_desc: Optional[str],
        inventory: List[str],
        available_actions: List[str],
        run_mode: Optional[str] = "socratic",
    ) -> str:
        system_prompt = "Your response should be in the following format: [THINK]Your thought\n[ACTION]Your action"
        if run_mode == "socratic":
            prompt = get_prompt_next_action_first_turn(
                direction, current_scene_desc, inventory, available_actions
            )
            response = run_inference_text(
                self.clients, model, prompt, "action", system_prompt
            )
        else:
            prompt = get_prompt_next_action_first_turn_vlm(
                direction, current_scene_desc, inventory, available_actions
            )
            response = run_inference_vision(
                self.clients, model, current_scene_desc, prompt
            )
            print(response)
        try:
            max_attempts = 3
            for attempt in range(max_attempts):
                if "[ACTION]" in response:
                    chosen_action = (
                        response.split("[ACTION]")[1].strip().replace(":", "")
                    )
                    if "\n" in chosen_action:
                        chosen_action = chosen_action.split("\n")[0].strip()
                    if chosen_action in available_actions:
                        return chosen_action, response
                    else:
                        print(
                            f"Action: [{chosen_action}] Attempt {attempt + 1}: is not in available_actions {available_actions}"
                        )
                        response = run_inference_text(
                            self.clients["gpt"], model, prompt, "action_retry"
                        )
                else:
                    for action in available_actions:
                        if action.lower() in response[:20].lower():
                            return action, response
                        print(
                            f"Action: [{chosen_action}] Attempt {attempt + 1}: No action found. Retrying..."
                        )
                        response = run_inference_text(
                            self.clients, model, prompt, "action", system_prompt
                        )

            print("All attempts failed. Returning default action.")
            return available_actions[0], response
        except Exception as e:
            print(
                f"Response {response} does not contain [ACTION] in available_actions {available_actions}"
            )
            return available_actions[0], response
        
    def get_next_action(
        self,
        model: str,
        direction: str,
        current_scene_desc: Optional[str],
        inventory: List[str],
        spatial_memory: str,
        salient_action_history: List[str],
        action_history: List[str],
        previous_react: str,
        available_actions: List[str],
        hint_message: Optional[str] = "",
        ispuzzle: Optional[bool] = False,
        run_mode: Optional[str] = "socratic",
    ) -> str:
        system_prompt = "Your response should be in the following format: [THINK]Your thought\n[ACTION]Your action"
        if run_mode == "socratic":
            prompt = get_prompt_next_action_withreason(
                direction,
                current_scene_desc,
                inventory,
                spatial_memory,
                salient_action_history,
                action_history,
                previous_react,
                available_actions,
                ispuzzle,
                hint_message,
            )
            response = run_inference_text(
                self.clients, model, prompt, "action", system_prompt
            )
        elif run_mode == "vlm":
            prompt = get_prompt_next_action_withreason_vlm(
                direction,
                current_scene_desc,
                inventory,
                spatial_memory,
                salient_action_history,
                action_history,
                previous_react,
                available_actions,
                ispuzzle,
                hint_message,
            )
            response = run_inference_vision(
                self.clients, model, current_scene_desc, prompt
            )
        print("---------------PROMPT------------------")
        print(prompt)
        print("---------------ANSWER------------------")
        print(response)
        print("---------------------------------------")
        try:
            max_attempts = 3
            for attempt in range(max_attempts):
                if ispuzzle:
                    if "<ANSWER>" in response:
                        answer = response.split("<ANSWER>")[1].strip()
                        if "</ANSWER>" in answer:
                            answer = answer.split("</ANSWER>")[0].strip()
                        else:
                            answer = answer.split(" ")[0]
                        return answer, response, True
                    else:
                        if "[ACTION]" in response:
                            chosen_action = (
                                response.split("[ACTION]")[1].strip().replace(":", "")
                            )
                            if "\n" in chosen_action:
                                chosen_action = chosen_action.split("\n")[0].strip()
                            if chosen_action in available_actions:
                                return chosen_action, response, False
                            else:
                                print(
                                    f"Attempt {attempt + 1}: Invalid action. Retrying..."
                                )
                                system_prompt = "Your response should be in the following format: [ACTION]Your action"
                                prompt = get_prompt_next_action_withreason_retry(
                                    direction,
                                    spatial_memory,
                                    chosen_action,
                                    available_actions,
                                    hint_message,
                                )
                                response = run_inference_text(
                                    self.clients["gpt"],
                                    model,
                                    prompt,
                                    "action_retry",
                                    system_prompt,
                                )
                                print("---------------RETRY PROMPT------------------")
                                print(prompt)
                                print("---------------ANSWER------------------")
                                print(response)
                                print("---------------------------------------")
                        else:
                            for action in available_actions:
                                if action.lower() in response[:20].lower():
                                    return action, response, False
                            print(
                                f"Attempt {attempt + 1}: No action found. Retrying..."
                            )
                            system_prompt = "Your response should be in the following format: [THINK]Your thought\n[ACTION]Your action"
                            response = run_inference_text(
                                self.clients, model, prompt, "action", system_prompt
                            )
                else:
                    if "[ACTION]" in response:
                        chosen_action = (
                            response.split("[ACTION]")[1].strip().replace(":", "")
                        )
                        if "\n" in chosen_action:
                            chosen_action = chosen_action.split("\n")[0].strip()
                        if chosen_action in available_actions:
                            return chosen_action, response, False
                        else:
                            print(
                                f"Action: [{chosen_action}] Attempt {attempt + 1}: is not in available_actions {available_actions}"
                            )
                            system_prompt = "Your response should be in the following format: [ACTION]Your action"
                            prompt = get_prompt_next_action_withreason_retry(
                                direction,
                                spatial_memory,
                                chosen_action,
                                available_actions,
                                hint_message,
                            )
                            response = run_inference_text(
                                self.clients["gpt"], model, prompt, "action_retry"
                            )
                            print("---------------RETRY PROMPT------------------")
                            print(prompt)
                            print("---------------ANSWER------------------")
                            print(response)
                            print("---------------------------------------")
                    else:
                        for action in available_actions:
                            if action.lower() in response[:20].lower():
                                return action, response, False
                        print(
                            f"Action: [{chosen_action}] Attempt {attempt + 1}: No action found. Retrying..."
                        )
                        system_prompt = "Your response should be in the following format: [THINK]Your thought\n[ACTION]Your action"
                        response = run_inference_text(
                            self.clients, model, prompt, "action", system_prompt
                        )

            print("All attempts failed. Returning default action.")
            return available_actions[0], response, False

        except Exception as e:
            print(
                f"Response {response} does not contain [ACTION] in available_actions {available_actions}"
            )
            return available_actions[0], response, False

    def get_action_feedback(
        self,
        model: str,
        previous_scene_desc: str,
        current_scene_desc: str,
        previous_action: str,
    ) -> str:
        prompt = get_prompt_action_feedback(
            previous_scene_desc, current_scene_desc, previous_action
        )
        response = run_inference_text(self.clients, model, prompt, "feedback")
        if "[ANALYSIS]" in response:
            return response.split("[ANALYSIS]")[1].strip()
        else:
            return response

    def get_first_spatial_memory(self, model: str, action_history: List[str]) -> str:
        system_prompt = "Your response should be in the following format: [SPATIAL MEMORY]spatial_json_format, [INSPECTED OBJECTS]inspected_objects_json_format, [UNINSPECTED OBJECTS]uninspected_objects_format, [ADDITIONAL MEMORY]additional_memory_format"
        prompt = get_prompt_spatial_memory_construct(action_history)
        print("in get_first_spatial_memory-", end="")
        response = run_inference_text(
            self.clients, model, prompt, "memory", system_prompt
        )
        return response

    def get_updated_spatial_memory(
        self, model: str, spatial_memory: str, action_history: List[str]
    ) -> str:
        system_prompt = "Your response should be in the following format: [SPATIAL MEMORY]spatial_json_format, [INSPECTED OBJECTS]inspected_objects_json_format, [UNINSPECTED OBJECTS]uninspected_objects_format, [ADDITIONAL MEMORY]additional_memory_format"
        prompt = get_prompt_spatial_memory_update(spatial_memory, action_history)
        response = run_inference_text(
            self.clients, model, prompt, "memory", system_prompt
        )
        return response

    # Helper
    def _get_client(self):
        """
        Create OpenAI clients for all configured models.
        Returns a dict mapping model names to OpenAI client instances.
        """
        clients = {}
        
        for model_name, model_config in self.config["models"].items():
            if model_config["type"] == "openai":
                # OpenAI API
                try:
                    clients[model_name] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                except Exception as e:
                    print(f"Warning: Failed to create OpenAI client for {model_name}: {e}")
            
            elif model_config["type"] == "vllm":
                # vLLM endpoint (OpenAI-compatible)
                base_url = model_config["base_url"]
                default_query = model_config.get("args", None)
                clients[model_name] = OpenAI(
                    api_key="EMPTY",
                    base_url=base_url,
                    default_query=default_query
                )
        
        return clients
