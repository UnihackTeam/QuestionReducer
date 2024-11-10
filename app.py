import flask
from DatabaseAccess import DatabaseAccess
import custom_llm
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

database = DatabaseAccess(SUPABASE_URL, SUPABASE_KEY)

app = flask.Flask(__name__)

@app.route('/summarize/<int:document_id>')
def reduce(document_id):
    database.clear()
    database.get_questions_by_pages(document_id)
    database.load_temporary_pdf(document_id)

    for page in database.questions_by_page:
        # get page text
        page_text = database.get_page_text(page)

        # get questions associated with this page
        questions = database.questions_by_page[page]

        # summarize questions 
        summary = custom_llm.summarize_questions(page_text, [question.question for question in questions])

        # store summarized questions
        database.write_summary_to_database(document_id, page, summary)

        print("Page: ", page)
        print("Summary: ", summary) 

    database.delete_temporary_pdf()
    return flask.jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=False)
    # curl http://127.0.0.1:5000/summarize/1