from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import ChatOllama

from typing import Literal

@tool
def move(tile_x: int, tile_y: int, room: int) -> None:
    """
    Decides to which tile and to which room to move.

    Args:
        tile_x (int): x-value of a tile in the room
        tile_y (int): y-value of a tile in the room
        room (int): int value of the room to move to
    """
    
    #print(f"Moving to tile {tile_x}, {tile_y} in room: {room}")
    return ([tile_x, tile_y], room)
    #self.sigmas[0].create_directions_to_point(self.game.rooms, self.game.rooms_exits, room, [tile_x, tile_y])


class Llama:
    def __init__(self, game):
        self.game = game
        self.sigmas = []
        self.tools = [move]

        self.last_thought = ""

        self.llm = ChatOllama(
            model="llama3.1",
            temperature=0,
        ).bind_tools(self.tools)

        self.think_llm = ChatOllama(
            model="llama3.1",
            temperature=0.7,
        )

    def add_sigma(self, sigma):
        self.sigmas.append(sigma)
    

    def update_thoughts(self, last_thougt):
        result = self.think_llm.invoke(
            f"You are a sigma male living in a sigma world.\n"
            f"Your last thoughts were: {last_thougt}\n"
            f"What are your next thoughts, be brief."
        )
        print(result.content)
        return result.content

    def step(self, room_description: str):
        result = self.llm.invoke(
            f"Here is a description of the room you are in: {room_description}\n"
            f"Your thoughts are {self.last_thought}"
            f"Choose a new place to move to."
        )

        print(result.tool_calls)

        tool_call = result.tool_calls[0]
        tools_dict = {t.name : t for t in self.tools}
        selected_tool = tools_dict[tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])

        tile, room = tool_output
        print(tile)
        print(room)

        self.last_thought = self.update_thoughts(self.last_thought)

        self.sigmas[0].create_directions_to_point(self.game.rooms, self.game.rooms_exits, room, tile)