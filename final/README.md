Luồng chung kết
- Đôi chơi:
  - S: Đăng nhập
  1. Vòng 1
  - R: Bắt đầu câu hỏi
  - S: Rung chuông

  2. Vòng 2
  - R: Bắt đầu câu hỏi
  - S: Trả lời câu hỏi
  - S: Giành quyền trả lời Chủ đề
  - R: Trả lời sai


- Admin
  1. Vòng 1
  - S: Lấy danh sách câu hỏi
  - S: Bắt đầu câu hỏi
  - R: Rung chuông
  - S: Xác nhận câu trả lời
  - S: Bắt đầu câu hỏi

  2. Vòng 2
  - S: Lấy danh sách câu hỏi từ khóa
  - S: Bắt đầu câu hỏi
  - R: Hết thời gian, danh sách kết quả
  - S: Bắt đầu câu hỏi
  - R: Dành quyền trả lời chủ đề
  - S: Xác nhận trả lời chủ đề


- Các type để gọi socket

TYPE_RESPONSE = 'send_response'
# Turn 1
TYPE_GET_QUESTIONS = 'get_questions'
TYPE_START_QUESTION = 'start_question'
TYPE_RING_BELL = 'ring_bell'
TYPE_TIMEOUT = 'timeout'
TYPE_ANSWER_QUESTION = 'answer_question'
# Turn 2
TYPE_GET_KQUESTIONS = 'get_kquestions'
TYPE_START_KQUESTION = 'start_kquestion'
TYPE_ANSWER_KQUESTION = 'answer_kquestion'
TYPE_ANSWER_KEYWORD = 'answer_keyword'
TYPE_ANSWERS_LIST = 'answers_list'