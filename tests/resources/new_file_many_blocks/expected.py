from typing import Dict, List
from .abstract_battleship import AbstractBattleship, Game, GameStatus, ShipPlacement, Turn, TurnResponse

class Battleship(AbstractBattleship):
    def __init__(self):
        self.games: Dict[str, Game] = {}

    def create_game(self, game_id: str, players: List[str]) -> None:
        if game_id in self.games:
            raise ValueError(f"Game with id {game_id} already exists.")

        board = [["" for _ in range(10)] for _ in range(10)]
        self.games[game_id] = Game(game_id=game_id, players=players, board=board, ships=[], turns=[])

    def create_ship_placement(self, game_id: str, placement: ShipPlacement) -> None:
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} does not exist.")

        ship_length = self.SHIP_LENGTHS[placement.ship_type]
        start_row, start_column = placement.start["row"] - 1, ord(placement.start["column"]) - ord("A")

        if placement.direction == "horizontal":
            if start_column + ship_length > 10:
                raise ValueError("Ship placement is out of bounds.")
            for i in range(ship_length):
                if game.board[start_row][start_column + i] != "":
                    raise ValueError("Ship placement overlaps with another ship.")
                game.board[start_row][start_column + i] = placement.ship_type
        else:  # placement.direction == "vertical"
            if start_row + ship_length > 10:
                raise ValueError("Ship placement is out of bounds.")
            for i in range(ship_length):
                if game.board[start_row + i][start_column] != "":
                    raise ValueError("Ship placement overlaps with another ship.")
                game.board[start_row + i][start_column] = placement.ship_type

        game.ships.append(placement)

    def create_turn(self, game_id: str, turn: Turn) -> TurnResponse:
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} does not exist.")

        row, column = turn.target["row"] - 1, ord(turn.target["column"]) - ord("A")
        if game.board[row][column] == "":
            result = "miss"
            ship_type = None
        else:
            result = "hit"
            ship_type = game.board[row][column]
            game.board[row][column] = ""

        game.turns.append(turn)
        return TurnResponse(result=result, ship_type=ship_type)

    def get_game_status(self, game_id: str) -> GameStatus:
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} does not exist.")

        is_game_over = all(cell == "" for row in game.board for cell in row)
        winner = game.players[0] if is_game_over else None
        return GameStatus(is_game_over=is_game_over, winner=winner)

    def get_winner(self, game_id: str) -> str:
        game_status = self.get_game_status(game_id)
        if not game_status.is_game_over:
            raise ValueError("The game is not over yet.")
        return game_status.winner

    def get_game(self, game_id: str) -> Game:
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} does not exist.")
        return game

    def delete_game(self, game_id: str) -> None:
        if game_id not in self.games:
            raise ValueError(f"Game with id {game_id} does not exist.")
        del self.games[game_id]