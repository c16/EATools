# Documentation Templates - Master Guide

This directory contains markdown templates used by the Sparx EA Documentation Generator to produce customizable documentation output.

## Overview

The template system allows you to customize the format and structure of generated documentation without modifying Python code. Templates use a simple placeholder and conditional syntax to control output.

## Template Files

### Active Templates (Currently Used)

| Template | Generator | Status | Description |
|----------|-----------|--------|-------------|
| `use_case_template.md` | UseCaseGenerator | ✅ Active | Use case documentation format |
| `state_machine_template.md` | StateMachineGenerator | ✅ Active | State machine documentation format |
| `component_template.md` | ComponentGenerator | 🔧 Ready | Component documentation format (TODO: needs data mapping) |
| `class_template.md` | ClassGenerator | 🔧 Ready | Class documentation format (TODO: needs data mapping) |

### Reference Documents

| File | Purpose |
|------|---------|
| `TEMPLATE_ATTRIBUTES.md` | Complete reference of all available attributes for each template type |
| `README.md` | This master guide document |

## Template Syntax

### 1. Placeholders

Replace with actual values from the data:

```markdown
# <element_name>

**Package:** <package_name>
**Description:** <description>
```

### 2. Conditional Sections

Include content only when data exists:

```markdown
<if_actors>**Actors:** <actors_list></if_actors>

<if_preconditions>## Preconditions

<precondition_description>
</if_preconditions>
```

**Syntax:** `<if_section_name>content</if_section_name>`

- Section name should match the data key without the `if_` prefix
- Content is included only if `if_section_name` is `True` in the data
- Supports multiline content

### 3. Repeating Sections (Future)

For repeating items like attributes or operations:

```markdown
<for_each_attribute>| <attribute_name> | <attribute_type> |
</for_each_attribute>
```

**Note:** Currently, repeating sections are pre-rendered by the generator and passed as complete content.

## How Templates Are Used

### 1. Template Loading

```python
# Automatic template detection
generator = UseCaseGenerator(extractor, output_dir)
# Looks for templates/ directory and use_case_template.md
```

### 2. Rendering Process

1. Generator loads template file
2. Builds data dictionary with all available attributes
3. Template renderer processes:
   - Conditional sections (`<if_xxx>`)
   - Placeholder replacements (`<attribute>`)
4. Generator adds breadcrumbs and writes output

### 3. Fallback Behavior

If template is missing or rendering fails:
- Generator logs a warning
- Automatically falls back to hard-coded generation
- Documentation is still produced

## Customizing Templates

### Quick Start

1. **Identify the template** you want to customize (e.g., `use_case_template.md`)
2. **Read the attributes reference** in `TEMPLATE_ATTRIBUTES.md` to see available data
3. **Edit the template** to change the format
4. **Regenerate documentation** - changes take effect immediately

### Example: Changing Section Order

**Original template:**
```markdown
<if_preconditions>## Preconditions
<precondition_description>
</if_preconditions>

<if_actors>**Actors:** <actors_list></if_actors>
```

**Modified template (actors first):**
```markdown
<if_actors>**Actors:** <actors_list></if_actors>

<if_preconditions>## Preconditions
<precondition_description>
</if_preconditions>
```

### Example: Adding Custom Headers

```markdown
## 📋 Description

<description>

## 👥 Stakeholders

<if_actors>**Actors:** <actors_list></if_actors>
```

### Example: Removing Sections

Simply delete or comment out unwanted sections:

```markdown
<!-- Removed preconditions section
<if_preconditions>## Preconditions
<precondition_description>
</if_preconditions>
-->
```

### Example: Changing Metadata Format

**Original:**
```markdown
**<metadata_parts>**
```

**Custom format:**
```markdown
---
**Metadata**
<metadata_parts>
---
```

## Template Best Practices

### 1. Preserve Critical Sections

Always keep these sections:
- Element name/title
- Package name
- Description

### 2. Use Conditionals

Wrap optional sections in conditionals to avoid showing "None" or empty sections:

```markdown
<!-- Good -->
<if_stereotype>**Stereotype:** <<stereotype>></if_stereotype>

<!-- Bad - shows even when no stereotype -->
**Stereotype:** <<stereotype>>
```

### 3. Test Your Changes

After modifying templates:

```bash
# Regenerate documentation
python sparx_doc_generator.py test_model.qea --output test_docs

# Check output files
cat test_docs/use-cases/login-use-case.md
```

### 4. Keep Backups

Before major changes:

```bash
cp templates/use_case_template.md templates/use_case_template.md.backup
```

### 5. Document Your Changes

Add comments in templates to explain custom formatting:

```markdown
<!-- Custom format: Shows actors before description -->
<if_actors>**Actors:** <actors_list></if_actors>
```

## Advanced Customization

### Creating Format Variations

You can maintain multiple template sets for different outputs:

```
templates/
├── default/
│   ├── use_case_template.md
│   └── class_template.md
├── technical/
│   ├── use_case_template.md  (detailed, technical)
│   └── class_template.md
└── executive/
    ├── use_case_template.md  (high-level, summary)
    └── class_template.md
```

Then specify which to use:

```bash
python sparx_doc_generator.py model.qea --output docs --template-dir templates/technical
```

**Note:** Template directory parameter support may need to be added to main script.

### Multi-Language Support

Create language-specific templates:

```markdown
<!-- French template: use_case_template_fr.md -->
# <use_case_name>

**Package:** <package_name>
**Description:** <description>

<if_actors>**Acteurs:** <actors_list></if_actors>

<if_preconditions>## Préconditions
<precondition_description>
</if_preconditions>
```

### Output Format Variations

Templates can produce different markdown flavors:

**GitHub Flavored Markdown:**
```markdown
## Preconditions

**<precondition_name>**

<precondition_description>
```

**With Callouts (for tools like Obsidian):**
```markdown
> [!NOTE] Preconditions
> **<precondition_name>**
>
> <precondition_description>
```

## Template Development Guide

### Adding New Templates

1. **Create the template file**
   ```bash
   touch templates/new_element_template.md
   ```

2. **Define the structure**
   - Use `TEMPLATE_ATTRIBUTES.md` as reference
   - Include all required sections
   - Add conditionals for optional sections

3. **Update the generator**
   - Modify generator's `_generate_with_template()` method
   - Build data dictionary with all attributes
   - Test rendering

4. **Document the template**
   - Add entry to `TEMPLATE_ATTRIBUTES.md`
   - Update this README
   - Provide usage examples

### Testing Templates

**Manual Testing:**
```bash
# Generate with your template
python sparx_doc_generator.py test_model.qea --output test_output

# Compare with golden baseline
diff test_output/use-cases/login-use-case.md docs_golden/use-cases/login-use-case.md
```

**Regression Testing:**
```bash
# After template changes that affect output
python test_doc_consistency.py

# If changes are intentional, update golden baseline
python test_doc_consistency.py --update
```

### Debugging Templates

**Enable verbose logging:**
```bash
python sparx_doc_generator.py test_model.qea --output test_output -v
```

**Check for:**
- Missing placeholders (show as `<placeholder_name>` in output)
- Empty sections (conditionals not working)
- Malformed conditionals (check matching tags)

## Template Syntax Reference

### Conditionals

```markdown
<if_section>
  Content shown only if if_section is True
</if_section>

<if_actors>**Actors:** <actors_list></if_actors>
```

**Rules:**
- Opening tag: `<if_name>`
- Closing tag: `</if_name>`
- Must match exactly (case-sensitive)
- Data key must be `if_name` with value `True`

### Placeholders

```markdown
<placeholder_name>
```

**Replacement behavior:**
- Replaces with data value if exists
- Empty string if value is `None`
- Comma-separated list if value is a list
- Kept as-is if data key doesn't exist

### Special Cases

**Pre-rendered content:**

Some complex sections are pre-rendered by the generator:

```markdown
<if_scenarios><scenario_content>
</if_scenarios>
```

Here, `scenario_content` contains fully formatted scenario text.

**Multi-line values:**

Values can contain newlines and markdown:

```markdown
<precondition_description>
```

Might render as:
```markdown
**Email address**

The user must have an email address.

**Valid user**

The user must exist in the system.
```

## Common Patterns

### Pattern: Optional Metadata

```markdown
<if_stereotype>**Stereotype:** <<stereotype>></if_stereotype>

**Package:** <package_name>

<if_metadata>**<metadata_parts>**</if_metadata>
```

### Pattern: Bulleted Lists

```markdown
<if_actors>**Actors:**
- <actors_list>
</if_actors>
```

### Pattern: Tables

```markdown
<if_attributes>## Attributes

| Name | Type | Description |
|------|------|-------------|
<for_each_attribute>| <attribute_name> | <attribute_type> | <attribute_description> |
</for_each_attribute>
</if_attributes>
```

### Pattern: Nested Sections

```markdown
<if_relationships>## Relationships

<if_inherits_from>**Inherits from:** <parent_classes></if_inherits_from>

<if_implements>**Implements:** <interfaces_list></if_implements>

</if_relationships>
```

## Troubleshooting

### Template Not Being Used

**Check:**
1. Template file exists in `templates/` directory
2. Template file name matches exactly (e.g., `use_case_template.md`)
3. No syntax errors in template
4. Generator has been updated to use templates

**Verify:**
```bash
ls -la templates/
# Should show your template file

python sparx_doc_generator.py test_model.qea --output test_output -v
# Should show template loading messages
```

### Sections Not Appearing

**Possible causes:**
1. Conditional tag mismatch: `<if_actors>` must close with `</if_actors>`
2. Data key wrong: Check `TEMPLATE_ATTRIBUTES.md` for correct key
3. Data is False/None: Conditional section is working correctly, data just doesn't exist

**Debug:**
```bash
# Look for debug log messages
python sparx_doc_generator.py test_model.qea -v 2>&1 | grep "Conditional"
```

### Extra Blank Lines

Template processing can add extra newlines. To minimize:

```markdown
<!-- Instead of this: -->
<if_actors>**Actors:** <actors_list>

</if_actors>

<!-- Do this: -->
<if_actors>**Actors:** <actors_list></if_actors>
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-08 | Initial template system implementation |
|  |  | - Use Case template (active) |
|  |  | - State Machine template (active) |
|  |  | - Component template (infrastructure) |
|  |  | - Class template (infrastructure) |
|  |  | - Template attributes reference |
|  |  | - Master README |

## Future Enhancements

### Planned Features

- [ ] **Loop support**: True `<for_each_xxx>` rendering in template engine
- [ ] **Template inheritance**: Base templates with overrides
- [ ] **Custom functions**: Date formatting, string manipulation
- [ ] **Validation**: Template syntax checker
- [ ] **IDE support**: Syntax highlighting for template files
- [ ] **Export formats**: HTML, PDF, DocX from templates
- [ ] **Template library**: Community-contributed templates

### Contributing Templates

To contribute custom templates:

1. Create your template in `templates/custom/`
2. Document available attributes
3. Test with multiple models
4. Submit with examples and documentation

## Resources

- **Attribute Reference**: See `TEMPLATE_ATTRIBUTES.md` for all available attributes
- **Examples**: Check existing templates for formatting patterns
- **Generator Code**: See `sparx_ea_doc/template_renderer.py` for rendering logic
- **User Docs**: See `QUICKSTART.md` for general project documentation

## Support

For questions or issues with templates:

1. Check this README and `TEMPLATE_ATTRIBUTES.md`
2. Review example templates in this directory
3. Enable verbose logging to debug issues
4. Check generator code for available data

---

**Last Updated**: 2025-11-08
**Template System Version**: 1.0
**Compatible with**: EATools documentation generator v1.0+
