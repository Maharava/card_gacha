"""
AI controller for managing the computer opponent's actions with varying difficulty levels.
"""
from typing import Tuple, List, Dict, Any, Optional
from enum import Enum
import random
from ..models.game_state import GameState, GamePhase
from ..models.player import Player
from ..models.card import Card
from ..models.deck import Deck
from ..constants import PLAYER_FIELD_SIZE


class AIDifficulty(Enum):
    """
    Enum representing different AI difficulty levels.
    """
    EASY = 1
    NORMAL = 2
    HARD = 3


class AIPersonality(Enum):
    """
    Enum representing different AI personalities/strategies.
    """
    AGGRESSIVE = "aggressive"  # Prefers attacking cards, goes for player damage
    DEFENSIVE = "defensive"    # Prefers high-health cards, protects own health
    BALANCED = "balanced"      # Mix of aggressive and defensive
    CONTROL = "control"        # Focuses on board control and resource efficiency


class AIController:
    """
    Controls the AI opponent's decisions during the game.
    
    This controller is responsible for:
    - Deciding which cards to play based on difficulty level
    - Choosing strategic card placements
    - Managing AI's turn phases
    - Adapting strategy based on game state
    """
    
    def __init__(self, game_state: GameState, difficulty: AIDifficulty = AIDifficulty.NORMAL, 
                 personality: AIPersonality = AIPersonality.BALANCED):
        """
        Initialize the AI controller.
        
        Args:
            game_state (GameState): The current game state
            difficulty (AIDifficulty): Difficulty level of the AI
            personality (AIPersonality): Personality/strategy of the AI
        """
        self.game_state = game_state
        self.difficulty = difficulty
        self.personality = personality
        
        # Initialize strategy weights based on personality
        self._init_strategy_weights()
    
    def _init_strategy_weights(self) -> None:
        """
        Initialize strategy weights based on AI personality.
        """
        # Default weights
        self.weights = {
            "attack": 1.0,
            "health": 1.0,
            "cost_efficiency": 1.0,
            "board_control": 1.0,
            "direct_damage": 1.0,
            "counter_opponent": 1.0,
        }
        
        # Adjust weights based on personality
        if self.personality == AIPersonality.AGGRESSIVE:
            self.weights["attack"] = 2.0
            self.weights["direct_damage"] = 1.8
            self.weights["health"] = 0.7
        elif self.personality == AIPersonality.DEFENSIVE:
            self.weights["health"] = 2.0
            self.weights["board_control"] = 1.5
            self.weights["direct_damage"] = 0.7
        elif self.personality == AIPersonality.CONTROL:
            self.weights["board_control"] = 2.0
            self.weights["counter_opponent"] = 1.8
            self.weights["cost_efficiency"] = 1.5
        
        # Further adjust weights based on difficulty
        if self.difficulty == AIDifficulty.EASY:
            # Introduce more randomness and reduce optimal play for easy AI
            for key in self.weights:
                self.weights[key] *= 0.7
                
        elif self.difficulty == AIDifficulty.HARD:
            # Make hard AI more efficient and optimal
            for key in self.weights:
                self.weights[key] *= 1.3
    
    def take_turn(self) -> Dict[str, Any]:
        """
        Execute the AI's turn.
        
        Returns:
            Dict[str, Any]: Results of the AI's actions during its turn
        """
        result = {
            "events": []
        }
        
        # Only process if it's the AI's turn
        if self.game_state.current_player != self.game_state.opponent:
            return result
        
        # Process based on current phase
        if self.game_state.current_phase == GamePhase.PLAY:
            # Try to play cards during the play phase
            play_results = self._play_cards()
            result["events"].extend(play_results["events"])
        
        return result
    
    def _play_cards(self) -> Dict[str, Any]:
        """
        AI attempts to play cards from its hand to the field strategically.
        
        Returns:
            Dict[str, Any]: Results of the AI's card plays
        """
        ai_player = self.game_state.opponent
        human_player = self.game_state.player
        result = {"events": []}
        
        # Get all field positions and evaluate their strategic value
        field_positions = self._evaluate_field_positions(ai_player, human_player)
        
        # Keep playing cards until no more good plays are available
        while True:
            # Evaluate all cards in hand
            playable_cards_with_scores = []
            
            for idx, card in enumerate(ai_player.hand):
                # Skip cards the AI can't afford
                if card.cost > ai_player.energy:
                    continue
                
                # Calculate the card's strategic value
                score = self._calculate_card_priority(card, ai_player, human_player)
                
                # Add randomness based on difficulty
                if self.difficulty == AIDifficulty.EASY:
                    score += random.uniform(-1.5, 1.5)
                elif self.difficulty == AIDifficulty.NORMAL:
                    score += random.uniform(-0.8, 0.8)
                elif self.difficulty == AIDifficulty.HARD:
                    score += random.uniform(-0.3, 0.3)
                
                playable_cards_with_scores.append((idx, card, score))
            
            # If no cards can be played, end the phase
            if not playable_cards_with_scores:
                break
            
            # Sort cards by their score (highest first)
            playable_cards_with_scores.sort(key=lambda x: x[2], reverse=True)
            
            # Get the best card to play
            best_card_idx, best_card, _ = playable_cards_with_scores[0]
            
            # Find the best position for this card
            best_position = None
            best_position_score = float('-inf')
            
            for pos, (position, score) in enumerate(field_positions):
                # Skip positions that are already filled
                if ai_player.field[position] is not None:
                    continue
                
                # Calculate how good this card would be in this position
                position_score = self._calculate_position_score(best_card, position, ai_player, human_player)
                
                # Apply position's base score
                position_score += score
                
                if position_score > best_position_score:
                    best_position_score = position_score
                    best_position = position
            
            # If no valid position found, stop playing cards
            if best_position is None:
                break
            
            # Play the card
            success, message = ai_player.play_card(best_card_idx, best_position)
            
            if success:
                # Record the event
                result["events"].append({
                    "type": "ai_card_played",
                    "card": best_card.name,
                    "field_position": best_position,
                    "energy_remaining": ai_player.energy
                })
            else:
                # If play failed for some reason, stop trying
                break
        
        return result
    
    def _evaluate_field_positions(self, ai_player: Player, human_player: Player) -> List[Tuple[int, float]]:
        """
        Evaluate all field positions based on strategic value.
        
        Args:
            ai_player (Player): The AI player
            human_player (Player): The human player
            
        Returns:
            List[Tuple[int, float]]: List of (position, score) tuples
        """
        position_scores = []
        
        for position in range(PLAYER_FIELD_SIZE):
            score = 0
            
            # Check if the position is already occupied
            if ai_player.field[position] is not None:
                continue
            
            # Check what's in the opposing position
            opposing_card = human_player.field[position]
            
            if opposing_card:
                # Position with opposing card gets higher score for board control
                score += opposing_card.attack * self.weights["counter_opponent"]
                
                # If we have aggressive personality, prioritize attacking high-health enemy cards
                if self.personality == AIPersonality.AGGRESSIVE:
                    score += opposing_card.hp * 0.5
                    
                # If we have defensive personality, prioritize blocking high-attack enemy cards
                if self.personality == AIPersonality.DEFENSIVE:
                    score += opposing_card.attack * 0.8
            else:
                # Empty opposing position means direct damage to player
                score += self.weights["direct_damage"] * 2
                
                # Aggressive AI really likes direct damage
                if self.personality == AIPersonality.AGGRESSIVE:
                    score += 2.0
            
            # Center position (1) is often strategically valuable
            if position == 1:
                score += 0.5
            
            position_scores.append((position, score))
        
        return position_scores
    
    def _calculate_position_score(self, card: Card, position: int, ai_player: Player, human_player: Player) -> float:
        """
        Calculate how well a specific card fits in a specific position.
        
        Args:
            card (Card): The card to evaluate
            position (int): The field position to evaluate
            ai_player (Player): The AI player
            human_player (Player): The human player
            
        Returns:
            float: Score indicating how good the placement is
        """
        score = 0
        
        # Check what's in the opposing position
        opposing_card = human_player.field[position]
        
        if opposing_card:
            # If our attack can destroy the opposing card, that's good
            if card.attack >= opposing_card.hp:
                score += opposing_card.attack * 1.2  # Value of removing threat
                
                # Aggressive AI values destroying enemy cards more
                if self.personality == AIPersonality.AGGRESSIVE:
                    score += opposing_card.attack * 0.5
            
            # If our health can survive the opposing attack, that's good
            if card.hp > opposing_card.attack:
                score += card.attack * 0.8  # We'll survive to attack again
                
                # Defensive AI values surviving enemy attacks more
                if self.personality == AIPersonality.DEFENSIVE:
                    score += card.hp * 0.5
            
            # If neither, we're trading cards, value based on efficiency
            else:
                # If we're trading up (our card is cheaper), that's good
                if card.cost < opposing_card.cost:
                    score += (opposing_card.cost - card.cost) * self.weights["cost_efficiency"]
        else:
            # No opposing card means direct damage to player
            score += card.attack * self.weights["direct_damage"]
            
            # High HP cards are better used to block than for direct damage
            if card.hp > 3 and self.personality == AIPersonality.DEFENSIVE:
                score -= card.hp * 0.3  # Slight penalty for "wasting" a high-health card
        
        return score
    
    def _calculate_card_priority(self, card: Card, ai_player: Player, human_player: Player) -> float:
        """
        Calculate the priority score for playing a card based on game state.
        
        Args:
            card (Card): The card to evaluate
            ai_player (Player): The AI player
            human_player (Player): The human player
            
        Returns:
            float: Priority score (higher is better)
        """
        # Base score based on card stats
        attack_value = card.attack * self.weights["attack"]
        health_value = card.hp * self.weights["health"]
        
        # Cost efficiency (stats per energy)
        stats_sum = card.attack + card.hp
        cost_efficiency = (stats_sum / max(1, card.cost)) * self.weights["cost_efficiency"]
        
        # Calculate base score from these components
        base_score = attack_value + health_value + cost_efficiency
        
        # Adjust based on AI personality and game state
        situational_score = 0
        
        # Aggressive AI prioritizes attack power
        if self.personality == AIPersonality.AGGRESSIVE:
            situational_score += card.attack * 0.5
            
            # When opponent is low on health, prioritize direct damage
            if human_player.health < 5:
                situational_score += card.attack * 1.5
        
        # Defensive AI prioritizes high health for protection
        elif self.personality == AIPersonality.DEFENSIVE:
            situational_score += card.hp * 0.5
            
            # When AI is low on health, prioritize defensive cards
            if ai_player.health < 5:
                situational_score += card.hp * 1.0
        
        # Control AI prioritizes efficient trades
        elif self.personality == AIPersonality.CONTROL:
            # Prioritize cards with balanced stats
            balance = 1.0 - abs(card.attack - card.hp) / max(1, (card.attack + card.hp))
            situational_score += balance * 2.0 * self.weights["board_control"]
        
        # Board state analysis
        empty_slots = sum(1 for slot in ai_player.field if slot is None)
        
        # If few slots remain, prioritize impactful cards
        if empty_slots <= 1:
            situational_score += card.attack * 0.8
        
        # Factor in current energy situation
        energy_ratio = ai_player.energy / ai_player.max_energy
        
        # If energy is high, slight preference for expensive cards
        if energy_ratio > 0.7:
            situational_score += card.cost * 0.3
        # If energy is low, preference for cheaper cards
        elif energy_ratio < 0.4:
            situational_score += (ai_player.max_energy - card.cost) * 0.4
        
        # Final score combination
        final_score = base_score + situational_score
        
        # Hard difficulty makes better use of special card properties (would expand with more card effects)
        if self.difficulty == AIDifficulty.HARD:
            # For now just a placeholder for future card effects
            if "dragon" in card.name.lower() or "phoenix" in card.name.lower():
                final_score += 1.0  # Value powerful-themed cards higher
                
        return final_score
    
    @classmethod
    def create_for_difficulty(cls, game_state: GameState, difficulty_level: str) -> 'AIController':
        """
        Factory method to create an AI controller with appropriate difficulty and personality.
        
        Args:
            game_state (GameState): The current game state
            difficulty_level (str): Difficulty level string ('easy', 'normal', 'hard')
            
        Returns:
            AIController: Configured AI controller
        """
        # Map string to enum values
        difficulty_map = {
            'easy': AIDifficulty.EASY,
            'normal': AIDifficulty.NORMAL,
            'hard': AIDifficulty.HARD
        }
        
        # Default to normal if invalid string
        difficulty = difficulty_map.get(difficulty_level.lower(), AIDifficulty.NORMAL)
        
        # Select a personality based on difficulty
        if difficulty == AIDifficulty.EASY:
            # Easy AI gets a random personality, but weighted toward basic strategies
            personalities = [
                AIPersonality.BALANCED, AIPersonality.BALANCED,  # Doubled to increase probability
                AIPersonality.AGGRESSIVE, AIPersonality.DEFENSIVE
            ]
            personality = random.choice(personalities)
        elif difficulty == AIDifficulty.NORMAL:
            # Normal AI gets a truly random personality
            personality = random.choice(list(AIPersonality))
        else:
            # Hard AI gets the most advanced strategy
            personality = AIPersonality.CONTROL
        
        return cls(game_state, difficulty, personality)


def create_ai_deck(card_database: Dict[str, Card], difficulty: AIDifficulty) -> Deck:
    """
    Create an AI deck based on difficulty level.
    
    Args:
        card_database (Dict[str, Card]): Dictionary of all available cards
        difficulty (AIDifficulty): Difficulty level of the AI
        
    Returns:
        Deck: Configured deck for the AI
    """
    # Group cards by rarity
    common_cards = [card for card in card_database.values() if card.rarity == "common"]
    uncommon_cards = [card for card in card_database.values() if card.rarity == "uncommon"]
    rare_cards = [card for card in card_database.values() if card.rarity == "rare"]
    epic_cards = [card for card in card_database.values() if card.rarity == "epic"]
    
    # Create a deck with rarity distribution based on difficulty
    ai_cards = []
    
    if difficulty == AIDifficulty.EASY:
        # Easy AI gets mostly common cards
        common_count = 20
        uncommon_count = 8
        rare_count = 2
        epic_count = 0
    elif difficulty == AIDifficulty.NORMAL:
        # Normal AI gets a balanced deck
        common_count = 15
        uncommon_count = 10
        rare_count = 4
        epic_count = 1
    else:  # HARD
        # Hard AI gets a powerful deck with more rare and epic cards
        common_count = 10
        uncommon_count = 12
        rare_count = 6
        epic_count = 2
    
    # Add cards to the deck
    if common_cards:
        for _ in range(common_count):
            ai_cards.append(random.choice(common_cards))
    
    if uncommon_cards:
        for _ in range(uncommon_count):
            ai_cards.append(random.choice(uncommon_cards))
    
    if rare_cards:
        for _ in range(rare_count):
            ai_cards.append(random.choice(rare_cards))
    
    if epic_cards and epic_count > 0:
        for _ in range(epic_count):
            ai_cards.append(random.choice(epic_cards))
    
    # Create and shuffle the deck
    ai_deck = Deck(name=f"{difficulty.name} AI Deck", cards=ai_cards)
    ai_deck.shuffle()
    
    return ai_deck


def create_ai_opponent(card_database: Dict[str, Card], difficulty: str = "normal") -> Player:
    """
    Create an AI opponent with appropriate difficulty level.
    
    Args:
        card_database (Dict[str, Card]): Dictionary of all available cards
        difficulty (str): Difficulty level string ('easy', 'normal', 'hard')
        
    Returns:
        Player: Configured AI player
    """
    # Map string to enum value
    difficulty_map = {
        'easy': AIDifficulty.EASY,
        'normal': AIDifficulty.NORMAL,
        'hard': AIDifficulty.HARD
    }
    ai_difficulty = difficulty_map.get(difficulty.lower(), AIDifficulty.NORMAL)
    
    # Create appropriate deck
    ai_deck = create_ai_deck(card_database, ai_difficulty)
    
    # Create player with name reflecting difficulty
    ai_name = f"{ai_difficulty.name.capitalize()} AI Opponent"
    
    return Player(ai_name, ai_deck)
