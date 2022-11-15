const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class KeywordAnswer extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  KeywordAnswer.init(
    {
      answer_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      team_id: DataTypes.INTEGER,
      question_id: DataTypes.INTEGER,
      answer: DataTypes.STRING,
    },
    {
      sequelize,
      tableName: 'final_keyword_answer',
      modelName: 'KeywordAnswer',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return KeywordAnswer;
};
