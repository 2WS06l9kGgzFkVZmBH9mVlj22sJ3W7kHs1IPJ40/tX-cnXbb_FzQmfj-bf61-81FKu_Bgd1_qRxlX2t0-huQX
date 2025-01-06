import google.generativeai as genai
import pyautogui
import os
import webbrowser
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyAwuWBNxTzqog_lkHz4X-sRMDbFHOvQZBY"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class ComputerControlAgent:
    def __init__(self):
        self.known_commands = {
            "open notepad": self._open_notepad,
            "open microsoft edge": self._open_microsoft_edge,
            "open powershell": self._open_powershell,
            "open command prompt": self._open_command_prompt,
            "open command prompt (admin)": self._open_command_prompt_admin,
            "open terminal": self._open_terminal,
        }

    def _open_notepad(self):
        self._open_application("notepad")

    def _open_microsoft_edge(self):
        self._open_application("msedge")

    def _open_powershell(self):
        self._open_application("powershell")

    def _open_command_prompt(self):
        self._open_application("cmd")

    def _open_command_prompt_admin(self):
        print("Execution: Attempting to open Command Prompt as Administrator (requires elevated privileges and more complex implementation).")
        pass

    def _open_terminal(self):
        platform = os.sys.platform
        if platform.startswith('win'):
            self._open_application("wt")  # Windows Terminal
        elif platform.startswith('darwin'):
            self._open_application("Terminal")
        elif platform.startswith('linux'):
            self._open_application("gnome-terminal")  # Or your distribution's terminal

    def _open_application(self, application_name):
        platform = os.sys.platform
        try:
            if platform.startswith('win'):
                os.system(f"start {application_name}")
            elif platform.startswith('darwin'):
                os.system(f"open -a '{application_name}'")
            elif platform.startswith('linux'):
                os.system(application_name)  # Might need full path or specific command
            print(f"Execution: Opened {application_name}.")
        except FileNotFoundError:
            print(f"Error: Application '{application_name}' not found.")
        except Exception as e:
            print(f"Error opening {application_name}: {e}")

    def format_search_query(self, query):
        return urllib.parse.quote_plus(query)

    def search_internet(self, query):
        formatted_query = self.format_search_query(query)
        search_url = f"https://html.duckduckgo.com/html/?q={formatted_query}"
        print(f"AI: Searching the internet for: {query}")
        return search_url

    def analyze_and_open_website(self, query, search_url):
        try:
            response = requests.get(search_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            for link_tag in soup.find_all('a', href=True):
                href = link_tag['href']
                if href.startswith("http") and "duckduckgo.com" not in href:
                    links.append(href)

            if not links:
                print("AI: Could not find any relevant website links on the search results page.")
                return

            print("AI: Analyzing websites for relevance...")
            best_match_url = None
            best_match_score = -1

            for url in links:
                prompt = f"Determine the relevance of the following website to the query: '{query}'. Website URL: {url}. Respond with a single number between 0 and 1, where 1 is a perfect match and 0 is not relevant at all."
                relevance_response = model.generate_content(prompt)
                try:
                    score = float(relevance_response.text.strip())
                    if 0 <= score <= 1 and score > best_match_score:
                        best_match_score = score
                        best_match_url = url
                    print(f"AI: Relevance of {url}: {score}")
                except ValueError:
                    print(f"AI: Could not parse relevance score for {url}: {relevance_response.text}")

            if best_match_url:
                print(f"AI: Opening the most relevant website: {best_match_url}")
                webbrowser.open(best_match_url)
            else:
                print("AI: Could not determine the most relevant website from the search results.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching search results: {e}")
        except Exception as e:
            print(f"Error analyzing websites: {e}")

    def execute_system_command(self, command):
        """Executes direct system commands using pyautogui."""
        if "move mouse to" in command.lower():
            try:
                parts = command.split()
                x = int(parts[-2].replace(',', ''))
                y = int(parts[-1])
                pyautogui.moveTo(x, y, duration=0.1)
                print(f"Execution: Moved mouse to ({x}, {y}).")
            except ValueError:
                print(f"Error parsing coordinates from command: {command}")
        elif "click" in command.lower():
            pyautogui.click()
            print("Execution: Clicked the mouse.")
        elif "type" in command.lower():
            text = command.split("type", 1)[1].strip()
            pyautogui.write(text)
            print(f"Execution: Typed '{text}'.")
        else:
            print(f"Error: Unknown system command for direct input: {command}")

    def generate_plan_and_execute(self, user_prompt):
        prompt = f"""
            You are an intelligent AI agent with the ability to control the user's computer.
            The user has asked: "{user_prompt}"

            Think step-by-step about how to best respond to the user's request. Consider the following:
            - If the user wants to open a specific application, the 'Action' should be the exact command from `self.known_commands` (e.g., "open notepad", "open microsoft edge").
            - If the request is to open a website and the name is not exact, the 'Action' should be: `search internet "[search query]"`.
            - If the request involves directly controlling the computer (e.g., mouse movements, clicks, typing), formulate the exact system command to execute with pyautogui.

            Structure your response as follows:
            "Thought: [Your detailed thought process]"
            "Plan: [A concise plan of action]"
            "Action: [The specific command to execute from `self.known_commands`, a 'search internet' command, or a pyautogui command]"
            """

        response = model.generate_content(prompt)
        response_text = response.text

        print(f"Gemini Response:\n{response_text}")

        try:
            thought = response_text.split("Thought:")[1].split("Plan:")[0].strip()
            plan = response_text.split("Plan:")[1].split("Action:")[0].strip()
            action = response_text.split("Action:")[1].strip()

            print(f"AI Thought: {thought}")
            print(f"AI Plan: {plan}")
            print(f"Gemini Action: {action}")  # Debugging: Print the exact action

            if action.lower().startswith("search internet"):
                try:
                    search_query = action.split('"')[1]
                    search_url = self.search_internet(search_query)
                    self.analyze_and_open_website(user_prompt, search_url) # Analyze and open
                except IndexError:
                    print(f"Error parsing search query from action: {action}")
            elif action.lower() in self.known_commands:
                print(f"Executing known command: {action}")  # Debugging
                self.known_commands[action.lower()]()
            elif action:
                print(f"AI: Proceeding with direct execution of input command: {action}")
                self.execute_system_command(action)
            else:
                print("AI: No specific action planned.")

        except IndexError:
            print("Error: Could not parse Gemini's response properly.")

if __name__ == "__main__":
    agent = ComputerControlAgent()
    while True:
        user_prompt = input("User: ")
        agent.generate_plan_and_execute(user_prompt)
        print("-" * 30)