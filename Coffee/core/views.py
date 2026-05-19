import os
import joblib
import pandas as pd
import json
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render, redirect
from core.models import PredictionInput

# Dynamically find the paths to your .pkl files
MODEL1_PATH = os.path.join(settings.BASE_DIR, 'core', 'ml_models', 'model1_demand_forecast.pkl')
MODEL2_PATH = os.path.join(settings.BASE_DIR, 'core', 'ml_models', 'model2_revenue_forecast.pkl')
MODEL3_PATH = os.path.join(settings.BASE_DIR, 'core', 'ml_models', 'model3_inventory_forecast.pkl')

# Load the models once when the server starts
def load_model(path):
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"Error loading model from {path}: {e}")
        return None

model1_demand = load_model(MODEL1_PATH)
model2_revenue = load_model(MODEL2_PATH)
model3_inventory = load_model(MODEL3_PATH)

def predict_coffee(request):
    # --- POST handling for preview and save actions ---
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'preview':
            # Store form data in the session for previewing
            request.session['temp_input'] = {
                'target_date': request.POST.get('target_date'),
                'store_location': request.POST.get('store_location'),
                'shift': request.POST.get('shift'),
                'prev_cups': request.POST.get('prev_cups'),
                'prev_revenue': request.POST.get('prev_revenue'),
            }
            # Use Post/Redirect/Get pattern to show the preview
            return redirect('temp_dashboard')
        
        elif action == 'save':
            temp_input = request.session.get('temp_input')
            if temp_input:
                try:
                    # Save the data from the session to the database
                    PredictionInput.objects.create(
                        target_date=temp_input.get('target_date'),
                        store_location=temp_input.get('store_location'),
                        shift=temp_input.get('shift'),
                        prev_cups=float(temp_input.get('prev_cups', 0)),
                        prev_revenue=float(temp_input.get('prev_revenue', 0))
                    )
                    # Important: Clear the session variable after saving
                    del request.session['temp_input']
                except Exception as e:
                    # Optionally, use Django's messages framework to show an error
                    print(f"Error saving previewed data: {e}")
                    pass
            # Redirect to see the final saved state (without the preview)
            return redirect('temp_dashboard')
        
        elif action == 'reset':
            if 'temp_input' in request.session:
                del request.session['temp_input']
            return redirect('temp_dashboard')

    # --- GET handling (for both normal load and preview states) ---
    
    import re
    branches_list = ['Astoria', 'Lower Manhattan', "Hell's Kitchen"]
    shifts_list = ['Morning', 'Afternoon', 'Evening']
    
    branches = [{'name': b, 'slug': re.sub(r'[^a-z0-9]+', '-', b.lower()).strip('-')} for b in branches_list]
    shifts = [{'name': s, 'slug': s.lower()} for s in shifts_list]
    
    inventory_labels = ['Bakery', 'Branded', 'Coffee', 'Coffee beans', 'Drinking Chocolate', 'Flavours', 'Loose Tea', 'Packaged Chocolate', 'Tea']
    if model3_inventory and hasattr(model3_inventory, 'target_names'):
        inventory_labels = list(model3_inventory.target_names)
    elif model3_inventory and hasattr(model3_inventory, 'classes_'):
        inventory_labels = list(model3_inventory.classes_)
    
    dashboard_data = []
    temp_input_data = request.session.get('temp_input')
    
    for b in branches:
        for s in shifts:
            branch_name = b['name']
            shift_name = s['name']
            
            input_source = None
            is_stale = True
            is_previewing_this_card = False

            # Check if we are in a preview state for the current branch/shift
            if temp_input_data and temp_input_data.get('store_location') == branch_name and temp_input_data.get('shift') == shift_name:
                input_source = temp_input_data
                is_stale = False # A preview is never stale
                is_previewing_this_card = True
            else:
                # If not previewing this specific card, use the latest data from the DB
                latest_input_from_db = PredictionInput.objects.filter(store_location=branch_name, shift=shift_name).order_by('-created_at').first()
                if latest_input_from_db:
                    # Check staleness from DB object
                    if (datetime.now().date() - latest_input_from_db.target_date).days < 2:
                        is_stale = False
                    
                    # Create a dictionary from the model object to use as the input_source
                    input_source = {
                        'target_date': latest_input_from_db.target_date,
                        'store_location': latest_input_from_db.store_location,
                        'shift': latest_input_from_db.shift,
                        'prev_cups': latest_input_from_db.prev_cups,
                        'prev_revenue': latest_input_from_db.prev_revenue,
                    }
            
            prediction_demand = None
            prediction_revenue = None
            prediction_inventory = None
            input_summary = None
            inventory_data = [320, 250, 210, 180, 150, 140, 110, 90, 80] # default fallback
            
            if input_source:
                # --- Prediction Logic ---
                date_str_or_obj = input_source.get('target_date')
                if isinstance(date_str_or_obj, str):
                    date_obj = datetime.strptime(date_str_or_obj, '%Y-%m-%d').date()
                else:
                    date_obj = date_str_or_obj
                
                input_summary = {
                    'target_date': date_obj.strftime('%Y-%m-%d'),
                    'store_location': input_source.get('store_location'),
                    'shift': input_source.get('shift'),
                    'prev_cups': float(input_source.get('prev_cups', 0)),
                    'prev_revenue': float(input_source.get('prev_revenue', 0))
                }
                
                day_of_week = date_obj.weekday()
                month = date_obj.month
                is_weekend = 1 if day_of_week >= 5 else 0
                day_name = date_obj.strftime('%A')

                current_input_data = {
                    'store_location': str(input_summary['store_location']),
                    'shift': str(input_summary['shift']),
                    'month': int(month),
                    'day_of_week': day_name,
                    'is_weekend': int(is_weekend),
                    'prev_cups': float(input_summary['prev_cups']),
                    'prev_revenue': float(input_summary['prev_revenue'])
                }

                def run_safe_predict(model_obj, model_name, base_data, extra_inputs=None):
                    if not model_obj: return None
                    
                    if hasattr(model_obj, 'feature_names_in_'):
                        expected = list(model_obj.feature_names_in_)
                    elif hasattr(model_obj, 'steps'):
                        expected = list(model_obj.steps[0][1].feature_names_in_)
                    else: # Fallback, might not be perfect
                        expected = ['store_location', 'shift', 'month', 'day_of_week', 'is_weekend', 'prev_cups', 'prev_revenue']

                    predict_data = base_data.copy()
                    if extra_inputs:
                        predict_data.update(extra_inputs)
                    
                    row = {col: predict_data.get(col, 0) for col in expected}
                    df = pd.DataFrame([row], columns=expected)

                    for col in expected:
                        if col in ['store_location', 'shift', 'day_of_week']:
                            df[col] = df[col].astype(str)
                        else:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                    try:
                        return model_obj.predict(df)[0]
                    except Exception as e:
                        print(f"Prediction for {model_name} failed: {str(e)}")
                        return None
                
                if model1_demand:
                    prediction_demand = run_safe_predict(model1_demand, "Demand Model", current_input_data)
                    
                if model2_revenue:
                    rev_extras = {}
                    if prediction_demand is not None:
                        rev_extras['total_cups'] = float(prediction_demand)
                    prediction_revenue = run_safe_predict(model2_revenue, "Revenue Model", current_input_data, extra_inputs=rev_extras)
                    
                if model3_inventory:
                    inv_extras = {}
                    if prediction_demand is not None:
                        inv_extras['total_shift_cups'] = float(prediction_demand)
                    prediction_inventory = run_safe_predict(model3_inventory, "Inventory Model", current_input_data, extra_inputs=inv_extras)
                    
                if prediction_inventory is not None:
                    try:
                        inventory_data = prediction_inventory.tolist() if hasattr(prediction_inventory, 'tolist') else list(prediction_inventory)
                    except TypeError:
                        inventory_data = [prediction_inventory]
                        
            slug = f"{b['slug']}-{s['slug']}"
            
            dashboard_data.append({
                'branch': branch_name,
                'shift': shift_name,
                'branch_slug': b['slug'],
                'shift_slug': s['slug'],
                'slug': slug,
                'input_summary': input_summary,
                'prediction_demand': prediction_demand,
                'prediction_revenue': prediction_revenue,
                'inventory_data': json.dumps(inventory_data),
                'is_stale': is_stale,
                'is_previewing_this_card': is_previewing_this_card,
            })

    return render(request, 'admin/dashboard.html', {
        'dashboard_data': dashboard_data,
        'branches': branches,
        'shifts': shifts,
        'inventory_labels': json.dumps(inventory_labels)
    })

def manual_input_view(request):
    success = False
    error = None
    if request.method == 'POST':
        try:
            PredictionInput.objects.create(
                target_date=request.POST.get('target_date'),
                store_location=request.POST.get('store_location'),
                shift=request.POST.get('shift'),
                prev_cups=float(request.POST.get('prev_cups', 0)),
                prev_revenue=float(request.POST.get('prev_revenue', 0))
            )
            success = True
        except Exception as e:
            error = f"Failed to save record: {str(e)}"
            
    return render(request, 'admin/manual_input.html', {'success': success, 'error': error})