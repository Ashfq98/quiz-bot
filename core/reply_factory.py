from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    # Get current question id from session, default to None for first interaction
    current_question_id = session.get("current_question_id", None)

    if current_question_id is None:
        # Welcome the user and show the first question
        bot_responses.append(BOT_WELCOME_MESSAGE)
        first_question, next_question_id = get_next_question(-1)  # Get the first question
        bot_responses.append(first_question)

        # Initialize current_question_id to 0 for the first question
        session["current_question_id"] = next_question_id
        session.save()
        return bot_responses

    # Record the user's answer and validate it
    success, error = record_current_answer(message, current_question_id, session)
    if not success:
        return [error]

    # Get the next question
    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)  # Present the next question to the user
    else:
        # End the quiz and show the final score
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    # Update the session with the next question id
    session["current_question_id"] = next_question_id
    session.save()
    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question to django session.
    """
    # Get the correct answer for the current question
    correct_answer = PYTHON_QUESTION_LIST[current_question_id]["answer"]

    # Store the user's answer
    session[f"answer_{current_question_id}"] = answer

    # Check if the user's answer is correct
    if answer == correct_answer:
        session[f"score_{current_question_id}"] = 1
    else:
        session[f"score_{current_question_id}"] = 0

    return True, ""


def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    """
    # Increment the question id to get the next question
    next_question_id = current_question_id + 1

    # Check if there are more questions
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        question_text = question_data["question_text"]
        options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question_data["options"])])
        return f"{question_text}\n\n{options}", next_question_id
    elif current_question_id == -1:  # Special case for getting the first question
        question_data = PYTHON_QUESTION_LIST[0]
        question_text = question_data["question_text"]
        options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question_data["options"])])
        return f"{question_text}\n\n{options}", 0
    else:
        return None, -1  # No more questions, end the quiz


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(session.get(f"score_{i}", 0) for i in range(total_questions))

    score_percentage = (correct_answers / total_questions) * 100

    return f"Quiz complete! Your score is {correct_answers}/{total_questions} ({score_percentage:.2f}%)."
