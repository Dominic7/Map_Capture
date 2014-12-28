Map_Capture
===========

Simple GUI based Stratego game to demonstrate Expectiminimax Algorithm 
 - 1 Human player and upto 3 computer players
 - 2 difficulties

Rules:
============
 - First to either capture the entire board or elimate all other players wins
 - Can only move one square in the 4 cardinal directions (N(Up),S(Down),E(Right),W(Left)) each turn
 - Claiming/Capturing a square works as follows:
    - Square with higher population has a higher percentage of winning
    - Smaller of two pops determines how many times square is attacked
    - If after the battle a square is left with 0 population then that square is claimed if it was the defending square else
      the attacking player looses that square
 - At the end of the players turn the population of each of their squares is increased based on the current popualtion count
    

To Run:
============
 - Make sure to have python version 2.7.8 (Could work with Python 3 but is untested) installed
 - tkinter module is installed
 - Needs to be run from GUI based OS (tkinter requires gui but underlying sim can be ported and ran from terminal/cmd)

 * Only tested on Windows(8.1) but should be no issues with Linux (as long as above requirements are met)
 $> python mapCapture.py
          or
 - Right click and open with IDLE and then Run Module
 

Needed Improvements (12-28-14):
============
 - Optimize Expectiminimax algorithm
    - Rework scoring function
    - Remove all traces of alpha/beta (No alpha/beta with expecti because of the battle chance)
 - Improve player start placement
 - Port to better GUI module - (PyGame, WxPython, others...)
    - Seperate GUI and underlying game in seperate threads(processes since GIL)
 - Look into putting each AI player(or only in pairs of two) on its own thread(Process since GIL) to speed up next move calculation 
    - Pairs of two possble implementation
      - First player seperate process - method doesn't change
      - Second player starts either 4 processes(one for each possible move of player 1) and finds its best move while checking
        to see if player 1's process has completed -- and in turn killing the processes that didn't guess that move
        or
      - Second player guesses player 1's best move and creates a process to calculate its best move based on that guess
        *Could introduce bias on player 2 for always basing move on guess
 - Ability to change game board base shape (hexagon, triangle, etc...)
 - Ability to have 0 - N human players and 0 - N computer players
 - Improve difficuilty levels
