from .sql_memory import build_memory

memory_map = {
    # sql로 백업되는 버퍼 메모리
    "sql_buffer_memory": build_memory
}