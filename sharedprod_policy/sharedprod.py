import profile
from urllib import response
from collections import defaultdict
import argparse
import json
import sys
import os
import platform
import glob


def shared_func():

    os.chdir('../sharedprod_policy/')

    ######ENV Variables########
    Devops = 'DevOpsAccess'
    Region = 'us-east-1'
    tfprofile = 'ACCOUNTID'
    tfprof_role = 'ACCOUNTID_DevOpsAccess'
    accountId = 'BACKENDACCOUNTID'
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

    credresponse = os.popen(f'aws sso get-role-credentials --account-id {tfprofile} --role-name {Devops} --access-token {sso_atoken} --region {sso_region}').read()
    creds = json.loads(credresponse)

    s3_akey_Id = creds['roleCredentials']['accessKeyId']
    s3_skey_Id = creds['roleCredentials']['secretAccessKey']
    s3_stoken_Id = creds['roleCredentials']['sessionToken']

    #Setting Shared Prod Env Variables
    credresponse = os.popen(f'aws sso get-role-credentials --account-id {accountId} --role-name {Devops} --access-token {sso_atoken} --region {sso_region}').read()
    creds = json.loads(credresponse)

    tf_akey_Id = creds['roleCredentials']['accessKeyId']
    tf_skey_Id = creds['roleCredentials']['secretAccessKey']
    tf_stoken_Id = creds['roleCredentials']['sessionToken']

    os.environ["AWS_ACCESS_KEY_ID"]=tf_akey_Id
    os.environ["AWS_SECRET_ACCESS_KEY"]=tf_skey_Id
    os.environ["AWS_SESSION_TOKEN"]=tf_stoken_Id

    init = os.system(f'terraform init \
    -backend-config="bucket=shared-terraform-backend" \
    -backend-config="key={accountId}/vm/role.tfstate" \
    -backend-config="region={Region}" \
    -backend-config="access_key={s3_akey_Id}" \
    -backend-config="secret_key={s3_skey_Id}" \
    -backend-config="token={s3_stoken_Id}" \
    -backend-config="profile={tfprof_role}" \
    --reconfigure')

    os.system('terraform plan') 

    # os.system('terraform apply --auto-approve')
    # os.system('terraform destroy --auto-approve')

if __name__ == '__main__':
    shared_func()
