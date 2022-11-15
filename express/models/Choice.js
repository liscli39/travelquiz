const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class Choice extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  Choice.init(
    {
      choice_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      choice_text: DataTypes.STRING,
      is_correct: DataTypes.BOOLEAN,
      question_id: DataTypes.INTEGER,
    },
    {
      sequelize,
      modelName: 'Choice',
      tableName: 'final_choice',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return Choice;
};
