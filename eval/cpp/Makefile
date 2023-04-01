WARNING_FLAGS = -Wall -Wextra
OPTIMISATION_FLAGS = -O3 -Ofast -march=native -mtune=native -funroll-loops
CPP_FLAGS = -std=c++17

lib: mcts.cpp lib.cpp
	echo "Making the libray"
	pip install pybind11
	c++ ${WARNING_FLAGS} ${OPTIMISATION_FLAGS} ${CPP_FLAGS} -shared -fPIC `python3 -m pybind11 --includes` mcts.cpp  lib.cpp -o _cpp_mcts`python3-config --extension-suffix`
	python cpp_mcts_test.py


test:
	c++ -O3 -Ofast -march=native -mtune=native -funroll-loops -std=c++17 mcts.cpp main.cpp -o cpp_test
	./cpp_test