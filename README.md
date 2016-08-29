==================================================================================
References
==================================================================================
1) Base Code, entirely modified though:  
https://www.grotto-networking.com/DiscreteEventPython.html , SimComponents.py  
2) Dijkstra Algorith:  
https://www.ics.uci.edu/~eppstein/161/python/dijkstra.py  

==================================================================================
About
==================================================================================

Discrete Event Simulation to simulate different core office edge architectures over an Optical ROADM network  

Edge components could be catagories as SDN or NFV to manipulate cost and delay. To calculate percentage NFV and SDN suitable for the network.  

Network Components include-  

1) Core Office
	-IP routers
		- 1G, 10G, 100G Linecards
	-Servers
	-Muxponders

2) Optical Core
	-ROADM
		- WSS
		- Splitter
		- Add Drop Module
Deliverables-

1) Load vs Packet Dropped by the network.  
2) Capital Expenditure.  
3) Operational Expenditure.
	
==================================================================================
Python Entry point
==================================================================================

python start.py

==================================================================================
COMMIT + PUSH
==================================================================================

git add .

git commit -m "[message]"

git push -u origin master (use option -f for force commit)


==================================================================================
SIMULATION WORK FLOW
==================================================================================

1) Network topology Setup (config xml in ./src/resource/xml/[ baseline| streamline ]/[ router.xml| roadm.xml| topology.xml ])

2) Simulation parameters configuration (src in ./src/configure.py & ./src/cost.py)

3) Execution

	There are 2 mode of execution (set in configuration )- [TestRun | NON TestRun]:
	
	NON TestRun
	- Concentrated on producing the final result (pkts dropped vs arrival rate, no. of packets produced, etc),
	  loggers are switched off from logging intermediatary infomation.
	- Results are stored in 
		- .src/resource/log/baseline/    if  baseline
		- .src/resource/log/streamline/  if  streamline
	- As the goal is to calculate the network capacity, the simulation runs for a range of packet arrival rates.
	- Observations such as pkt drop count are recorded.
	- Arrival rates are incremented after each run.
	
	TestRun
	- Only executes once (not a range of arrival rates).
	- The arrival rate selected is the start_rate defined in configuration.py 
	- Simulation collects all sorts of information. (stored in ./src/resource/log/)
	- Logs:
		- tolopology.log --> can be used to verify the links
		- simulation.log --> logs pcks generated and pcks received in the cronological order of events
		- packet.log	 --> each segment in the file stores information about the pkt's entire lifetime from src to dest. 
				     e.g. delays experienced on linecard, propagation etc



==================================================================================
CONFIGS
==================================================================================


**General configuration**
-------------------------
configure.py
-------------------------

1) architecture - {achitecture = architecture_list[0]}:  
There are 2 achitectures to choose from.
The config xmls to follow depends on the chosen architecture- either src/resource/xml/baseline/ OR src/resource/xml/streamline/ .
The same applies for the result files- src/resource/log/baseline/ OR src/resource/log/streamline/

2) qlimit:  
Buffer size. Queue limits expressed in bytes.

3) mean_pkt_size:  
Mean pkt size in bytes. Exponential distribution applied.

4) delay_over_IP:  
The propagation delay experienced by packets on every link (except on optical links, propagation delay over optical is considered 0)

5) N_Channels:  
No. of lambdas permitted by the system.

6) nPrioLevels: (e.g. 8)  
Levels of priority for the packets generated. Would be used by priority queues in IP routers to discriminate the priority.

7) start_rate / end_rate / rate_increments:  
If the values are 10 20 and 2 respectively, the simulation will run the code for arrival rates-
[10, 12, 14, 16 and 18]
The first run takes 10 to be the MEAN arrival rate for all servers in the system, the second run takes 12 and so on.

8) delay_fact_SDN / delay_fact_NFV:  
The factor by which the delay produced by an SDN / NFV components exceeds the delay produced by traditional network hardware.

9) simulation_until:  
The time until when the descrete event simulation runs.

10) testrun  = (True / False):  
The difference is discribed above in the work flow section.

11) simulate_delay_on_server  = (True / False):  
Ideally this should be set to true.

** XML Configuration **
------------------------------
Topology.xml / Router.xml
------------------------------

1) How to classify a network component as NFV or a SDN

2) How you could tone down the values of 1G / 10G / 100G.

1 >> 
This xml snippet from Topology.xml descibes the network components inside core office "C1". 
Wiring information for this core office can be found in Router.xml.

	<object id="C1" class="network.Core_Office">
		<constructor-arg name="network_components">		
			<list>
			    	<ref object="C1_PE1"/>
				<ref object="C1_PE2"/>
				<ref object="C1_PE3"/>
		
				<ref object="C1_AGG1"/>
				<ref object="C1_AGG2"/>

				<ref object="C1_P1"/>
				<ref object="C1_P2"/>

				<ref object="C1_Mux"/>

			</list>
   		</constructor-arg>
	</object>

Topology.xml also has a list to distingush network components as sdn or nfv. Dropping a reference here would apply the SDN or NFV cost and delay factor to it.

	<object id="nfv_sdn" class="network.NFV_SDN">
		<property name="sdn_list">
			<list>
				<ref object="C1_AGG1"/> <!-- * -->
				<ref object="C1_AGG2"/> <!-- * -->
			</list>
   		</property>
				
		<property name="nfv_list">
			<list>
				
			</list>
   		</property>
	</object>

2 >>
You can tone down the values of 1G / 10G and 100G by reducing the values in the xml section shown below (Router.xml)

	<long id="1GE"  >1000000000   </long>
	<long id="10GE" >10000000000  </long>
	<long id="100GE">100000000000 </long>
	<long id="1TE"  >1000000000000</long>

** Cost Configuration **
---------------------------------
cost.py
---------------------------------

1) cost_reduction_fact_SDN:  
Factor by which a SDN component cost less compared to traditional network component. 

2) cost_reduction_fact_NFV:  
Factor by which a NFV component cost less compared to traditional network component.

3)
self.linecard_cost_map[ context.get_object("1GE")  ] = 1  
self.linecard_cost_map[ context.get_object("10GE") ] = 2.5  
self.linecard_cost_map[ context.get_object("100GE")] = 12  

Cost for 1G / 10G / 100G linecards

4) Other costs such as muxponders and servers.

