# Skribbler 0.1.0
- Skribbl.io is an online multiplayer drawing and guessing game where players take turns illustrating a word while others attempt to guess it.
- This project is a Skribbl.io bot coded in Python using Selenium that automatically guesses words based on available hints.
- It implements a custom Trie data structure and employs a Breadth-First Search (BFS) algorithm to efficiently find potentially matching words during gameplay.

## Features
- > **Automatic Word Guessing** : Utilizes the hints available to guess the word.
- > **Custom Trie Data Structure** : Employs BFS on a custom Trie data structure to efficiently find potentially matching words.
- > **Identifies Game State** : Identifies the current phase of the game
- > **Custom Initial Settings** : Can run on a custom wordlist and join private lobbies based on configuration loaded from a `config.json` file or from command line arguments.

## Installation
1. Clone the repository :
```
git clone https://github.com/gmbcode/R3T_Project.git
cd R3T_Project\T2
```
2. Install the dependencies (preferably in a virtual environment)
`pip install -r requirements.txt`

3. Make sure you have Firefox installed and Selenium Webdriver for firefox downloaded
## Usage
1. Run Selenium Webdriver for Firefox 
2. Run `main.py` with desired command line arguments
### Command Line Arguments
| Argument | Command Line Argument | Usage                         |
|----------|-----------------------|-------------------------------| 
| name     | `--name` or `-n`      | Specify the player name       |
| link     | `--link` or `-l`      | Specify link of private lobby |
### Example JSON file usage
```
{
  "name": "playername",
  "wordlistpath" : "path\to\word\list"
}
```
## License
[GNU LGPLv3](https://choosealicense.com/licenses/lgpl-3.0/)