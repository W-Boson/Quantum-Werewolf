"""
Created on Sun Jan  4 16:20:54 2026

@author: Z_Boson
"""

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import cli as cli_module
import backend

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    original_system = cli_module.system
    
    def patched_system(cmd):
        if cmd == 'clear':
            clear_screen()
        else:
            original_system(cmd)
    
    cli_module.system = patched_system
    
    cli_module.cli()