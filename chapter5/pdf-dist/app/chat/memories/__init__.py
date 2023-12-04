from .sql_memory import build_memory
from .window_memory import window_buffer_memory_builder

memory_map = {
    # sql로 백업되는 버퍼 메모리
    "sql_buffer_memory": build_memory,
    "sql_window_memory": window_buffer_memory_builder
}