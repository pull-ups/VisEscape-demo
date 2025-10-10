import os
from typing import List, Optional

from openai import OpenAI

from vis_escape.config.models import get_config
from vis_escape.experiment.agent.inference import (
    run_inference_text,
    run_inference_vision,
    run_inference_vision_noimage,
)

from .prompt import *


class Agent:
    def __init__(self, model_cfg=None):
        self.config = get_config(model_cfg)
        self.clients = self._get_client()

    def get_next_action_first_turn(self, model: str,
                       direction: str,
                       current_scene_desc: Optional[str],
                       inventory: str,
                       available_actions: List[str],
                       run_mode: Optional[str] = "vlm",
                       ) -> tuple[str, str]:
        system_prompt = "Your response should be in the following format: [ACTION]Your action"
        
        if run_mode == "socratic":
            prompt = get_prompt_next_action_first_turn(direction, current_scene_desc, inventory, available_actions)
            response = run_inference_text(self.clients, model, prompt, "action", system_prompt)
        else:  # vlm mode
            prompt = get_prompt_next_action_first_turn_vlm(direction, current_scene_desc, inventory, available_actions)
            response = run_inference_vision(self.clients, model, current_scene_desc, prompt)
            
        print("---------------PROMPT------------------")
        print(prompt)
        print("---------------ANSWER------------------")
        print(response)
        print("---------------------------------------")
        try:
            if "[ACTION]" in response:
                chosen_action = response.split("[ACTION]")[1].strip().replace(":", "")
                if "\n" in chosen_action:
                    chosen_action = chosen_action.split("\n")[0].strip()
                if chosen_action in available_actions:
                    return chosen_action, response
            else:
                for action in available_actions:
                    if action.lower() in response[:20].lower():
                        return action, response
        except Exception as e:
            print(f"Response {response} does not contain [ACTION] in available_actions {available_actions}")
            return available_actions[0], response
        

    def get_next_action(self, model: str,
                       direction: str,
                       current_scene_desc: Optional[str],
                       inventory: str,
                       salient_action_history: List[dict],
                       action_history: List[dict],
                       previous_action: str,
                       available_actions: List[str],
                       hint_message: Optional[str] = "",
                       ispuzzle: Optional[bool] = False,
                       run_mode: Optional[str] = "vlm",
                       ) -> tuple[str, str, bool]:
        system_prompt = "Your response should be in the following format: [ACTION]Your action"
        
        if run_mode == "socratic":
            prompt = get_prompt_next_action_withreason(
                direction, current_scene_desc, inventory, 
                salient_action_history, action_history, 
                previous_action, available_actions, 
                ispuzzle, hint_message
            )
            response = run_inference_text(self.clients, model, prompt, "action", system_prompt)
        else:  # vlm mode
            prompt = get_prompt_next_action_withreason_vlm(
                direction, current_scene_desc, inventory, 
                salient_action_history, action_history, 
                previous_action, available_actions, 
                ispuzzle, hint_message
            )
            response = run_inference_vision(self.clients, model, current_scene_desc, prompt)
            
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
                            chosen_action = response.split("[ACTION]")[1].strip().replace(":", "")
                            if "\n" in chosen_action:
                                chosen_action = chosen_action.split("\n")[0].strip()
                            if chosen_action in available_actions:
                                return chosen_action, response, False
                            else:
                                print(f"Attempt {attempt + 1}: Invalid action. Retrying...")
                                system_prompt = "Your response should be in the following format: [ACTION]Your action"
                                prompt = get_prompt_next_action_withreason_retry(direction, chosen_action, available_actions, hint_message)
                                if run_mode == "socratic":
                                    response = run_inference_text(self.clients, model, prompt, "action_retry", system_prompt)
                                else:
                                    response = run_inference_vision_noimage(self.clients, model, prompt, "action_retry", system_prompt)
                                print("---------------RETRY PROMPT------------------")
                                print(prompt)
                                print("---------------ANSWER------------------")
                                print(response)
                                print("---------------------------------------")
                        else:
                            for action in available_actions:
                                if action.lower() in response[:20].lower():
                                    return action, response, False
                            print(f"Attempt {attempt + 1}: No action found. Retrying...")
                            system_prompt = "Your response should be in the following format: [ACTION]Your action"
                            if run_mode == "socratic":
                                response = run_inference_text(self.clients, model, prompt, "action", system_prompt)
                            else:
                                response = run_inference_vision_noimage(self.clients, model, prompt, "action", system_prompt)
                else:
                    if "[ACTION]" in response:
                        chosen_action = response.split("[ACTION]")[1].strip().replace(":", "")
                        if "\n" in chosen_action:
                            chosen_action = chosen_action.split("\n")[0].strip()
                        if chosen_action in available_actions:
                            return chosen_action, response, False
                        else:
                            print(f"Action: [{chosen_action}] Attempt {attempt + 1}: is not in available_actions {available_actions}")
                            system_prompt = "Your response should be in the following format: [ACTION]Your action"
                            prompt = get_prompt_next_action_withreason_retry(direction, chosen_action, available_actions, hint_message)
                            if run_mode == "socratic":
                                response = run_inference_text(self.clients, model, prompt, "action_retry", system_prompt)
                            else:
                                response = run_inference_vision_noimage(self.clients, model, prompt, "action_retry")
                            print("---------------RETRY PROMPT------------------")
                            print(prompt)
                            print("---------------ANSWER------------------")
                            print(response)
                            print("---------------------------------------")
                    else:
                        for action in available_actions:
                            if action.lower() in response[:20].lower():
                                return action, response, False
                        print(f"Action: [{chosen_action}] Attempt {attempt + 1}: No action found. Retrying...")
                        system_prompt = "Your response should be in the following format: [ACTION]Your action"
                        if run_mode == "socratic":
                            response = run_inference_text(self.clients, model, prompt, "action", system_prompt)
                        else:
                            response = run_inference_vision_noimage(self.clients, model, prompt, "action", system_prompt)
            print("All attempts failed. Returning default action.")
            return available_actions[0], response, False
                
        except Exception as e:
            print(f"Response {response} does not contain [ACTION] in available_actions {available_actions}")
            return available_actions[0], response, False





       
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