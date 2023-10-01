
from typing import Dict, List
from .abstract_battleship import TurnResponse

class Battleship(AbstractBattleship):
    def __init__(self):
        self.games: Dict[str, Game] = {}

    def create_game(self, game_id: str) -> None:
        if game_id in self.games:
            raise ValueError(f"Game with id {game_id} already exists.")

        # Initialize an empty 10x10 grid for each player
        grid = {player: [["" for _ in range(10)] for _ in range(10)] for player in ["player1", "player2"]}

        # Initialize an empty list for turns and ship placements
        turns = []
        ships = []

        # Create a new game and add it to the games dictionary
        self.games[game_id] = Game(game_id=game_id, players=["player1", "player2"], board=grid, ships=ships, turns=turns)

    def delete_game(self, game_id: str) -> None:
        if game_id not in self.games:
            raise ValueError(f"Game with id {game_id} does not exist.")

        del self.games[game_id]

    def create_ship_placement(self, game_id: str, placement: ShipPlacement) -> None:
        if game_id not in self.games:
            raise ValueError(f"Game with id {game_id} does not exist.")

        game = self.games[game_id]
        ship_length = self.SHIP_LENGTHS[placement.ship_type]
        start_row = placement.start["row"]
        start_column = ord(placement.start["column"]) - ord('A')  # Convert column from letter to number

        # Check if the ship placement is within the grid and does not overlap with any placed ship
        if placement.direction == "horizontal":
            if start_column + ship_length > 10:
                raise ValueError("Ship placement is out of grid.")
            for i in range(start_column, start_column + ship_length):
                if game.board["player1"][start_row - 1][i] != "":
                    raise ValueError("Ship placement overlaps with another ship.")
        else:  # direction is vertical
            if start_row + ship_length > 10:
                raise ValueError("Ship placement is out of grid.")
            for i in range(start_row, start_row + ship_length):
                if game.board["player1"][i - 1][start_column] != "":
                    raise ValueError("Ship placement overlaps with another ship.")

        # Place the ship on the grid
        if placement.direction == "horizontal":
            for i in range(start_column, start_column + ship_length):
                game.board["player1"][start_row - 1][i] = placement.ship_type
        else:  # direction is vertical
            for i in range(start_row, start_row + ship_length):
                game.board["player1"][i - 1][start_column] = placement.ship_type

        # Add the ship's placement details to the game's 'ships' list
        game.ships.append(placement)

    def create_turn(self, game_id: str, turn: Turn) -> TurnResponse:
        if game_id not in self.games:
            raise ValueError(f"Game with id {game_id} does not exist.")

        game = self.games[game_id]

        # Check if it's the player's turn
        if len(game.turns) % 2 == 0:
            current_player = "player1"
            opponent_player = "player2"
        else:
            current_player = "player2"
            opponent_player = "player1"

        target_row = turn.target["row"]
        target_column = ord(turn.target["column"]) - ord('A')  # Convert column from letter to number

        # Check if the target cell is within the grid
        if not (1 <= target_row <= 10 and 0 <= target_column < 10):
            raise ValueError("Target cell is out of grid.")

        # Check if the target cell has already been targeted
        if game.board[opponent_player][target_row - 1][target_column] in ["hit", "miss"]:
            raise ValueError("Target cell has already been targeted.")

        # Check if the target cell contains a part of a ship
        if game.board[opponent_player][target_row - 1][target_column] != "":
            # If yes, mark the cell as a hit and check if the ship has been sunk
            game.board[opponent_player][target_row - 1][target_column] = "hit"
            ship_type = game.board[opponent_player][target_row - 1][target_column]
            if not any(cell == ship_type for row in game.board[opponent_player] for cell in row):
                # If the ship has been sunk, return a TurnResponse with the result as "hit" and the ship_type
                return TurnResponse(result="hit", ship_type=ship_type)
            else:
                # If the ship has not been sunk, return a TurnResponse with the result as "hit" and the ship_type as None
                return TurnResponse(result="hit", ship_type=None)
        else:
            # If no, mark the cell as a miss and return a TurnResponse with the result as "miss" and the ship_type as None
            game.board[opponent_player][target_row - 1][target_column] = "miss"
            return TurnResponse(result="miss", ship_type=None)