const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class KeywordQuestion extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  KeywordQuestion.init(
    {
      question_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      question_text: DataTypes.STRING,
      image: DataTypes.INTEGER,
      keyword: DataTypes.STRING,
      order: DataTypes.INTEGER,
    },
    {
      sequelize,
      tableName: 'final_keyword_question',
      modelName: 'KeywordQuestion',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return KeywordQuestion;
};
