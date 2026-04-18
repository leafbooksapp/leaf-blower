# Cognito identity providers (Google & Sign in with Apple)

The CloudFormation stack creates a user pool with **email (COGNITO)** only. Add Google and Apple as federated providers, then update the app client so Hosted UI and native flows can use them.

## Prerequisites

- User pool ID and app client ID from stack outputs (`UserPoolId`, `UserPoolClientId`).
- Hosted UI domain from output `CognitoHostedUIDomain` (already set by `CognitoDomainPrefix` parameter).

## Google

1. In [Google Cloud Console](https://console.cloud.google.com/), create an **OAuth 2.0 Client ID** (type **Web application** for Cognito federation).
2. Authorized redirect URIs must include:
   - `https://<CognitoHostedUIDomain>/oauth2/idpresponse`
3. Copy **Client ID** and **Client secret**.
4. In AWS Console → Cognito → your user pool → **Sign-in experience** → **Federated identity provider sign-in** → **Add identity provider** → **Google** → paste client ID/secret.
5. In **App integration** → **App clients** → select the iOS client → **Edit hosted UI** (or **Attribute permissions**):
   - Under **Identity providers**, enable **Google**.
   - Ensure callback URL includes `jobsuite.leaf://signin` (already in the template).

Or use AWS CLI:

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id <POOL_ID> \
  --provider-name Google \
  --provider-type Google \
  --provider-details client_id=<>,client_secret=<> \
  --attribute-mapping email=email,username=sub \
  --profile leaf-blower

aws cognito-idp update-user-pool-client \
  --user-pool-id <POOL_ID> \
  --client-id <CLIENT_ID> \
  --supported-identity-providers COGNITO Google \
  --profile leaf-blower
```

(Keep `COGNITO` so email/password still works.)

## Sign in with Apple

1. In [Apple Developer](https://developer.apple.com/account/) → **Identifiers**:
   - Enable **Sign in with Apple** on the **App ID** for `jobsuite.leaf`.
   - Create a **Services ID** (e.g. `com.jobsuite.leaf.signin`) used as Apple’s “client id” for web/Cognito.
2. Configure the Services ID: **Sign in with Apple** → **Configure** → Primary App ID = your iOS app id; add **Return URLs**:
   - `https://<CognitoHostedUIDomain>/oauth2/idpresponse`
3. Create a **Key** (Apple Sign In) and note **Key ID**, **Team ID**, and download the **.p8** private key.
4. In Cognito → **Add identity provider** → **Sign in with Apple**:
   - Services ID, Team ID, Key ID, private key (paste .p8 contents).
5. Update the app client supported identity providers to include `SignInWithApple`:

```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id <POOL_ID> \
  --client-id <CLIENT_ID> \
  --supported-identity-providers COGNITO Google SignInWithApple \
  --profile leaf-blower
```

(Adjust the list to match which providers you actually enabled.)

## iOS app checklist

- **URL scheme** `jobsuite.leaf` is registered for OAuth redirect (see Xcode project).
- **Sign in with Apple** capability enabled on the `jobsuite.leaf` target.
- **Google iOS client** (optional): if using native Google SDK in addition to Hosted UI, add the reversed client ID as a URL scheme; Amplify `signInWithWebUI` often only needs Cognito Hosted UI + universal links / custom scheme as configured above.

After any Cognito change, update **LeafConfig.plist** (pool id, client id, region, domain, API URL) if outputs changed.
