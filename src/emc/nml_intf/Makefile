TARGET := /home/fukang/Gitee/qtvcp/lib/liblinuxcnc.a

CC := gcc
CXX := g++
AR := ar
RANLIB := ranlib
LIBS :=
LDFLAGS :=
DEFINES := 
INCLUDE := -I./ -I../ -I../../ -I../motion -I../../libnml/posemath -I../rs274ngc -I../../libnml/rcs \
	-I../../libnml/nml -I../../libnml/cms -I../../rtapi -I../../libnml/inifile -I../../hal -I../../libnml/linklist
CFLAGS := -g -Wall -o3 $(DEFINES) $(INCLUDE)
CXXFLAGS := $(CFLAGS) -DHAVE_CONFIG_H -std=gnu++11

#SOURCE := $(wildcard *.c) $(wildcard *.cc)
SOURCE := \
    ./emcglb.c \
    ../rs274ngc/modal_state.cc \
    ./emc.cc \
    ./emcpose.c \
    ./emcargs.cc \
    ./emcops.cc \
    ./canon_position.cc \
    ../ini/emcIniFile.cc \
    ../ini/iniaxis.cc \
    ../ini/inijoint.cc \
    ../ini/initool.cc \
    ../ini/initraj.cc \
    ../ini/inihal.cc \
    ./interpl.cc
OBJS := $(patsubst %.c, %.o, $(patsubst %.cc, %.o, $(SOURCE)))

.PHONY : everything objs clean veryclean rebuild

everything : $(TARGET)

all : $(TARGET)

objs : $(OBJS)

rebuild : veryclean everything

clean :
	rm -fr *.o

veryclean : clean
	rm -fr $(TARGET)

$(TARGET) : $(OBJS)
	$(AR) cru $(TARGET) $(OBJS)
	$(RANLIB) $(TARGET)
