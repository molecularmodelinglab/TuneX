# TuneX
A graphical interface for experimental and process optimization


## Current Status: Early Development

This is a very early prototype with basic functionality only.

## What's Implemented

### Campaign Creation Wizard
- **Step 1: Campaign Info** - Basic campaign setup (name, description, target configuration)
- **Step 2: Parameters** - Configure experimental parameters with constraints
- **Step 3: Data Import** - Placeholder for historical data upload

### Parameter System
- Extensible parameter types: continuous numerical, discrete numerical (regular/irregular), categorical, fixed values, substance (SMILES)
- Type-specific constraint widgets with validation
- Factory pattern for easy parameter type extension
- Serialization/deserialization for saving campaign configurations

## What's NOT Implemented Yet

- [ ] Actual Excel data import and validation
- [ ] User-friendly error messages (currently just console prints)
- [ ] Campaign management (view, edit, delete)
- [ ] Optimization algorithm integration
- [ ] Results visualization
- [ ] Many more screens and features...
- [ ] TESTS

## Tech Stack
- **UI Framework**: PySide6 (Qt6)
- **Language**: Python 3.x

---
*This is just the beginning - much more functionality planned.*