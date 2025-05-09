library(dplyr)
library(ggplot2)
library(plotly)
library(tidyr)

data <- read.csv(file.choose())

processed_data <- data %>%
  group_by(Year) %>% 
  summarise(
    `Avg Temperature (°C)` = mean(`Avg.Temperature...C.`, na.rm = TRUE),
    `CO2 Emissions (tons/capita)` = mean(`CO2.Emissions..Tons.Capita.`, na.rm = TRUE),
    `Sea Level Rise (mm)` = mean(`Sea.Level.Rise..mm.`, na.rm = TRUE)
  ) %>%
  ungroup() %>%
  pivot_longer(
    cols = c(`Avg Temperature (°C)`, `CO2 Emissions (tons/capita)`, `Sea Level Rise (mm)`),
    names_to = "Indicator",
    values_to = "Value"
  ) %>%
  mutate(
    Tooltip = case_when(
      grepl("Temperature", Indicator) ~ paste0("Year: ", Year, "<br>",
                                              "Indicator: ", Indicator, "<br>",
                                              "Global Average: ", round(Value, 1), "°C"),
      grepl("CO2", Indicator) ~ paste0("Year: ", Year, "<br>",
                                     "Indicator: ", Indicator, "<br>",
                                     "Global Average: ", round(Value, 1), " tons/capita"),
      grepl("Sea Level", Indicator) ~ paste0("Year: ", Year, "<br>",
                                           "Indicator: ", Indicator, "<br>",
                                           "Global Average: ", round(Value, 1), " mm")
    )
  )

p <- ggplot(processed_data, aes(x = Year, y = Value, fill = Indicator, group = Indicator,
                               text = Tooltip)) +
  geom_area(position = "stack", alpha = 0.8) +
  scale_fill_manual(values = c("Avg Temperature (°C)" = "#FF6B6B", 
                              "CO2 Emissions (tons/capita)" = "#4ECDC4", 
                              "Sea Level Rise (mm)" = "#556270")) +
  labs(title = "Contribution of Environmental Indicators Over Time (Globally)",
       x = "Year",
       y = NULL,
       fill = "Environmental Indicators") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"))

interactive_plot <- ggplotly(p, tooltip = "text") %>%
  layout(hovermode = "x unified",
         yaxis = list(title = ""),
         margin = list(t = 70)) 


htmlwidgets::saveWidget(interactive_plot, "env_indicators_plot.html")
