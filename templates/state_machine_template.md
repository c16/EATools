# State Machine: <state_machine_name>

**Package:** <package_name>

**Description:** <description>

<if_states>## States

<for_each_state>### <state_name>

| Property | Value |
|----------|-------|
| Type | <state_type> |
| Entry | <entry_operations> |
| Do | <do_operations> |
| Exit | <exit_operations> |
| Description | <state_description> |

</for_each_state>
</if_states>

<if_no_states>*No states defined for this state machine.*
</if_no_states>

<if_transitions>## Transitions

| From | To | Trigger | Guard | Notes |
|------|----|---------|-------|-------|
<for_each_transition>| <from_state> | <to_state> | <trigger> | <guard> | <notes> |
</for_each_transition>
</if_transitions>

<if_no_transitions>*No transitions defined.*
</if_no_transitions>
