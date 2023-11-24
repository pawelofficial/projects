
import sys
from pathlib import Path
# Add the parent directory to sys.path to find animal.py
sys.path.append(str(Path(__file__).parent))

from animal import Animal


class Dog(Animal):
    def __init__(self, name):
        super().__init__("Dog")  # Dog is always the species
        self.name = name

    def make_sound(self):
        print("Woof!")
        
        
if __name__=='__main__':
    d=Dog('Fido')
    d.make_sound()