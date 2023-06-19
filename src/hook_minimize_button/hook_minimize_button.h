#include <windows.h>
#include <tchar.h>
#include <stdlib.h>
#include <stdio.h>

#ifdef UNICODE
#define LPCSTR_T  LPCWSTR
#else
#define LPCSTR_T  LPCSTR
#endif // !UNICODE

#define DLLIMPORT __declspec(dllexport)

BOOL DLLIMPORT RegisterHook(DWORD, HMODULE);
void DLLIMPORT UnRegisterHook();