"""Skribbler main file"""
# TODO : Add error handling and support for drawing
import time
from sys import exit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from TrieImplementation import *
import argparse
import json
import os

# Set default word list path
wordlist_path = 'Wordlist\\wtxt.txt'
parser = argparse.ArgumentParser()
parser.add_argument('--name', '-n', type=str, help='Set skribbl.io player name', action='store')
parser.add_argument('--link', '-l', type=str, help='Set skribbl.io game link', action='store')

game_states = {
    'Home Screen': 0,
    'Waiting Screen': 1,
    'Guess Phase': 2,
    'Draw Phase': 3,
    'Invalid State': 4
}

args = parser.parse_args()
player_name = args.name
game_link = args.link
if player_name is not None:
    pass
else:
    # Default name set
    player_name = 'Skribbler'
if game_link is not None:
    pass
else:
    game_link = 'https://skribbl.io/'
# Let json file take priority
try:
    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        wl_path = config['wordlistpath']
        name = config['name']
        if name is not None:
            player_name = name
        if wl_path is not None:
            if os.path.isfile(wl_path):
                wordlist_path = wl_path
except Exception:
    pass
# Create the Trie of the specified word list
root = load_root(wordlist_path)
driver = webdriver.Firefox()
driver.get(game_link)
driver.maximize_window()
input_name = driver.find_element(By.CLASS_NAME, 'input-name')
play_button = driver.find_element(By.CLASS_NAME, 'button-play')


def get_game_state() -> int:
    """
    Returns an integer representing the current game state
    :return : An integer representing the current game state
    :rtype: int
    """
    try:
        driver.find_element(By.CLASS_NAME, 'input-name')
        driver.find_element(By.CLASS_NAME, 'button-play')
        home_element = driver.find_element(By.ID, 'home')
        style_info = home_element.get_attribute('style')
        if style_info == 'display: none;':
            pass
        else:
            return game_states['Home Screen']
    except Exception:
        pass
    try:
        hints = driver.find_elements(By.CLASS_NAME, 'hint')
        if len(hints) > 1:
            return game_states['Guess Phase']
        else:
            pass
    except Exception:
        pass
    try:
        driver.find_element(By.CLASS_NAME, 'description.waiting')
        return game_states['Waiting Screen']
    except Exception as e:
        pass
    try:
        word_element = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[2]/div[4]/div[1]')
        if word_element.text == 'DRAW THIS':
            return game_states['Draw Phase']
    except Exception:
        pass
    return game_states['Invalid State']


print(f"Current game state : {get_game_state()}")
input_name.send_keys(player_name)
play_button.send_keys(Keys.ENTER)
driver.implicitly_wait(5)
time.sleep(5)

hints = driver.find_elements(By.CLASS_NAME, 'hint')

while True:
    print(f"Current game state : {get_game_state()}")
    if get_game_state() == game_states['Guess Phase']:
        hints = driver.find_elements(By.CLASS_NAME, 'hint')
        input_element = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[8]/form/input')

        search_query = ''.join(hint.text for hint in hints)
        if len(search_query) > 1:
            print(search_query)
            # Get possible guesses
            guess_list = custom_search(root, search_query)
            # Only initiate auto guessing if less than 10 possible words
            if 0 < len(guess_list) < 10:
                for elem in guess_list:
                    if get_game_state() != game_states['Guess Phase']:
                        continue
                    input_element.send_keys(elem)
                    input_element.send_keys(Keys.ENTER)
                    time.sleep(1.5)
    if get_game_state() == game_states['Draw Phase']:
        hints = driver.find_elements(By.CLASS_NAME, 'hint')
        word = ''.join(hint.text for hint in hints)


    time.sleep(0.5)
driver.close()
exit(0)
