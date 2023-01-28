import game_pb2 as Game

myGame = Game.Observation()

print(myGame.debug, myGame.vehicle.current_brake)