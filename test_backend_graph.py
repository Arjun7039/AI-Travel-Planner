import asyncio
from backend.core.graph import build_graph

async def run():
    graph = build_graph()
    initial_state = {
        'user_request': '',
        'destination': 'Goa',
        'origin': 'Bengaluru',
        'travel_dates': {'start': '2026-10-10', 'end': '2026-10-15'},
        'num_travellers': 2,
        'budget_inr': 50000,
        'preferences': {'accommodation': 'mid-range', 'activities': ['sightseeing'], 'cuisine': ['local']},
        'replan_count': 0,
        'agent_messages': []
    }
    try:
        res = await asyncio.to_thread(graph.invoke, initial_state)
        print("SUCCESS:")
        print(res)
    except Exception as e:
        print("EXCEPTION OCCURRED:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
