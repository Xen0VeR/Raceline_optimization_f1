import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import yaml

# Load data from CSV
data = np.loadtxt('/home/xenover/Downloads/mod/17_2_l.csv', delimiter=",")
yaml_path = '/home/xenover/Downloads/mod/17_2_.yaml'

with open(yaml_path, 'r') as file:
    yaml_data = yaml.safe_load(file)
resolution = yaml_data.get('resolution', 0.1)  # Default to 0.1 if not found
origin = yaml_data.get('origin', [0.0, 0.0, 0.0])
# map_path = '/home/kshitij-vaidya/Downloads/timed1.pgm'
map_path = '/home/xenover/Downloads/mod/17_2_.pgm'

x, y = data[:, 0], data[:, 1]
# Create figure and scatter plot
fig, ax = plt.subplots()
sc = ax.scatter(x, y, color="blue", picker=True)  # Enable picking
ax.set_xlabel("X")
ax.set_ylabel("Y")
plt.title("Drag and Drop Point Adjustment")
# Load and display the background image
img = plt.imread(map_path)
# print(type(img))
# ax.imshow(img, extent=[x.min(), x.max(), y.min(), y.max()], aspect='auto')
# Calculate extent for the map image based on origin and resolution
map_width = img.shape[1] * resolution
map_height = img.shape[0] * resolution
map_extent = [
    origin[0],  # Minimum x-coordinate
    origin[0] + map_width,  # Maximum x-coordinate
    origin[1],  # Minimum y-coordinate
    origin[1] + map_height  # Maximum y-coordinate
]

# Load and display the background image with proper alignment
ax.imshow(img, extent=map_extent, aspect='auto', alpha=0.5)

# Adjust axis limits to ensure both map and points are visible
ax.set_xlim(min(x.min(), map_extent[0]), max(x.max(), map_extent[1]))
ax.set_ylim(min(y.min(), map_extent[2]), max(y.max(), map_extent[3]))


selected_index = None  # To store the index of the selected point
dragging_point = False  # To track dragging state
remove_mode = False  # To track removal mode
add_mode = False  # To track add mode

# Event handler for mouse button press


def on_press(event):
    global x, y, selected_index, dragging_point, remove_mode, add_mode
    if event.inaxes != ax:
        return

    # If remove mode is active, delete the closest point
    if remove_mode:
        distances = np.sqrt((x - event.xdata)**2 + (y - event.ydata)**2)
        selected_index = np.argmin(distances)
        if distances[selected_index] < 0.1:  # Close enough to delete
            x = np.delete(x, selected_index)
            y = np.delete(y, selected_index)
            sc.set_offsets(np.c_[x, y])
            fig.canvas.draw_idle()
            print(f"Point at index {selected_index} removed.")
    # If add mode is active, add a new point
    elif add_mode:
        x = np.append(x, event.xdata)
        y = np.append(y, event.ydata)
        sc.set_offsets(np.c_[x, y])
        fig.canvas.draw_idle()
        print(f"Point added at ({event.xdata}, {event.ydata}).")
    else:
        # Calculate the closest point to the click for dragging
        distances = np.sqrt((x - event.xdata)**2 + (y - event.ydata)**2)
        selected_index = np.argmin(distances)
        if distances[selected_index] < 0.1:  # Set a small threshold for selection
            dragging_point = True

# Event handler for mouse motion


def on_motion(event):
    global dragging_point
    if dragging_point and selected_index is not None:
        # Update the position of the selected point
        x[selected_index] = event.xdata
        y[selected_index] = event.ydata
        sc.set_offsets(np.c_[x, y])
        fig.canvas.draw_idle()

# Event handler for mouse button release


def on_release(event):
    global dragging_point
    dragging_point = False

# Event handler for double-click to remove a point (alternative method)


def on_double_click(event):
    global x, y
    if event.inaxes != ax:
        return
    # Check if the click was a double-click
    if event.dblclick:
        distances = np.sqrt((x - event.xdata)**2 + (y - event.ydata)**2)
        selected_index = np.argmin(distances)
        if distances[selected_index] < 0.1:  # Set a small threshold for selection
            x = np.delete(x, selected_index)
            y = np.delete(y, selected_index)
            sc.set_offsets(np.c_[x, y])
            fig.canvas.draw_idle()
            print(f"Point at index {selected_index} removed.")

# Toggle remove mode on button click


def toggle_remove(event):
    global remove_mode, add_mode
    remove_mode = not remove_mode
    add_mode = False  # Disable add mode when switching to remove mode
    print("Remove mode: " + ("ON" if remove_mode else "OFF"))

# Toggle add mode on button click


def toggle_add(event):
    global add_mode, remove_mode
    add_mode = not add_mode
    remove_mode = False  # Disable remove mode when switching to add mode
    print("Add mode: " + ("ON" if add_mode else "OFF"))


# Save button
save_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
save_button = Button(
    save_ax, 'Save', color='lightgoldenrodyellow', hovercolor='0.975')


def save(event):
    np.savetxt("/home/xenover/Downloads/mod/17_2_l.csv",
               np.c_[x, y], delimiter=",", fmt="%.7f")
    print("Points saved to final_ok_updated.csv")


# Remove Point button
remove_ax = plt.axes([0.8, 0.075, 0.1, 0.04])
remove_button = Button(remove_ax, 'Remove Point',
                       color='lightcoral', hovercolor='0.975')
remove_button.on_clicked(toggle_remove)

# Add Point button
add_ax = plt.axes([0.8, 0.125, 0.1, 0.04])
add_button = Button(add_ax, 'Add Point',
                    color='lightgreen', hovercolor='0.975')
add_button.on_clicked(toggle_add)

# Connect events to the figure
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)
# Handling double-clicks for point removal
fig.canvas.mpl_connect("button_press_event", on_double_click)
save_button.on_clicked(save)

plt.show()
