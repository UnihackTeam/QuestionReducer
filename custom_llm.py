import ollama

def summarize_questions(page_text: str, questions: list[str]):
	
	prompt = """
	You are an assistant for a teacher who has assigned students a reading task. The students were asked to generate questions based on the text, and you will receive both the text context and the students' questions.

	Please summarize the questions asked by the students. If multiple questions are asked about the same topic, you can group them together. 
	This overview should help the teacher prepare to answer the questions in the next lesson. Especially point out which topics where unclear or difficult for the students. Do not provide answers to the questions.

	Your anser should be strucutred as follows:
	- "Questions": A refined list of the students' questions. Combine similar questions into one.
	- "Problems": A list of the topics that seemed to be unclear or difficult for the students.


	The reading context is as follows:
	<context>
	{}
	</context>

	The students' questions are as follows:
	""".format(page_text)

	for question in questions:
		prompt += "\n- {}".format(question)

	prompt


	response = ollama.chat(model='llama3.1:8b', messages=[
	{
		'role': 'user',
		'content': prompt,
	},
	])
	
	return response['message']['content']