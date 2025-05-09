# Load required libraries
library(plotly)
library(dplyr)
library(readr)
library(htmlwidgets)
# Read the data
data <- read_csv("datasets/Plastic Waste vs. Population Affected_Scatter Plots.csv")

# Calculate global totals
total_global_plastic <- sum(data$Plastic_Waste_Tons, na.rm = TRUE)
total_global_burned <- sum(data$Burned_Waste_Tons, na.rm = TRUE)
total_global_waste <- total_global_plastic + total_global_burned

# Aggregate data by country (focusing on plastic waste)
agg_data <- data %>%
  group_by(Country) %>%
  summarize(
    Total_Plastic_Waste = sum(Plastic_Waste_Tons, na.rm = TRUE),
    Total_Burned_Waste = sum(Burned_Waste_Tons, na.rm = TRUE),
    Avg_Population_Affected = mean(Population_Affected, na.rm = TRUE)
  ) %>%
  arrange(desc(Total_Plastic_Waste)) %>%  # Sort by plastic waste
  head(10)  # Top 10 countries by plastic waste

# Create interactive donut chart focused on plastic waste
fig <- plot_ly(agg_data, 
               labels = ~Country, 
               values = ~Total_Plastic_Waste,  # Using plastic waste as primary metric
               type = 'pie',
               hole = 0.6,
               textinfo = 'label+percent',
               hoverinfo = 'text',
               text = ~paste(
                 '<b>', Country, '</b>',
                 '<br>Plastic Waste: ', format(round(Total_Plastic_Waste), big.mark = ","), " tons",
                 '<br>Burned Waste: ', format(round(Total_Burned_Waste), big.mark = ","), " tons",
                 '<br>Total Waste: ', format(round(Total_Plastic_Waste + Total_Burned_Waste), big.mark = ","), " tons",
                 '<br>Avg Population Affected: ', format(round(Avg_Population_Affected), big.mark = ","),
                 '<br>% of Global Plastic: ', round(Total_Plastic_Waste/total_global_plastic*100, 1), "%"
               ),
               marker = list(line = list(color = '#FFFFFF', width = 1)),
               showlegend = TRUE)

# Add title and annotations
fig <- fig %>% layout(
  title = list(
    text = '<b>Plastic Wastes per country</b>',
    font = list(size = 18)
  ),
  annotations = list(
    list(
      text = "Plastic Waste\nDistribution",
      x = 0.5, y = 0.5,
      font = list(size = 14),
      showarrow = FALSE
    ),
    list(
      text = paste(
        "Global Waste Totals:",
        "<br>", format(round(total_global_plastic), big.mark = ","), " tons Plastic",
        "<br>", format(round(total_global_burned), big.mark = ","), " tons Burned",
        "<br>", format(round(total_global_waste), big.mark = ","), " tons Combined"
      ),
      x = 0.5, y = -0.15,
      font = list(size = 12),
      showarrow = FALSE,
      xref = 'paper',
      yref = 'paper',
      align = 'center'
    )
  )
)

htmlwidgets::saveWidget(fig, "plastic_waste_chart.html", selfcontained = TRUE)
browseURL("plastic_waste_chart.html")