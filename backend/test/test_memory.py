from langchain_core.messages import HumanMessage
def test_memory_isolation(app_instance):

    memory = app_instance.state.chat_memory

    memory.add_message(
        "user_a",
        HumanMessage(content="hello")
    )

    history_a = memory.get_history("user_a")
    history_b = memory.get_history("user_b")

    assert len(history_a) == 1
    assert len(history_b) == 0