######################################################################
#
#   File: common.mk
#
#   Description:
#
#
#
######################################################################
#

############################ APP VERSION #############################
REPO_DIR = $(dir $(lastword $(MAKEFILE_LIST)))

include $(REPO_DIR)version.mk

#
######################## BUILD PATHS - BEGIN #########################
OBJ_ROOT = obj
LIB_ROOT = lib
BIN_ROOT = bin
SRCDIR = src
TESTDIR = test
CLIDIR = cli
TEST_OBJ_ROOT = $(OBJ_ROOT)/test
CLI_OBJ_ROOT = $(OBJ_ROOT)/cli

COMMON_DIR = $(REPO_DIR)Common

ifeq ($(arch),x86)
  ARCHDIR = x86
else ifeq ($(arch),ARM)
  ARCHDIR = arm
else
  ARCHDIR = x86
endif

LIBDIR = $(LIB_ROOT)/$(ARCHDIR)
BINDIR = $(BIN_ROOT)/$(ARCHDIR)
OBJDIR = $(OBJ_ROOT)/$(ARCHDIR)
TOBJDIR = $(TEST_OBJ_ROOT)/$(ARCHDIR)
COBJDIR = $(CLI_OBJ_ROOT)/$(ARCHDIR)

#
# Cumulative Includes
#
# Combination of APP and TC Includes, defined in module's Makefile
#
INCLUDES = $(APP_INCLUDES) $(TC_INCLUDES)


SRCS = $(shell find $(SRCDIR) -name '*.cpp')
OBJS = $(patsubst $(SRCDIR)/%.cpp, $(OBJDIR)/%.o, $(SRCS))

TESTS = $(shell find $(TESTDIR) -name '*.cpp')
TOBJS = $(patsubst $(TESTDIR)/%.cpp, $(TOBJDIR)/%.o, $(TESTS))

CLIS = $(shell if [ -d "cli" ]; then find $(CLIDIR) -name '*.cpp'; fi) 
CLIOBJS =  $(patsubst $(CLIDIR)/%.cpp, $(COBJDIR)/%.o, $(CLIS)) 

TESTLIBS = -lpthread 


ifeq ($(ARCHDIR),x86)
	TESTLIBS+= -lCppUTest -lCppUTestExt
endif



#
# Compute LD_LIBRARY_PATH
#
EMPTY =
EMPTY +=
TESTLIB_PATHS = $(subst $(EMPTY),:,$(patsubst -L%,%,$(filter -L%, $(TESTLIBS))))

CLI_TARGET_DIR = $(REPO_DIR)/Deliverables/gateway/cli

######################## BUILD PATHS - END ##########################
#
#################### TOOLCHAIN SELECTION - BEGIN ####################

ifeq ($(arch),x86)
        CXX = g++ -g 
else ifeq ($(arch),ARM)
        ifneq ($(toolchain),)
                CXX = $(toolchain) -s 
        else
        $(error Toolchain Parameter value not specified)
        endif
else
        CXX = g++ -g 
endif

ifeq ($(arch),x86)
        CXXFLAGS = -Wall -fprofile-arcs -ftest-coverage -fpermissive -fPIC -std=c++0x -g 
else ifeq ($(arch),ARM)
        CXXFLAGS = -Wall -fpermissive -fPIC
else
        CXXFLAGS = -Wall -fprofile-arcs -ftest-coverage -fpermissive -fPIC -std=c++0x -g 
endif

#################### TOOLCHAIN SELECTION - END ######################
#
######################## TARGETS - BEGIN ############################

ifeq ($(REQLOG),true)
all: build-logger build-main
clean: clean-logger
cli: build-logger build-cli
build-cli: build-main $(CLIOBJS) $(LOBJ)
	$(CXX) $(CXXFLAGS) -o $(CLI_TARGET) $(CLIOBJS) $(LOBJ) -L$(LIBDIR) $(LIBS) $(TESTLIBS)  $(CLILIBS)
else
all: build-main
cli: build-cli
build-cli: build-main $(CLIOBJS)
	$(CXX) $(CXXFLAGS) -o $(CLI_TARGET) $(CLIOBJS) -L$(LIBDIR) $(LIBS) $(TESTLIBS)  $(CLILIBS)
endif

test: build-test

clean:
	rm $(OBJ_ROOT) $(LIB_ROOT) $(BIN_ROOT) $(TEST_PLUGIN_OBJ_DIR) -Rf

copy: build-main
	mkdir -p $(TARGET_DIR)
	cp -Rf $(TARGET) $(TARGET_DIR)

cli_copy: build-main build-cli
	mkdir -p $(CLI_TARGET_DIR)
	cp -Rf $(CLI_TARGET) $(CLI_TARGET_DIR)



build-main: create-paths $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS) $(LIBS)


build-test: build-main $(TOBJS)
	$(CXX) $(CXXFLAGS) -o $(TEST_TARGET) $(TOBJS) -L$(LIBDIR) $(LIBS) $(TESTLIBS)
	

run_test: test
	export LD_LIBRARY_PATH=$(TESTLIB_PATHS) && $(TEST_TARGET) $(TEST_ARGS)
	
run_cli: build-cli
	export LD_LIBRARY_PATH=$(TESTLIB_PATHS) && $(CLI_TARGET) $(CLI_ARGS)

run_cli_debug: build-cli
	export LD_LIBRARY_PATH=$(TESTLIB_PATHS) && gdb --args $(CLI_TARGET) $(CLI_ARGS)
	
run_test_debug: test
	export LD_LIBRARY_PATH=$(TESTLIB_PATHS) && gdb --args $(TEST_TARGET) $(TEST_ARGS)

run_test_valgrind: test
	export LD_LIBRARY_PATH=$(TESTLIB_PATHS) && valgrind --track-origins=yes --leak-check=full $(TEST_TARGET) 2>valgrind.out

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@


$(TOBJDIR)/%.o: $(TESTDIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@
	
$(COBJDIR)/%.o: $(CLIDIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@


create-paths:
	mkdir -p $(OBJDIR)
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(TOBJDIR)
	mkdir -p $(COBJDIR)


######################## TARGETS - END ##############################


