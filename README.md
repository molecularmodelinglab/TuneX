# TuneX
A graphical interface for experimental and process optimization

## Current Status: Early Development

This is a very early prototype with basic functionality only.

## What's Implemented

### Campaign Creation Wizard
- **Step 1: Campaign Info** - Basic campaign setup (name, description, target configuration)
- **Step 2: Parameters** - Configure experimental parameters with constraints and validation
- **Step 3: Data Import** - CSV file upload with validation against parameter constraints

### Parameter System
- Extensible parameter types: continuous numerical, discrete numerical (regular/irregular), categorical, fixed values, substance (SMILES)
- Type-specific constraint widgets with validation
- Factory pattern for easy parameter type extension
- Serialization/deserialization for saving campaign configurations

### Data Import Features
- CSV template generation with example data
- File upload via drag & drop or browse dialog
- Data validation against parameter constraints
- Preview table for imported data (no errors shown in interface yet)
- Detailed error reporting

## What's NOT Implemented Yet

- [ ] User-friendly error messages in UI (currently console output only)
- [ ] Campaign management (view, edit, delete existing campaigns)
- [ ] Optimization algorithm integration
- [ ] Results visualization and analysis
- [ ] Data export functionality
- [ ] User settings and preferences
- [ ] Many more screens and features...

## Tech Stack
- **UI Framework**: PySide6 (Qt6)
- **Language**: Python 3.11

## Precommit checks
poetry run pre-commit

## Testing

This project uses `pytest` for testing. To run the tests, execute the following command:

```bash
poetry run pytest
```

### Test Coverage

To generate a test coverage report, you can use `pytest-cov`. Run the following command:

```bash
poetry run pytest --cov=app tests/
```

This will run the tests and output a coverage report to the console. To generate an HTML report for more detailed analysis, use:

```bash
poetry run pytest --cov=app --cov-report=html tests/
```

The report will be generated in an `htmlcov` directory.

## Architecture Overview

### Code Structure
```
app/
├── main_application.py     # Main application entry point
├── core/                   # Core components, base classes
│   └── base.py
├── models/                 # Data models for the application
│   ├── enums.py
│   └── parameters/         # Parameter definitions
│       ├── base.py
│       └── types.py
├── screens/                # UI screens
│   ├── campaign/           # Campaign creation wizard screens
│   │   ├── campaign_wizard.py
│   │   └── steps/          # Individual steps in the wizard
│   │       └── ...
│   └── start/              # Start screen
│       └── start_screen.py
├── shared/                 # Shared components and styles
│   ├── components/
│   └── styles/
```

### Key Classes

**Parameter System:**
- `BaseParameter` - Abstract base with registry pattern, extensible via inheritance
- Parameter types: `DiscreteNumericalRegular`, `ContinuousNumerical`, `Categorical`, `Fixed`, `Substance`
- Each parameter handles its own validation, value conversion, and example generation

**UI Architecture:**
- `ParameterRowManager` - Manages parameters table and constraint widgets
- `CSVTemplateGenerator` - Creates CSV templates from parameter definitions
- `CSVDataImporter` - Imports and validates CSV data against parameters
- `DataPreviewWidget` - Displays imported CSV data with validation status
- Constraint widgets: `MinMaxStepWidget`, `ValuesListWidget`, `FixedValueWidget`, etc.
- `FileValidator`, `DragDropArea` - File upload components
- Widget factory pattern for creating parameter-specific constraint widgets

**Communication:**
- Qt signals for widget communication
- Shared `campaign_data` dict for step coordination

---
*This is just the beginning - much more functionality planned.*
