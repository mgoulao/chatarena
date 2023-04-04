from pettingzoo.classic.chess.chess_utils import *
import re
from typing import List
from pettingzoo.classic import chess_v5

from chatarena.environments.base import Environment, TimeStep
from chatarena.message import Message

def action_string_to_alphazero_format(action: str, player_index: int) -> int:
    pattern = r"Move \((\d), (\d)\) to \((\d), (\d)\)"
    match = re.match(pattern, action)

    if not match:
        raise ValueError(f"Invalid action string format: {action}")

    coords = [int(coord) for coord in match.groups()]
    x1, y1, x2, y2 = coords

    if player_index == 1:
        x1, y1, x2, y2 = 7 - x1, 7 - y1, 7 - x2, 7 - y2
    move = chess.Move(from_square=8 * y1 + x1, to_square=8 * y2 + x2, promotion=None)
    move_plane = get_move_plane(move)

    return x1 * 8 * 73 + y1 * 73+ move_plane


class ChessEnvironment(Environment):
    type_name = "pettingzoo:chess"
    def __init__(self, player_names: List[str]):
        super().__init__(player_names)
        self.env = chess_v5.env(render_mode="ansi")
        self.reset()

    def reset(self):
        self.env.reset()
        self.current_player = 0
        self.turn = 0

    def get_next_player(self) -> str:
        return self.player_names[self.current_player]

    def get_observation(self, player_name=None) -> List[Message]:
        board_string = self.env.render()
        return [Message(agent_name="ChessEnv", content=board_string, turn=self.turn)]

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."

        # Convert the action to the AlphaZero format
        alphazero_move = action_string_to_alphazero_format(action, self.current_player)

        obs_dict, reward, termination, truncation, info = self.env.last()
        print(obs_dict["action_mask"])
        self.env.step(alphazero_move)
        terminal = termination
        reward = reward

        self.current_player = 1 - self.current_player
        self.turn += 1

        observation = self.get_observation()
        return TimeStep(observation=observation, reward=reward, terminal=terminal)

    def check_action(self, action: str, agent_name: str) -> bool:
        # This can be implemented depending on how you want to validate actions for a given agent
        pass

    def print(self):
        print(self.env.render())

def test_chess_environment():
    player_names = ["player1", "player2"]
    env = ChessEnvironment(player_names)

    env.reset()
    assert env.get_next_player() == "player1"
    env.print()

    # Move sequence: 1. e4 e5 2. Nf3 Nc6
    moves = ["Move (4, 1) to (4, 3)", "Move (4, 6) to (4, 4)",
             "Move (6, 0) to (5, 2)", "Move (1, 7) to (2, 5)"]

    for i, move in enumerate(moves):
        timestep = env.step(env.get_next_player(), move)
        print(timestep.reward)
        print(timestep.terminal)

        env.print()

if __name__ == "__main__":
    env = chess_v5.env()

    # Test the conversion function with an example action string
    action = "Move (0, 1) to (0, 3)"
    alphazero_move = action_string_to_alphazero_format(action, 0)
    print(alphazero_move)

    test_chess_environment()