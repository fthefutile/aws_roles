# aws_role
# Local Setup
Run these commands sequentially
...
python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
...

When using VsCode, VsCode will ask if you want to use the virtual environment that's detected, select Yes.

How to Use:

Requires DevOpsAccess for all accounts.

Run aws configure sso to configure your sso account.  Or aws login sso.

Run main.py

Currently both terraform apply/destroy have --auto-approve flag attached.  Remove if you'd like to manually accept.