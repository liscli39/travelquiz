const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class Answer extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  Answer.init(
    {
      answer_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      team_id: DataTypes.INTEGER,
      choice_id: DataTypes.INTEGER,
      question_id: DataTypes.INTEGER,
    },
    {
      sequelize,
      tableName: 'final_answer',
      modelName: 'Answer',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return Answer;
};
