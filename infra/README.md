# Leaf-blower infrastructure (CloudFormation)

Templates live in [cloudformation/template.yaml](cloudformation/template.yaml). There is **no SAM transform**; GitHub Actions (or the CLI) uploads a **Lambda zip to S3**, then deploys the stack with parameters pointing at that object.

## What you need in AWS (account `075723833107` or your target)

1. **S3 bucket** for Lambda artifacts (same region as the stack, e.g. `us-east-1`). The GitHub OIDC role must allow `s3:PutObject` (and `s3:GetObject` if you use console) on that bucket/prefix.
2. **IAM role for GitHub OIDC** trusted by `token.actions.githubusercontent.com`, with:
   - `cloudformation:*` for the stack (scoped policies recommended in production)
   - `iam:PassRole` for the Lambda execution role created by the stack
   - `lambda:*` as required for stack updates
   - `apigateway:*`, `cognito-idp:*`, `s3:PutObject` on the artifact bucket
3. A **globally unique** `CognitoDomainPrefix` per region (set as GitHub secret `COGNITO_DOMAIN_PREFIX`).

## GitHub repository secrets

| Secret | Purpose |
| ------ | -------- |
| `AWS_ROLE_ARN` | IAM role ARN for OIDC (e.g. `arn:aws:iam::075723833107:role/github-actions-leaf-blower`) |
| `ARTIFACT_BUCKET` | Bucket name for Lambda zips |
| `COGNITO_DOMAIN_PREFIX` | e.g. `leaf-blower-dev-yourname` (must satisfy Cognito domain rules) |

Optional: change `STACK_NAME` and `AWS_REGION` in [../.github/workflows/deploy-infrastructure.yml](../.github/workflows/deploy-infrastructure.yml).

## Manual deploy (CLI)

Run from the **repository root** (or adjust paths). The zip must contain `health.py` and `me.py` at the **root** of the archive (same layout as `src/`).

```bash
export AWS_PROFILE=leaf-blower
export AWS_REGION=us-east-1
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
