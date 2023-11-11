const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class Question extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  Question.init(
    {
      question_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      question_text: DataTypes.STRING,
    },
    {
      sequelize,
      tableName: 'final_question',
      modelName: 'Question',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return Question;
};
