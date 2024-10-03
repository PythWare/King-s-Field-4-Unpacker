import os
import sys
class KF4():
    """The main class for handling the KF4 game"""

    MOVE_TO_FILE_START = 0x40 # The offset where file reading and unpacking will begin
    FILENAME_LENGTH = 0x30 # the length for reading encoded filenames
    ERROR_FILE = "Error.txt"
    def __init__(self):
        """Variables that will be used across the script"""
        
        self.container = "KF4.dat" # Container file
        self.container_size = None # Size of the container file
        self.file_count = None # total files within the container
        self.filename = None # used for the encoded filename reading
        self.folder = None # used for storing the extracted files
        self.main_folder = "KF4_Unpacked" # The main folder for storing unpacked files and folders
        self.basename = None # the filename itself with extension
        self.unknown2 = None # unknown 4 byte value for now
        self.file_size = None # file size of the file without padding
        self.file_size_padding = None # file size of the file + the padding at the end of it
        self.file_offset = None # offset to the file data
        self.file_data = None # The file data itself
        self.return_offset = None # offset to return to
        self.container_file_reader() # call the file reading function

    def log_error(self, message: str) -> None:
        """This function handles error detection"""

        try:
            with open(self.ERROR_FILE, "a") as w1: # open error file
                w1.write(message + "\n") # write the error message
        except Exception as e:
            print(f"Failed to write to error log: {e}")
                
    def remove_error_file(self) -> None:
        """This is a cleanup function that will remove the error file when no error is detected"""
        
        if os.path.isfile(self.ERROR_FILE): # if the error file exists
            os.remove(self.ERROR_FILE) # remove the error file
            
    def container_file_reader(self) -> None:
        """This function handles reading of the container file"""
        
        try:
            print("Task is now starting.")
            with open(self.container, "rb") as f1: # open the container file
                self.container_size = f1.read(4) # read the container's file size solely for reading and not keeping
                self.file_count = int.from_bytes(f1.read(4), "little") # get the file count
                f1.seek(self.MOVE_TO_FILE_START) # go to the start of the first file in the container to begin file reading and writing
                for i in range(0, self.file_count): # loop for file reading
                    self.filename = f1.read(self.FILENAME_LENGTH).decode() # get and decode the filename
                    self.filename = self.filename.strip('\x00') # remove null values
                    self.folder = os.path.dirname(self.filename) # make the folder that is part of the file path
                    self.basename = os.path.basename(self.filename) # get the filename only
                    self.unknown2 = f1.read(4) # read unknown metadata
                    self.file_size = int.from_bytes(f1.read(4), "little") # get the file size
                    self.file_size_padding = f1.read(4) # read the file size + padding
                    self.file_offset = int.from_bytes(f1.read(4), "little") # get the offset to file data
                    self.return_offset = f1.tell() # the position to return to
                    f1.seek(self.file_offset) # go to the file data offset
                    self.file_data = f1.read(self.file_size) # read the file data based on the size
                    self.container_file_unpacking(self.folder, self.basename, self.file_data) # call the file writing function while passing data
                    f1.seek(self.return_offset) # return to the return offset
                    
        except FileNotFoundError:
            self.log_error(f"Error: The file {self.container} does not exist.")
            sys.exit(1)
        except PermissionError:
            self.log_error(f"Error: Permission denied for file {self.container}.")
            sys.exit(1)
        except IOError as e:
            self.log_error(f"Error. An I/O error occured. Details: {e}")
            sys.exit(1)
        else:
            self.remove_error_file() # remove the error file if it exists since an error did not occur

    def container_file_unpacking(self, folder: str, file: str, data: bytes) -> None:
        """This function handles file creation"""
        
        # Create the main output folder if it doesn't exist
        os.makedirs(self.main_folder, exist_ok=True)

        # Construct the full path for the file
        file_path = os.path.join(self.main_folder, folder)  # Combine the main folder with the subfolder
        os.makedirs(file_path, exist_ok=True)  # Create the subfolder if it doesn't exist
        
        # Complete file path
        complete_file_path = os.path.join(file_path, file)  # Full path for the file
        with open(complete_file_path, "wb") as w1: # open the file for writing
            w1.write(data) # write the file data
            
if __name__ == "__main__":
    KF4()

