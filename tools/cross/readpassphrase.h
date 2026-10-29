#pragma once
#include <stddef.h>
#define RPP_REQUIRE_TTY 0x02
char *readpassphrase(const char *, char *, size_t, int);
