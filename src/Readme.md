## Functions in Kiosk_main.py

### `Main_window.capture_image()`
- This method is called when the user clicks the **"Add"** button on the main window interface.
- It captures an image from the camera, processes it using the YOLOv5 model to detect objects, retrieves their names, and fetches their prices from a CSV file.
- The detected objects along with their quantities and prices are added to the cart displayed in the treeview widget on the main window interface.

### `Main_window.remove()`
- This method is called when the user clicks the **"Remove"** button on the main window interface.
- It removes the selected item from the cart displayed in the treeview widget and updates the total cost accordingly.

### `Main_window.update_total_cost()`
- This method updates the total cost displayed on the main window interface after adding or removing items from the cart.

### `Payment.destroyed()`
- This method is called when the user clicks the **"Finish"** button on the payment window interface.
- It resets the total cost to zero and closes the payment window, returning the user to the start window.

---

These functions encapsulate various functionalities such as image processing, cart management, and interface navigation in the self-checkout kiosk system. They collectively enable the system to capture, process, and display information to the user effectively.
