import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np

def calculate_macros(age, gender, weight_kg, height_cm, activity_level, goal):
    """
    Calculate macronutrients based on user information for muscle building or cutting
    
    Parameters:
    age (int): Age in years
    gender (str): 'Male' or 'Female'
    weight_kg (float): Weight in kilograms
    height_cm (float): Height in centimeters
    activity_level (str): Activity level description
    goal (str): Fitness goal
    
    Returns:
    dict: Calculated macros including calories, protein, carbs, and fats
    """
    # Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    if gender == 'Male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multiplier
    activity_multipliers = {
        'Sedentary (little or no exercise)': 1.2,
        'Lightly active (light exercise/sports 1-3 days/week)': 1.375,
        'Moderately active (moderate exercise/sports 3-5 days/week)': 1.55,
        'Very active (hard exercise/sports 6-7 days/week)': 1.725,
        'Extra active (very hard exercise, physical job or training twice a day)': 1.9
    }
    
    tdee = bmr * activity_multipliers[activity_level]
    
    # Adjust calories based on goal
    goal_adjustments = {
        'Muscle gain (bulk)': 1.15,  # 15% surplus
        'Recomposition (maintain weight)': 1.0,  # Maintenance
        'Lean bulk (slight surplus)': 1.10,  # 10% surplus
        'Moderate cut (fat loss)': 0.85,  # 15% deficit
        'Aggressive cut (rapid fat loss)': 0.75,  # 25% deficit
    }
    
    target_calories = tdee * goal_adjustments[goal]
    
    # Calculate macros based on goal
    if goal == 'Muscle gain (bulk)':
        protein_g_per_kg = 2.2  # Higher end for bulking
        fat_percentage = 0.25   # 25% of calories from fat
    elif goal == 'Recomposition (maintain weight)':
        protein_g_per_kg = 2.0  # Still high protein for recomp
        fat_percentage = 0.30   # Slightly higher fat for maintenance
    elif goal == 'Lean bulk (slight surplus)':
        protein_g_per_kg = 2.2  # Higher protein for lean gains
        fat_percentage = 0.25   # Moderate fat
    elif goal == 'Moderate cut (fat loss)':
        protein_g_per_kg = 2.3  # Higher protein to preserve muscle
        fat_percentage = 0.30   # Moderate fat for hormone production
    else:  # Aggressive cut
        protein_g_per_kg = 2.5  # Very high protein to preserve muscle
        fat_percentage = 0.25   # Lower but sufficient fat
    
    # Calculate macros in grams
    protein_g = weight_kg * protein_g_per_kg
    protein_calories = protein_g * 4
    
    fat_calories = target_calories * fat_percentage
    fat_g = fat_calories / 9
    
    remaining_calories = target_calories - protein_calories - fat_calories
    carbs_g = remaining_calories / 4
    
    # Ensure minimum carbs (at least 50g for brain function)
    if carbs_g < 50:
        carbs_g = 50
        carbs_calories = 50 * 4
        remaining_calories = target_calories - protein_calories - carbs_calories
        fat_g = remaining_calories / 9
    
    return {
        'calories': round(target_calories),
        'protein': round(protein_g),
        'carbs': round(carbs_g),
        'fats': round(fat_g)
    }

def create_pdf(user_data, macros):
    """
    Create a PDF report of the macronutrient calculations
    
    Parameters:
    user_data (dict): User information
    macros (dict): Calculated macronutrients
    
    Returns:
    BytesIO: PDF file as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    # Create content elements
    elements = []
    
    # Title
    elements.append(Paragraph("Personalized Fitness Nutrition Plan", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # User Information Section
    elements.append(Paragraph("User Information", subtitle_style))
    
    user_data_table = [
        ["Age", f"{user_data['age']} years"],
        ["Gender", user_data['gender']],
        ["Height", f"{user_data['height_cm']} cm"],
        ["Weight", f"{user_data['weight_kg']} kg"],
        ["Activity Level", user_data['activity_level']],
        ["Goal", user_data['goal']],
        ["Diet Preference", user_data['diet_preference']]
    ]
    
    t = Table(user_data_table, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.25*inch))
    
    # Macronutrient Section
    elements.append(Paragraph("Daily Macronutrient Targets", subtitle_style))
    
    macro_data = [
        ["Nutrient", "Amount", "Calories", "% of Total"],
        ["Calories", f"{macros['calories']} kcal", "-", "100%"],
        ["Protein", f"{macros['protein']} g", f"{macros['protein'] * 4} kcal", f"{round((macros['protein'] * 4) / macros['calories'] * 100)}%"],
        ["Carbohydrates", f"{macros['carbs']} g", f"{macros['carbs'] * 4} kcal", f"{round((macros['carbs'] * 4) / macros['calories'] * 100)}%"],
        ["Fats", f"{macros['fats']} g", f"{macros['fats'] * 9} kcal", f"{round((macros['fats'] * 9) / macros['calories'] * 100)}%"]
    ]
    
    t = Table(macro_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.25*inch))
    
    # Recommendations Section
    elements.append(Paragraph("Nutrition Recommendations", subtitle_style))
    
    # Determine if user is on cutting or bulking plan
    is_cutting = "cut" in user_data['goal'].lower()
    
    # Protein recommendations
    elements.append(Paragraph("Protein Recommendations:", header_style))
    if is_cutting:
        protein_text = (
            f"Aim for {macros['protein']}g daily. During cutting phases, higher protein intake is crucial to preserve "
            "muscle mass while in a caloric deficit. Distribute protein evenly throughout the day with 25-40g per meal. "
            "Focus on lean protein sources like chicken breast, white fish, egg whites, and low-fat dairy."
        )
    else:
        protein_text = (
            f"Aim for {macros['protein']}g daily. Protein is essential for muscle repair and growth. "
            "Distribute protein evenly throughout the day with 20-40g per meal. "
            "Include protein-rich foods like lean meats, fish, eggs, dairy, and plant-based proteins."
        )
    elements.append(Paragraph(protein_text, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Carb recommendations
    elements.append(Paragraph("Carbohydrate Recommendations:", header_style))
    if is_cutting:
        carb_text = (
            f"Aim for {macros['carbs']}g daily. During cutting, strategically time your carbohydrates around workouts "
            "when your body can utilize them most effectively. Include 20-40g before workouts and 20-40g after. "
            "Choose high-fiber, nutrient-dense carbs like vegetables, berries, and sweet potatoes to maximize satiety."
        )
    else:
        carb_text = (
            f"Aim for {macros['carbs']}g daily. Carbohydrates fuel your workouts and support recovery. "
            "Include more carbs around workout times with 30-60g before and after training. "
            "Choose a mix of complex carbs (whole grains, potatoes) and simpler carbs around workouts."
        )
    elements.append(Paragraph(carb_text, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Fat recommendations
    elements.append(Paragraph("Fat Recommendations:", header_style))
    if is_cutting:
        fat_text = (
            f"Aim for {macros['fats']}g daily. While reduced during cutting, maintain adequate fat intake "
            "to support hormone production and general health. Focus on quality sources like fatty fish, "
            "olive oil, avocados, and nuts in smaller portions."
        )
    else:
        fat_text = (
            f"Aim for {macros['fats']}g daily. Healthy fats support hormone production and overall health. "
            "Include sources like olive oil, nuts, seeds, avocados, and fatty fish. "
            "Keep fat intake lower immediately before and after workouts."
        )
    elements.append(Paragraph(fat_text, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add Meal Plan Section
    elements.append(Paragraph("Sample Meal Plan", subtitle_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Determine if user is on cutting or bulking plan
    is_cutting = "cut" in user_data['goal'].lower()
    
    if is_cutting:
        if user_data['diet_preference'] == "Non-Vegetarian":
            if user_data['protein_supplement'] == "Yes":
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 5 egg whites + 1 whole egg scrambled\n" +
                     "• 1/2 cup oatmeal with cinnamon and stevia\n" +
                     "• 1/2 cup berries"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup fat-free Greek yogurt\n" +
                     "• 1/2 cup berries\n" +
                     "• 5 almonds"],
                    ["1:00 PM", "Lunch", 
                     "• 150g grilled chicken breast\n" +
                     "• 100g (uncooked weight) brown rice or 150g sweet potato\n" +
                     "• 2 cups mixed green vegetables\n" +
                     "• 1 tsp olive oil for dressing"],
                    ["3:30 PM", "Pre-Workout", 
                     "• Protein shake with 1 scoop whey protein\n" +
                     "• 1 small apple or banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• Protein shake with 1 scoop whey protein\n" +
                     "• 25g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 150g white fish or lean beef\n" +
                     "• Large salad with mixed vegetables\n" +
                     "• 1 tbsp olive oil + vinegar dressing\n" +
                     "• 100g sweet potato (only on training days)"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese OR casein protein shake\n" +
                     "• 1/2 tbsp natural almond butter"]
                ]
            else:
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 6 egg whites + 1 whole egg scrambled\n" +
                     "• 1/2 cup oatmeal with cinnamon and stevia\n" +
                     "• 1/2 cup berries"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup fat-free Greek yogurt\n" +
                     "• 1/2 cup berries\n" +
                     "• 5 almonds"],
                    ["1:00 PM", "Lunch", 
                     "• 200g grilled chicken breast\n" +
                     "• 100g (uncooked weight) brown rice or 150g sweet potato\n" +
                     "• 2 cups mixed green vegetables\n" +
                     "• 1 tsp olive oil for dressing"],
                    ["3:30 PM", "Pre-Workout", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 small apple or banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• 1 cup Greek yogurt\n" +
                     "• 25g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 200g white fish or lean beef\n" +
                     "• Large salad with mixed vegetables\n" +
                     "• 1 tbsp olive oil + vinegar dressing\n" +
                     "• 100g sweet potato (only on training days)"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1/2 tbsp natural almond butter"]
                ]
        else:
            if user_data['protein_supplement'] == "Yes":
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 5 egg whites + 1 whole egg scrambled (or tofu scramble)\n" +
                     "• 1/2 cup oatmeal with cinnamon and stevia\n" +
                     "• 1/2 cup berries"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup fat-free Greek yogurt\n" +
                     "• 1/2 cup berries\n" +
                     "• 5 almonds"],
                    ["1:00 PM", "Lunch", 
                     "• 150g grilled tofu or tempeh\n" +
                     "• 100g (uncooked weight) brown rice or 150g sweet potato\n" +
                     "• 2 cups mixed green vegetables\n" +
                     "• 1 tsp olive oil for dressing"],
                    ["3:30 PM", "Pre-Workout", 
                     "• Plant-based protein shake\n" +
                     "• 1 small apple or banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• Plant-based protein shake\n" +
                     "• 25g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 150g grilled tofu or seitan\n" +
                     "• Large salad with mixed vegetables\n" +
                     "• 1 tbsp olive oil + vinegar dressing\n" +
                     "• 100g sweet potato (only on training days)"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese OR casein protein shake\n" +
                     "• 1/2 tbsp natural almond butter"]
                ]
            else:
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 6 egg whites + 1 whole egg scrambled (or tofu scramble)\n" +
                     "• 1/2 cup oatmeal with cinnamon and stevia\n" +
                     "• 1/2 cup berries"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup fat-free Greek yogurt\n" +
                     "• 1/2 cup berries\n" +
                     "• 5 almonds"],
                    ["1:00 PM", "Lunch", 
                     "• 200g grilled tofu or tempeh\n" +
                     "• 100g (uncooked weight) brown rice or 150g sweet potato\n" +
                     "• 2 cups mixed green vegetables\n" +
                     "• 1 tsp olive oil for dressing"],
                    ["3:30 PM", "Pre-Workout", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 small apple or banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• 1 cup Greek yogurt\n" +
                     "• 40g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 200g grilled tofu or seitan\n" +
                     "• Large salad with mixed vegetables\n" +
                     "• 1 tbsp olive oil + vinegar dressing\n" +
                     "• 100g sweet potato (only on training days)"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1/2 tbsp natural almond butter"]
                ]
    else:
        if user_data['diet_preference'] == "Non-Vegetarian":
            if user_data['protein_supplement'] == "Yes":
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 4 egg whites + 1 whole egg scrambled\n" +
                     "• 1 cup oatmeal with berries and 1 tbsp honey\n" +
                     "• 1 medium banana"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup Greek yogurt\n" +
                     "• 1 handful of almonds\n" +
                     "• 1 apple"],
                    ["1:00 PM", "Lunch", 
                     "• 150g chicken breast\n" +
                     "• 1 cup brown rice\n" +
                     "• 1 cup mixed vegetables\n" +
                     "• 1 tbsp olive oil for cooking"],
                    ["3:30 PM", "Pre-Workout", 
                     "• Protein shake with 1 scoop whey protein\n" +
                     "• 1 banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• Protein shake with 1 scoop whey protein\n" +
                     "• 40g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 150g salmon or lean beef\n" +
                     "• 200g sweet potato\n" +
                     "• 2 cups mixed vegetables\n" +
                     "• 1 tbsp olive oil"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 tbsp natural peanut butter"]
                ]
            else:
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 5 egg whites + 1 whole egg scrambled\n" +
                     "• 1 cup oatmeal with berries and 1 tbsp honey\n" +
                     "• 1 medium banana"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup Greek yogurt\n" +
                     "• 1 handful of almonds\n" +
                     "• 1 apple"],
                    ["1:00 PM", "Lunch", 
                     "• 200g chicken breast\n" +
                     "• 1 cup brown rice\n" +
                     "• 1 cup mixed vegetables\n" +
                     "• 1 tbsp olive oil for cooking"],
                    ["3:30 PM", "Pre-Workout", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• 1 cup Greek yogurt\n" +
                     "• 40g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 200g salmon or lean beef\n" +
                     "• 200g sweet potato\n" +
                     "• 2 cups mixed vegetables\n" +
                     "• 1 tbsp olive oil"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 tbsp natural peanut butter"]
                ]
        else:
            if user_data['protein_supplement'] == "Yes":
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 4 egg whites + 1 whole egg scrambled (or tofu scramble)\n" +
                     "• 1 cup oatmeal with berries and 1 tbsp honey\n" +
                     "• 1 medium banana"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup Greek yogurt\n" +
                     "• 1 handful of almonds\n" +
                     "• 1 apple"],
                    ["1:00 PM", "Lunch", 
                     "• 150g grilled tofu or tempeh\n" +
                     "• 1 cup brown rice\n" +
                     "• 1 cup mixed vegetables\n" +
                     "• 1 tbsp olive oil for cooking"],
                    ["3:30 PM", "Pre-Workout", 
                     "• Plant-based protein shake\n" +
                     "• 1 banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• Plant-based protein shake\n" +
                     "• 40g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 150g grilled tofu or seitan\n" +
                     "• 200g sweet potato\n" +
                     "• 2 cups mixed vegetables\n" +
                     "• 1 tbsp olive oil"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 tbsp natural peanut butter"]
                ]
            else:
                meal_plan_data = [
                    ["Time", "Meal", "Food Items"],
                    ["7:00 AM", "Breakfast", 
                     "• 5 egg whites + 1 whole egg scrambled (or tofu scramble)\n" +
                     "• 1 cup oatmeal with berries and 1 tbsp honey\n" +
                     "• 1 medium banana"],
                    ["10:00 AM", "Mid-Morning Snack", 
                     "• 1 cup Greek yogurt\n" +
                     "• 1 handful of almonds\n" +
                     "• 1 apple"],
                    ["1:00 PM", "Lunch", 
                     "• 200g grilled tofu or tempeh\n" +
                     "• 1 cup brown rice\n" +
                     "• 1 cup mixed vegetables\n" +
                     "• 1 tbsp olive oil for cooking"],
                    ["3:30 PM", "Pre-Workout", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 banana"],
                    ["5:30 PM", "Post-Workout", 
                     "• 1 cup Greek yogurt\n" +
                     "• 40g fast-digesting carbs (sports drink or white rice)"],
                    ["7:00 PM", "Dinner", 
                     "• 200g grilled tofu or seitan\n" +
                     "• 200g sweet potato\n" +
                     "• 2 cups mixed vegetables\n" +
                     "• 1 tbsp olive oil"],
                    ["9:00 PM", "Evening Snack (Optional)", 
                     "• 1 cup cottage cheese\n" +
                     "• 1 tbsp natural peanut butter"]
                ]
    
    # Create and style the meal plan table
    t = Table(meal_plan_data, colWidths=[1*inch, 1.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 0.25*inch))
    
    # Footer
    footer_text = (
        "This plan is based on general formulas and may need adjustment based on your individual response. "
        "Monitor your progress and adjust as needed. For personalized guidance, consider consulting with a "
        "registered dietitian or nutrition professional."
    )
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def get_download_link(buffer, filename, text):
    """
    Generate a link to download the PDF file
    
    Parameters:
    buffer (BytesIO): PDF file as bytes
    filename (str): Name of the file to download
    text (str): Text to display as the download link
    
    Returns:
    str: HTML link to download the PDF
    """
    pdf_bytes = buffer.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{text}</a>'

def create_macro_chart(macros):
    """
    Create a pie chart showing macro distribution
    
    Parameters:
    macros (dict): Calculated macronutrients
    
    Returns:
    plotly.graph_objects.Figure: Pie chart figure
    """
    macro_data = {
        'Macro': ['Protein', 'Carbohydrates', 'Fats'],
        'Calories': [
            macros['protein'] * 4,
            macros['carbs'] * 4,
            macros['fats'] * 9
        ],
        'Color': ['#FF6B6B', '#4ECDC4', '#45B7D1']
    }
    
    fig = px.pie(
        macro_data,
        values='Calories',
        names='Macro',
        color='Color',
        color_discrete_map={
            'Protein': '#FF6B6B',
            'Carbohydrates': '#4ECDC4',
            'Fats': '#45B7D1'
        },
        title='Daily Calorie Distribution by Macronutrients',
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_progress_gauge(current_weight, target_weight, goal):
    """
    Create a gauge chart showing progress towards goal
    
    Parameters:
    current_weight (float): Current weight
    target_weight (float): Target weight
    goal (str): Fitness goal
    
    Returns:
    plotly.graph_objects.Figure: Gauge chart figure
    """
    if "cut" in goal.lower():
        # For cutting, progress is weight loss
        progress = max(0, min(100, (current_weight - target_weight) / current_weight * 100))
        title = "Weight Loss Progress"
        color = "red"
    else:
        # For bulking, progress is weight gain
        progress = max(0, min(100, (target_weight - current_weight) / current_weight * 100))
        title = "Weight Gain Progress"
        color = "green"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 0},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 50], 'color': "gray"},
                {'range': [50, 75], 'color': "darkgray"},
                {'range': [75, 100], 'color': color}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': progress
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_meal_timing_chart():
    """
    Create a timeline chart showing optimal meal timing
    
    Returns:
    plotly.graph_objects.Figure: Timeline chart
    """
    meal_data = {
        'Time': ['7:00 AM', '10:00 AM', '1:00 PM', '3:30 PM', '5:30 PM', '7:00 PM', '9:00 PM'],
        'Meal': ['Breakfast', 'Snack', 'Lunch', 'Pre-Workout', 'Post-Workout', 'Dinner', 'Evening Snack'],
        'Protein': [25, 15, 30, 20, 25, 30, 15],
        'Carbs': [30, 15, 40, 25, 40, 35, 10],
        'Fats': [10, 8, 12, 5, 5, 15, 8]
    }
    
    fig = go.Figure()
    
    # Add protein bars
    fig.add_trace(go.Bar(
        name='Protein',
        x=meal_data['Time'],
        y=meal_data['Protein'],
        marker_color='#FF6B6B',
        opacity=0.8
    ))
    
    # Add carbs bars
    fig.add_trace(go.Bar(
        name='Carbs',
        x=meal_data['Time'],
        y=meal_data['Carbs'],
        marker_color='#4ECDC4',
        opacity=0.8
    ))
    
    # Add fats bars
    fig.add_trace(go.Bar(
        name='Fats',
        x=meal_data['Time'],
        y=meal_data['Fats'],
        marker_color='#45B7D1',
        opacity=0.8
    ))
    
    fig.update_layout(
        title='Optimal Meal Timing and Macro Distribution',
        barmode='stack',
        height=400,
        xaxis_title='Time of Day',
        yaxis_title='Macro Amount (g)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def main():
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🏋️‍♂️ Fitness Macronutrient Calculator</h1>
        <p>Get personalized nutrition recommendations for muscle building or cutting</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add fitness icons and description
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>💪 Muscle Building</h3>
            <p>Optimize your nutrition for maximum gains</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>🔥 Fat Loss</h3>
            <p>Strategic cutting for lean results</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>⚖️ Recomposition</h3>
            <p>Transform your body composition</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Personal Information")
        age = st.number_input("🎂 Age (years)", min_value=16, max_value=100, value=30)
        gender = st.selectbox("👥 Gender", options=["Male", "Female"])
        height_cm = st.number_input("📏 Height (cm)", min_value=120, max_value=250, value=175)
    
    with col2:
        st.markdown("### 🎯 Goals & Preferences")
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=40, max_value=200, value=75)
        activity_level = st.selectbox(
            "🏃‍♂️ Activity Level",
            options=[
                "Sedentary (little or no exercise)",
                "Lightly active (light exercise/sports 1-3 days/week)",
                "Moderately active (moderate exercise/sports 3-5 days/week)",
                "Very active (hard exercise/sports 6-7 days/week)",
                "Extra active (very hard exercise, physical job or training twice a day)"
            ],
            index=2
        )
        goal = st.selectbox(
            "🎯 Goal",
            options=[
                "Muscle gain (bulk)",
                "Lean bulk (slight surplus)",
                "Recomposition (maintain weight)",
                "Moderate cut (fat loss)",
                "Aggressive cut (rapid fat loss)"
            ],
            index=1
        )
        diet_preference = st.selectbox(
            "🥗 Diet Preference",
            options=["Non-Vegetarian", "Vegetarian"],
            index=0
        )
        protein_supplement = st.selectbox(
            "💊 Include Protein Supplements?",
            options=["Yes", "No"],
            index=0
        )
    
    if st.button("Calculate My Macros", help="Click to generate your personalized nutrition plan"):
        macros = calculate_macros(age, gender, weight_kg, height_cm, activity_level, goal)
        
        # Success animation and header
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 2rem 0;">
            <h1>🎯 Your Personalized Nutrition Plan</h1>
            <p>Based on your unique profile and goals</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display macros in styled cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #667eea; text-align: center;">🔥 Calories</h3>
                <h2 style="text-align: center; color: #2c3e50;">{macros['calories']}</h2>
                <p style="text-align: center; color: #7f8c8d;">kcal/day</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #e74c3c; text-align: center;">💪 Protein</h3>
                <h2 style="text-align: center; color: #2c3e50;">{macros['protein']}g</h2>
                <p style="text-align: center; color: #7f8c8d;">{(macros['protein'] * 4) / macros['calories'] * 100:.1f}% of calories</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #27ae60; text-align: center;">🌾 Carbs</h3>
                <h2 style="text-align: center; color: #2c3e50;">{macros['carbs']}g</h2>
                <p style="text-align: center; color: #7f8c8d;">{(macros['carbs'] * 4) / macros['calories'] * 100:.1f}% of calories</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #f39c12; text-align: center;">🥑 Fats</h3>
                <h2 style="text-align: center; color: #2c3e50;">{macros['fats']}g</h2>
                <p style="text-align: center; color: #7f8c8d;">{(macros['fats'] * 9) / macros['calories'] * 100:.1f}% of calories</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Create a dataframe for the detailed breakdown
        macro_percentages = {
            "Nutrient": ["Protein", "Carbohydrates", "Fats"],
            "Grams": [macros['protein'], macros['carbs'], macros['fats']],
            "Calories": [
                macros['protein'] * 4,
                macros['carbs'] * 4,
                macros['fats'] * 9
            ],
            "% of Total Calories": [
                round((macros['protein'] * 4) / macros['calories'] * 100),
                round((macros['carbs'] * 4) / macros['calories'] * 100),
                round((macros['fats'] * 9) / macros['calories'] * 100)
            ]
        }
        
        df = pd.DataFrame(macro_percentages)
        st.table(df)
        
        # Add macro distribution chart
        st.markdown("### 📊 Macro Distribution Visualization")
        macro_chart = create_macro_chart(macros)
        st.plotly_chart(macro_chart, use_container_width=True)
        
        # Add meal timing chart
        st.markdown("### ⏰ Optimal Meal Timing")
        meal_chart = create_meal_timing_chart()
        st.plotly_chart(meal_chart, use_container_width=True)
        
        # Prepare PDF export
        user_data = {
            'age': age,
            'gender': gender,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'activity_level': activity_level,
            'goal': goal,
            'diet_preference': diet_preference,
            'protein_supplement': protein_supplement
        }
        
        pdf_buffer = create_pdf(user_data, macros)
        
        # Create download button
        st.markdown(
            get_download_link(
                pdf_buffer, 
                "fitness_nutrition_plan.pdf", 
                "📥 Download Nutrition Plan as PDF"
            ), 
            unsafe_allow_html=True
        )
        
        # Determine if user is on cutting or bulking plan
        is_cutting = "cut" in goal.lower()
        
        # Detailed recommendations section with icons
        if is_cutting:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); border-radius: 10px; color: white; margin: 2rem 0;">
                <h1>🔥 Cutting & Fat Loss Nutrition Guide</h1>
                <p>Strategic nutrition for maximum fat loss while preserving muscle</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-radius: 10px; color: white; margin: 2rem 0;">
                <h1>💪 Muscle Building Nutrition Guide</h1>
                <p>Optimize your nutrition for maximum muscle growth and strength gains</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("💪 Protein Recommendations", expanded=True):
            if is_cutting:
                st.write(f"""
                ### Daily Protein Target: {macros['protein']}g
                
                **Why this matters for cutting:** Higher protein intake is crucial during a caloric deficit to preserve lean muscle mass while losing fat. Research shows elevated protein needs during caloric restriction.
                
                **Optimal timing:**
                - 25-40g protein per meal, spaced evenly throughout the day (4-5 meals)
                - Include 25-30g of protein within 1-2 hours before and after workouts
                - Consider casein protein before bed to reduce muscle breakdown during overnight fasting
                
                **Best sources:**
                - Lean meats: chicken breast (31g per 100g), turkey (29g per 100g)
                - White fish: cod (20g per 100g), tilapia (26g per 100g)
                - Egg whites (11g per 100g)
                - Low-fat dairy: Greek yogurt (10g per 100g), cottage cheese (11g per 100g)
                - Plant-based: tofu (8g per 100g), tempeh (19g per 100g), protein powder supplements
                """)
            else:
                st.write(f"""
                ### Daily Protein Target: {macros['protein']}g
                
                **Why this matters:** Protein is the building block of muscle tissue. Consuming adequate protein (especially leucine-rich sources) helps stimulate muscle protein synthesis.
                
                **Optimal timing:**
                - 20-40g protein per meal, evenly distributed throughout the day
                - Include a protein source within 1-2 hours before and after workouts
                
                **Best sources:**
                - Lean meats: chicken breast (31g per 100g), turkey (29g per 100g)
                - Fish: tuna (30g per 100g), salmon (25g per 100g)
                - Dairy: Greek yogurt (10g per 100g), cottage cheese (11g per 100g)
                - Eggs: whole eggs (6g per egg)
                - Plant-based: tofu (8g per 100g), lentils (9g per 100g), protein powder supplements
                """)
        
        with st.expander("🌾 Carbohydrate Recommendations"):
            if is_cutting:
                st.write(f"""
                ### Daily Carbohydrate Target: {macros['carbs']}g
                
                **Why this matters for cutting:** Carbohydrates are strategically reduced during cutting phases, but still important to fuel workouts and recovery. Lower carb intake helps create a caloric deficit while maintaining training performance.
                
                **Optimal timing:**
                - Prioritize carbs around workout times
                - Consume 20-40g of carbs with protein 1-2 hours before workouts
                - Include 20-40g fast-digesting carbs after workouts along with protein
                - Reduce carbs in meals further from workout times
                
                **Best sources:**
                - Complex carbs: oats, sweet potatoes, quinoa, vegetables
                - Low glycemic fruits: berries, apples, pears
                - Vegetables (unlimited leafy greens and fibrous veggies)
                - Around workouts: white rice, sports drinks, fruit (faster digestion)
                
                **Pro tip:** Focus on high-fiber, low-calorie carb sources to increase satiety during your caloric deficit.
                """)
            else:
                st.write(f"""
                ### Daily Carbohydrate Target: {macros['carbs']}g
                
                **Why this matters:** Carbohydrates are your body's primary energy source for high-intensity training. They replenish muscle glycogen stores, which fuels your workouts and supports recovery.
                
                **Optimal timing:**
                - Higher carb intake around workouts
                - Include 30-60g of carbs in your pre-workout meal (1-3 hours before)
                - Consume 30-60g of carbs with protein after workouts for optimal recovery
                
                **Best sources:**
                - Complex carbs: oats, brown rice, sweet potatoes, quinoa, whole grain pasta
                - Fruits: bananas, berries, apples
                - Starchy vegetables: potatoes, corn, peas
                - Simple carbs (best around workouts): white rice, sports drinks, fruit juice
                """)
        
        with st.expander("🥑 Fat Recommendations"):
            if is_cutting:
                st.write(f"""
                ### Daily Fat Target: {macros['fats']}g
                
                **Why this matters for cutting:** While reduced during a cutting phase, adequate fat intake remains essential for hormone production (especially testosterone), which helps preserve muscle mass during caloric restriction.
                
                **Optimal timing:**
                - Distribute throughout the day in smaller amounts
                - Lower fat intake immediately before and after workouts (focus on protein and carbs then)
                - Include some fat at meals further from workout times
                
                **Best sources:**
                - Healthy oils: olive oil (use sparingly, measure by teaspoon)
                - Fatty fish: salmon, mackerel (excellent omega-3 sources)
                - Avocado (1/4 to 1/2 depending on your fat target)
                - Nuts and seeds in moderation (almonds, walnuts, chia seeds)
                - Whole eggs (mix with egg whites for higher protein, lower fat)
                - Avoid trans fats and limit saturated fats
                """)
            else:
                st.write(f"""
                ### Daily Fat Target: {macros['fats']}g
                
                **Why this matters:** Dietary fats support hormone production (including testosterone), provide essential fatty acids, and help with vitamin absorption.
                
                **Optimal timing:**
                - Distribute throughout the day
                - Lower fat intake immediately before and after workouts to optimize carb and protein absorption
                
                **Best sources:**
                - Healthy oils: olive oil, avocado oil
                - Nuts and seeds: almonds, walnuts, flaxseeds
                - Fatty fish: salmon, mackerel (omega-3 sources)
                - Avocados
                - Eggs (yolks)
                - Limit saturated and trans fats
                """)
        
        with st.expander("🍽️ Sample Meal Plan"):
            if is_cutting:
                if diet_preference == "Non-Vegetarian":
                    st.write(f"""
                    ### Sample Daily Cutting Meal Plan for {macros['calories']} calories (Non-Vegetarian)
                    
                    **Breakfast (7:00 AM)**
                    - 5 egg whites + 1 whole egg scrambled
                    - 1/2 cup oatmeal with cinnamon and stevia
                    - 1/2 cup berries
                    
                    **Mid-Morning Snack (10:00 AM)**
                    - 1 cup fat-free Greek yogurt
                    - 1/2 cup berries
                    - 5 almonds
                    
                    **Lunch (1:00 PM)**
                    - 150g grilled chicken breast
                    - 100g (uncooked weight) brown rice or 150g sweet potato
                    - 2 cups mixed green vegetables
                    - 1 tsp olive oil for dressing
                    
                    **Pre-Workout (3:30 PM)**
                    - Protein shake with 1 scoop whey protein
                    - 1 small apple or banana
                    
                    **Post-Workout (5:30 PM)**
                    - Protein shake with 1 scoop whey protein
                    - 25g fast-digesting carbs (sports drink or white rice)
                    
                    **Dinner (7:00 PM)**
                    - 150g white fish or lean beef
                    - Large salad with mixed vegetables
                    - 1 tbsp olive oil + vinegar dressing
                    - 100g sweet potato (only on training days)
                    
                    **Evening Snack (9:00 PM) - Optional**
                    - 1 cup cottage cheese OR casein protein shake
                    - 1/2 tbsp natural almond butter
                    """)
                else:
                    st.write(f"""
                    ### Sample Daily Cutting Meal Plan for {macros['calories']} calories (Vegetarian)
                    
                    **Breakfast (7:00 AM)**
                    - 5 egg whites + 1 whole egg scrambled (or tofu scramble)
                    - 1/2 cup oatmeal with cinnamon and stevia
                    - 1/2 cup berries
                    
                    **Mid-Morning Snack (10:00 AM)**
                    - 1 cup fat-free Greek yogurt
                    - 1/2 cup berries
                    - 5 almonds
                    
                    **Lunch (1:00 PM)**
                    - 150g grilled tofu or tempeh
                    - 100g (uncooked weight) brown rice or 150g sweet potato
                    - 2 cups mixed green vegetables
                    - 1 tsp olive oil for dressing
                    
                    **Pre-Workout (3:30 PM)**
                    - Plant-based protein shake
                    - 1 small apple or banana
                    
                    **Post-Workout (5:30 PM)**
                    - Plant-based protein shake
                    - 25g fast-digesting carbs (sports drink or white rice)
                    
                    **Dinner (7:00 PM)**
                    - 150g grilled tofu or seitan
                    - Large salad with mixed vegetables
                    - 1 tbsp olive oil + vinegar dressing
                    - 100g sweet potato (only on training days)
                    
                    **Evening Snack (9:00 PM) - Optional**
                    - 1 cup cottage cheese OR casein protein shake
                    - 1/2 tbsp natural almond butter
                    """)
            else:
                if diet_preference == "Non-Vegetarian":
                    st.write(f"""
                    ### Sample Daily Muscle Building Meal Plan for {macros['calories']} calories (Non-Vegetarian)
                    
                    **Breakfast (7:00 AM)**
                    - 4 egg whites + 1 whole egg scrambled
                    - 1 cup oatmeal with berries and 1 tbsp honey
                    - 1 medium banana
                    
                    **Mid-Morning Snack (10:00 AM)**
                    - 1 cup Greek yogurt
                    - 1 handful of almonds
                    - 1 apple
                    
                    **Lunch (1:00 PM)**
                    - 150g chicken breast
                    - 1 cup brown rice
                    - 1 cup mixed vegetables
                    - 1 tbsp olive oil for cooking
                    
                    **Pre-Workout (3:30 PM)**
                    - Protein shake with 1 scoop whey protein
                    - 1 banana
                    
                    **Post-Workout (5:30 PM)**
                    - Protein shake with 1 scoop whey protein
                    - 40g fast-digesting carbs (sports drink or white rice)
                    
                    **Dinner (7:00 PM)**
                    - 150g salmon or lean beef
                    - 200g sweet potato
                    - 2 cups mixed vegetables
                    - 1 tbsp olive oil
                    
                    **Evening Snack (9:00 PM) - Optional**
                    - 1 cup cottage cheese
                    - 1 tbsp natural peanut butter
                    """)
                else:
                    st.write(f"""
                    ### Sample Daily Muscle Building Meal Plan for {macros['calories']} calories (Vegetarian)
                    
                    **Breakfast (7:00 AM)**
                    - 4 egg whites + 1 whole egg scrambled (or tofu scramble)
                    - 1 cup oatmeal with berries and 1 tbsp honey
                    - 1 medium banana
                    
                    **Mid-Morning Snack (10:00 AM)**
                    - 1 cup Greek yogurt
                    - 1 handful of almonds
                    - 1 apple
                    
                    **Lunch (1:00 PM)**
                    - 150g grilled tofu or tempeh
                    - 1 cup brown rice
                    - 1 cup mixed vegetables
                    - 1 tbsp olive oil for cooking
                    
                    **Pre-Workout (3:30 PM)**
                    - Plant-based protein shake
                    - 1 banana
                    
                    **Post-Workout (5:30 PM)**
                    - Plant-based protein shake
                    - 40g fast-digesting carbs (sports drink or white rice)
                    
                    **Dinner (7:00 PM)**
                    - 150g grilled tofu or seitan
                    - 200g sweet potato
                    - 2 cups mixed vegetables
                    - 1 tbsp olive oil
                    
                    **Evening Snack (9:00 PM) - Optional**
                    - 1 cup cottage cheese
                    - 1 tbsp natural peanut butter
                    """)
        
        if is_cutting:
            with st.expander("🎯 Cutting Tips & Strategies"):
                st.write("""
                ### Effective Cutting Strategies
                
                **1. Gradual Caloric Deficit**
                - Start with a moderate 15-20% deficit from maintenance calories
                - Adjust every 2-3 weeks based on progress (aim for 0.5-1% body weight loss per week)
                - Consider diet breaks every 4-6 weeks at maintenance calories to reset hormones
                
                **2. Training Modifications**
                - Maintain or slightly increase training volume to preserve muscle
                - Focus on compound movements with moderate-to-heavy weights (70-85% 1RM)
                - Add strategic cardio: 2-3 HIIT sessions (20-30 min) and 2-3 LISS sessions (30-45 min)
                
                **3. Diet Strategies**
                - Increase protein intake as shown in your plan (helps preserve muscle and increases satiety)
                - Focus on high-volume, low-calorie foods (vegetable soups, salads, etc.)
                - Implement nutrient timing (carbs around workouts)
                - Consider intermittent fasting if it suits your schedule (16:8 protocol)
                
                **4. Recovery & Monitoring**
                - Prioritize 7-9 hours of sleep (critical for fat loss and muscle preservation)
                - Track progress with photos, measurements, and weight (weekly averages)
                - Watch for signs of overtraining: excessive fatigue, decreased performance, poor sleep
                
                **5. Supplement Considerations**
                - Protein powder (whey/casein)
                - Creatine monohydrate (5g daily)
                - Caffeine pre-workout (100-200mg)
                - Fish oil (1-3g EPA/DHA)
                - Fiber supplements
                """)
                
        # Add progress tracking section
        st.markdown("### 📈 Progress Tracking")
        st.markdown("Track your progress towards your fitness goals:")
        
        # Add target weight input for progress tracking
        col1, col2 = st.columns(2)
        with col1:
            target_weight = st.number_input("Target Weight (kg)", min_value=40.0, max_value=200.0, value=weight_kg, step=0.5)
        
        with col2:
            if st.button("Update Progress Chart"):
                progress_chart = create_progress_gauge(weight_kg, target_weight, goal)
                st.plotly_chart(progress_chart, use_container_width=True)
        
        # Add motivational section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 2rem 0;">
            <h2>🚀 Ready to Transform Your Body?</h2>
            <p>Consistency is key! Stick to your nutrition plan and training routine for the best results.</p>
            <p><strong>Remember:</strong> Progress takes time, but every day you follow your plan brings you closer to your goals!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add tips section with icons
        st.markdown("### 💡 Quick Tips for Success")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #667eea;">
                <h4>📱 Track Your Food</h4>
                <p>Use a food tracking app to monitor your daily intake</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #27ae60;">
                <h4>💧 Stay Hydrated</h4>
                <p>Aim for 8-10 glasses of water daily</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #f39c12;">
                <h4>😴 Get Enough Sleep</h4>
                <p>7-9 hours of quality sleep is crucial for results</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.warning("Note: This calculator provides estimates based on general formulas. Individual needs may vary based on genetics, training intensity, and specific body composition goals. Consider consulting with a registered dietitian for personalized guidance.")

if __name__ == "__main__":
    main()