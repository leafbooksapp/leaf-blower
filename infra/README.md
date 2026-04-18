# Leaf-blower infrastructure (CloudFormation)

Templates live in [cloudformation/template.yaml](cloudformation/template.yaml). There is **no SAM transform**; GitHub Actions (or the CLI) uploads a **Lambda zip to S3**, then deploys the stack with parameters pointing at that object.

## What you need in AWS (account `075723833107` or your target)

1. **S3 bucket** for Lambda artifacts (same region as the stack, e.g. `us-east-1`). CI needs `s3:PutObject` (and usually `s3:GetObject`) on that bucket/prefix.
2. **AWS credentials for GitHub Actions** — choose **one**:
   - **IAM user (simplest):** e.g. user `github-user` with an access key stored in GitHub secrets (see below). Do **not** set repository variable `AWS_AUTH_METHOD` to `oidc`.
   - **IAM role + OIDC:** no long-lived keys; set repository variable `AWS_AUTH_METHOD` to `oidc` and secret `AWS_ROLE_ARN`. The role’s trust policy must allow `token.actions.githubusercontent.com` for this repo.
3. Permissions for that principal (tighten for production):
   - `cloudformation:*` on the stack (or scoped stack ARN)
   - `iam:PassRole` on the Lambda execution role ARN created/used by the stack
   - `lambda:*`, `apigateway:*`, `cognito-idp:*` as needed for stack create/update
   - `s3:PutObject` (and list/get as needed) on the artifact bucket
4. A **globally unique** `CognitoDomainPrefix` per AWS region (GitHub secret or variable `COGNITO_DOMAIN_PREFIX` — this becomes your Cognito Hosted UI domain prefix, e.g. `leaf-blower-dev-yourname`).

### IAM user `github-user` (recommended if OIDC is not set up)

1. IAM → Users → Create user → name e.g. `github-user` (programmatic access only is fine).
2. Attach policies or an inline policy granting the permissions above (for a dev account, some teams use `AdministratorAccess` temporarily; prefer least privilege).
3. Security credentials → Create access key → **Access key** + **Secret access key** (copy once).
4. In the GitHub repo → **Settings → Secrets and variables → Actions**, add:
   - `AWS_ACCESS_KEY_ID` — access key id  
   - `AWS_SECRET_ACCESS_KEY` — secret access key  
5. Leave **repository variable** `AWS_AUTH_METHOD` **unset** (or set to anything other than `oidc`) so the workflow uses these secrets.

### OIDC (optional)

1. Create an IAM role trusted by GitHub OIDC for this repository.
2. Set repository variable **`AWS_AUTH_METHOD`** = `oidc`.
3. Set secret **`AWS_ROLE_ARN`** to that role’s ARN.

## GitHub repository secrets

| Secret | When |
| ------ | ---- |
| `AWS_ACCESS_KEY_ID` | IAM user path (default) |
| `AWS_SECRET_ACCESS_KEY` | IAM user path (default) |
| `AWS_ROLE_ARN` | OIDC path only (`AWS_AUTH_METHOD=oidc`) |
| `ARTIFACT_BUCKET` | Always — **or** set repository **variable** `ARTIFACT_BUCKET` (bucket names are not secret; variables are easier to edit) |
| `COGNITO_DOMAIN_PREFIX` | Always — **or** repository **variable** `COGNITO_DOMAIN_PREFIX` (same value; not a password) |

| Variable | Purpose |
| -------- | -------- |
| `AWS_AUTH_METHOD` | Set to `oidc` to use `AWS_ROLE_ARN`; leave unset for IAM user keys |

Optional: change `STACK_NAME` and `AWS_REGION` in [../.github/workflows/deploy-infrastructure.yml](../.github/workflows/deploy-infrastructure.yml).

## Manual deploy (CLI)

Run from the **repository root** (or adjust paths). The zip must contain `health.py` and `me.py` at the **root** of the archive (same layout as `src/`).

```bash
export AWS_PROFILE=leaf-blower
export AWS_REGION=us-west-2
export BUCKET=your-artifact-bucket
export PREFIX=your-unique-cognito-domain-prefix
STAMP=$(date +%s)
KEY="leaf-blower/manual-${STAMP}.zip"

( cd src && zip -r /tmp/lambda.zip . )
aws s3 cp /tmp/lambda.zip "s3://${BUCKET}/${KEY}"

aws cloudformation deploy \
  --template-file infra/cloudformation/template.yaml \
  --stack-name leaf-blower-dev \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    "CognitoDomainPrefix=${PREFIX}" \
    "LambdaCodeBucket=${BUCKET}" \
    "LambdaCodeKey=${KEY}" \
    "DeploymentNonce=manual-${STAMP}" \
  --region "${AWS_REGION}"
```

Copy stack outputs into the iOS app `LeafConfig.plist` in the sibling **leaf** repo (see [../../leaf/leaf/README.md](../../leaf/leaf/README.md) when both repos live under the same parent folder, e.g. `leaf-app/`).
