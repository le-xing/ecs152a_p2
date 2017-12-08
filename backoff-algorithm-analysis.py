# This is a simpy based  simulation of a M/M/1 queue system

import random
import simpy
import math
import matplotlib.pyplot as plt

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1

class server:
    def __init__(self, env, arrival_rate, num_hosts, exponential):
        self.env = env
        self.hosts = []
        self.senders = []
        self.cur_time_slot = 0
        self.successful_slot = 0
        self.exponential = exponential

        for host in range(0, num_hosts):
            Packet_Delay = StatObject()
            Server_Idle_Periods = StatObject()
            new_host = server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods)
            self.hosts.append(new_host)

    def run_server(self, env):
        for host in self.hosts:
            #start packet arrival process for each host
            env.process(host.packets_arrival(env))
        while True:
            self.senders = [host for host in self.hosts if host.next_time_slot == self.cur_time_slot]
            if len(self.senders) == 1 and self.senders[0].queue_len > 0:
                #one host sending, successful
                self.successful_slot += 1
                self.senders[0].n = 0
                self.senders[0].queue_len -= 1
                self.senders[0].next_time_slot += 1
            else:
                #failed time slot, multiple senders
                for host in self.senders:
                    #exponential backoff
                    if self.exponential:
                        host.next_time_slot += 1 + random.randint(0, pow(2, min(host.n, 10)))
                    #linear backoff
                    else:
                        host.next_time_slot += 1 + random.randint(0, min(host.n, 1024))
                    host.n += 1
            self.cur_time_slot += 1
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
            self.queue_len -= 1
            if self.queue_len == 0:
                self.flag_processing = 0
                self.start_idle_time = env.now
				
    def packets_arrival(self, env):
        while True:
        # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
            # arrival time of one packet

            self.packet_number += 1
            # packet id
            arrival_time = env.now  
            new_packet = Packet(self.packet_number,arrival_time)
            if self.flag_processing == 0:
                self.flag_processing = 1
                idle_period = env.now - self.start_idle_time
                self.Server_Idle_Periods.addNumber(idle_period)
            self.queue_len += 1
	

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
        # get the middle number
        if n//2 != 0: 
            return self.dataset[n//2]
        # find the average of the middle two numbers
        else:
            return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)
    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum/(len(self.dataset) - 1)
        return math.sqrt(sum)


def main():
    random.seed(RANDOM_SEED)
    plotdata = []
    for backoff in ["Exponential", "Linear"]:
        print("{}:".format(backoff))
        print("Total time slots: ", SIM_TIME)
        print(r"{:<9} & {:<9} & {:<9} & {:<9} \\".format("Lambda", "Total Time Slots", "Successful Transmissions", "Throughput"))
        print(r"\hline")
        lambdas = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
        throughputs = []
        for arrival_rate in lambdas:
            env = simpy.Environment()
            new_server = server(env, arrival_rate, 10, backoff == "Exponential")
            env.process(new_server.run_server(env))
            env.run(until=SIM_TIME)
            print(r"{:<9.3f} & {:<9} & {:<9} & {:<9.3f} \\".format(arrival_rate, new_server.cur_time_slot, new_server.successful_slot, new_server.successful_slot/new_server.cur_time_slot))
            throughputs.append(new_server.successful_slot/new_server.cur_time_slot)
        print()
        # plot specific backoff
        plt.plot(lambdas, throughputs)
        plt.title("{} Backoff".format(backoff))
        plt.xlabel("λ")
        plt.ylabel("Throughput")
        plt.savefig("{}_plot.png".format(backoff), bbox_inches='tight', dpi=600)
        #plt.show()
        plt.close()
        plotdata.append((lambdas, throughputs))
    # print both on one plot
    plt.plot(plotdata[0][0], plotdata[0][1], color='b', label="Exponential", alpha = 0.8, linestyle="--")
    plt.plot(plotdata[1][0], plotdata[1][1], color='r', label="Linear", alpha = 0.8)
    plt.title("Exponential and Linear Backoff".format())
    plt.xlabel("λ")
    plt.ylabel("Throughput")
    plt.legend()
    plt.savefig("Exponential_Linear_plot.png", bbox_inches='tight', dpi=600)
    #plt.show()
    plt.close()
	
if __name__ == '__main__': main()
