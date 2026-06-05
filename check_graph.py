from backend.core.graph import build_graph

try:
    g = build_graph()
    print("Graph compiled successfully")
except Exception as e:
    print("Graph compilation failed:", repr(e))
