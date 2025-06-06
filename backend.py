import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
import os
# Import the function from lib.py
from lib import answer_question_from_csv
import tempfile # Added for temporary file handling

app = FastAPI()

CSV_FILE = "feedback.csv"

class FeedbackBase(BaseModel):
    Category: str
    Message: str

class FeedbackEntry(FeedbackBase):
    ID: str
    Timestamp: str

# New Pydantic models for the query endpoint
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# New Pydantic models for topic frequency endpoint
class TopicRequest(BaseModel):
    topic: str

class TopicFrequencyResponse(BaseModel):
    raw_count: int
    percentage: float

@app.post("/feedback", response_model=FeedbackEntry)
async def append_feedback(entry: FeedbackBase):
    """
    Appends a new feedback entry to the CSV file.
    Generates a unique ID and current timestamp for the entry.
    """
    new_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y/%m/%d, %I:%M:%S %p") # Adjusted format to match example

    new_entry_data = {
        "ID": new_id,
        "Timestamp": timestamp,
        "Category": entry.Category,
        "Message": entry.Message
    }

    try:
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            df = pd.read_csv(CSV_FILE)
        else:
            df = pd.DataFrame(columns=["ID", "Timestamp", "Category", "Message"])

        new_df_row = pd.DataFrame([new_entry_data])
        df = pd.concat([df, new_df_row], ignore_index=True)
        
        df.to_csv(CSV_FILE, index=False)
        
        return FeedbackEntry(**new_entry_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

@app.get("/feedback", response_model=List[FeedbackEntry])
async def get_feedback():
    """
    Retrieves all feedback entries from the CSV file.
    """
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return []
    try:
        df = pd.read_csv(CSV_FILE)
        # Ensure Timestamp is string, handle potential NaT or float if column was empty before
        df['Timestamp'] = df['Timestamp'].astype(str)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {str(e)}")

@app.post("/query-feedback", response_model=QueryResponse)
async def query_feedback_data(request: QueryRequest):
    """
    Answers a question based on the feedback data stored in the CSV file.
    """
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        raise HTTPException(status_code=404, detail="Feedback data not found or is empty.")
    
    try:
        answer = answer_question_from_csv(question=request.question, csv_file=CSV_FILE)
        return QueryResponse(answer=answer)
    except Exception as e:
        # Catching generic exception from lib or other issues
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/topic-frequency", response_model=TopicFrequencyResponse)
async def get_topic_frequency(request: TopicRequest):
    """
    Classifies each piece of feedback based on a given topic and returns
    the raw count and percentage of feedback related to that topic.
    """
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return TopicFrequencyResponse(raw_count=0, percentage=0.0)

    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty:
            return TopicFrequencyResponse(raw_count=0, percentage=0.0)

        total_messages = len(df)
        topic_related_count = 0

        for index, row in df.iterrows():
            message_content = str(row.get('Message', '')) # Ensure message is a string
            if not message_content.strip(): # Skip if message is empty or whitespace
                continue

            # Create a temporary CSV with only the current feedback item
            temp_df_data = {col: [row[col]] for col in df.columns}
            temp_df = pd.DataFrame(temp_df_data)
            
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv', newline='') as tmp_file:
                    temp_df.to_csv(tmp_file, index=False)
                    temp_file_path = tmp_file.name
                
                # Ensure the file is flushed and closed before answer_question_from_csv reads it
                # The with statement handles closing, flushing might depend on OS/Python version buffering.
                # If issues arise, explicit flush (tmp_file.flush()) before closing might be needed.

                question = f"Is the following feedback message: '{message_content}' primarily about the topic '{request.topic}'? Answer only with 'yes' or 'no'."
                
                # Call the imported function for classification
                # This assumes answer_question_from_csv can process a CSV with one entry
                # and answer the specific yes/no question.
                answer_text = answer_question_from_csv(question=question, csv_file=temp_file_path)
                
                if answer_text and answer_text.strip().lower() == "yes":
                    topic_related_count += 1
            
            except Exception as e:
                # Log error or handle as needed, e.g., skip this message or raise
                # For now, we'll print a warning and continue, not counting it as related
                print(f"Warning: Error classifying message ID {row.get('ID', 'N/A')}: {str(e)}")
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        percentage = (topic_related_count / total_messages) * 100 if total_messages > 0 else 0.0
        
        return TopicFrequencyResponse(raw_count=topic_related_count, percentage=round(percentage, 2))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Feedback CSV file not found.")
    except pd.errors.EmptyDataError: # Handles empty CSV file after os.path.exists check
        return TopicFrequencyResponse(raw_count=0, percentage=0.0)
    except Exception as e:
        # Catching generic exceptions from pandas or other issues
        raise HTTPException(status_code=500, detail=f"Error processing topic frequency: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Note: The CSV file path is relative to where this script is run.
    # For robust deployment, consider absolute paths or environment variables.
    print(f"Attempting to use CSV file: feedback.csv")
    uvicorn.run(app, host="0.0.0.0", port=8000)
