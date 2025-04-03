# Card Game Implementation

This is a Python-based implementation of a turn-based card game with deck building elements.

## Project Structure

```
card_game/
│
├── assets/
│ ├── images/
│ │ ├── cards/ # 512x768 PNG card images
│ │ │ ├── common/
│ │ │ ├── uncommon/
│ │ │ ├── rare/
│ │ │ └── epic/
│ │ ├── ui/ # UI elements
│ │ └── backgrounds/
│ │
│ └── sounds/ # Game audio
│
├── data/
│ ├── cards.json # Card definitions
│ └── player_data.json # Player progress
│
├── src/
│ ├── main.py # Game entry point
│ ├── constants.py # Game constants
│ │
│ ├── models/ # Game data models
│ │ ├── card.py
│ │ ├── player.py
│ │ ├── deck.py
│ │ └── game_state.py
│ │
│ ├── screens/ # Game screens (to be implemented)
│ │ ├── home_screen.py
│ │ ├── game_screen.py
│ │ ├── deck_building_screen.py
│ │ └── shop_screen.py
│ │
│ ├── controllers/ # Game logic (to be implemented)
│ │ ├── game_controller.py
│ │ ├── player_controller.py
│ │ └── ai_controller.py
│ │
│ └── utils/ # Helper functions
│ ├── resource_loader.py
│ └── save_manager.py
│
└── README.md
```

## Implementation Stages

Currently implemented:

- **Stage 1: Core Models & Data Structures**
  - Card Model
  - Player Model
  - Deck Model
  - Game State Model
  - Resource loading and saving utilities

Future stages to be implemented:

- **Stage 2:** Game Logic
- **Stage 3:** AI Opponent
- **Stage 4:** User Interface
- **Stage 5:** Deck Building System
- **Stage 6:** Economy & Progression
- **Stage 7:** Polish & Quality of Life

## Game Mechanics

- Turn-based card game with energy cost system
- Each player has 10 health and starts with 3 energy per turn
- Players have a hand of cards and a field with 3 slots for cards
- Cards have cost, attack, and health values
- Cards attack the directly opposing card or the player if no card is present
- Different card rarities: Common, Uncommon, Rare, and Epic

## Getting Started

1. Ensure you have Python 3.8+ installed
2. Set up the directory structure as shown above
3. Place all the files in their appropriate locations
4. Run the game with:

```bash
python src/main.py
```

## Development Notes

- Card images should be 512x768 PNG files
- Additional card effects and abilities will be implemented in later stages
- The game uses JSON files for data storage and persistence

## Testing the Core Models

The current implementation includes a simple demonstration game loop in `main.py` which will:

1. Load cards from `cards.json`
2. Create a new player or load an existing one
3. Create an AI opponent
4. Run through a simplified 3-turn game sequence
5. Save the player's progress

This demonstrates the core functionality of the Card, Player, Deck, and GameState models.
#   c a r d _ g a c h a  
 