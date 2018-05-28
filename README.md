PythonJoust
===========

Fork of PythonJoust from https://github.com/StevePaget/PythonJoust.

Wraps the game into a PLE environment. The PLE package was also forked and updated to enable multi player agent learning.


# Installation

To install the updated version of PLE, execute:


```bash
cd lib
git clone https://github.com/bjoernWahle/PyGame-Learning-Environment.git
cd PyGame-Learning-Environment/
pip install -e .
```

All other requirements can be found in requirements.txt

# Usage

main.py starts the RL implementation with agents with a simplified DQN

main_rulebased.py starts the simulation with rule-based agents