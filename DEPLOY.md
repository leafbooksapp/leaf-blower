# leaf-blower deployment

Target account: **075723833107** (use AWS profile `leaf-blower` locally).

## Recommended: GitHub Actions

Infrastructure is **pure CloudFormation** at [infra/cloudformation/template.yaml](infra/cloudformation/template.yaml). The workflow [.github/workflows/deploy-infrastructure.yml](.github/workflows/deploy-infrastructure.yml) packages `src/`, uploads the zip to S3, and runs `aws cloudformation deploy`.

Configure repository secrets and an OIDC IAM role as described in [infra/README.md](infra/README.md), then push to `main` (or run the workflow manually).

## Manual CLI deploy

See the “Manual deploy” section in [infra/README.md](infra/README.md). You still need an **S3 bucket** for the Lambda zip before `cloudformation deploy`.

## Verify AWS identity

```bash
export AWS_PROFILE=leaf-blower
aws sts get-caller-identity
```

## After deploy

Copy stack outputs into the iOS app [LeafConfig.plist](../leaf/leaf/LeafConfig.plist) (see [../leaf/leaf/README.md](../leaf/leaf/README.md)).

## Social sign-in

Configure Google and Apple in Cognito using [COGNITO_IDPS.md](COGNITO_IDPS.md).
