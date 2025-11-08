# State Machine: Order State Machine

[Home](../index.md) > [State Machines](index.md) > Order State Machine


**Package:** StateMachines

**Description:** No description available


## States

### Cancelled

| Property | Value |
|----------|-------|
| Type | State |
| Entry | - Send email |
| Do | - Check customer acknowledgement |
| Exit | - |
| Description | - |

### Delivered

| Property | Value |
|----------|-------|
| Type | State |
| Entry | - |
| Do | - Check customer acknowledged package |
| Exit | - |
| Description | - |

### Final

| Property | Value |
|----------|-------|
| Type | StateNode |
| Entry | - |
| Do | - |
| Exit | - |
| Description | - |

### Initial

| Property | Value |
|----------|-------|
| Type | StateNode |
| Entry | - |
| Do | - |
| Exit | - |
| Description | Item has been selected. |

### Pending

| Property | Value |
|----------|-------|
| Type | State |
| Entry | - Check Stock |
| Do | - |
| Exit | - |
| Description | - |

### Processing

| Property | Value |
|----------|-------|
| Type | State |
| Entry | - Take payment |
| Do | - |
| Exit | - |
| Description | - |

### Shipped

| Property | Value |
|----------|-------|
| Type | StateMachine |
| Entry | - |
| Do | - |
| Exit | - |
| Description | - |



## Transitions

| From | To | Trigger | Guard | Notes |
|------|----|---------|-------|-------|
| Cancelled | Final | - | - | - |
| Delivered | Final | DELIVERED | - | - |
| Initial | Pending | - | - | - |
| Pending | Processing | STOCK_CHECKED | item in stock | - |
| Pending | Cancelled | STOCK_CHECKED | item not in stock | - |
| Processing | Cancelled | PAYMENT | payment not successful | - |
| Processing | Delivered | PAYMENT | payment successful | - |

