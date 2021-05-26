MAX_CARS_PER_LANE = 100
LAST_CAR = 0
QUANTUM = 20

CURRENT_TIME = 0
edges_lst = [("north", "t1", MAX_CARS_PER_LANE), ("t1", "north", MAX_CARS_PER_LANE),
             ("south", "t1", MAX_CARS_PER_LANE), ("t1", "south", MAX_CARS_PER_LANE),
             ("east", "t2", MAX_CARS_PER_LANE), ("t2", "east", MAX_CARS_PER_LANE),
             ("west", "t2", MAX_CARS_PER_LANE), ("t2", "west", MAX_CARS_PER_LANE)]
current_flow = dict()
loss_dict = dict()

lambda_lst = [10, 12, 14, 16]
distribution_dict = dict()
IS_POISSON = False
IS_LIMITED_CAPACITY = True