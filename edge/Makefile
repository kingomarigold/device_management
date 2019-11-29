include version.mk

exe=$(version)
lib=$(version)

ifeq ($(arch),)
	arch = x86
endif

all:
	make -C common
	
test:
	make test -C common

run_test: test
	make run_test -C common
	
clean:
	make clean -C common

copy:

tar :
	mkdir -p deliverrables
