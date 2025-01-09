from chatbot import recommend_medicine

while True:
    question = input("Enter your symptoms (or type 'exit' to quit): ")
    if question.lower() == "exit":
        break
    response = recommend_medicine(question)
    print(response)




