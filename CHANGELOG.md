# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-11-08

### Fixed
- Fixed additional Unicode encoding issues in README.md output directory structure section
- Replaced Unicode characters with standard ASCII tree characters (├──, └──) for consistent rendering

## [1.0.2] - 2025-11-08

### Fixed
- Fixed Unicode box-drawing characters in README.md Project Structure section to use ASCII tree characters for universal markdown compatibility

## [1.0.1] - 2025-11-08

### Fixed
- Fixed Unicode card suit symbols in README and report generator to use ASCII notation (C, D, H, S) for better markdown compatibility
- Removed obsolete documentation files (ANALYSIS_GUIDE.md, HAND_TRACKING_TODO.md, WORKFLOW.md)

### Changed
- Updated report_generator.py to convert Unicode suit symbols to ASCII in generated markdown reports

## [1.0.0] - 2025-11-07

### Added
- Initial release of Cribbage Statistics simulator and analysis tool
- Core cribbage game simulation with full rule implementation
- Random state tracking for reproducibility
- Comprehensive analysis modules:
  - Best/worst/middle-tier hand analysis
  - Scoring distribution analysis
  - Dealer advantage analysis
  - Card values analysis with special 5s analysis
- Markdown report generator with embedded visualizations
- Three visualization plots: score distribution, dealer advantage, card values
- CSV export for hands and game summaries
- CLI interface with verbosity controls
- Session logging system
- Documentation: README, ANALYSIS_GUIDE, WORKFLOW, HAND_TRACKING_TODO

### Features
- Simulate 100k+ games with detailed tracking
- Analyze card rank values and scoring patterns
- Generate comprehensive markdown reports with explanations
- Track random seeds for reproducible simulations
- Export detailed hand-by-hand and game summary data
