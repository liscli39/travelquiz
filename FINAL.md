### Cấu trúc

- Nội dung gửi lên
```
{
    "f": "login",
    "args": {
        "team_id": 1,
        "team_name": "Team 1"
    }
}
```
- `f` là tên rpc
- `args` là data truyền lên

Rút gọn vào hàm rpc sẽ có dạng
```
rpc("login", {
  "team_id": 1,
  "team_name": "Team 1"
})

```

- Format trả về 
  -  `rpc_ret`: 
```
{
  "err": 0,
  "ret": "ok"
}
```
  - `notify`:
```
{
    "e": "countdown",
    "args": {}
}
```

### Các lệnh trong game

- Bắt đầu vòng `rpc("start_round", { round: 1 })`
  - Thông báo: `{"e":"start_round","args":{ "round": 1 }}`

- Danh sách các đội `rpc("teams", {})`

- Đăng nhập của đội `rpc("login", {"team_id": 1, "team_name": "Team 1"})`
  - Thống báo:  `{"e":"login","args":{ "team_id": 1 }}`

Vòng 1
- Danh sách câu hỏi `rpc("questions", {})`

- Bắt đầu câu hỏi `rpc("start_question", { question_id: 1 })`
  - Thông báo: `{"e":"start_question","args":{ "question_id": 1, ... }}`
  - Đếm ngược: `{"e":"countdown","args":{"sec":3999}}`
  - Hết giờ: `{"e":"timeout","args":{}}`

- Rung chuông `rpc("ringbell", {})`
  - Thông báo: `{"e":"ringbell","args":{}}`

- Trả lời `rpc("answer", { team_id: 1, choice_id: 1 })`
  - Thông báo: `{"e":"answer","args":{ team_id: 1, choice_id: 1, is_correct: true }}`
  
Vòng 2

- Danh sách câu hỏi `rpc("kquestions", {})`

- Bắt đầu câu hỏi `rpc("start_kquestion", { question_id: 1 })`
  - Thông báo: `{"e":"start_kquestion","args":{ "question_id": 1, ... }}`
  - Đếm ngược: `{"e":"countdown","args":{"sec":3999}}`
  - Hết giờ: `{"e":"timeout","args":{}}`

- Trả lời `rpc("kanswer", { team_id: 1, answer: "keyword" })`
- Danh sách câu trả lời `rpc("kanswers", { question_id: 1 })`