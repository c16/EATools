# Template Attributes Reference

This document describes all available attributes (placeholders) for each documentation template type. Use this reference when customizing your templates.

## Table of Contents

1. [Use Case Template](#use-case-template)
2. [State Machine Template](#state-machine-template)
3. [Component Template](#component-template)
4. [Class Template](#class-template)
5. [Common Conventions](#common-conventions)

---

## Use Case Template

**Template file:** `use_case_template.md`

### Basic Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<use_case_name>` | Name of the use case | `Login Use Case` |
| `<stereotype>` | UML stereotype if present | `business` |
| `<package_name>` | Name of the containing package | `User Management` |
| `<description>` | Clean description text from notes field | `Allows users to authenticate...` |
| `<metadata_parts>` | Combined metadata string | `Version: 1.0 \| Modified: 2025-01-15 \| GUID: {ABC-123}` |

### Metadata Components

These make up `<metadata_parts>`:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<version>` | Version number | `1.0` |
| `<modified_date>` | Last modification date | `2025-01-15` |
| `<guid>` | Enterprise Architect GUID | `{EA-GUID-123}` |

### Relationships

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<actors_list>` | Comma-separated list of actors | `Customer, Administrator` |
| `<included_use_case>` | Use case included via <<include>> | `Validate Credentials` |
| `<extending_use_case>` | Use case that extends this one via <<extend>> | `Forgot Password` |
| `<related_use_case>` | Other associated use cases | `Register Account` |

### Constraints (from constraints table)

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<precondition_name>` | Name of precondition | `User Not Logged In` |
| `<precondition_description>` | Description of precondition | `User must not have active session` |
| `<postcondition_name>` | Name of postcondition | `User Authenticated` |
| `<postcondition_description>` | Description of postcondition | `User has valid session token` |

### Structured Note Sections

These are parsed from the notes field with section headers:

| Section | Description |
|---------|-------------|
| `<main_flow_content>` | Main flow section content |
| `<alternative_flows_content>` | Alternative flows section content |
| `<business_rule>` | Individual business rule (repeating) |
| `<exceptions_content>` | Exceptions section content |

### Scenarios (from t_objectscenarios table)

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<scenario_type>` | Type of scenario | `Basic Path`, `Alternate`, `Exception` |
| `<scenario_level>` | Step level prefix for alternates/exceptions | `1.a` |
| `<scenario_name>` | Name of the scenario | `Happy Path` |
| `<step_number>` | Step number in scenario | `1`, `2`, `3` |
| `<step_description>` | Text of the step | `User enters credentials` |
| `<extension_level>` | Level for extension reference | `1.a` |
| `<flow_type>` | Type of flow for extensions | `Alternate flow`, `Exception flow` |
| `<extension_name>` | Name of referenced extension | `Invalid Credentials` |
| `<scenario_notes>` | Notes for the scenario | `Implements OAuth 2.0` |

### Conditional Sections

Use these to control when sections appear:

- `<if_stereotype>` - Show if stereotype exists
- `<if_actors>` - Show if actors are associated
- `<if_includes>` - Show if includes relationships exist
- `<if_extends>` - Show if extended by other use cases
- `<if_related>` - Show if related use cases exist
- `<if_preconditions>` - Show if preconditions defined
- `<if_postconditions>` - Show if postconditions defined
- `<if_main_flow>` - Show if main flow section exists
- `<if_scenarios>` - Show if scenarios exist
- `<if_alternative_flows>` - Show if alternative flows section exists
- `<if_business_rules>` - Show if business rules section exists
- `<if_exceptions>` - Show if exceptions section exists
- `<if_scenario_details>` - Repeating section for each scenario
- `<if_scenario_notes>` - Show if scenario has notes

---

## State Machine Template

**Template file:** `state_machine_template.md`

### Basic Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<state_machine_name>` | Name of the state machine | `Order Processing` |
| `<package_name>` | Name of the containing package | `Business Logic` |
| `<description>` | Clean description text from notes | `Manages order lifecycle...` |

### State Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<state_name>` | Name of the state | `Pending Approval` |
| `<state_type>` | Type of state element | `StateNode`, `State`, `FinalState` |
| `<entry_operations>` | List of entry operations | `- validateOrder<br>- notifyManager` |
| `<do_operations>` | List of do operations | `- processPayment` |
| `<exit_operations>` | List of exit operations | `- cleanupResources` |
| `<state_description>` | Description of the state | `Waiting for manager approval` |

### Transition Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<from_state>` | Source state name | `Pending Approval` |
| `<to_state>` | Target state name | `Approved` |
| `<trigger>` | Event that triggers transition | `approve` |
| `<guard>` | Guard condition | `[amount < 1000]` |
| `<notes>` | Notes about the transition | `Automatic for small orders` |

### Conditional Sections

- `<if_states>` - Show if states are defined
- `<if_no_states>` - Show if no states defined
- `<if_transitions>` - Show if transitions exist
- `<if_no_transitions>` - Show if no transitions exist
- `<for_each_state>` - Repeating section for each state
- `<for_each_transition>` - Repeating section for each transition

---

## Component Template

**Template file:** `component_template.md`

### Basic Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<component_name>` | Name of the component | `Payment Service` |
| `<stereotype>` | UML stereotype if present | `service` |
| `<package_name>` | Name of the containing package | `Services` |
| `<description>` | Clean description text from notes | `Handles payment processing...` |

### Interface Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<provided_interface>` | Interface provided by component | `IPaymentProcessor` |
| `<required_interface>` | Interface required by component | `IDatabase` |

### Dependency Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<dependencies_list>` | Comma-separated list of dependencies | `Logger, ConfigManager` |
| `<used_by_list>` | Comma-separated list of components using this | `OrderService, InvoiceService` |

### Attribute Attributes (for components)

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<attribute_name>` | Name of the attribute | `connectionString` |
| `<attribute_type>` | Type of the attribute | `String` |
| `<visibility>` | Visibility scope | `Private`, `Public`, `Protected` |
| `<default_value>` | Default value | `localhost:5432` |
| `<is_static>` | Whether attribute is static | `Yes`, `No` |

### Operation Attributes (for components)

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<operation_name>` | Name of the operation | `processPayment` |
| `<parameters>` | Comma-separated parameters | `amount: Decimal, currency: String` |
| `<return_type>` | Return type of operation | `PaymentResult` |
| `<visibility>` | Visibility scope | `Public` |

### Conditional Sections

- `<if_stereotype>` - Show if stereotype exists
- `<if_interfaces>` - Show if any interfaces exist
- `<if_provided_interfaces>` - Show if provided interfaces exist
- `<if_required_interfaces>` - Show if required interfaces exist
- `<if_dependencies>` - Show if dependencies exist
- `<if_depends_on>` - Show if component depends on others
- `<if_used_by>` - Show if component is used by others
- `<if_attributes>` - Show if attributes are defined
- `<if_operations>` - Show if operations are defined
- `<for_each_attribute>` - Repeating section for each attribute
- `<for_each_operation>` - Repeating section for each operation

---

## Class Template

**Template file:** `class_template.md`

### Basic Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<class_name>` | Name of the class | `Order` |
| `<stereotype>` | UML stereotype if present | `entity` |
| `<package_name>` | Name of the containing package | `Domain` |
| `<visibility>` | Class visibility | `Public`, `Package` |
| `<description>` | Clean description text from notes | `Represents a customer order...` |

### Attribute Attributes (for classes)

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<attribute_name>` | Name of the attribute | `orderId` |
| `<attribute_type>` | Type of the attribute | `Integer` |
| `<visibility>` | Visibility scope | `Private`, `Public`, `Protected`, `Package` |
| `<default_value>` | Default value | `0` |
| `<is_static>` | Whether attribute is static | `Yes`, `No` |
| `<is_const>` | Whether attribute is constant | `Yes`, `No` |
| `<attribute_description>` | Description of the attribute | `Unique order identifier` |

### Method Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<method_name>` | Name of the method | `calculateTotal` |
| `<parameters>` | Comma-separated parameters | `tax: Decimal, discount: Decimal` |
| `<return_type>` | Return type of method | `Decimal` |
| `<visibility>` | Visibility scope | `Public`, `Private`, etc. |
| `<is_abstract>` | Whether method is abstract | `Yes`, `No` |
| `<is_static>` | Whether method is static | `Yes`, `No` |
| `<method_description>` | Description of the method | `Calculates order total with tax` |

### Relationship Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `<parent_classes>` | Comma-separated list of parent classes | `BaseEntity, Auditable` |
| `<interfaces_list>` | Comma-separated list of interfaces | `IValidatable, ISerializable` |
| `<association_target>` | Target class of association | `Customer` |
| `<cardinality>` | Cardinality of association | `(0..*)`, `(1)` |
| `<role>` | Role name in association | `buyer` |
| `<association_type>` | Type of association | `Association`, `Aggregation`, `Composition` |
| `<dependencies_list>` | Comma-separated list of dependencies | `Logger, Validator` |

### Conditional Sections

- `<if_stereotype>` - Show if stereotype exists
- `<if_attributes>` - Show if attributes are defined
- `<if_methods>` - Show if methods are defined
- `<if_relationships>` - Show if any relationships exist
- `<if_inherits_from>` - Show if class inherits from parent(s)
- `<if_implements>` - Show if class implements interface(s)
- `<if_associations>` - Show if associations exist
- `<if_dependencies>` - Show if dependencies exist
- `<for_each_attribute>` - Repeating section for each attribute
- `<for_each_method>` - Repeating section for each method

---

## Common Conventions

### Conditional Blocks

Sections wrapped in `<if_...>` tags will only appear if the corresponding data exists:

```markdown
<if_stereotype>**Stereotype:** <<stereotype>></if_stereotype>
```

If no stereotype exists, the entire line is omitted from output.

### Repeating Sections

Sections wrapped in `<for_each_...>` tags will repeat for each item:

```markdown
<for_each_attribute>| <attribute_name> | <attribute_type> |
</for_each_attribute>
```

This generates one table row per attribute.

### Null/Empty Values

When a value is not available:
- Text fields: Shown as `No description available` or similar
- Table cells: Shown as `-`
- Lists: Section is hidden via `<if_...>` conditional

### Multi-line Values

Some attributes contain formatted content:
- `<entry_operations>` - Multiple operations separated by `<br>` for HTML line breaks
- `<do_operations>` - Multiple operations separated by `<br>`
- `<exit_operations>` - Multiple operations separated by `<br>`

### Metadata Format

The `<metadata_parts>` attribute combines multiple metadata fields:
- If all present: `Version: 1.0 | Modified: 2025-01-15 | GUID: {ABC-123}`
- If partial: Only includes available fields with ` | ` separator

### Parameter Format

The `<parameters>` attribute formats method/operation parameters:
- Empty: `-`
- Single: `amount: Decimal`
- Multiple: `amount: Decimal, currency: String`

---

## Customization Tips

### Changing Section Headers

To change a section header, simply modify the markdown:

```markdown
## Preconditions  →  ## Pre-conditions
```

### Adding Custom Sections

You can add static text that appears for all documents:

```markdown
## Notes

This use case was auto-generated from Enterprise Architect.
```

### Reordering Sections

Rearrange template sections to change the order in generated documentation:

```markdown
## Methods
...
## Attributes
...
```

### Conditional Custom Text

Combine conditionals with custom text:

```markdown
<if_actors>## Actors Involved

The following actors participate in this use case:

**Actors:** <actors_list>
</if_actors>
```

### Table Customization

Add or remove columns from tables:

```markdown
| Name | Type | Description |
|------|------|-------------|
<for_each_attribute>| <attribute_name> | <attribute_type> | <attribute_description> |
```

---

## Examples

### Example: Changing Precondition Format

**Original:**
```markdown
<if_preconditions>## Preconditions

**<precondition_name>**

<precondition_description>
</if_preconditions>
```

**Custom Format:**
```markdown
<if_preconditions>## Pre-condition: <precondition_name>: <precondition_description>
</if_preconditions>
```

### Example: Simplified Use Case

**Minimal template:**
```markdown
# <use_case_name>

<description>

**Actors:** <actors_list>

### Basic Path: <scenario_name>

<step_number>. <step_description>
```

### Example: Detailed Class Documentation

**Enhanced template:**
```markdown
# Class: <class_name>

> **Package:** <package_name>
> **Visibility:** <visibility>

## Overview

<description>

<if_inherits_from>
**Extends:** <parent_classes>
</if_inherits_from>

<if_implements>
**Implements:** <interfaces_list>
</if_implements>

## Public API

<if_methods>
<for_each_method>### <method_name>(<parameters>): <return_type>

<method_description>

</for_each_method>
</if_methods>
```

---

**Last Updated:** 2025-11-08
**Template Version:** 1.0
