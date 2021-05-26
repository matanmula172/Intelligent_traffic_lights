import networkx as nx
import matplotlib.pyplot as plt
import random
from car import *
from consts import *
import numpy as np


# returns true of edged is entering a traffic light node
def entering_traffic_light(edge):
    return edge[1][0] == 't'


def insert_cars_into_queue(queue, cars):
    for i in range(cars):
        global LAST_CAR
        global CURRENT_TIME
        LAST_CAR += 1
        car = Car(CURRENT_TIME, LAST_CAR)
        queue.append(car)
    return queue


def remove_cars_from_queue(queue, cars):
    for i in range(cars):
        queue.pop(0)
    return queue


def transfer_cars_q1_to_q2(q1, q2, cars):
    for i in range(cars):
        if len(q1) == 0:
            break
        car = q1.pop(0)
        q2.append(car)
    return q1, q2


# returns traffic light id of an edge
def get_traffic_light_id(edge):
    if entering_traffic_light(edge):
        return edge[1]
    return edge[0]


# initializes current flow dict to zeroes
def init_current_flow():
    for edge in edges_lst:
        current_flow[edge] = list()


def init_distribution_dict():
    i = 0
    global lambda_lst
    for edge in edges_lst:
        if not entering_traffic_light(edge):
            distribution_dict[edge] = lambda_lst[i]
            e = get_succ_edge(edge)
            distribution_dict[e] = lambda_lst[i]
            i += 1


# initializes loss dict to zeroes
def init_loss_dict():
    loss_dict["t1"] = 0
    loss_dict["t2"] = 0


# returns a successor edge of edge
def get_succ_edge(edge):
    if entering_traffic_light(edge):
        return None
    for e in edges_lst:
        if entering_traffic_light(e) and e[1] == edge[0] and e[0] == edge[1]:
            return e
    return None


# adds random number of cars (flow - by allowed capacity) to the roads entering the intersection
def add_rand_flow():
    # print("add random flow:")
    for edge in edges_lst:
        if entering_traffic_light(edge):
            capacity = edge[2]
            added_cars = random.randint(0, capacity - len(current_flow[edge]))
            current_flow[edge] = insert_cars_into_queue(current_flow[edge], added_cars)
    #         print(str(edge) + " add = " + str(added_cars), end=',')
    # print()


# redacts random number of cars (flow - by current flow) from the roads exiting
# the intersection
def redact_rand_flow():
    for edge in edges_lst:
        if not entering_traffic_light(edge):
            cars_num = len(current_flow[edge])
            redacted_cars = random.randint(0, cars_num)
            current_flow[edge] = remove_cars_from_queue(current_flow[edge], redacted_cars)


# adds number of cars (flow - by allowed capacity) to the roads entering the intersection by poisson distribution
def add_poisson_flow():
    global IS_LIMITED_CAPACITY
    for edge in edges_lst:
        if entering_traffic_light(edge):
            added_flow = np.random.poisson(distribution_dict[edge], 1)[0]
            edge_flow = len(current_flow[edge])
            capacity = edge[2]
            if IS_LIMITED_CAPACITY and edge_flow + added_flow <= capacity:
                added_flow = capacity - edge_flow
                current_flow[edge] = insert_cars_into_queue(current_flow[edge], added_flow)
            else:
                current_flow[edge] = insert_cars_into_queue(current_flow[edge], added_flow)


# redacts number of cars (flow - by current flow) from the roads exiting
# the intersection by poisson distribution
def redact_poisson_flow():
    for edge in edges_lst:
        if not entering_traffic_light(edge):
            cars_num = len(current_flow[edge])
            redacted_cars = np.random.poisson(distribution_dict[edge], 1)[0]
            if redacted_cars > cars_num:
                redacted_cars = cars_num
            current_flow[edge] = remove_cars_from_queue(current_flow[edge], redacted_cars)


# given to edges that theirs light has been turned green, updates the number of cars (flow)
# under the assumption all cars have crossed
def update_green_light_flow(succ_edge, edge, quantum):
    global IS_LIMITED_CAPACITY
    is_limited_capacity = IS_LIMITED_CAPACITY
    added_flow = min(quantum, len(current_flow[succ_edge]))
    capacity = edge[2]
    edge_flow = len(current_flow[edge])
    if not is_limited_capacity:
        current_flow[succ_edge], current_flow[edge] = transfer_cars_q1_to_q2(current_flow[succ_edge],
                                                                             current_flow[edge], added_flow)
        return

    if edge_flow + added_flow <= capacity:
        current_flow[succ_edge], current_flow[edge] = transfer_cars_q1_to_q2(current_flow[succ_edge],
                                                                             current_flow[edge], added_flow)
    else:
        real_flow = capacity - len(current_flow[edge])
        current_flow[succ_edge], current_flow[edge] = transfer_cars_q1_to_q2(current_flow[succ_edge],
                                                                             current_flow[edge], real_flow)


# given a light that has been switched to green, updates all relevant edge's flows
def green_light(light, quantum):
    for edge in edges_lst:
        if not entering_traffic_light(edge) and edge[0] == light:
            succ_edge = get_succ_edge(edge)
            if succ_edge is not None:
                update_green_light_flow(succ_edge, edge, quantum)


# init a graph
def create_graph(edges_weighted_lst):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges_weighted_lst)
    return G


def calculate_queue_weight(queue):
    loss = 0
    global CURRENT_TIME
    for car in queue:
        loss += car.get_car_weight(CURRENT_TIME)
    return loss


# calculate a loss to each edge
def calculate_edge_loss(edge):
    # this edge is not going into the intersection
    if edge[0] == "t1" or edge[0] == "t2":
        return 0
    loss = 0
    for e in edges_lst:
        if entering_traffic_light(e) and e[1] != edge[1]:
            loss += calculate_queue_weight(current_flow[e])
    return loss


# switches the lights according to the loss
def switch_lights(quantum):
    for edge in edges_lst:
        loss = calculate_edge_loss(edge)
        loss_dict[get_traffic_light_id(edge)] += loss
    if loss_dict["t1"] < loss_dict["t2"]:
        green_light("t1", quantum)
    else:
        green_light("t2", quantum)


# plots the graph
def plot_graph(graph):
    nx.draw_networkx(graph, node_color='green')
    plt.show()


def get_avg_waiting_time(edge):
    global CURRENT_TIME
    queue = current_flow[edge]
    total_waiting_time = 0
    if len(queue) == 0:
        return 0
    for car in queue:
        total_waiting_time += (CURRENT_TIME - car.get_arrival_time())
    avg = float(total_waiting_time) / float(len(queue))
    return avg


def get_max_waiting_time(edge):
    global CURRENT_TIME
    queue = current_flow[edge]
    if len(queue) == 0:
        return 0
    return CURRENT_TIME - queue[0].get_arrival_time()


def plot_all(edge, avg_time_quantum, min_q, max_q, stat_type, is_poisson=False):
    my_time = [i for i in range(100)]
    for q in range(min_q, max_q):
        y_axis = avg_time_quantum[q]
        plt.legend()
        if is_poisson:
            plt.title("lambda = " + str(distribution_dict[edge]))
        plt.plot(my_time, y_axis, label=str("line " + str(q)))
    plt.savefig(str(edge[0]) + ' to ' + str(edge[1]) + '_' + stat_type + '.png')
    plt.clf()
    # plt.show()


def stat_avg_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    for e in edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(100):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_current_flow()
                init_loss_dict()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_LIMITED_CAPACITY:
                        add_rand_flow()
                        redact_rand_flow()
                    else:
                        add_poisson_flow()
                        redact_poisson_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_avg_waiting_time(e)

        avg_time_quantum = avg_time_quantum / 100
        plot_all(e, avg_time_quantum, min_q, max_q, "avg", is_poisson)


def stat_max_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    for e in edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(100):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_current_flow()
                init_loss_dict()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_LIMITED_CAPACITY:
                        add_rand_flow()
                        redact_rand_flow()
                    else:
                        add_poisson_flow()
                        redact_poisson_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_max_waiting_time(e)

        avg_time_quantum = avg_time_quantum / 100
        plot_all(e, avg_time_quantum, min_q, max_q, "max", is_poisson)


def print_stage(stage):
    print(stage)
    print(CURRENT_TIME)
    for l in current_flow.keys():
        print(str(l) + " " + str(len(current_flow[l])) + " " + str(calculate_edge_loss(l)))
    print()


if __name__ == "__main__":
    # stat_avg_quantum()
    # stat_max_quantum()

    init_distribution_dict()
    init_current_flow()
    init_loss_dict()
    for i in range(100):
        CURRENT_TIME += 1
        if IS_LIMITED_CAPACITY:
            add_rand_flow()
            print_stage("add")
            redact_rand_flow()
            print_stage("redact")
        else:
            add_poisson_flow()
            print_stage("add")
            redact_poisson_flow()
            print_stage("redact")

        switch_lights(QUANTUM)
        print_stage("switch")
