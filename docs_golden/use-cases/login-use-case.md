# Login Use Case

[Home](../index.md) > [Use Cases](index.md) > Login Use Case

**Package:** UseCases

**Version: 1.0 | Modified: 2025-11-05 20:02:49 | GUID: {3C1EC733-25CF-4d37-A38D-70C48FA12AEE}**

**Description:** The login use case shows how the user logs into the system.

**Actors:** User (primary)

**Related Use Cases:**
- Reset Password
- Validate Credentials

## Preconditions

**Email address**

The user must have an email address specified by the administrator.

**Valid user**

The user must have been added by the system administrator.

## Postconditions

**User validated**

The user can continue to use the payment system.

### Basic Path: Login

**Steps:**

1. The user enters their user name on the login screen
2. The user enters their password on the login screen
3. <<include>> Validate Credentials
4. The application screen is shown to the user
   4a. Exception flow: Incorrect password
5. Use case end

### 4a Exception: Incorrect password

**Steps:**

1. The incorrect password screen is shown to the user
2. The reset password option is shown to the user
3. Use case end

