#Matteson Daniel-Padgett, 999096167
#Lena Tan, 999098385

# This is a simpy based simulation of a M/M/1 queue system with a finite buffer size.
# The main() function evaluates the probability of packet loss at B=10 and B=50 for
# various lambdas.

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1



""" Queue system  """		
class server_queue:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods, B):
        self.server = simpy.Resource(env, capacity = 1)
        self.env = env
        self.queue_len = 0
        self.flag_processing = 0
        self.packet_number = 0
        self.sum_time_length = 0
        self.start_idle_time = 0
        self.arrival_rate = arrival_rate
        self.Packet_Delay = Packet_Delay
        self.Server_Idle_Periods = Server_Idle_Periods
        self.B = B
        self.dropped_pkts = 0
        self.total_pkts = 0

    def process_packet(self, env, packet):
        with self.server.request() as req:
            start = env.now
            yield req 
            yield env.timeout(random.expovariate(MU))
            latency = env.now - packet.arrival_time
            self.Packet_Delay.addNumber(latency)
            #print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
            self.queue_len -= 1
            if self.queue_len == 0:
                self.flag_processing = 0
                self.start_idle_time = env.now

    def packets_arrival(self, env):
        # packet arrivals

        while True:
             # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
              # arrival time of one packet

            self.total_pkts += 1

            if self.queue_len < self.B:
                #buffer isn't full, add packet to queue
                self.packet_number += 1
                # packet id
                arrival_time = env.now
                #print(self.num_pkt_total, "packet arrival")
                new_packet = Packet(self.packet_number,arrival_time)
                if self.flag_processing == 0:
                    self.flag_processing = 1
                    idle_period = env.now - self.start_idle_time
                    self.Server_Idle_Periods.addNumber(idle_period)
                    #print("Idle period of length {0} ended".format(idle_period))
                self.queue_len += 1
                env.process(self.process_packet(env, new_packet))
            else:
                #buffer is full, drop the packet
                self.dropped_pkts += 1


""" Packet class """			
class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


class StatObject:
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)
    def sum(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum
    def mean(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum/n
    def maximum(self):
        return max(self.dataset)
    def minimum(self):
        return min(self.dataset)
    def count(self):
        return len(self.dataset)
    def median(self):
        self.dataset.sort()
        n = len(self.dataset)
        if n//2 != 0: # get the middle number
            return self.dataset[n//2]
        else: # find the average of the middle two numbers
            return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)
    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum/(len(self.dataset) - 1)
        return math.sqrt(sum)


def main():
    print("Simple queue system model:mu = {0}".format(MU))
    print(r"{:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} & {:<9} \\".format("B", "Lambda", "Count",
                                                                                             "Min", "Max", "Mean",
                                                                                             "Median", "Sd",
                                                                                             "Utilization", "Dropped", "$P_d$"))
    print("\hline")
    random.seed(RANDOM_SEED)
    for B in [10, 50]:
        for arrival_rate in [0.2, 0.4, 0.6, 0.8,  0.9, 0.99]:
            env = simpy.Environment()
            Packet_Delay = StatObject()
            Server_Idle_Periods = StatObject()
            router = server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods, B)
            env.process(router.packets_arrival(env))
            env.run(until=SIM_TIME)
            print(r"{:<9} & {:<9.3f} & {:<9} & {:<9.3f} & {:<9.3f} & {:<9.3f} & {:<9.3f} & {:<9.3f} & {:<9.3f} & {:<9} & {:<9.3f} \\".format(
                B,
                round(arrival_rate, 3),
                int(Packet_Delay.count()),
                round(Packet_Delay.minimum(), 3),
                round(Packet_Delay.maximum(), 3),
                round(Packet_Delay.mean(), 3),
                round(Packet_Delay.median(), 3),
                round(Packet_Delay.standarddeviation(), 3),
                round(1-Server_Idle_Periods.sum()/SIM_TIME, 3),
                int(router.dropped_pkts),
                round(router.dropped_pkts/Packet_Delay.count(),3)))

if __name__ == '__main__': main()
