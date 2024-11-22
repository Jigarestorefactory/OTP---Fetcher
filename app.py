import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv
import os

def fetch_and_save_otp():
    """Fetch OTP from website and save to CSV"""
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
                # Get OTP and current time
                otp = otp_div.text.strip()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Prepare data for CSV
                data = [current_time, otp]
                
                # Save to CSV
                file_exists = os.path.exists('otp_history.csv')
                with open('otp_history.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        # Write header if file is new
                        writer.writerow(['Timestamp', 'OTP'])
                    writer.writerow(data)
                
                # Print to console
                print(f"\nTime: {current_time}")
                print(f"OTP: {otp}")
                print("Saved to otp_history.csv")
                print("-" * 30)
            else:
                print("Could not find OTP on page")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    print("Starting OTP Fetcher...")
    print("Fetching OTP every 30 seconds. Press Ctrl+C to stop.")
    print("OTPs will be saved to otp_history.csv")
    
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