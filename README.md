# 🏋️‍♂️ Fitness Assistant & Macro Calculator

A sophisticated, AI-driven nutrition planning web application built with Python and Streamlit that provides personalized macronutrient recommendations for fitness enthusiasts, bodybuilders, and anyone pursuing specific body composition goals.

## 🌟 Overview

The Fitness Assistant & Macro Calculator is an intelligent nutrition planning tool that calculates personalized daily macronutrient targets based on individual user profiles, activity levels, and fitness goals. The application leverages scientifically-backed formulas (Mifflin-St Jeor Equation) to deliver accurate caloric and macro recommendations tailored for muscle building, fat loss, or body recomposition.

## ✨ Key Features

### 🎯 Personalized Nutrition Planning
- **Scientific BMR Calculation**: Uses the Mifflin-St Jeor Equation for precise Basal Metabolic Rate calculations
- **Goal-Specific Adjustments**: Supports multiple fitness objectives including:
  - Muscle gain (bulk)
  - Lean bulk (slight surplus)
  - Body recomposition (maintenance)
  - Moderate cut (fat loss)
  - Aggressive cut (rapid fat loss)
- **Activity Level Customization**: Accounts for 5 different activity levels from sedentary to extra active

### 📊 Interactive Data Visualization
- **Macro Distribution Charts**: Beautiful Plotly-powered pie charts showing caloric breakdown
- **Meal Timing Timeline**: Stacked bar charts displaying optimal nutrient timing throughout the day
- **Progress Tracking Gauges**: Visual progress indicators for weight goals
- **Responsive Design**: Mobile-friendly charts that adapt to screen size

### 🍽️ Comprehensive Meal Planning
- **Customized Meal Plans**: Generates detailed daily meal plans based on:
  - Diet preference (vegetarian/non-vegetarian)
  - Protein supplement usage
  - Cutting vs. bulking phase
- **Nutrient Timing Optimization**: Strategic meal timing around workouts for maximum results
- **Portion-Specific Guidelines**: Exact food quantities and serving sizes

### 📄 Professional PDF Reports
- **Downloadable Nutrition Plans**: Generate beautifully formatted PDF reports using ReportLab
- **Complete User Profile**: Includes all personal metrics and calculated targets
- **Detailed Recommendations**: Science-based nutrition guidance specific to user's goals
- **Sample Meal Plans**: Ready-to-follow daily eating schedules

### 💡 Educational Resources
- **Expandable Information Sections**: Detailed explanations for:
  - Protein recommendations and timing
  - Carbohydrate strategies
  - Healthy fat intake guidelines
- **Goal-Specific Tips**: Tailored advice for cutting vs. bulking phases
- **Food Source Lists**: Comprehensive lists of optimal protein, carb, and fat sources with nutritional values

## 🚀 Technology Stack

- **Frontend Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Express, Plotly Graph Objects, Matplotlib
- **PDF Generation**: ReportLab
- **Language**: Python 3.x

## 📋 Prerequisites

```bash
python >= 3.7
streamlit
pandas
plotly
matplotlib
reportlab
numpy
```

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/Nethran-offcl/fitness-assistant-macro-calculator.git
cd fitness-assistant-macro-calculator
```

2. Install required dependencies:
```bash
pip install streamlit pandas plotly matplotlib reportlab numpy
```

3. Run the application:
```bash
streamlit run fitnesscalc.py
```

4. Open your browser and navigate to:
```
http://localhost:8501
```

## 💻 Usage

1. **Enter Personal Information**:
   - Age, gender, height (cm), and weight (kg)
   
2. **Set Your Goals**:
   - Select activity level
   - Choose fitness goal (bulk, cut, recomp)
   - Specify diet preference
   - Indicate protein supplement usage

3. **Calculate Macros**:
   - Click "Calculate My Macros" button
   - View personalized daily targets
   
4. **Explore Recommendations**:
   - Review macro distribution charts
   - Check meal timing suggestions
   - Read detailed nutrition guidelines
   
5. **Download Your Plan**:
   - Generate and download PDF report
   - Save for offline reference

## 🔬 Scientific Methodology

### Basal Metabolic Rate (BMR)
The application uses the **Mifflin-St Jeor Equation**, recognized as one of the most accurate BMR prediction formulas:

**For Males:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
```

**For Females:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
```

### Total Daily Energy Expenditure (TDEE)
```
TDEE = BMR × Activity Multiplier
```

Activity multipliers range from 1.2 (sedentary) to 1.9 (extra active).

### Macronutrient Distribution
- **Protein**: 2.0-2.5g per kg body weight (varies by goal)
- **Fats**: 20-30% of total calories (hormone regulation)
- **Carbohydrates**: Remaining calories (energy and recovery)

## 📊 Application Architecture

```
fitnesscalc.py
│
├── calculate_macros()          # Core BMR/TDEE calculation logic
├── create_pdf()                # PDF report generation
├── create_macro_chart()        # Plotly pie chart visualization
├── create_meal_timing_chart()  # Meal timing timeline
├── create_progress_gauge()     # Progress tracking visualization
└── main()                      # Streamlit UI and user interaction
```

## 🎨 User Interface Highlights

- **Gradient Headers**: Eye-catching gradient backgrounds for sections
- **Metric Cards**: Stylized cards displaying key nutrition metrics
- **Expandable Sections**: Clean, organized information architecture
- **Color-Coded Macros**: Consistent color scheme (Protein: Red, Carbs: Teal, Fats: Blue)
- **Responsive Layout**: Optimized for desktop and mobile viewing

## 📈 Future Enhancements

- [ ] User authentication and profile management
- [ ] Progress tracking database integration
- [ ] Food logging and macro tracking
- [ ] Recipe suggestions based on macro targets
- [ ] Integration with fitness tracking APIs
- [ ] Multi-language support
- [ ] Dark mode theme option
- [ ] Weekly meal prep planning
- [ ] Grocery list generation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Developer

**Nethran**  
GitHub: [@Nethran-offcl](https://github.com/Nethran-offcl)

## 🙏 Acknowledgments

- Mifflin-St Jeor Equation for BMR calculation methodology
- Sports nutrition research for macronutrient distribution guidelines
- Streamlit community for excellent documentation
- Fitness and nutrition communities for best practices

## 📞 Support

For questions, suggestions, or issues, please open an issue on GitHub or contact the developer.

---

**Note**: This calculator provides estimates based on scientifically-validated formulas. Individual nutritional needs may vary based on genetics, medical conditions, training intensity, and specific goals. Always consult with a registered dietitian or healthcare professional before making significant dietary changes.

**Built with ❤️ for the fitness community