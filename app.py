import requests
from bs4 import BeautifulSoup
import time
import csv
import os

def fetch_and_save_otp():
    """Fetch OTP from website and save to or update CSV"""
    url = "https://otp-generator-sm20.onrender.com/"
    
    try:
        # Make the request
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the OTP
            otp_div = soup.find('div', class_='otp')
            
            if otp_div:
                # Get OTP
                otp = otp_div.text.strip()
                
                # Update or append to CSV
                update_or_append_csv(otp)
                
                # Print to console
                print(f"OTP: {otp}")
                print("Saved to otp_history.csv")
                print("-" * 30)
            else:
                print("Could not find OTP on page")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error occurred: {e}")

def update_or_append_csv(otp):
    """Update OTP in CSV (keep only the latest OTP)"""
    file_path = 'otp_history.csv'
    rows = []
    file_exists = os.path.exists(file_path)
    
    # Read existing data if the file exists
    if file_exists:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
    
    # Separate header and data rows
    header = rows[0] if rows else ['OTP']
    data_rows = rows[1:] if len(rows) > 1 else []
    
    # Keep only the latest OTP
    data_rows = [[otp]]  # Overwrite with the latest OTP
    
    # Write back to the CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        writer.writerows(data_rows)  # Write the latest OTP row

def main():
    print("Starting OTP Fetcher...")
    print("Fetching OTP every 30 seconds. Press Ctrl+C to stop.")
    print("Only the latest OTP will be saved to otp_history.csv")
    
    while True:
        try:
            fetch_and_save_otp()
            time.sleep(30)  # Wait 30 seconds before next fetch
        except KeyboardInterrupt:
            print("\nStopping OTP Fetcher...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait 5 seconds before retrying

if __name__ == "__main__":
    main()
