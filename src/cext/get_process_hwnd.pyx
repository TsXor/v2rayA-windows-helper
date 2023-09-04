# distutils: sources = native/get_process_hwnd.c

cdef extern from "native/get_process_hwnd.h":
    void* FindMainWindow(unsigned long process_id)

def find_main_window(process_id: int) -> int:
    return <size_t>FindMainWindow(process_id)
