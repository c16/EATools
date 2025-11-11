# Sample Diagrams

These are sample diagrams generated from `test_model.qea` demonstrating the improved diagram rendering capabilities.

## Improvements Demonstrated

### Color Matching to EA Palette
- **Use Cases** (`usecases.png`): Light blue (#E7F0FA) fill with #5B9BD5 outline
- **Classes** (`domain.png`): Tan/beige (245,245,220) for classes, lavender for interfaces, light green for enumerations
- **Components** (`components.png`): Misty rose/light pink (255,228,225) matching EA
- **State Machines** (`order_state_machine.png`, `shipped.png`): Tan/beige (245,245,220) for states

### Connector Enhancements
- **Stereotypes**: Visible on relationships (e.g., «extend», «include» in use case diagrams)
- **Line Styles**: Dashed lines for extend/include relationships
- **Labels**: Navy blue text for better visibility

## Files

- `usecases.png` - Use case diagram with stereotypes and actor relationships
- `domain.png` - Class diagram showing Entity, User, Order, and related classes
- `components.png` - Component diagram with BusinessLogic, DataAccess, and UserInterface
- `order_state_machine.png` - State machine for order processing workflow
- `shipped.png` - Substate diagram for the Shipped state
- `requirements.png` - Requirements diagram
