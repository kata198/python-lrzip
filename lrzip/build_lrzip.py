'''
    Copyright (c) 2017 Timothy Savannah, All Rights Reserved

    Code is licensed under terms of LGPL v3

    Requires lrzip to be installed.
'''
# vim: syntax=c

import cffi
import os

if '_HAS_LIBSHMFILE' in os.environ:
    linkWith = ['lrzip', 'shmfile']
    os.environ['CFLAGS'] = os.environ.get('CFLAGS', '') + ' -D_HAS_LIBSHMFILE=1'
else:
    linkWith = ['lrzip']

ffi = cffi.FFI()

ffi.cdef('''
    char *doCompress(const char *data, size_t dataSize, int compressMode, size_t *outLen);
    void _do_free(void *ptr);

    char *doDecompress(const char *data, size_t dataSize, size_t *outLen);
''')

ffi.set_source('_lrzip', '''
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#ifdef _HAS_LIBSHMFILE

#include <shmfile.h>

#endif

#if _POSIX_C_SOURCE >= 200809L
  #define HAS_MEMSTREAM
#else
  #warning "No memstream, building without memstream support!"
#endif

#include <Lrzip.h>

#ifdef _HAS_LIBSHMFILE

static inline FILE *_getShmFile(void *data)
{
    FILE *ret;
    char instreamName[64];

_shmfile_regen_name_retry:
    sprintf(instreamName, "/%p_%d_%d_%d_%d", data, getpid(), rand() % 9000000, rand() % 9000000, rand() % 9000000);

    /*printf("Name is: %s\\n", instreamName);*/
    errno = 0;
    ret = fshm_open(instreamName, 0600, FSHM_OWNER);
    if ( !ret )
    {
        if ( errno == EEXIST )
            /* We generated a name that collided with another... try again! */
            goto _shmfile_regen_name_retry;
        /*fprintf(stderr, "Error is: [ %d ]  %s\\n\\n", errno, strerror(errno));*/
        return NULL;
    }

    return ret;
}
#else
  #warning "No libshmfile! Building without shmfile support."
#endif

char *doCompress(const char *data, size_t dataSize, int compressMode, size_t *outLen)
{
    bool success;
    Lrzip *lr;
    char *ret = NULL;

    FILE *inStream;

    FILE *outStream;
    size_t outStreamSize;

    #ifdef HAS_MEMSTREAM
      char *outStreamBuffer;

      outStream = open_memstream(&outStreamBuffer, &outStreamSize);
    #else
      #ifndef _HAS_LIBSHMFILE
      outStream = tmpfile();
      #else
      outStream = _getShmFile((void*)data);
      if ( !outStream )
        outStream = tmpfile();
      #endif
    #endif

    fflush(outStream);

    /* LRZIP Input not supported from memstream (requires a real fd) */
    #ifndef _HAS_LIBSHMFILE
      inStream = tmpfile();
    #else
      inStream = _getShmFile((void*)data);
      if ( inStream == NULL )
          inStream = tmpfile();
    #endif


    write(fileno(inStream), data, dataSize);

    lseek(fileno(inStream), 0, SEEK_SET);

    success = lrzip_init();
    if ( !success )
    {
        fclose(inStream);
        fclose(outStream);
        return NULL;
    }


    lr = lrzip_new((Lrzip_Mode)compressMode);

/*    lrzip_config_env(lr); */
    lrzip_log_level_set(lr, 0); 
    lrzip_outfile_set(lr, outStream);
    lrzip_file_add(lr, inStream);
    lrzip_log_stdout_set(lr, NULL);
    lrzip_log_stderr_set(lr, NULL);

    success = lrzip_run(lr);

    lrzip_free(lr);
    fflush(outStream);
    if ( success )
    {

        #ifdef HAS_MEMSTREAM
          ret = malloc(outStreamSize + 1);
          memcpy(ret, outStreamBuffer, outStreamSize);
        #else
          fseek(outStream, 0L, SEEK_END);
          outStreamSize = ftell(outStream);

          fseek(outStream, 0L, SEEK_SET);
          lseek(fileno(outStream), 0L, SEEK_SET);

          ret = malloc(outStreamSize + 1);
          fread(ret, 1, outStreamSize, outStream);
    //      read(fileno(outStream), ret, outStreamSize);
       #endif

        ret[outStreamSize] = '\\0';

        *outLen = outStreamSize;
    }

    fclose(outStream);

    #ifdef HAS_MEMSTREAM
      free(outStreamBuffer);
    #endif


    fclose(inStream);

    return ret;
}


char *doDecompress(const char *data, size_t dataSize, size_t *outLen)
{
    bool success;
    Lrzip *lr;
    char *ret = NULL;

    FILE *inStream;

    FILE *outStream;
    size_t outStreamSize;

    #ifdef HAS_MEMSTREAM
      char *outStreamBuffer;

      outStream = open_memstream(&outStreamBuffer, &outStreamSize);
    #else
      #ifndef _HAS_LIBSHMFILE
      outStream = tmpfile();
      #else
      outStream = _getShmFile((void*)data);
      if ( !outStream )
        outStream = tmpfile();
      #endif
    #endif

    fflush(outStream);

    #ifndef _HAS_LIBSHMFILE
      inStream = tmpfile();
    #else
      inStream = _getShmFile((void*)data);
      if ( inStream == NULL )
          inStream = tmpfile();
    #endif

    write(fileno(inStream), data, dataSize);

    lseek(fileno(inStream), 0, SEEK_SET);

    success = lrzip_init();
    if ( !success )
    {
        fclose(inStream);
        fclose(outStream);
        return NULL;
    }


    lr = lrzip_new(LRZIP_MODE_DECOMPRESS);

/*    lrzip_config_env(lr); */
    lrzip_log_level_set(lr, 0); 
    lrzip_outfile_set(lr, outStream);
    lrzip_file_add(lr, inStream);
    lrzip_log_stdout_set(lr, NULL);
    lrzip_log_stderr_set(lr, NULL);

    
    success = lrzip_run(lr);

    lrzip_free(lr);
    fflush(outStream);

    if ( success )
    {
        #ifdef HAS_MEMSTREAM
          ret = malloc(outStreamSize + 1);
          memcpy(ret, outStreamBuffer, outStreamSize);
        #else
          fseek(outStream, 0L, SEEK_END);
          outStreamSize = ftell(outStream);

          lseek(fileno(outStream), 0L, SEEK_SET);

          ret = malloc(outStreamSize + 1);
          read(fileno(outStream), ret, outStreamSize);
       #endif

        ret[outStreamSize] = '\\0';
        fclose(outStream);

        *outLen = outStreamSize;
    }

    #ifdef HAS_MEMSTREAM
      free(outStreamBuffer);
    #endif


    fclose(inStream);

    return ret;
}

void _do_free(void *ptr)
{
    free(ptr);
}

''', libraries=linkWith)

if __name__ == '__main__':
    ffi.compile()


