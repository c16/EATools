# Process Order

[Home](../index.md) > [Use Cases](index.md) > Process Order



**Package:** UseCases

**Version: 1.0 | Modified: 2025-11-05 20:18:11 | GUID: {5A7174FA-7DAA-49df-8F67-710412B60C89}**

**Description:** Business Rules: The customer must have an account The item must be in stock The customer must have a valid payment card registered


**Actors:** Customer, Payment System

**Requirements:**
- [Add Item to Basket](../requirements/add-item-to-basket.md)
- [Address Re-entry](../requirements/address-re-entry.md)
- [Customer Account Requirement](../requirements/customer-account-requirement.md)
- [Customer Actor Support](../requirements/customer-actor-support.md)
- [Invalid Address Handling](../requirements/invalid-address-handling.md)
- [Item Quantity Selection](../requirements/item-quantity-selection.md)
- [Item Reservation](../requirements/item-reservation.md)
- [Item Stock Requirement](../requirements/item-stock-requirement.md)
- [Out of Stock Error](../requirements/out-of-stock-error.md)
- [Package Dispatch](../requirements/package-dispatch.md)
- [Payment Card Requirement](../requirements/payment-card-requirement.md)
- [Payment Declined Error](../requirements/payment-declined-error.md)
- [Payment Information Entry](../requirements/payment-information-entry.md)
- [Payment Processing](../requirements/payment-processing.md)
- [Payment System Integration](../requirements/payment-system-integration.md)
- [Shipping Address Selection](../requirements/shipping-address-selection.md)
- [Stock Verification](../requirements/stock-verification.md)


## Business Rules

- The customer must have an account
- The item must be in stock
- The customer must have a valid payment card registered

### Basic Path: Select item

**Steps:**

1. The customer places the item in the basket
2. The customer selects item quality
3. The system checks the item quantity is in stock
   3a. Alternate flow: Out of stock
4. The item gets reserved in the warehouse
5. The customer enters payment information
6. The user selects the shipping address
   6a. Alternate flow: Invalid address
7. The payment system takes the payment from the customer
   7a. Alternate flow: Payment declined
8. The package gets dispatched to the customer

### 3a Alternate: Out of stock

**Steps:**

1. An error screen is shown to the customer
2. Use case end

### 6a Alternate: Invalid address

**Steps:**

1. An error screen is shown to the user
2. The customer enters a new address on the screen
3. Continue from step 7

### 7a Alternate: Payment declined

**Steps:**

1. An error screen is presented to the customer
2. Use case end


