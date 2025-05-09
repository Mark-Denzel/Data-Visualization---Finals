library(ggplot2)
library(readr)
library(plotly)
library(lubridate)
library(dplyr)
library(htmlwidgets)

# Read and preprocess data
deforest_data <- read_csv("datasets/Deforestation or Forest Fires Over Time.csv") %>%
  mutate(Date = as.Date(Date, format = "%d/%m/%Y")) %>%
  filter(Forest_Fires_Reported > 0)

# Generate list of countries and date ticks
countries_with_fires <- unique(deforest_data$Country)
jan_dates <- seq.Date(from = floor_date(min(deforest_data$Date), "year"),
                      to = ceiling_date(max(deforest_data$Date), "year"),
                      by = "year")

# Summarize deforestation data
deforest_lines <- deforest_data %>%
  group_by(Country, Date) %>%
  summarize(Deforestation_Area_Ha = mean(Deforestation_Area_Ha), .groups = "drop")

# Scaling factor for dual y-axis
fire_max <- max(deforest_data$Forest_Fires_Reported, na.rm = TRUE)
deforest_max <- max(deforest_lines$Deforestation_Area_Ha, na.rm = TRUE)
scaling_factor <- fire_max / deforest_max

# Create tooltip columns
deforest_lines <- deforest_lines %>%
  mutate(line_tooltip = paste("Country:", Country,
                              "<br>Date:", format(Date, "%b %d, %Y"),
                              "<br>Deforestation (Ha):", round(Deforestation_Area_Ha, 2)))

deforest_data <- deforest_data %>%
  mutate(point_tooltip = paste("Date:", format(Date, "%b %d, %Y"),
                               "<br>Country:", Country,
                               "<br>Forest Fires:", Forest_Fires_Reported,
                               "<br>Air Quality Index:", round(Air_Quality_Index, 2)))

# Create ggplot
base_plot <- ggplot(deforest_data, aes(x = Date)) +
  geom_line(data = deforest_lines,
            aes(y = Deforestation_Area_Ha * scaling_factor,
                group = Country, color = Country,
                text = line_tooltip),
            linewidth = 1, alpha = 0.7) +
  geom_point(aes(y = Forest_Fires_Reported,
                 color = Country,
                 text = point_tooltip),
             alpha = 0.7, size = 3) +
  scale_y_continuous(
    name = "Number of Forest Fires Reported",
    sec.axis = sec_axis(~./scaling_factor, name = "Deforestation Area (Ha)")
  ) +
  scale_x_date(breaks = jan_dates, labels = scales::date_format("%Y"),
               limits = c(min(deforest_data$Date), max(deforest_data$Date))) +
  labs(title = "Forest Fires and Deforestation Trends",
       x = "Year",
       caption = "Lines show deforestation area (right axis), points show forest fires (left axis)") +
  theme_minimal() +
  theme(
    legend.position = "none",
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.title.y = element_text(color = "darkred"),
    axis.title.y.right = element_text(color = "darkgreen"),
    plot.caption = element_text(face = "italic", size = 9),
    plot.title = element_text(size = 14, face = "bold")
  )

# Convert ggplot to plotly
interactive_plot <- ggplotly(base_plot, tooltip = "text") %>%
  layout(
    hoverlabel = list(bgcolor = "white", font = list(size = 12)),
    updatemenus = list(
      list(
        type = "dropdown",
        active = 0,
        buttons = c(
          list(list(
            method = "restyle",
            args = list("visible", rep(TRUE, length(countries_with_fires))),
            label = "All Countries"
          )),
          lapply(seq_along(countries_with_fires), function(i) {
            list(
              method = "restyle",
              args = list("visible", replace(rep(FALSE, length(countries_with_fires)), i, TRUE)),
              label = countries_with_fires[i]
            )
          })
        ),
        x = 1.05,
        y = 0.05,
        xanchor = "right",
        yanchor = "bottom",
        bgcolor = "#EEEEEE",
        bordercolor = "#CCCCCC"
      )
    )
  )

# Save the widget (use selfcontained = FALSE to avoid Pandoc requirement)
saveWidget(interactive_plot, "deforestation_fires_plot.html", selfcontained = FALSE)
