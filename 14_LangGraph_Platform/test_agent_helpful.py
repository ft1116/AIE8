from langgraph_sdk import get_sync_client


def main():
    client = get_sync_client(url="http://localhost:2024")
    for chunk in client.runs.stream(
        None,  # Threadless run
        "agent_with_helpfulness",  # Graph id from langgraph.json (graphs)
        input={
            "messages": [
                {
                    "role": "human",
                    "content": "What is the MuonClip optimizer, and what paper did it first appear in?",
                }
            ]
        },
        stream_mode="updates",
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        # Show node name if it's an update event
        if chunk.event == "updates" and chunk.data:
            for node_name in chunk.data.keys():
                print(f"Node: {node_name}")
        print(chunk.data)
        print("\n\n")


if __name__ == "__main__":
    main()

