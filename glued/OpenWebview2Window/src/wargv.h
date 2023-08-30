#pragma once
#ifndef __WARGV_H__
#define __WARGV_H__

#ifdef __cplusplus
extern "C" {
#endif

int get_argc(void);
wchar_t** get_wargv(void);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // __WARGV_H__
