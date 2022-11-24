const express = require('express');
const app = express();
const http = require('http');
const socketio = require("socket.io");
const {
  sequelize,
  Question,
  Choice,
  Team,
  KeywordQuestion,
  Answer,
  KeywordAnswer,
} = require('../models/index');

const WAIT = 0
const COUNTDOWN = 1
const ANSWER = 2
const TURN_TIMEOUT = 15

function Server() {
  this.io = null;

  this.sockets = {};

  this.turn_countdown = TURN_TIMEOUT;
  this.game_status = WAIT;
  this.round = null;

  this.question = null;
  this.flag = null;
  this.answered = null;

  this.wrongs = {};
}

Server.prototype.start = async function (instance_id) {
  const server = this;

  const httpserver = http.createServer(app);
  this.io = new socketio.Server(httpserver);

  // --------------------------------------------
  app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
  });

  this.io.on("connection", function (socket) {
    server.onConnected(socket);
  });

  httpserver.listen(5000, () => {
    console.log('listening on *:5000');
  });

  try {
    await sequelize.authenticate();
    console.log('Connection has been established successfully.');
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
}

Server.prototype.onConnected = function (socket) {
  const server = this;
  console.log("New connection from " + socket.conn.remoteAddress);

  socket.on("rpc", function (req) {
    if (typeof req !== "object" || typeof req.f !== "string") {
      socket.emit("rpc_ret", {
        seq: req.seq,
        err: 400,
        ret: "Invalid rpc req",
      });
      return;
    }

    if (req.args && typeof req.args !== "object") {
      socket.emit("rpc_ret", {
        seq: req.seq,
        err: 400,
        ret: "Invalid type args",
      });
      return;
    }

    var func_name = "on_" + req.f;
    var method = server[func_name];

    req.socket_id = socket.id;
    req.host = socket.handshake.headers.host;
    if (typeof method === "function") {
      method.call(server, req, function (err, ret) {
        socket.emit("rpc_ret", {
          seq: req.seq,
          err: err,
          ret: ret,
        });
      });
    }
  });

  socket.on("disconnect", function () {
    server.onDisconnected(socket);
  });

  server.sockets[socket.id] = socket;
  server.sockets_count++;
};

Server.prototype.onDisconnected = async function (socket) {
  const server = this;
  console.log("Disconnect from " + socket.conn.remoteAddress);

  const team = await Team.findOne({
    where: {
      socket_id: socket.id,
    }
  });

  delete server.sockets[socket.id];
  server.sockets_count--;
  server.notifyAll("disconnect", team);
  if (team) team.update({ socket_id: null });
};

Server.prototype.notifyAll = async function (event, args) {
  const sockets = this.sockets;
  let blocked = Object.keys(this.wrongs).filter(k => !!this.wrongs[k]);

  for (const socket of Object.values(sockets)) {
    if (!blocked.includes(socket.id)) socket.emit("notify", {
      e: event,
      args: args,
    })
  }
}

Server.prototype.notifyTo = async function (to, event, args) {
  const socket = this.sockets[to];
  if (socket) {
    socket.emit("notify", {
      team_id: to,
      e: event,
      args: args,
    })
  }
}

Server.prototype.on_login = async function (req, func) {
  const { team_id, team_name } = req.args;

  let team = await Team.findOne({
    where: {
      team_id: team_id,
    },
    raw: true
  });

  if (!team) {
    team = await Team.create({
      team_id: team_id,
      team_name: team_name,
      socket_id: req.socket_id,
      point_first: 0,
      point_second: 0,
    });
  } else {
    await Team.update({ socket_id: req.socket_id }, {
      where: {
        team_id: team_id,
      }
    });
  }

  this.notifyAll('login', {
    team_id,
    team_name,
  })
  return func(0, 'ok')
}

Server.prototype.on_teams = async function (req, func) {
  const teams = await Team.findAll();
  return func(0, teams)
}

Server.prototype.on_start_round = function (req, func) {
  const server = this;
  const { round } = req.args;

  server.wrongs = {};
  server.notifyAll('start_round', {
    round,
  })

  server.round = round;
  return func(0, 'ok')
}

Server.prototype.on_questions = async function (req, func) {
  const questions = await Question.findAll({ raw: true });
  for (const question of questions) {
    question.choices = await Choice.findAll({
      where: {
        question_id: question.question_id,
      },
      nest: true,
    });
  }

  return func(0, questions)
}

Server.prototype.on_start_question = async function (req, func) {
  const server = this;
  const { question_id } = req.args;

  const question = await Question.findOne({
    where: {
      question_id,
    },
    raw: true,
  });
  if (!question) return func(400, "Question not exists");
  Object.keys(server.wrongs).forEach(k => server.wrongs[k]--); 

  question.choices = await Choice.findAll({
    where: {
      question_id,
    },
    nest: true,
  });

  server.game_status = COUNTDOWN
  server.question = question
  server.turn_countdown = TURN_TIMEOUT
  server.flag = null
  server.answered = null

  server.notifyAll('start_question', question)

  setTimeout(() => server.tickTurn(), 1000);

  return func(0, 'ok')
}

Server.prototype.on_restart_question = async function (req, func) {
  const server = this;

  server.game_status = COUNTDOWN
  server.turn_countdown = TURN_TIMEOUT
  server.flag = null

  server.notifyAll('restart_question', server.question)
  setTimeout(() => server.tickTurn(), 1000);

  return func(0, 'ok')
}

Server.prototype.tickTurn = function () {
  const server = this;

  if (server.game_status != COUNTDOWN) {
    return;
  } else if (server.turn_countdown > 0) {
    server.turn_countdown--;
    server.notifyAll("countdown", {
      sec: server.turn_countdown,
    });

    setTimeout(() => server.tickTurn(), 1000);
  } else if (server.turn_countdown < 1) {
    server.game_status = WAIT;
    server.notifyAll("timeout", {});
  }
};

Server.prototype.on_ringbell = async function (req, func) {
  const server = this;
  if (server.flag) return func(400, "Out turn");

  if (server.round == 1) {
    if (server.game_status != COUNTDOWN) return func(400, "Question not start");
    server.game_status = ANSWER;
  }

  const team = await Team.findOne({
    where: {
      socket_id: req.socket_id,
    },
    raw: true,
  });

  this.flag = team;
  server.notifyAll("ringbell", team);
  func(0, "ok");
}

Server.prototype.on_answer = async function (req, func) {
  if (this.question == null) return func(400, "Question not start");
  const { team_id, choice_id } = req.args;

  const server = this;
  if (server.game_status == WAIT) {
    return func(400, "Timeout!");
  }

  server.game_status = WAIT;

  const team = await Team.findOne({
    where: {
      team_id,
    },
  });

  if (!server.answered) server.answered = team.socket_id;

  const choices = server.question.choices;
  if (!choices.find(c => c.choice_id == choice_id && c.is_correct)) {
    server.notifyAll("answer", {
      team_id,
      team_name: team.team_name,
      choice_id,
      is_correct: false
    })

    server.wrongs[team.socket_id] = 2;
    return func(400, "Choice incorrect!")
  }

  let point_reward = server.question.point || 10;;
  if (server.answered != team.socket_id) point_reward = 10;

  team.point_first += point_reward;
  team.save()

  server.notifyAll("answer", {
    team_id,
    team_name: team.team_name,
    choice_id,
    is_correct: true
  })

  await Answer.create({
    team_id,
    choice_id,
    question_id: server.question.question_id
  });

  func(0, "ok");
}

Server.prototype.on_kquestions = async function (req, func) {
  const questions = await KeywordQuestion.findAll({ raw: true });

  return func(0, questions.map(q => ({ ...q, image: new URL(process.env.API_HOST + '/media/' + q.image) })))
}

Server.prototype.on_start_kquestion = async function (req, func) {
  const server = this;
  const { question_id } = req.args;

  const question = await KeywordQuestion.findOne({
    where: {
      question_id,
    },
  });
  if (!question) return func(400, "Question not exists");

  question.image = new URL(process.env.API_HOST + '/media/' + question.image)

  server.game_status = COUNTDOWN
  server.question = question
  server.turn_countdown = 20
  server.flag = null

  // ---------------------------------------------------
  const teams = await Team.findAll({
    raw: true,
  });
  const excludes = teams.map(t => t.socket_id);

  for (const socket of Object.values(this.sockets)) {
    if (!excludes.includes(socket.socket_id)) {
      socket.emit("notify", {
        e: 'start_kquestion',
        args: question,
      })
    }
  }
  // ---------------------------------------------------

  setTimeout(() => server.tickTurn(), 1000);

  return func(0, 'ok')
}

Server.prototype.on_kanswer = async function (req, func) {
  const server = this;

  if (server.game_status == WAIT || server.question == null) return func(400, "Question not start");
  const { team_id, keyword } = req.args;
  const team = await Team.findOne({
    where: {
      team_id,
    },
  });

  let is_correct = false;

  let _keyword = keyword.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D')
    .replace(/\s/g, '')
    .toLowerCase();

  let _answer = server.question.keyword.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D')
    .replace(/\s/g, '')
    .toLowerCase();

  if (_keyword && _keyword == _answer) {
    is_correct = true;

    team.point_second += server.question.point || 50;
    team.sec += 20 - server.turn_countdown;
    team.save()
  } else {
    server.wrongs[team.socket_id] = 9999;
  }

  server.notifyAll('kanswer', {
    team_id,
    team_name: team.team_name,
    keyword,
    is_correct,
    sec: 20 - server.turn_countdown,
    point: team.point_second,
  })

  await KeywordAnswer.destroy({
    where: {
      team_id,
      question_id: server.question.question_id,
    }
  })

  await KeywordAnswer.create({
    team_id,
    answer: keyword,
    question_id: server.question.question_id,
    is_correct,
    sec: 20 - server.turn_countdown,
  })

  func(0, "ok");
}

Server.prototype.on_kanswers = async function (req, func) {
  const server = this;

  const answers = await KeywordAnswer.findAll({
    where: {
      question_id: server.question.question_id,
    },
  });

  const result = [];
  for (const answer of answers) {
    answer.sec *= 0.01;

    const team = await Team.findOne({
      where: {
        team_id: answer.team_id,
      },
      raw: true, 
    });

    result.push({
      ...answer.dataValues,
      team_name: team.team_name,
    })
  }

  func(0, result);
}

Server.prototype.on_kverify = async function (req, func) {
  const server = this;

  const { team_id, is_correct } = req.args;
  const team = await Team.findOne({
    where: {
      team_id,
    },
  });

  if (is_correct) {
    team.point_second = 100;
  }

  team.save()
  server.notifyAll('kverify', {
    team_id,
    team_name: team.team_name,
    is_correct,
    point: team.point_second,
  })

  func(0, "ok");
}

Server.prototype.on_top_first = async function (req, func) {
  const teams = await Team.findAll({
    order: [['point_first', 'DESC']],
  });

  this.notifyAll('top_first', { teams })
  return func(0, 'ok')
}

Server.prototype.on_top_second = async function (req, func) {
  const teams = await Team.findAll({
    order: [
      ['point_second', 'DESC'],
      ['sec', 'ASC']
    ],
  });

  this.notifyAll('top_second', { teams })
  return func(0, 'ok')
}

Server.prototype.on_top_third = async function (req, func) {
  const teams = await Team.findAll({
    order: [['point_third', 'DESC']],
  });

  this.notifyAll('top_third', { teams })
  return func(0, 'ok')
}


new Server().start()