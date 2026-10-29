#pragma once
#include <stddef.h>
typedef struct __sFILE FILE;
extern FILE *__stderrp;
#define stderr __stderrp
int printf(const char *, ...);
int fprintf(FILE *, const char *, ...);
int fputs(const char *, FILE *);
int puts(const char *);
int putchar(int);
