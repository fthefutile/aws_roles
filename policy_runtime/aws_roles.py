from asyncio.windows_events import NULL
import profile
from urllib import response
from collections import defaultdict
import argparse
import json
import sys
import os
import platform
import glob




def role_func():

    os.chdir('./policy_runtime/')

    ######ENV Variables########
    Devops = 'DevOpsAccess'
    Region = 'us-east-1'
    tfprofile = 'ACCOUNTID'
    tfprof_role = 'ACCOUNTID_DevOpsAccess'
    accounts = 'AWS_Accounts.json'
    deets = []
    ###########################

    #Creating Terraform init variables
    #Checking OS Version, getting credential file
    os_type = platform.system()
    if os_type == "Windows": 
        sso_path = os.path.expanduser(os.sep.join(["~",".aws\sso\cache\*"]))
        sso_glob = glob.glob(sso_path)
        sso_json = max(sso_glob, key=os.path.getmtime)
    else:
        sso_path = os.path.expanduser(os.sep.join(["~","/.aws/sso/cache/*"]))
        sso_glob = glob.glob(sso_path)
        sso_json = max(sso_glob, key=os.path.getmtime)

    with open(sso_json, 'r') as f:
        data = json.load(f)

    sso_atoken = data['accessToken']
    sso_region = data['region']

    #AWS_Accounts.json creation.
    acc_json = os.popen(f'aws sso list-accounts --access-token {sso_atoken} --region {sso_region}').read()

    with open("AWS_Accounts.json", "w") as outfile:
        outfile.write(acc_json)

    #Terraform Init Variable creation.
    credresponse = os.popen(
        f'aws sso get-role-credentials --account-id {tfprofile} --role-name {Devops} --access-token {sso_atoken} --region {sso_region}').read()
    creds = json.loads(credresponse)

    tf_akey_Id = creds['roleCredentials']['accessKeyId']
    tf_skey_Id = creds['roleCredentials']['secretAccessKey']
    tf_stoken_Id = creds['roleCredentials']['sessionToken']

    with open(accounts, 'r') as k:

        info = json.load(k)


    #Looping through AWS_Accounts.json
    for i in info['accountList']:

        #SharedProd-Role-Policy.json creation
        data = {
            "Version": "2012-10-17",

            "Statement": {

                "Effect": "Allow",

                "Action": "sts:AssumeRole",

                "Resource": deets
            }
        }

        accountId = i['accountId']

        data_str = f"arn:aws:iam::{accountId}:role/CrossAccount-Role"

        credresponse = os.popen(
            f'aws sso get-role-credentials --account-id {accountId} --role-name {Devops} --access-token {sso_atoken} --region {sso_region}').read()
        creds = json.loads(credresponse)

        env_akey = creds['roleCredentials']['accessKeyId']
        env_skey = creds['roleCredentials']['secretAccessKey']
        env_stoken = creds['roleCredentials']['sessionToken']

        os.environ["AWS_ACCESS_KEY_ID"] = env_akey
        os.environ["AWS_SECRET_ACCESS_KEY"] = env_skey
        os.environ["AWS_SESSION_TOKEN"] = env_stoken

        print(response)
        os.system('aws sts get-caller-identity')

        
        init = os.system(f'terraform init \
        -backend-config="bucket=shared-terraform-backend" \
        -backend-config="key={accountId}/vm/role.tfstate" \
        -backend-config="region={Region}" \
        -backend-config="access_key={tf_akey_Id}" \
        -backend-config="secret_key={tf_skey_Id}" \
        -backend-config="token={tf_stoken_Id}" \
        -backend-config="profile={tfprof_role}" \
        --reconfigure')

        os.system('terraform plan')
        # os.system('terraform apply --auto-approve')
        # os.system('terraform destroy --auto-approve')

        deets.append(data_str)


    json_object = json.dumps(data, indent=4)
    with open("./../sharedprod_policy/NameOfPolicy.json", "w") as outfile:
        outfile.write(json_object)

if __name__ == '__main__':
    role_func()