import game_pb2 as Game

myGame = Game.observation()
myGame.test = "hey"
myGame.vehicle.current_speed = 100



print(myGame.vehicle.current_speed)