TARGET := /home/fukang/Gitee/qtvcp/lib/liblinuxcncini.so

LIBNMLSRCS := ./inifile.cc ./inivar.cc

CC := gcc
CXX := g++
LDFLAGS :=
DEFINES :=
INCLUDES := ..
INCLUDE := $(patsubst %,-I%, $(INCLUDES)) -I./  -I../../
CFLAGS := -g -Wall -o3 -fPIC $(DEFINES) $(INCLUDE)
CXXFLAGS := $(CFLAGS) -DHAVE_CONFIG_H -std=gnu++11
SHARE :=  -shared -o

OBJS := $(patsubst %.cc,%.o,$(patsubst %.c,%.o,$(LIBNMLSRCS)))

.PHONY : everything objs clean veryclean rebuild

everthing : $(TARGET)

all : $(TARGET)

objs : $(OBJS)

rebuild : veryclean everthing

clean :
	rm -fr *.o

veryclean : clean
	rm -fr $(TARGET)

$(TARGET) : $(OBJS)
	$(CXX) $(CXXFLAGS) $(SHARE) $@ $(OBJS) $(LDFLAGS) $(LIBS)

