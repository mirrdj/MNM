import pandas as pd
from transformers import pipeline

def answer_question_from_csv(question: str, csv_file: str) -> str:
    """
    Answers a question based on feedback data from a CSV file.

    Parameters:
    - question (str): The question to be answered.
    - csv_file (str): Path to the CSV file containing feedback data.

    Returns:
    - str: The answer extracted from the feedback data.
    """
    # Load the feedback data
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        return f"Error: The file '{csv_file}' was not found."
    except pd.errors.EmptyDataError:
        return f"Error: The file '{csv_file}' is empty."
    except pd.errors.ParserError:
        return f"Error: The file '{csv_file}' could not be parsed."

    # Check if the 'Message' column exists
    if 'Message' not in df.columns:
        return "Error: The CSV file does not contain a 'Message' column."

    # Shuffle the DataFrame rows
    df = df.sample(frac=1).reset_index(drop=True)

    # Combine all feedback entries into a single context
    context = "\n".join(df['Message'].dropna().astype(str).tolist())

    # Define the system prompt
    system_prompt = ("System: You are an AI assistant that provides anonymous transformations of user feedback. "
                     "Never identify an individual user. Based on the following feedback, answer the question. Question: ")
    
    # Prepend the system prompt to the user's question
    modified_question = f"{system_prompt}{question}"

    # Initialize the question-answering pipeline with a more advanced pre-trained model
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

    # Use the pipeline to answer the question based on the context
    result = qa_pipeline(question=modified_question, context=context)

    return result['answer']

if __name__ == "__main__":
    # Example usage
    question = "What are the common themes in the feedback?"
    csv_file = "feedback.csv"  # Replace with your actual CSV file path
    answer = answer_question_from_csv(question, csv_file)
    print(answer)