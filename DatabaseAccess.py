
from typing import List
from supabase import create_client, Client
from urllib import request
import PyPDF2
import os

class Question:
    def __init__(self, id: int, question: str, doc: int, page: int):
        self.id = id
        self.question = question
        self.doc = doc
        self.page = page

    def to_json(self):
        timestamp = ""
        return {
            "id": self.id,
            "doc": self.doc,
            "asked_by": 0,
            "position": self.position,
            "question": self.question,
            "answer": "",
            "created_at": timestamp
        }

class DatabaseAccess:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase : Client = create_client(supabase_url, supabase_key)
        self.questions_by_page : dict = {}

        self.reduced_questions : List[Question] = []

    def clear(self):
        self.questions_by_page = {}
        self.reduced_questions = []

    def __get_questions_from_database(self, document_id: int):      
        response = self.supabase.table("questions").select("*").execute()
   
        if response.data == []:
            print("No questions found")
            return []

        questions = [Question(row["id"], row["question"], row["doc"], row["page"]) for row in response.data]
        return questions
    
    def __group_questions_by_page(self, questions : List[Question]) -> dict:
        questions_by_page = {}
        for question in questions:
            if question.page in questions_by_page:
                questions_by_page[question.page].append(question)
            else:
                questions_by_page[question.page] = [question]
        return questions_by_page
    
    def load_temporary_pdf(self, document_id: int):
        pdf_url = self.supabase.table("docs").select("file_path").eq("id", document_id).execute().data[0]["file_path"]

        # load pdf from url
        local_file_name = "temp.pdf"

        # Download and save the file
        request.urlretrieve(pdf_url, local_file_name)

    def get_page_text(self, page_number: int):
        page_text = ""

        # Open the PDF file
        with open("temp.pdf", "rb") as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            
            # Extract text from the specific page
            page_text = pdf_reader.pages[page_number].extract_text()
            page_text = page_text.replace(" -\n", "")
        
        return page_text
    
    def delete_temporary_pdf(self):
        os.remove("temp.pdf")


    def get_questions_by_pages(self, document_id: int):
        questions = self.__get_questions_from_database(document_id)
        self.questions_by_page = self.__group_questions_by_page(questions)
  
    def write_summary_to_database(self, document_id: int, page: int, summary: str):
        # check if the page already has a summary
        response = self.supabase.table("pages").select("*").eq("doc_id", document_id).eq("page_number", page).execute()
        if response.data != []:
            # update the summary
            self.supabase.table("pages").update({"summarization": summary}).eq("doc_id", document_id).eq("page_number", page).execute()
        else:
            # insert new summary
            self.supabase.table("pages").insert({"doc_id": document_id, "page_number": page, "summarization": summary}).execute()


