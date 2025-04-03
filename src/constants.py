"""
Game constants for the card game.
"""

# Player constants
PLAYER_STARTING_HEALTH = 10
PLAYER_MAX_ENERGY = 3
PLAYER_FIELD_SIZE = 3
PLAYER_STARTING_HAND_SIZE = 4

# Card rarities
RARITY_COMMON = "common"
RARITY_UNCOMMON = "uncommon"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"

# Card rarity probabilities (for shop)
RARITY_PROBABILITIES = {
    RARITY_COMMON: 0.60,
    RARITY_UNCOMMON: 0.25,
    RARITY_RARE: 0.10,
    RARITY_EPIC: 0.05
}

# Shop constants
SHOP_CARDS_OFFERED = 5
SHOP_COST = 30
VICTORY_REWARD = 20

# File paths
CARDS_DATA_PATH = "data/cards.json"
PLAYER_DATA_PATH = "data/player_data.json"
