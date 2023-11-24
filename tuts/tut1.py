import sys
from pathlib import Path
# Add the parent directory of tut to sys.path to find the zoo package
sys.path.append(str(Path(__file__).parent.parent))
import zoo
d=zoo.Dog('Fido')
d.make_sound()