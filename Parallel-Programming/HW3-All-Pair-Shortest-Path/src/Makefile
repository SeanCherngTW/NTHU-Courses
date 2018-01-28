CC = mpicc
CXX = mpicxx
CFLAGS = -O
CXXFLAGS = -O
TARGETS = APSP_Pthread APSP_MPI_sync APSP_MPI_async

.PHONY: all
all: $(TARGETS)

.PHONY: clean
clean:
	rm -f $(TARGETS) $(TARGETS:=.o)
