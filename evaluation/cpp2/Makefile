WARNING_FLAGS = -Wall -Wextra
OPTIMISATION_FLAGS = -O3 -Ofast -march=native -mtune=native -funroll-loops
CPP_FLAGS = -std=c++17

lib: source/lib.cpp
	@echo "Making the libray"
	pip install -q pybind11
	c++ ${WARNING_FLAGS} ${OPTIMISATION_FLAGS} ${CPP_FLAGS} -shared -fPIC `python3 -m pybind11 --includes` source/lib.cpp -o _cpp_mcts`python3-config --extension-suffix`
	python _lib_test.py
	@echo 'Success. Use `import _cpp_mcts` to import the module.'


clean:
	rm -f _cpp_mcts*.so


test: source/main.cpp
	@echo "Test the compilation of the library"
	c++ ${WARNING_FLAGS} ${CPP_FLAGS} -DDEBUG source/main.cpp -o cpp_test
	./cpp_test
	rm cpp_test