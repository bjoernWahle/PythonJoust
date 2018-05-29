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

The python code was only tested with python 2.7, as the PLE package was also designed to work with python 2.7.

# Usage

main.py starts the RL implementation with agents with a simplified DQN
main_rulebased.py starts the simulation with rule-based agents