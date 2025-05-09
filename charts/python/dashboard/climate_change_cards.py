import pandas as pd
from datetime import datetime

def calculate_global_temp_stats():
    try:
        temp_df = pd.read_csv('datasets/yearl_temperature.csv')
        
        temp_1940 = temp_df[temp_df['year'] == 1940]['Average surface temperature'].mean()
        temp_2024 = temp_df[temp_df['year'] == 2024]['Average surface temperature'].mean()
        
        temp_increase = temp_2024 - temp_1940
        temp_percentage_increase = (temp_increase / temp_1940) * 100
        
        return {
            'current_temp': round(temp_2024, 1),
            'increase': round(temp_increase, 1),
            'percentage_increase': round(temp_percentage_increase, 1)
        }
    except Exception as e:
        print(f"Error processing temperature data: {e}")
        return {
            'current_temp': "N/A",
            'increase': "N/A",
            'percentage_increase': "N/A"
        }

def calculate_co2_stats():
    try:
        co2_df = pd.read_csv('datasets/yearly-co2-emissions.csv')
        
        co2_1949 = co2_df[co2_df['Year'] == 1949]['Annual CO₂ emissions'].sum()
        co2_2023 = co2_df[co2_df['Year'] == 2023]['Annual CO₂ emissions'].sum()
        
        co2_percentage_increase = ((co2_2023 - co2_1949) / co2_1949) * 100
        
        return {
            'current_co2': round(co2_2023 / 1_000_000, 1),
            'percentage_increase': round(co2_percentage_increase, 1)
        }
    except Exception as e:
        print(f"Error processing CO2 data: {e}")
        return {
            'current_co2': "N/A",
            'percentage_increase': "N/A"
        }

def calculate_sea_level_stats():
    try:
        sea_df = pd.read_csv('datasets/Climate_Change_Dataset.csv')
        
        sea_df.columns = sea_df.columns.str.strip()
        if 'Sea Level Rise (mm)' not in sea_df.columns:
            sea_df = pd.read_csv('datasets/Climate_Change_Dataset.csv', header=None, 
                                names=['Year', 'Country', 'Sea Level Rise (mm)'])
        
        sea_2000 = sea_df[sea_df['Year'] == 2000]['Sea Level Rise (mm)'].sum()
        sea_2023 = sea_df[sea_df['Year'] == 2023]['Sea Level Rise (mm)'].sum()
        
        sea_increase = sea_2000 - sea_2023
        
        return {
            'current_sea_level': round(sea_2023, 1),
            'increase': round(sea_increase, 1)
        }
    except Exception as e:
        print(f"Error processing sea level data: {e}")
        return {
            'current_sea_level': "N/A",
            'increase': "N/A"
        }

def calculate_population_stats():
    file_path = 'datasets/population.csv'
    
    pop_df = pd.read_csv(file_path)
    pop_df.columns = pop_df.columns.str.strip()
    
    pop_col = None
    for col in pop_df.columns:
        if 'population' in col.lower():
            pop_col = col
            break
    
    if pop_col is None:
        print("Population column not found in the dataset")
        return {
            'current_population': "N/A"
        }
    
    pop_2023 = pop_df[pop_df['Year'] == 2023][pop_col].sum()
    pop_in_billions = round(pop_2023 / 1_000_000_000, 1)
    
    return {
        'current_population': pop_in_billions
    }

def generate_html():
    temp_stats = calculate_global_temp_stats()
    co2_stats = calculate_co2_stats()
    sea_stats = calculate_sea_level_stats()
    pop_stats = calculate_population_stats()
    
    current_date = datetime.now().strftime("%B %d, %Y %H:%M")
    
    html_template = f"""
    <div class="min-h-screen bg-black py-20 px-4 sm:px-6 lg:px-8">
        <!-- Dashboard Header -->
        <div class="max-w-8xl mx-auto mb-8">
            <h1 class="text-3xl font-bold text-green-400">Climate Dashboard</h1>
            <p class="text-gray-400 mt-2">Real-time monitoring of global climate indicators</p>
            
            <!-- Date/Time and Stats Row -->
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mt-6 gap-4">
                <div class="text-gray-300">
                    <span id="current-date" class="font-medium">{current_date}</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full sm:w-auto">
                    <!-- Stat Cards -->
                    <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-green-500">
                        <p class="text-gray-400 text-sm">Global Temp</p>
                        <p class="text-2xl font-bold text-white">+{temp_stats['increase']}°C</p>
                        <p class="text-xs text-gray-500">+{temp_stats['percentage_increase']}% since 1940</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
                        <p class="text-gray-400 text-sm">CO₂ Level</p>
                        <p class="text-2xl font-bold text-white">{co2_stats['current_co2']}M tons</p>
                        <p class="text-xs text-gray-500">+{co2_stats['percentage_increase']}% since 1949</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-yellow-500">
                        <p class="text-gray-400 text-sm">Sea Level Rise</p>
                        <p class="text-2xl font-bold text-white">+{sea_stats['increase']}mm</p>
                        <p class="text-xs text-gray-500">Total increase since 2000</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-red-500">
                        <p class="text-gray-400 text-sm">Global Population</p>
                        <p class="text-2xl font-bold text-white">{pop_stats['current_population']}B</p>
                        <p class="text-xs text-gray-500">in 2023</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html_template

html_output = generate_html()
with open('card_output.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("HTML file generated successfully!")