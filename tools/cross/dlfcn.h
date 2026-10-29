#pragma once
#define RTLD_LAZY 0x1
#define RTLD_LOCAL 0x4
void *dlopen(const char *, int);
void *dlsym(void *, const char *);
int dlclose(void *);
char *dlerror(void);
