# When used like $(call TOxxx, ...) these turn a list of source files
# into the corresponding list of object files, dependency files,
# or both.  When a source file has to be compiled with special flags,
# TOOBJSDEPS is used.  Confusingly, TOOBJSDEPS includes preprocessed source
# file names, but this is what allows 'make src.i' to produce proper
# preprocessed source when src.c needs a customized compile flag.
# See Submakefile.skel for an example.
#TOOBJS = $(patsubst %.cc,../objects/%.o,$(patsubst %.c,../objects/%.o,$(1)))
#TODEPS = $(patsubst %.cc,../objects/%.d,$(patsubst %.c,../objects/%.d,$(1)))
#TOOBJSDEPS = $(call TOOBJS,$(1)) $(call TODEPS, $(1)) $(patsubst %.cc,%.ii,$(patsubst %.c,%.i,$(1)))

TARGET := libnml.so

LIBNMLSRCS := $(addprefix ,\
        rcs/rcs_print.cc rcs/rcs_exit.cc \
\
        os_intf/_sem.c os_intf/_shm.c os_intf/_timer.c os_intf/sem.cc \
        os_intf/shm.cc os_intf/timer.cc \
\
        buffer/locmem.cc buffer/memsem.cc buffer/phantom.cc buffer/physmem.cc \
        buffer/recvn.c buffer/sendn.c buffer/shmem.cc buffer/tcpmem.cc \
\
        cms/cms.cc cms/cms_aup.cc cms/cms_cfg.cc cms/cms_in.cc cms/cms_dup.cc \
        cms/cms_pm.cc cms/cms_srv.cc cms/cms_up.cc cms/cms_xup.cc \
        cms/cmsdiag.cc cms/tcp_opts.cc cms/tcp_srv.cc \
\
        nml/cmd_msg.cc nml/nml_mod.cc nml/nml_oi.cc nml/nml_srv.cc nml/nml.cc \
        nml/nmldiag.cc nml/nmlmsg.cc nml/stat_msg.cc \
\
        linklist/linklist.cc)

CC := gcc
CXX := g++
LDFLAGS :=
DEFINES :=
INCLUDES := ..
INCLUDE := $(patsubst %,-I%, $(INCLUDES)) -I$(RTDIR)/include -I./rcs -I./os_intf -I./buffer -I./cms -I./nml
INCLUDE += -I./linklist -I../rtapi -I./posemath -I./inifile
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


#$(call TOOBJSDEPS, $(LIBNMLSRCS)) : EXTRAFLAGS=-fPIC

#USERSRCS += $(LIBNMLSRCS)

#TARGETS += ../lib/libnml.so ../lib/libnml.so.0

#../lib/libnml.so.0: $(call TOOBJS,$(LIBNMLSRCS)) ../lib/liblinuxcnchal.so
#	$(ECHO) Creating shared library $(notdir $@)
#	@mkdir -p ../lib
#	@rm -f $@
#	$(Q)$(CXX) $(LDFLAGS) -Wl,-soname,$(notdir $@) -shared -o $@ $^
