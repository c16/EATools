# Process Order

[Home](../index.md) > [Use Cases](index.md) > Process Order

**Package:** UseCases

**Version: 1.0 | Modified: 2025-11-05 20:18:11 | GUID: {5A7174FA-7DAA-49df-8F67-710412B60C89}**

**Actors:** Customer, Payment System

**Diagrams:**

![Diagram {1FC8DD1E-BDFA-4b48-8540-49BB480298C0}](../diagrams/usecases.png)

## Business Rules

- The customer must have an account
- The item must be in stock
- The customer must have a valid payment card registered

### Basic Path: Select item

**Steps:**

1. The customer places the item in the basket
2. The customer selects item quality
3. The system checks the item quantity is in stock
   - _3a. Alternate flow: Out of stock_
4. The item gets reserved in the warehouse
5. The customer enters payment information
6. The user selects the shipping address
   - _6a. Alternate flow: Invalid address_
7. The payment system takes the payment from the customer
   - _7a. Alternate flow: Payment declined_
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

