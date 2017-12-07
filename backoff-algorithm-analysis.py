# This is a simpy based  simulation of a M/M/1 queue system

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1

class server:
    def __init__(self, env, arrival_rate, num_hosts):
        self.env = env
        self.hosts = []
        self.senders = []
        self.cur_time_slot = 0
        self.successful_slot = 0
        for host in range(0, num_hosts):
            Packet_Delay = StatObject()
            Server_Idle_Periods = StatObject()
            new_host = server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods)
            self.hosts.append(new_host)

    def run_server(self, env):
        for host in self.hosts:
            env.process(host.packets_arrival(env)) #start packet arrival process for each host
        while True:
            #print("Current time slot:", self.cur_time_slot)
            for host in self.hosts:
                #print("Host next time slot:", host.next_time_slot)
                if(host.next_time_slot == self.cur_time_slot):
                    self.senders.append(host)
            if len(self.senders) == 1 and self.senders[0].queue_len > 0: #only one host sending, so no collisions 
                #print("Successful Slot!")
                self.successful_slot += 1
                self.senders[0].n = 0 #packet successfully sent, reset number of retransmissions
                self.senders[0].queue_len -= 1
                self.senders[0].next_time_slot += 1
            else:
                #print("Failed Slot", len(self.senders), " hosts tried to send")
                for host in self.senders:
                    #print("Host.N", host.n)
                    if host.n < 10:
                        host.next_time_slot += 1 + random.randint(0, pow(2,host.n))
                    else:
                        host.next_time_slot += 1 + random.randint(0, pow(2, 10))
                    host.n += 1
            self.cur_time_slot += 1
            self.senders = []
            yield self.env.timeout(1)


""" Queue system  """		
class server_queue:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods):
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
        self.next_time_slot = 0
        self.n = 0
		
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
 #           env.process(self.process_packet(env, new_packet))
	

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
#	print("Simple queue system model:mu = {0}".format(MU))
#	print ("{0:<9} {1:<9} {2:<9} {3:<9} {4:<9} {5:<9} {6:<9} {7:<9}".format(
#        "Lambda", "Count", "Min", "Max", "Mean", "Median", "Sd", "Utilization"))
#	random.seed(RANDOM_SEED)
#	for arrival_rate in [0.1, 0.2, 0.5,  0.9]:
#		env = simpy.Environment()
#		Packet_Delay = StatObject()
#		Server_Idle_Periods = StatObject()
#		router = server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods)
#		env.process(router.packets_arrival(env))
#		env.run(until=SIM_TIME)
#		print ("{0:<9.3f} {1:<9} {2:<9.3f} {3:<9.3f} {4:<9.3f} {5:<9.3f} {6:<9.3f} {7:<9.3f}".format(
#			round(arrival_rate, 3),
#			int(Packet_Delay.count()),
#			round(Packet_Delay.minimum(), 3),
#			round(Packet_Delay.maximum(), 3),
#			round(Packet_Delay.mean(), 3),
#			round(Packet_Delay.median(), 3),
#			round(Packet_Delay.standarddeviation(), 3),
#			round(1-Server_Idle_Periods.sum()/SIM_TIME, 3)))

    random.seed(RANDOM_SEED)
    print("Total time slots: ", SIM_TIME)
    print(r"{:<9} & {:<9} & {:<9} & {:<9} \\".format("Lambda", "Total time slots", "Successful", "Throughput"))
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        env = simpy.Environment()
        new_server = server(env, arrival_rate, 10)
        env.process(new_server.run_server(env))
        env.run(until=SIM_TIME)
        print(r"{:<9.3f} & {:<9} & {:<9} & {:<9.3f} \\".format(arrival_rate, new_server.cur_time_slot, new_server.successful_slot, new_server.successful_slot/new_server.cur_time_slot))
	
if __name__ == '__main__': main()
