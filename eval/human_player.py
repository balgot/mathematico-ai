import pygame
from mathematico import Player, Board, HumanPlayer


class ConsolePlayer(HumanPlayer):
    ...


CELL_SIZE = 100
SCREEN_WIDTH = 5 * CELL_SIZE + CELL_SIZE
SCREEN_HEIGHT = 5 * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class PyGamePlayer(Player):
    def __init__(self):
        super().__init__()
        self.screen = None
        self.font = None
        self._prepare_window()

    def _prepare_window(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.Font(None, 50)

    def _close_window(self):
        pygame.display.quit()
        pygame.quit()

    def reset(self) -> None:
        self._close_window()
        self.board = Board()
        self._prepare_window()

    def _render_text(self, text, cx, cy, color):
        number_surface = self.font.render(
            str(text),
            True,
            color
        )
        number_rect = number_surface.get_rect(center=(cx, cy))
        self.screen.blit(number_surface, number_rect)

    def _update_display(self, card: 'int | str'):
        assert(self.screen is not None)
        assert(self.font is not None)
        self.screen.fill(WHITE)

        for row in range(5):
            for col in range(5):
                # Draw the cell
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1
                )

                # Draw the number if the cell is not empty
                if self.board.grid[row][col] != 0:
                    cx = col * CELL_SIZE + CELL_SIZE // 2
                    cy = row * CELL_SIZE + CELL_SIZE // 2
                    self._render_text(self.board.grid[row][col], cx, cy, BLACK)

        # Draw the current number on the right
        cx = SCREEN_WIDTH - CELL_SIZE // 2
        cy = SCREEN_HEIGHT // 2
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (SCREEN_WIDTH - CELL_SIZE, 0, CELL_SIZE, SCREEN_HEIGHT)
        )
        self._render_text(card, cx, cy, WHITE)

        # Update the display
        pygame.display.update()

    def move(self, card_number: int) -> None:
        self._update_display(card_number)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise RuntimeError("Closing the window during the game")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    # Check if the click was within the grid
                    if x < CELL_SIZE * 5 and y < CELL_SIZE * 5:
                        row = y // CELL_SIZE
                        col = x // CELL_SIZE

                        if self.board.grid[row][col] == 0:
                            # Place the current number in the cell
                            self.board.make_move((row, col), card_number)
                            self._update_display(" ")

                            if self.board.occupied_cells == 5*5:
                                print(f"Score: {self.board.score()}")

                            return
