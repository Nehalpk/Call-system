def convert_to_string(knowledge_list):
    knowledge = ""
    for item in knowledge_list:
        question = item.get('Question', '')
        answer = item.get('Answer', '')
        knowledge += f"Question: {question}\nAnswer: {answer}\n\n"
    return knowledge.strip()


