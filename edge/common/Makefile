################################################################################
#
#   File:Makefile
# 
#   Description: This make file can build the object for
#		x86 as well as ARM platform.
# 		Usage> make (Default x86)
#                      make arch=x86
#                      make arch=ARM toolchain=<toolchainpath>
# 
################################################################################

include ../common.mk

#Include Path for Headers
APP_INCLUDES = -I./include -I../test_utils/include

MAIN_APP_PATH = ../deliverables
TARGET_DIR = $(MAIN_APP_PATH)/$(LIBDIR)

LDFLAGS = -shared -g

LIBS = 

#Final Output Build App Name
APP_NAME = common

# Executable Path
TARGET = $(LIBDIR)/lib$(APP_NAME).so
TEST_TARGET = $(BINDIR)/test_client_socket

TESTLIBS += $(LIBS) -L$(LIBDIR) -l$(APP_NAME) -lCppUTest -lCppUTestExt
