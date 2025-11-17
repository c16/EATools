# Generate Report

[Home](../index.md) > [Use Cases](index.md) > Generate Report



**Package:** UseCases

**Version: 1.0 | Modified: 2025-11-05 20:21:04 | GUID: {1AA0EE9F-6693-48bb-8268-768EBEA1460B}**

**Description:** No description available


**Actors:** Manager

**Related Use Cases:**
- Fetch Data


**Requirements:**
- [Data Collection for Reports](../requirements/data-collection-for-reports-137.md)
- [Data Presentation to Manager](../requirements/data-presentation-to-manager-138.md)
- [Manager Actor Support](../requirements/manager-actor-support-140.md)
- [Report Generation Selection](../requirements/report-generation-selection-136.md)


### Basic Path: Basic Path

**Steps:**

1. The manager selects generate report on the system
2. The system collects all data: <<include>> Fetch Data
3. The data is presented to the manager


