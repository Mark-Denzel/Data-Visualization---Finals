import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.patches import Circle
from matplotlib.text import Text

class BubbleChart:
    def __init__(self, area, bubble_spacing=0):
        """
        Setup for bubble collapse.
        Parameters
        ----------
        area : array-like
            Area of the bubbles.
        bubble_spacing : float, default: 0
            Minimal spacing between bubbles after collapsing.
        """
        area = np.asarray(area)
        r = np.sqrt(area / np.pi)

        self.bubble_spacing = bubble_spacing
        self.bubbles = np.ones((len(area), 4))
        self.bubbles[:, 2] = r
        self.bubbles[:, 3] = area
        self.maxstep = 2 * self.bubbles[:, 2].max() + self.bubble_spacing
        self.step_dist = self.maxstep / 2

        length = np.ceil(np.sqrt(len(self.bubbles)))
        grid = np.arange(length) * self.maxstep
        gx, gy = np.meshgrid(grid, grid)
        self.bubbles[:, 0] = gx.flatten()[:len(self.bubbles)]
        self.bubbles[:, 1] = gy.flatten()[:len(self.bubbles)]

        self.com = self.center_of_mass()

    def center_of_mass(self):
        return np.average(
            self.bubbles[:, :2], axis=0, weights=self.bubbles[:, 3]
        )

    def center_distance(self, bubble, bubbles):
        return np.hypot(bubble[0] - bubbles[:, 0],
                        bubble[1] - bubbles[:, 1])

    def outline_distance(self, bubble, bubbles):
        center_distance = self.center_distance(bubble, bubbles)
        return center_distance - bubble[2] - \
            bubbles[:, 2] - self.bubble_spacing

    def check_collisions(self, bubble, bubbles):
        distance = self.outline_distance(bubble, bubbles)
        return len(distance[distance < 0])

    def collides_with(self, bubble, bubbles):
        distance = self.outline_distance(bubble, bubbles)
        return np.argmin(distance, keepdims=True)

    def collapse(self, n_iterations=50):
        """
        Move bubbles to the center of mass.
        Parameters
        ----------
        n_iterations : int, default: 50
            Number of moves to perform.
        """
        for _i in range(n_iterations):
            moves = 0
            for i in range(len(self.bubbles)):
                rest_bub = np.delete(self.bubbles, i, 0)
                dir_vec = self.com - self.bubbles[i, :2]

                dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))

                new_point = self.bubbles[i, :2] + dir_vec * self.step_dist
                new_bubble = np.append(new_point, self.bubbles[i, 2:4])

                if not self.check_collisions(new_bubble, rest_bub):
                    self.bubbles[i, :] = new_bubble
                    self.com = self.center_of_mass()
                    moves += 1
                else:
                    for colliding in self.collides_with(new_bubble, rest_bub):
                        dir_vec = rest_bub[colliding, :2] - self.bubbles[i, :2]
                        dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))
                        orth = np.array([dir_vec[1], -dir_vec[0]])
                        new_point1 = (self.bubbles[i, :2] + orth *
                                      self.step_dist)
                        new_point2 = (self.bubbles[i, :2] - orth *
                                      self.step_dist)
                        dist1 = self.center_distance(
                            self.com, np.array([new_point1]))
                        dist2 = self.center_distance(
                            self.com, np.array([new_point2]))
                        new_point = new_point1 if dist1 < dist2 else new_point2
                        new_bubble = np.append(new_point, self.bubbles[i, 2:4])
                        if not self.check_collisions(new_bubble, rest_bub):
                            self.bubbles[i, :] = new_bubble
                            self.com = self.center_of_mass()

            if moves / len(self.bubbles) < 0.1:
                self.step_dist = self.step_dist / 2

df = pd.read_csv('datasets/population.csv')
df['population_millions'] = df['population'] / 1_000_000

years = sorted(df['Year'].unique())
min_year, max_year = min(years), max(years)
countries = df['Entity'].unique()

fig, ax = plt.subplots(figsize=(12, 10))
plt.subplots_adjust(bottom=0.25)

ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
year_slider = Slider(
    ax=ax_slider,
    label='Year',
    valmin=min_year,
    valmax=max_year,
    valinit=min_year,
    valstep=1
)

circles = []
labels = []
current_year_df = None
annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def format_population(population):
    if population >= 1_000_000_000:
        return f"{population/1_000_000_000:,.2f}B"
    elif population >= 1_000_000:
        return f"{population/1_000_000:,.2f}M"
    elif population >= 1_000:
        return f"{population/1_000:,.2f}K"
    else:
        return f"{population:,.2f}"

def update_annot(ind, bubble_index):
    row = current_year_df.iloc[bubble_index]
    population = row['population']
    formatted_pop = format_population(population)
    annot.xy = (circles[bubble_index].center[0], circles[bubble_index].center[1])
    text = f"{row['Entity']}\nPopulation: {formatted_pop}"
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.8)

def hover(event):
    if event.inaxes == ax:
        vis = annot.get_visible()
        for i, circle in enumerate(circles):
            cont, ind = circle.contains(event)
            if cont:
                update_annot(ind, i)
                annot.set_visible(True)
                fig.canvas.draw_idle()
                return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

def update(val):
    global current_year_df
    year = int(year_slider.val)
    
    current_year_df = df[df['Year'] == year].sort_values('population', ascending=False).head(30)
    
    for circ in circles:
        circ.remove()
    circles.clear()
    
    for label in labels:
        label.remove()
    labels.clear()
    
    bubble_chart = BubbleChart(area=current_year_df['population_millions'], bubble_spacing=0.1)
    bubble_chart.collapse()
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(current_year_df)))
    
    for i in range(len(bubble_chart.bubbles)):
        circ = Circle(
            bubble_chart.bubbles[i, :2], 
            bubble_chart.bubbles[i, 2], 
            color=colors[i],
            alpha=0.7
        )
        ax.add_patch(circ)
        circles.append(circ)

        if bubble_chart.bubbles[i, 2] > 0.5:
            label = ax.text(
                *bubble_chart.bubbles[i, :2], 
                current_year_df.iloc[i]['Entity'],
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=8
            )
            labels.append(label)
    
    ax.set_title(f'World Population - {year} (Top 30 Countries)', fontsize=14)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()

update(min_year)

year_slider.on_changed(update)

plt.axis('off')
plt.tight_layout()
plt.show()