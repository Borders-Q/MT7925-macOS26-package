#pragma once
void exit(int) __attribute__((noreturn));
int atexit(void (*)(void));
