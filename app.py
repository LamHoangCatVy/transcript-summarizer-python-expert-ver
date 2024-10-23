import os
import streamlit as st
import openai
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables in a file called .env
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('MODEL_NAME')  # Sử dụng mô hình đã được định nghĩa trong .env

# Function to summarize transcript content
def summarize_content(transcript):
    system_prompt = """You are an assistant tasked with summarizing lessons on Python programming. 
    Generate a summary of the main topics covered in the lesson and provide a basic Python code example.
    Additionally, generate a few review questions based on the content of the lesson."""
    
    user_prompt = f"Transcript content: {transcript}\n\nSummarize the content and generate a Python example with review questions."

    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message['content']

# Function to convert questions into a pandas DataFrame
def create_question_dataframe(questions):
    question_list = questions.strip().split('\n')  # Assuming each question is separated by a new line
    data = {'STT': range(1, len(question_list) + 1), 'Câu hỏi': question_list}
    df = pd.DataFrame(data)
    return df

# Function to convert DataFrame to Excel and return as downloadable file
def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Review Questions')
    writer.close()  # Ensure to close the writer
    processed_data = output.getvalue()
    return processed_data

# Streamlit app interface
st.title("Tool summarizer script Python")

# Text area for inputting transcript
transcript = st.text_area("Paste your transcript here")

# If transcript is provided, process it
if transcript:
    try:
        # Generate summary, code example, and review questions
        summary_response = summarize_content(transcript)
        st.write("Generated Summary, Code Example, and Review Questions:")
        st.write(summary_response)  # Display the generated content
        
        # Assuming the response contains questions at the end, you can manually extract and create a DataFrame
        # For example, splitting questions from the response (customize if needed)
        if "Questions:" in summary_response:
            questions = summary_response.split("Questions:")[1].strip()
            df = create_question_dataframe(questions)
            st.dataframe(df)  # Display the DataFrame
        
            # Convert DataFrame to Excel and provide download link
            excel_data = convert_df_to_excel(df)
            st.download_button(label="Download Review Questions as Excel", 
                               data=excel_data, 
                               file_name="review_questions.xlsx", 
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please paste your transcript to generate a summary, code example, and review questions.")
