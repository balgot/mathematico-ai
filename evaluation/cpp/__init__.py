from agent import CPPPlayer


class CPPPlayer__100ms__10Kiters(CPPPlayer):
    def __init__(self):
        super().__init__(100, 10_000)


class CPPPlayer__100ms__10KitersVERBOSE(CPPPlayer):
    def __init__(self):
        super().__init__(100, 10_000)

    def move(self, card_number: int) -> None:
        return super().move(card_number, True)


class CPPPlayer__100ms__1Biters(CPPPlayer):
    def __init__(self):
        super().__init__(100, 1_000_000_000)


class CPPPlayer__1000ms__100Miters(CPPPlayer):
    def __init__(self):
        super().__init__(1000, 100_000_000)
