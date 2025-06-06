import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
import os
# Import the function from lib.py
from lib import answer_question_from_csv

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

if __name__ == "__main__":
    import uvicorn
    # Note: The CSV file path is relative to where this script is run.
    # For robust deployment, consider absolute paths or environment variables.
    print(f"Attempting to use CSV file: feedback.csv")
    uvicorn.run(app, host="0.0.0.0", port=8000)
