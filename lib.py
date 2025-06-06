import pandas as pd
import json

# Attempt to import transformers and set a flag
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None  # Define pipeline as None if import fails

def answer_question_from_csv(question: str, csv_file: str) -> str:
    """
    Answers a question based on feedback data from a CSV file.
    Handles cases where the 'transformers' library might not be available.

    Parameters:
    - question (str): The question to be answered.
    - csv_file (str): Path to the CSV file containing feedback data.

    Returns:
    - str: The answer extracted from the feedback data, or an error message.
    """
    if not TRANSFORMERS_AVAILABLE:
        return "Error: The 'transformers' library is not installed or failed to import. LLM functionality is unavailable."

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

    try:
        # Initialize the question-answering pipeline
        # This check is redundant if TRANSFORMERS_AVAILABLE is false, but good for clarity
        if not pipeline: 
            return "Error: Transformers pipeline could not be initialized (likely due to import failure)."
        
        qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

        # Use the pipeline to answer the question based on the context
        result = qa_pipeline(question=modified_question, context=context)
        
        if result and 'answer' in result and result['answer'] is not None:
            return result['answer']
        else:
            return "Error: Could not extract an answer from the model. The context might be too short or irrelevant."

    except Exception as e:
        return f"Error during question answering pipeline execution: {str(e)}"

def analyze_topic_json(topic: str, message: str) -> dict:
    """
    Analyzes if a message is about a specific topic using the QA pipeline,
    and returns a structured JSON response.
    
    Parameters:
    - topic (str): The topic to check for in the message.
    - message (str): The feedback message content to analyze.
    
    Returns:
    - dict: A dictionary with 'is_related' (bool) and 'explanation' (str) keys.
    """
    if not TRANSFORMERS_AVAILABLE:
        return {"is_related": False, "explanation": "Error: Transformers library not available"}
        
    try:
        if not pipeline:
            return {"is_related": False, "explanation": "Error: Pipeline initialization failed"}
            
        qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
        
        # Create a structured prompt that guides the model to return JSON-like answers
        system_prompt = ("System: You are an AI assistant that analyzes if feedback is related to a specific topic. "
                         "Respond in a very specific format as follows: "
                         "{\"is_related\": true/false, \"explanation\": \"brief explanation of your reasoning\"}")
        
        question = f"{system_prompt}\n\nIs this feedback about '{topic}'? Message: '{message}'"
        
        # Create a context that contains the instructions for structured output
        context = (f"The feedback message is: {message}\n\n"
                  f"When analyzing if it's related to '{topic}', always respond with a "
                  f"JSON structure with 'is_related' (boolean) and 'explanation' (string) fields.")
                  
        result = qa_pipeline(question=question, context=context)
        answer = result.get('answer', '')
        
        # Try to parse the answer as JSON
        try:
            # Look for JSON-like patterns in the answer
            if '{' in answer and '}' in answer:
                json_str = answer[answer.find('{'):answer.rfind('}')+1]
                parsed_result = json.loads(json_str)
                
                # Ensure required fields exist
                if not isinstance(parsed_result, dict):
                    parsed_result = {}
                    
                # Set default values if keys are missing
                return {
                    "is_related": parsed_result.get("is_related", False),
                    "explanation": parsed_result.get("explanation", "No explanation provided")
                }
            else:
                # If no JSON structure found, make a best effort to determine relation
                is_related = "yes" in answer.lower() or "true" in answer.lower() or "related" in answer.lower()
                return {
                    "is_related": is_related,
                    "explanation": answer.strip()
                }
                
        except json.JSONDecodeError:
            # If we can't parse JSON, fall back to simple pattern matching
            is_related = "yes" in answer.lower() or "true" in answer.lower() or "related" in answer.lower()
            return {
                "is_related": is_related, 
                "explanation": answer.strip()
            }
            
    except Exception as e:
        return {
            "is_related": False,
            "explanation": f"Error during topic analysis: {str(e)}"
        }

if __name__ == "__main__":
    # Example usage
    question = "What are the common themes in the feedback?"
    csv_file = "feedback.csv"  # Replace with your actual CSV file path
    answer = answer_question_from_csv(question, csv_file)
    print(answer)