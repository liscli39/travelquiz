const SQLModel = require('sequelize').Model;

module.exports = (sequelize, DataTypes) => {
  class Team extends SQLModel {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
  }
  Team.init(
    {
      team_id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      team_name: DataTypes.STRING,
      socket_id: DataTypes.STRING,
      point: DataTypes.INTEGER,
    },
    {
      sequelize,
      tableName: 'final_team',
      modelName: 'Team',
      freezeTableName: true,
      timestamps: false,
    },
  );
  return Team;
};