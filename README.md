# leaf-blower

Python Lambdas behind **Amazon API Gateway (REST)** with **Amazon Cognito** JWT authorization and **stage caching** on `GET /health`.

## Deploy

- **GitHub Actions** (recommended): see [infra/README.md](infra/README.md) and [DEPLOY.md](DEPLOY.md).
- **Template**: [infra/cloudformation/template.yaml](infra/cloudformation/template.yaml) (no SAM; standard CloudFormation).

Copy stack outputs into the iOS app `LeafConfig.plist` (see [../leaf/leaf/README.md](../leaf/leaf/README.md)).

## Endpoints

| Method | Path    | Auth   | Notes        |
| ------ | ------- | ------ | ------------ |
| GET    | /health | None   | Cached ~60s  |
| GET    | /me     | Cognito JWT (`Authorization: Bearer <idToken>`) | Returns `sub`, `email` |

## Social sign-in

Configure Google and Apple in Cognito using [COGNITO_IDPS.md](COGNITO_IDPS.md).
