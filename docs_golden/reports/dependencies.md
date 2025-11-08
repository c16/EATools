# Dependency Analysis

## Total Dependencies: 3

| Source | Target | Type |
|--------|--------|------|
| Login Use Case | Validate Credentials | UseCase → UseCase |
| BusinessLogic | DataAccess | Component → Component |
| BusinessLogic | UserInterface | Component → Component |

## Dependency Graph

```mermaid
graph LR
    N10["Login Use Case"]
    N8["Validate Credentials"]
    N10 --> N8
    N27["BusinessLogic"]
    N28["DataAccess"]
    N27 --> N28
    N26["UserInterface"]
    N27 --> N26
```

