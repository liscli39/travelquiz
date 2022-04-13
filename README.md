# travelquiz-python


POST /register - Đăng ký
- Params: phone, name, address, office, password
- Response: { token }


POST /login - Đăng nhập
- Params: phone, password
- Response: { token }


GET /questions - Danh sách id của câu hỏi
- Response: [{ "question_id": "d938a485f045f141" }]


GET /questions/<str:question_id> - Chi tiết câu hỏi
- Response: {
    "question_id": "d938a485f045f141",
    "question_text": "Tôi là ai?",
    "choices": [
        {
            "choice_id": "31b1d73de88bce26",
            "choice_text": "A"
        },
        {
            "choice_id": "52bfd199eea4e194",
            "choice_text": "B"
        }
    ]
}


POST /questions/<str:question_id> - Trả lời câu hỏi
- Params: choice_id, time
- Response: ok


GET /answers - Thông kê câu trả lời
- Response: {
    "corrects": 1,
    "total": 2
}


GET /ranks - Xếp hạng
- Response: "result": [
    {
        "name": "name",
        "phone": "0123456",
        "corrects": 1,
        "time": 10
    }
]
