import os
import sys


gui_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)
static_dir = os.path.abspath(os.path.join(gui_dir, "static"))
template_dir = os.path.abspath(os.path.join(gui_dir, "templates"))
app_data_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "AppData"))
auth_dir = os.path.abspath(os.path.join(app_data_dir, "auth"))
db_dir = os.path.abspath(os.path.join(app_data_dir, "storage"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "output"))
