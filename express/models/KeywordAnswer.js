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
      sec: DataTypes.INTEGER,
      is_correct: DataTypes.BOOLEAN,
    },
    {
      sequelize,
      tableName: 'final_keywordanswer',
      modelName: 'KeywordAnswer',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return KeywordAnswer;
};
