'''
    Copyright (c) 2017 Timothy Savannah, All Rights Reserved

    Code is licensed under terms of LGPL v3

    Requires lrzip to be installed.
'''
# vim: syntax=c

import cffi

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


#if _POSIX_C_SOURCE >= 200809L
  #define HAS_MEMSTREAM
#endif

#include <Lrzip.h>

char *doCompress(const char *data, size_t dataSize, int compressMode, size_t *outLen)
{
    bool success;
    Lrzip *lr;
    char *ret;

    FILE *inStream;

    FILE *outStream;
    size_t outStreamSize;

    #ifdef HAS_MEMSTREAM
      char *outStreamBuffer;

      outStream = open_memstream(&outStreamBuffer, &outStreamSize);
    #else
      outStream = tmpfile();
    #endif


    fflush(outStream);

    /* LRZIP Input not supported from memstream (requires a real fd) */
    inStream = tmpfile();

    write(fileno(inStream), data, dataSize);

    lseek(fileno(inStream), 0, SEEK_SET);

    success = lrzip_init();
    if ( !success )
            return NULL;


    lr = lrzip_new((Lrzip_Mode)compressMode);

/*    lrzip_config_env(lr); */
    lrzip_log_level_set(lr, 0); 
    lrzip_outfile_set(lr, outStream);
    lrzip_file_add(lr, inStream);
    lrzip_log_stdout_set(lr, NULL);
    lrzip_log_stderr_set(lr, NULL);

    success = lrzip_run(lr);
    if ( !success )
    {
        fprintf(stderr, "Failed\\n");
    }


    lrzip_free(lr);
    fflush(outStream);

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
    fclose(outStream);

    #ifdef HAS_MEMSTREAM
      free(outStreamBuffer);
    #endif

    *outLen = outStreamSize;


    return ret;
}


char *doDecompress(const char *data, size_t dataSize, size_t *outLen)
{
    bool success;
    Lrzip *lr;
    char *ret;

    FILE *inStream;

    FILE *outStream;
    size_t outStreamSize;

    #ifdef HAS_MEMSTREAM
      char *outStreamBuffer;

      outStream = open_memstream(&outStreamBuffer, &outStreamSize);
    #else
      outStream = tmpfile();
    #endif

    fflush(outStream);

    /* LRZIP Input not supported from memstream (requires a real fd) */
    inStream = tmpfile();

    write(fileno(inStream), data, dataSize);

    lseek(fileno(inStream), 0, SEEK_SET);

    success = lrzip_init();
    if ( !success )
            return NULL;


    lr = lrzip_new(LRZIP_MODE_DECOMPRESS);

/*    lrzip_config_env(lr); */
    lrzip_log_level_set(lr, 0); 
    lrzip_outfile_set(lr, outStream);
    lrzip_file_add(lr, inStream);
    lrzip_log_stdout_set(lr, NULL);
    lrzip_log_stderr_set(lr, NULL);

    
    success = lrzip_run(lr);
    if ( !success )
    {
        fprintf(stderr, "Failed\\n");
    }


    lrzip_free(lr);
    fflush(outStream);

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

    #ifdef HAS_MEMSTREAM
      free(outStreamBuffer);
    #endif

    *outLen = outStreamSize;


    return ret;
}

void _do_free(void *ptr)
{
    free(ptr);
}

''', libraries=['lrzip'])

if __name__ == '__main__':
    ffi.compile()


