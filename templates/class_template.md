# Class: <class_name>

<if_stereotype>**Stereotype:** <<stereotype>></if_stereotype>

**Package:** <package_name>

**Visibility:** <visibility>

**Description:** <description>
<if_diagrams>

**Diagrams:**
<diagram_list></if_diagrams>

<if_attributes>## Attributes

| Name | Type | Visibility | Default | Static | Const | Description |
|------|------|------------|---------|--------|-------|-------------|
<for_each_attribute>| <attribute_name> | <attribute_type> | <visibility> | <default_value> | <is_static> | <is_const> | <attribute_description> |
</for_each_attribute>
</if_attributes>

<if_methods>## Methods

| Name | Parameters | Return Type | Visibility | Abstract | Static | Description |
|------|------------|-------------|------------|----------|--------|-------------|
<for_each_method>| <method_name> | <parameters> | <return_type> | <visibility> | <is_abstract> | <is_static> | <method_description> |
</for_each_method>
</if_methods>

<if_relationships>## Relationships

<if_inherits_from>**Inherits from:** <parent_classes></if_inherits_from>

<if_implements>**Implements:** <interfaces_list></if_implements>

<if_associations>**Associations:**

- <association_target> <cardinality> <role> [<association_type>]

</if_associations>

<if_dependencies>**Dependencies:** <dependencies_list></if_dependencies>
</if_relationships>
