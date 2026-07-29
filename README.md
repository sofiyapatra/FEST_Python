# FEST:  Faculty Evaluation System

**Summer 2026 · Vanderbilt University**

---

## Overview

FEST (Faculty Evaluation System) is a desktop application built with Python and Tkinter that manages student academic records, visualizations, and campus resources. Originally developed as a monolithic script, the codebase has been refactored into a modular, object-oriented architecture with theme support, new features, and improved maintainability.

---

## Major Changes & Additions

### 1. Modular File Structure *(attributed to Sofiya)*

**Before**: Single `main.py` file (~1,500 lines) containing all functionality (UI, data management, authentication, and visualizations) & global variables.

We created eight distinct modules, each with a single responsibility:

- [PLACEHOLDER: TABLE EXPLAINING DIFF MODULES]

**Reasoning**: Separation of concerns allows independent development, testing, and debugging. Sofiya was also getting dizzy reading through the giant main.py file

---

### 2. Theme Management & Light/Dark Mode *(attributed to Sofiya)*

**Before**: Hardcoded colors throughout the application with no way to switch themes.

**After**: `ThemeManager` class provides two palettes (`dark` and `light`) with a single toggle that refreshes the entire UI.

- **Dark Mode**: Deep charcoal background (#1A1A1A) with warm gold accents
[PLACEHOLDER: SCREENSHOT DARK MODE]
- **Light Mode**: Cream/ivory background (#F5F0E8) with rich brown tones
[PLACEHOLDER: SCREENSHOT LIGHT MODE]

**Reasoning**: Users can choose their preferred visual style. All (ideally) UI components now fetch colors dynamically via `self.theme.get_color()`, ensuring consistency.

---

### 3. New Menu Options

#### a. Dean's List *(attributed to Sofiya)*
Displays students with an average GPA of 3.5 or higher across all recorded coursework. Honors are presented with medal icons (🥇🥈🥉) for the top three performers.
[PLACEHOLDER: SCREENSHOT DEAN's LIST]
[PLACEHOLDER: SCREENSHOT CODE SNIPPET IN OPERATIONS.PY AND DATA.PY]

#### b. Statistics Dashboard *(attributed to Sofiya)*
Comprehensive analytics including:
- Overview metrics (total students, courses, avg/max/min GPA)
- Grade distribution (A-F)
- Top 5 students with GPA rankings
- Major distribution summary
- [PLACEHOLDER: SCREENSHOT STATISTICS DASHBOARD]
- [PLACEHOLDER: SCREENSHOT CODE SNIPPET IN OPERATIONS.PY AND DATA.PY]

#### c. Student Organizations *(attributed to Dania)*
Manages campus clubs and organizations with:
- Searchable table of clubs
- Member counts and average GPAs
- Statistics card overview
- *(Currently static data; future update for dynamic management)*
- [PLACEHOLDER: SCREENSHOT STUDENT ORGS]

##### ci.  Student Organizations Integration with Student ID *(attributed to Jay)*

Student ID cards now display organization affiliations based on the student's major:
- [PLACEHOLDER: SCREENSHOT TABLE CORRESPONDING MAJOR AND ORG]
- [PLACEHOLDER: SCREENSHOT STUDENT ID CARD WITH STUDENT ORG HIGHLIGHTED]

- *(Currently static data; future update for dynamic management)*

**Reasoning**: shows a student's campus involvement, giving a more complete student profile.

#### d. Tutoring Finder *(attributed to Iris)*
Find tutoring sessions by major:
- Dropdown selection of available majors
- Displays session details (days, times, subjects, locations)
- Styled with the application's theme system
- [PLACEHOLDER: SCREENSHOT TUTORING FINDER]

---

## Challenges Encountered

### Version Control
- Multiple team members contributed features independently using the original monolithic file structure.
- Committing directly into main (bad practice)
- Limited time prevented full refactoring of every feature to fully integrate into new architecture

### Time Constraints
- The final integration sprint was compressed, resulting in some features (e.g., Add/Edit/Delete in Student Organizations) being implemented as "Coming Soon" placeholders.
- Not all UI elements were fully migrated to use the ThemeManager for all colors, causing occasional style inconsistencies.

---

## Next Steps:

### 1. Make All Popup Windows Scrollable
Currently, only the main menu supports scrolling. Every popup (e.g., Statistics Dashboard, Student Organizations) should be wrapped in a scrollable canvas to handle content that exceeds the window height.

### 2. Better Integration with ThemeManager/DataManager
- **ThemeManager**: Ensure every widget uses `self.theme.get_color()` instead of hardcoded colors.
- **DataManager**: Move static data (club lists, tutoring data, dean's list thresholds) from methods into the `DataManager` for easier updates and persistence.

### 3. Complete "Coming Soon" Features
- Student Organizations: Add, Edit, Delete functionality
- Student Clubs: Dynamic membership tracking and enrollment
- Export Reports: PDF/CSV export for statistics and Dean's List

### 4. Unit Testing
Implement unit tests for each manager class to ensure reliability as the codebase grows.

---

## Repository Structure: 
- [PLACEHOLDER: SCREENSHOT OF REPOSITORY STRUCTURE]

---

## Requirements:

- Python 3.10+
- `matplotlib`, `seaborn`, `pandas`, `numpy`
- Tkinter
---
