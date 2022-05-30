# travelquiz-python

## I. Global

POST /register - Đăng ký
- Params: phone, name, address, office, password
- Response: { token }


POST /login - Đăng nhập
- Params: phone, password
- Response: { token }


GET /profile - Lấy thông tin người dùng
- Response: {
    user_id: 4,
    phone: '0123456789',
    name: 'Nguyen',
    address: 'Ha Noi',
    office: 'Miichisoft'
}


GET /questions - Danh sách id của câu hỏi
- Response: [{ 'question_id': 'd938a485f045f141' }]


GET /questions/<str:question_id> - Chi tiết câu hỏi
- Response: {
    'question_id': 'd938a485f045f141',
    'question_text': 'Tôi là ai?',
    'choices': [
        {
            'choice_id': '31b1d73de88bce26',
            'choice_text': 'A'
        },
        {
            'choice_id': '52bfd199eea4e194',
            'choice_text': 'B'
        }
    ]
}


POST /questions/<str:question_id> - Trả lời câu hỏi
- Params: choice_id, time
- Response: ok


GET /answers - Thông kê câu trả lời
- Response: {
    'corrects': 1,
    'total': 2
}


GET /ranks - Xếp hạng
- Response: 'result': [
    {
        'name': 'name',
        'phone': '0123456',
        'corrects': 1,
        'time': 10
    }
]

## II. Group

### 1. API

POST /groups - Tạo group
- Params: group_title
- Response: { 
    group_id: '06d28254102c49a5'
    group_title: 'group_title'
    status: 2
    created_by: 1
    created_at: '2022-05-26T04:53:05.676996Z'
}


GET /groups/<str:group_id> - Lấy thông tin nhóm
- Response: { 
    group_id: '06d28254102c49a5'
    group_title: 'group_title'
    status: 'waiting'
    created_by: 1
    created_at: '2022-05-26T04:53:05.676996Z'
    users: [
        {
            user_id: 4,
            phone: '0123456789',
            name: 'Nguyen',
            address: 'Ha Noi',
            office: 'Miichisoft',
            status: 'waiting'
        }
    ],
}


PUT /groups/<str:group_id> - Bắt đầu chơi
- Response: ok


DELETE /groups/<str:group_id> - Hủy nhóm
- Response: ok


POST /groups/<str:group_id>/join - Tham gia nhóm
- Response: ok


POST /groups/<str:group_id>/ready - Sẵn sàng chơi
- Response: ok


GET /groups/<str:group_id>/answers - Lịch sử trả lời của user
- Response: {
    'corrects': 1,
    'total': 2
}


POST /groups/<str:group_id>/ranks - Xếp hạng user trong nhóm
- Response: 'result': [
    {
        'name': 'name',
        'phone': '0123456',
        'corrects': 1,
        'time': 10
    }
]

### 2. Websocket
- Socket URL: 'ws://' + *host* + '/ws/group/' + *group_id* + '/?' + *token*
- Event: 
    - game_start {
        'event': 'game_start',
        'not_ready': [1, 2, 3],
    }

    - join_room {
        'event': 'join_room',
        'user': 1,
    }

    - ready_play {
        'event': 'ready_play',
        'user': 1,
    }

    - gameover {
        'event': 'gameover',
    }