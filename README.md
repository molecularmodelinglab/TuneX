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
- [ ] TESTS
- [ ] Many more screens and features...

## Tech Stack
- **UI Framework**: PySide6 (Qt6)
- **Language**: Python 3.x

---
*This is just the beginning - much more functionality planned.*