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
│ ├── main.py # Command-line game entry point
│ ├── main_gui.py # GUI game entry point
│ ├── constants.py # Game constants
│ │
│ ├── models/ # Game data models
│ │ ├── card.py
│ │ ├── player.py
│ │ ├── deck.py
│ │ └── game_state.py
│ │
│ ├── screens/ # Game screens
│ │ ├── screen.py
│ │ ├── screen_manager.py
│ │ ├── ui_elements.py
│ │ ├── home_screen.py
│ │ ├── game_screen.py
│ │ ├── deck_building_screen.py
│ │ └── shop_screen.py
│ │
│ ├── controllers/ # Game logic
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

- **Stage 2: Game Logic**
  - Game state management
  - Card combat system
  - Energy system

- **Stage 3: AI Opponent**
  - Basic AI decision-making
  - Difficulty scaling (Easy, Normal, Hard)
  - AI personality/strategy variation

- **Stage 4: User Interface**
  - Screen framework with screen manager
  - Game screen with board visualization
  - Home screen with main menu
  - Deck building screen
  - Shop screen
  - UI elements (buttons, panels, labels, etc.)

- **Stage 5: Deck Building System**
  - Card collection management
  - Deck builder interface with card filtering and sorting
  - Deck validation (30 cards, max 3 of each)

- **Stage 6: Economy & Progression**
  - Difficulty-based credit rewards
    - Easy: 20 credits
    - Normal: 25 credits 
    - Hard: 30 credits
  - Card pack system (5 cards per pack for 30 credits)
  - Automatic conversion of excess cards to credits
    - Common: 1 credit
    - Uncommon: 3 credits
    - Rare: 5 credits
    - Epic: 10 credits

Future stages to be implemented:

- **Stage 7:** Polish & Quality of Life (animations, sound effects, visual feedback)

## Game Mechanics

- Turn-based card game with energy cost system
- Each player has 10 health and starts with 3 energy per turn
- Players have a hand of cards and a field with 3 slots for cards
- Cards have cost, attack, and health values
- Cards attack the directly opposing card or the player if no card is present
- Different card rarities: Common, Uncommon, Rare, and Epic
- Winning matches rewards credits based on difficulty
- Credits can be used to purchase card packs
- Collection is limited to 3 copies of each card, with excess cards automatically converted to credits

## Getting Started

1. Ensure you have Python 3.8+ installed
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Set up the directory structure as shown above
4. Place all the files in their appropriate locations
5. Run the command-line version with:
   ```bash
   python src/main.py
   ```
6. Run the GUI version with:
   ```bash
   python src/main_gui.py
   ```

## Command-Line Version

The command-line version provides a text-based interface for testing the core game mechanics.

## GUI Version

The GUI version provides a graphical interface with:
- Home screen with menu options
- Game screen with visual card representations
- Deck building screen for managing your collection
- Shop screen for purchasing card packs

## Development Notes

- Card images should be 512x768 PNG files
- Additional card effects and abilities will be implemented in later stages
- The game uses JSON files for data storage and persistence