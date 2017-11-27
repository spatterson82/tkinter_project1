import os
import tkFont
import tkMessageBox

from PIL import Image, ImageTk
from Tkinter import Tk, BOTH, X, N, S, E, W, Entry
from tkinter.ttk import Frame, Button, Label, Style

from arcpy.sa import Idw as idw
from arcpy.sa import ZonalStatisticsAsTable  as Z_Stats
from arcpy import env, CheckOutExtension, AddJoin_management, \
    MakeFeatureLayer_management, mapping, GetMessages, OrdinaryLeastSquares_stats, \
    ApplySymbologyFromLayer_management


class IdwApp(Frame):
    """
    Main app object for creating a Python GUI
    to calculate and display Inverse Distance Weighted
    spatial analysis for cancer occurrences.

    :param tkinter.ttk.Frame Frame: Parent Frame widget

    """

    def __init__(self, root_window):
        """
        Constructor method for setting up the window
        and user interface

        :param Tkinter.Tk root_window: Main window object
        """

        Frame.__init__(self)
        self.root = root_window
        self.master.state('zoomed')

        # set font
        font_type = "Helvetica"
        self.main_font = tkFont.Font(family=font_type, size=16)
        self.sub_font = tkFont.Font(family=font_type, size=13)
        self.small_font = tkFont.Font(family=font_type, size=8)

        # placeholder for Entry box
        self.k_input = None
        # placeholder for image
        self.idw_image_jov = None
        # placeholder for message
        self.info_message = None

        self.initGIS()

        self.initUI()


    def initGIS(self):
        """
        Factory method for setting up required ArcPy processing
        """

        # GIS globals
        env.overwriteOutput = True
        env.extent = "MINOF"
        CheckOutExtension("Spatial")

        self.output_location = os.path.join(os.getcwd(), 'tkinter_output')
        print self.output_location
        if not os.path.isdir(self.output_location):
            os.mkdir(self.output_location)

        env.workspace = self.output_location

        self.tracts_file = os.path.join(self.output_location, "cancer_tracts.shp")
        self.mxd = mapping.MapDocument(os.path.join(self.output_location, "cancer_data.mxd"))

    def initUI(self):
        """
        Method for creating the user interface and calling
        all required widget creation methods
        """

        self.columnconfigure(0, minsize=30, weight=2)

        self.style = Style()

        Style().configure("TFrame", background="#333")

        self.master.title("Cancer Research")
        self.pack(fill=BOTH, expand=True)

        # Put text and image on same row
        frame1 = self.create_frame()
        self.frame = frame1

        self.create_description_text(frame1)
        self.info_message = self.set_status_message()
        self.create_image(frame1)

        # Add any buttons
        self.create_buttons()

    def get_screen_h(self):
        """
        Method for obtaining the user's screen height value

        :return int: Screen height in pixels
        """
        return self.master.winfo_screenheight()

    def get_screen_w(self):
        """
        Method for obtaining the user's screen height value

        :return int: Screen width in pixels
        """

        return self.master.winfo_screenwidth()

    def create_frame(self):
        """
        Factory method for creating a new frame when needed

        :return tkinter.ttk.Frame: Frame object
        """
        new_frame = Frame(self)
        new_frame.pack(fill=X)
        new_frame.config()

        return new_frame

    def create_description_text(self, frame):
        """
        Method for implementing the text boxes that describe the application
        """
        one = "High concentrations of nitrate have\n"
        two = "been found during routine sampling\n"
        three = "of water wells throughout Wisconsin.\n\n"
        four = "This tool will generate a map\n"
        five = "based on an inverted-distance\n"
        six = "weighted analysis that approximates\n"
        seven = "the geographic extent of nitrate\nbased on sample locations."
        main_text = "{}{}{}{}{}{}{}".format(one, two, three, four, five, six, seven)

        """1st section"""
        style = Style()
        style.configure("grey.TLabel", foreground="white", background="#333")
        text_label = Label(frame, text=main_text, width=30, font=self.main_font, style="grey.TLabel")
        # text_label.pack(side=LEFT, padx=5, pady=5)
        text_label.grid(row=0, column=0, columnspan=2, rowspan=6,
                        padx=30, pady=70, sticky=W+N+E)

        """2nd section"""
        k_label = Label(frame, text="Enter a value for k:  (ex: 2-30)", font=self.sub_font, style="grey.TLabel")
        k_label.grid(row=4, column=0, columnspan=1, rowspan=1,
                     padx=30, pady=40, sticky=W)
        self.k_input = Entry(frame, width=7)
        self.k_input.focus_set()
        self.k_input.grid(row=4, column=1, columnspan=1, rowspan=1,
                     padx=1, pady=50, sticky=W)

        """3rd section"""
        small_text = "where k = power exponent of distance\nfor consideration of surrounding points"
        small_label = Label(frame, text=small_text, font=self.small_font, style="grey.TLabel")
        small_label.grid(row=4, column=0, columnspan=1, rowspan=2,
                     padx=55, pady=50, sticky=W + E)

    def create_image(self, frame, new=False):
        """
        Method for initializing the main image and resizing
        it to fit the required size

        :param tkinter.ttk.Frame frame: Frame object used for current image
        :param bool new: Placeholder variable for swapping default image
        """

        if new is False:
            orig_image = Image.open(os.path.join(os.getcwd(), "sample_output.jpg"))
        else:
            orig_image = Image.open(os.path.join(os.getcwd(), "idwout.jpg"))
        resize_image = orig_image.resize((1000, 600), Image.ANTIALIAS)

        idw_image_jov = ImageTk.PhotoImage(resize_image)

        idw_label = Label(frame, image=idw_image_jov)
        idw_label.image = idw_image_jov
        idw_label.grid(row=0, column=2, rowspan=8,
                       padx=1, pady=30, sticky=W+S+N)

    def set_status_message(self):
        """
        Method to set a status message Label for later manipulation

        :return tkinter.ttk.Label: Label object for holding text
        """

        """4th section"""
        processing = "Running IDW and creating output image...."
        info_message = Label(self.frame, text=processing, font=self.main_font, foreground="#333", background="#333") #style="grey.TLabel")
        info_message.grid(row=8, column=2, columnspan=1, rowspan=1,
                         padx=80, pady=50, sticky=W)

        return info_message

    def update_status_message(self, color=False):
        """
        Method for changing the color of the status Label object

        :param bool color: Check for adding or removing color
        """

        if color:
            self.info_message.configure(foreground="white")
        else:
            self.info_message.configure(foreground="#333")
        self.root.update()

    def process_k_value(self):
        """
        Method for verifying the K value and passing
        it to the back-end processing

        Also enforces a range of values
        """

        k = self.k_input.get()
        if k == "" or not k.isdigit():
            tkMessageBox.showinfo("Warning", "Integer K value between 2 - 30 is required!")
        elif k and not 2 <= int(k) <= 30:
            tkMessageBox.showinfo("Warning", "Your Value: {}\nChoose value between 2 - 30".format(k))
        else:
            self.update_status_message(True)
            k_val = int(k)
            if k_val:
                try:
                    self.run_idw_process(k_val)
                    self.create_image(self.frame, new=True)
                except:
                    raise ValueError("Unable to process IDW function! \n{}".format(GetMessages()))

    def output_message(self, message):
        """
        Simple method for custom error messaging

        :param str message: Custom error message
        """

        tkMessageBox.showinfo("Success", message)

    def run_idw_process(self, k_val):
        """
        Method for calculating the Inverse-Distance Weighted

        :param int k_val: User supplied k value
        """

        filename = "idwout"
        full_filename = filename + ".tif"
        point_file = os.path.join(self.output_location, "well_nitrate.shp")

        # Run IDW process
        output_raster = idw(point_file, "nitr_ran", power=k_val)
        output_raster.save(full_filename)

        self.run_zonal_statistics(os.path.join(self.output_location, full_filename))

    def run_zonal_statistics(self, output_raster):
        """
        Method for calculating the Zonal Statistics

        :param str output_raster: Path to raster file
        """

        output_table = os.path.join(self.output_location, "zonal_table.dbf")
        Z_Stats(self.tracts_file, "GEOID10", output_raster, output_table)

        self.join_table_to_tracts(output_table)

    def join_table_to_tracts(self, output_table):
        """
        Method for creating an editable layer and joining
        the Zonal Statistics table to the census tracts shapefile

        :param str output_table: Path for the zonal statistics table that was created
        """

        tracts_layer = "tracts_layer"
        MakeFeatureLayer_management(self.tracts_file, tracts_layer)

        attribute = "GEOID10"
        AddJoin_management(tracts_layer, attribute, output_table, attribute)

        self.run_ordinary_least_squres(tracts_layer)

    def run_ordinary_least_squres(self, tracts_layer):
        """
        Method  for calculating Ordinary Least Squares Statistics

        :param str tracts_layer: Name of the in-memory feature layer
        """

        output_file = os.path.join(self.output_location, "Least Squares.shp")
        OrdinaryLeastSquares_stats(tracts_layer, "zonal_table.OID",
                                   output_file,
                                   "zonal_table.MEAN",
                                   ["cancer_tracts.canrate"])

        self.add_layer_to_mxd(output_file)

    def add_layer_to_mxd(self, filename):
        """
        Method for applying symbology to the in-memory layer
        and adding it to a template MXD file for output

        :param str filename: Name of the final output file for adding to the application
        """

        df = mapping.ListDataFrames(self.mxd, "")
        create_layer = mapping.Layer(filename)

        ApplySymbologyFromLayer_management(create_layer, os.path.join(self.output_location, "least_squares.lyr"))
        mapping.AddLayer(df[0], create_layer, "BOTTOM")

        self.output_image("idwout.jpg")

    def output_image(self, image_name):
        """
        Factory method for exporting different image types in ArcMap

        :param str image_name: Name of output image with file extension
        :return:
        """
        if image_name.endswith("jpg"):
            mapping.ExportToJPEG(self.mxd, os.path.join(self.output_location, image_name))
        # Add other image outputs if needed

        self.update_status_message()
        self.output_message("Process Completed")

    def create_buttons(self, button_text=None):
        """
        Method to create and place all buttons for the application
        """

        if button_text is None:
            button_text = "Run"
        button = Button(self, text=button_text, command=self.process_k_value)
        button.place(x=self.get_screen_w() * .75, y=self.get_screen_h() * .80)

        quit_button = Button(self, text="Quit", command=self.quit)
        quit_button.place(x=self.get_screen_w() * .80, y=self.get_screen_h() * .80)



def start_app():
    """
    Function for creating a default Tkinter window
    and passing it to the IdwApp class
    """

    root = Tk()
    app = IdwApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_app()
