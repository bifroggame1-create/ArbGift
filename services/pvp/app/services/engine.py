"""
PvP Game Engine.

Provably Fair рулетка на гифтах.
Логика по образцу Rolls.codes.
"""
import hashlib
import secrets
from decimal import Decimal
from typing import Optional, List, Tuple
from dataclasses import dataclass

from app.models import Room, Bet, RoomStatus


@dataclass
class SpinResult:
    """Результат спина рулетки."""
    winning_ticket: int
    winning_bet_id: int
    winner_user_id: int
    spin_degree: Decimal
    raw_value: float


class ProvablyFairEngine:
    """
    Provably Fair генератор случайных чисел.

    Алгоритм:
    1. Сервер генерирует server_seed ДО игры
    2. Хеш server_seed показывается игрокам
    3. Клиент предоставляет client_seed
    4. Результат = SHA256(server_seed + client_seed + nonce)
    5. После игры server_seed раскрывается для проверки
    """

    @staticmethod
    def generate_server_seed() -> str:
        """Генерация криптографически безопасного server seed."""
        return secrets.token_hex(64)

    @staticmethod
    def hash_server_seed(server_seed: str) -> str:
        """Хеш server seed для показа игрокам до игры."""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    @staticmethod
    def generate_result(
        server_seed: str,
        client_seed: str,
        nonce: int,
    ) -> float:
        """
        Генерация случайного числа 0-1.

        Args:
            server_seed: Секретный сид сервера
            client_seed: Сид от клиента
            nonce: Порядковый номер игры

        Returns:
            Число от 0 до 1
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()

        # Используем первые 8 символов hex как случайное значение
        random_value = int(hash_hex[:8], 16) / (16 ** 8)
        return random_value

    @staticmethod
    def verify_result(
        server_seed: str,
        client_seed: str,
        nonce: int,
        claimed_result: float,
        tolerance: float = 0.0001,
    ) -> bool:
        """
        Проверка результата клиентом.

        Args:
            server_seed: Раскрытый server seed
            client_seed: Client seed
            nonce: Nonce
            claimed_result: Заявленный результат
            tolerance: Допустимая погрешность

        Returns:
            True если результат честный
        """
        actual = ProvablyFairEngine.generate_result(server_seed, client_seed, nonce)
        return abs(actual - claimed_result) < tolerance


class PvPGameEngine:
    """
    Движок PvP игры.

    Механика:
    1. Игроки кладут гифты в пул
    2. Каждый гифт = N тикетов (1 тикет = 0.01 TON)
    3. Рулетка выбирает случайный тикет
    4. Владелец тикета — победитель
    5. Победитель получает все гифты минус комиссия
    """

    TICKET_VALUE_TON = Decimal("0.01")  # 1 тикет = 0.01 TON

    def __init__(self):
        self.fair_engine = ProvablyFairEngine()

    def calculate_tickets(self, value_ton: Decimal) -> int:
        """
        Рассчитать количество тикетов для ставки.

        Args:
            value_ton: Стоимость гифта в TON

        Returns:
            Количество тикетов
        """
        return int(value_ton / self.TICKET_VALUE_TON)

    def assign_tickets(self, bets: List[Bet]) -> int:
        """
        Присвоить тикеты всем ставкам.

        Args:
            bets: Список ставок

        Returns:
            Общее количество тикетов
        """
        current_ticket = 0

        for bet in bets:
            tickets = self.calculate_tickets(bet.gift_value_ton)
            bet.tickets_start = current_ticket
            bet.tickets_end = current_ticket + tickets - 1
            bet.tickets_count = tickets
            current_ticket += tickets

        return current_ticket

    def calculate_win_chances(self, bets: List[Bet], total_tickets: int) -> None:
        """
        Рассчитать шанс победы для каждой ставки.

        Args:
            bets: Список ставок
            total_tickets: Общее количество тикетов
        """
        for bet in bets:
            if total_tickets > 0:
                chance = (Decimal(bet.tickets_count) / Decimal(total_tickets)) * 100
                bet.win_chance_percent = round(chance, 6)
            else:
                bet.win_chance_percent = Decimal("0")

    def spin_wheel(
        self,
        room: Room,
        bets: List[Bet],
        client_seed: Optional[str] = None,
    ) -> SpinResult:
        """
        Крутить рулетку и определить победителя.

        Args:
            room: Комната
            bets: Список ставок
            client_seed: Сид от клиента (опционально)

        Returns:
            Результат спина
        """
        # Присваиваем тикеты
        total_tickets = self.assign_tickets(bets)
        self.calculate_win_chances(bets, total_tickets)

        if total_tickets == 0:
            raise ValueError("No tickets in pool")

        # Генерируем результат
        used_client_seed = client_seed or secrets.token_hex(16)
        raw_value = self.fair_engine.generate_result(
            room.server_seed,
            used_client_seed,
            room.nonce,
        )

        # Определяем выигрышный тикет
        winning_ticket = int(raw_value * total_tickets)
        if winning_ticket >= total_tickets:
            winning_ticket = total_tickets - 1

        # Находим владельца тикета
        winner_bet = None
        for bet in bets:
            if bet.tickets_start <= winning_ticket <= bet.tickets_end:
                winner_bet = bet
                bet.is_winner = True
                break

        if not winner_bet:
            raise ValueError(f"No winner found for ticket {winning_ticket}")

        # Угол спина для анимации (0-360)
        spin_degree = Decimal(str(raw_value * 360))

        return SpinResult(
            winning_ticket=winning_ticket,
            winning_bet_id=winner_bet.id,
            winner_user_id=winner_bet.user_id,
            spin_degree=spin_degree,
            raw_value=raw_value,
        )

    def calculate_winnings(
        self,
        total_pool_ton: Decimal,
        house_fee_percent: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """
        Рассчитать выигрыш после комиссии.

        Args:
            total_pool_ton: Общий пул в TON
            house_fee_percent: Процент комиссии

        Returns:
            (выигрыш, комиссия)
        """
        fee = total_pool_ton * (house_fee_percent / 100)
        winnings = total_pool_ton - fee
        return winnings, fee

    def create_room(
        self,
        room_code: str,
        min_bet_ton: Decimal = Decimal("1"),
        max_bet_ton: Optional[Decimal] = None,
        max_players: int = 10,
        house_fee_percent: Decimal = Decimal("5"),
    ) -> dict:
        """
        Создать параметры новой комнаты.

        Returns:
            Словарь с параметрами комнаты
        """
        server_seed = self.fair_engine.generate_server_seed()
        server_seed_hash = self.fair_engine.hash_server_seed(server_seed)

        return {
            "room_code": room_code,
            "server_seed": server_seed,
            "server_seed_hash": server_seed_hash,
            "min_bet_ton": min_bet_ton,
            "max_bet_ton": max_bet_ton,
            "max_players": max_players,
            "house_fee_percent": house_fee_percent,
            "status": RoomStatus.WAITING,
        }
