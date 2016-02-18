
#!/usr/local/bin/python
__author__ = 'Sakkarin Namwong'
import boto.ec2
import boto.ec2.elb
import boto
import sys
import time
import sys, os,string,datetime
# import your AWS key
from   awskey                               import access_key,secret_access_key
from   StartEC2                             import StartEC2InstanceList
from   StopEC2                              import StopEC2InstanceList

# set timeout for checking ELB
settimeout = 60*1  #1 minute

# ----------------------------------
# All list funcation 
# ----------------------------------    

def GetEC2Connection():
# Get EC2 connection to your aws account
        ec2con = boto.ec2.connect_to_region("ap-southeast-1",aws_access_key_id=access_key,aws_secret_access_key=secret_access_key)
        return ec2con

def GetELBConnection():
# Get ELB connection to your aws account
        elbcon = boto.ec2.elb.connect_to_region("ap-southeast-1",aws_access_key_id=access_key,aws_secret_access_key=secret_access_key)
        return elbcon

def CheckStusEC2(ec2con,EC2Instance,command):
	iStatus = False 
# function to check ec2 status before run command
	info_ec2 = ec2con.get_all_instances(EC2Instance)
	for res in info_ec2:
		for inst in res.instances:
			print "%s  (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)
			ec2_status = inst.state
			if inst.state == command:
				print 'EC2  %s  already    >>>  [%s] '	%(EC2Instance,command)
			else:
				print 'EC2  %s  status is  >>>  [%s] '	%(EC2Instance,inst.state)
				iStatus = True

	return iStatus

def PullStatus(getConnection,EC2Instance,Checkstatus):
		iStatus = False 
		#Start checking add instances to running
		start = time.time()
		print 'Start Time >>> %s' %(start)
		timeout = time.time() + settimeout 
		print 'Time Out   >>> %s' %(timeout)
		while True:
			info_ec2 = getConnection.get_all_instances(EC2Instance)
			for res in info_ec2:
				for inst in res.instances:
					#print "%s  (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)
					ec2_status = inst.state
			if time.time() < timeout:
				print 'Checking   >>> %s [%s] '	%(EC2Instance,ec2_status)
				if inst.state== Checkstatus:
					print 'Instance %s now %s use time [%s] s' % (EC2Instance,ec2_status,(time.time()-start))
					iStatus = True
					break

			else:
				print 'Failed !! Timeout '
				break	
			time.sleep(1)

		return iStatus

def StopEC2Instance(ec2con,EC2Instance):
		print ">>>>>   Stopping EC2Instance  [ %s ]...."  %(EC2Instance)
		iStatus = CheckStusEC2(ec2con,EC2Instance,'stopped')
		if iStatus == True:	
			ec2con.stop_instances(instance_ids=EC2Instance)
			iStatus = PullStatus(ec2con,EC2Instance,'stopped')

	 	print 'Done funcation StopEC2Instance %s' %(iStatus)


def StartEC2Instance(ec2con,EC2Instance):
		print ">>>>>   Stating EC2Instance  [ %s ]...."  %(EC2Instance)
		iStatus = CheckStusEC2(ec2con,EC2Instance,'running')
		if iStatus == True:			
			ec2con.start_instances(instance_ids=EC2Instance)
	 		iStatus = PullStatus(ec2con,EC2Instance,'running')

	 	print 'Done funcation StartEC2Instance %s' %(iStatus)



def ListAllEC2(ec2con,status):
# List all your EC2 
	reservations = ec2con.get_all_instances()
	for res in reservations:
		for inst in res.instances:
			if 'Name' in inst.tags:
				if inst.state == status: # input running , stopped
					print "%s  (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)			


def ListAllELB(elbcon):
# List all your ELB
	reservations = elbcon.get_all_load_balancers()

def AddEC2InstanceToELB(ec2con,EC2Instance,elbcon,LoadBalancers):

 	print 'Adding %s to ELB %s' % (EC2Instance, LoadBalancers)
	# Command add instances to ELB
	elbcon.register_instances(LoadBalancers,EC2Instance)
	# Start checking add instances to ELB
	iStatus = PullStatus(elbcon,EC2Instance,'InService')
 	
 	print 'Done funcation AddEC2InstanceToELB %s' %(iStatus)


def RemoveEC2InstanceFromELB(ec2con,EC2Instance,elbcon,LoadBalancers):
    # get the aws ec2 instance id for the current machine
 	#instance_id = boto.utils.get_instance_metadata()[name]
	print 'Removeing %s to ELB %s' % (EC2Instance, LoadBalancers)
	elbcon.deregister_instances(LoadBalancers,EC2Instance)
	print 'Done Remove %s to ELB %s' % (EC2Instance, LoadBalancers)

# ----------------------------------
# Main
# ----------------------------------  

if __name__ == "__main__":

	os_path = os.path.dirname(sys.argv[0])       
	basename = os.path.basename(sys.argv[0])

	file_name, ext_name = os.path.splitext( basename )  

	print "--------------------------------------------------"
	print "-----------------True Money AWS-------------------"
	print "--------------------------------------------------"

	total = len(sys.argv)
	cmdargs = str(sys.argv)
	print ("The total numbers of args passed to the script: %d " % total)
	print ("Args list: %s " % cmdargs)
	# Pharsing args one by one 
	print ("Script name: %s" % str(sys.argv[0]))
	print ("\n\nYour Command Start or Stop : %s" % str(sys.argv[1]))
	command = sys.argv[1]
	#print ("Yourname : %s" % str(sys.argv[2]))
	#print StartEC2InstanceList
	if command == "start":
		print("start instance command")
		for startec2 in StartEC2InstanceList:
			StartEC2Instance(GetEC2Connection(),startec2)
	elif command == "stop":
		print("Stop instance command")
		for stopec2 in StopEC2InstanceList:
			StopEC2Instance(GetEC2Connection(),stopec2)
	else:
		print("command not support %s" % str(sys.argv[1]))





	#LoadBalancers = 'Suchinda-Test-LB'
	#EC2Instance   = 'i-018ef4a5'
	#EC2Instance2   ='i-3488da90' #Suchinda-Public

	#print ConnectionEC2Status
	#status = 'running'
	#ListAllEC2(GetEC2Connection(),status)
	#EC2InstanceID = 'i-018ef4a5'
	#StopEC2Instance(GetEC2Connection(),EC2Instance2)
	#StartEC2Instance(GetEC2Connection(),EC2Instance2)
	#ConnectionEC2Status.start_instances(instance_ids=EC2InstanceID)




	#ListAllELB(GetELBConnection())
	# ec2 = GetEC2Connection()
	#info_ec2 = ec2.get_all_instances(EC2InstanceID)
	#print info_ec2

	# info_ec2 = ec2.get_all_instances(EC2InstanceID)
	# for res in info_ec2:
	# 	for inst in res.instances:
	# 		print "%s  (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)
	#elb = GetELBConnection()
	#elb.register_instances(LoadBalancers,EC2Instance)
	#info = elb.describe_instance_health(LoadBalancers,EC2Instance2)
	#print info[0]
	#b = str(info[0]).split (",") 
	#c = str(info[0]).split (",")[1].split (")")
	#print c[0]


	#AddEC2InstanceToELB(GetEC2Connection(),EC2Instance2,GetELBConnection(),LoadBalancers)
	#RemoveEC2InstanceFromELB(GetEC2Connection(),EC2Instance2,GetELBConnection(),LoadBalancers)
