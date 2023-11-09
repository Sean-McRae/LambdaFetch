import subprocess 
import json
import os
import argparse

parser = argparse.ArgumentParser(description="Script information")
parser.add_argument("-p", "--profile", type=str, help="Specify AWS Profile")

args = parser.parse_args()

def getAccountId(profileName):
		account = subprocess.check_output(["aws", "sts", "get-caller-identity","--profile",profileName])
		data = json.loads(account)
		return data['Account']

def listRegions(profileName):
	regions = []
	try:
		region = subprocess.check_output(["aws", "account", "list-regions","--profile",profileName])
		data = json.loads(region)
		for site in data['Regions']:
			if site['RegionOptStatus'] == 'DISABLED':
				pass
			else:
				regions.append(site['RegionName'])
	except Exception as e:
		print('Token Possibly Expired...')
	return regions

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def downloadFunctions(name,region,accountNumber,profileName):
	os.system("aws lambda get-function --function-name "+name+" --query 'Code.Location' --profile "+profileName+" --region "+region+" | xargs wget -O ./LambdaFunctions/"+accountNumber+"/"+region+"/"+name+".zip --no-check-certificate")

def listFunctions(regions,accountNumber,profileName):
	try:
		for site in regions:
			function = subprocess.check_output(["aws", "lambda", "list-functions","--profile",profileName,"--region",site])
			data = json.loads(function)
			for name in data['Functions']:
				if name is not None:
					create_folder('./LambdaFunctions/'+accountNumber+'/'+site+'/')
					downloadFunctions(name['FunctionName'],site,accountNumber,profileName)
	except Exception as e:
		print('Token Possibly Expired...')


def main():
	if not args.profile:
	    print("No AWS Profile Specified.")
	    parser.print_help()
	else:
		accountNumber = getAccountId(args.profile)
		create_folder('./LambdaFunctions/'+str(accountNumber)+'/')
		regions = listRegions(args.profile)
		listFunctions(regions,str(accountNumber),args.profile)

main()

