#!/usr/bin/env python3
"""
Canva Phone Number Automation Tool
Run in Termux: python canva_automation.py
"""

import os
import time
import random
import string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CanvaAutomation:
    def __init__(self, headless=False):
        """Initialize the automation with Chrome options"""
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configure and setup Chrome driver for Termux"""
        chrome_options = Options()
        
        # Essential options for Termux
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--window-size=1280,720')
        
        # Optional: Run in background
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # User agent to avoid detection
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36')
        
        try:
            # For Termux - Chrome path
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            logger.info("Make sure chromium is installed: pkg install chromium")
            return False
    
    def generate_random_name(self):
        """Generate a random Indian-sounding name"""
        first_names = ['Aarav', 'Vihaan', 'Vivaan', 'Ananya', 'Diya', 'Advik', 'Kabir', 
                      'Aarohi', 'Sai', 'Arjun', 'Aadhya', 'Reyansh', 'Ayaan', 'Krishna',
                      'Ishaan', 'Myra', 'Shaurya', 'Pari', 'Anaya', 'Dhruv']
        
        last_names = ['Sharma', 'Verma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Gupta',
                     'Joshi', 'Malhotra', 'Mehta', 'Choudhary', 'Rao', 'Thakur', 'Mishra']
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def read_phone_numbers(self, filename='numbers.txt'):
        """Read phone numbers from file"""
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
                # Assuming phone numbers are in first column
                numbers = df.iloc[:, 0].tolist()
            else:
                with open(filename, 'r') as f:
                    numbers = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Loaded {len(numbers)} phone numbers")
            
            # Clean numbers (remove any non-digit characters)
            cleaned_numbers = []
            for num in numbers:
                # Remove any non-digit characters
                clean = ''.join(filter(str.isdigit, str(num)))
                if len(clean) >= 10:  # Valid phone number check
                    cleaned_numbers.append(clean)
            
            return cleaned_numbers
        except FileNotFoundError:
            logger.error(f"File {filename} not found!")
            logger.info("Creating sample numbers.txt file...")
            self.create_sample_file()
            return []
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return []
    
    def create_sample_file(self):
        """Create a sample numbers.txt file"""
        sample_numbers = """9876543210
9876543211
9876543212
9876543213
9876543214"""
        
        with open('numbers.txt', 'w') as f:
            f.write(sample_numbers)
        logger.info("Created sample numbers.txt with 5 test numbers")
    
    def process_number(self, phone_number):
        """Process a single phone number"""
        try:
            logger.info(f"Processing number: {phone_number}")
            
            # Step 1: Go to Canva signup
            self.driver.get("https://www.canva.com/en_in/signup/")
            time.sleep(3)
            
            # Step 2: Click on "Continue with phone number"
            try:
                phone_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'phone')]"))
                )
                phone_button.click()
                logger.info("Clicked 'Continue with phone number'")
                time.sleep(2)
            except:
                # Alternative selectors
                try:
                    phone_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Use phone')]")
                    phone_button.click()
                except:
                    logger.warning("Phone button not found, might already be on phone input")
            
            # Step 3: Enter phone number
            try:
                phone_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='tel' or @name='phone' or contains(@placeholder, 'Phone')]"))
                )
                phone_input.clear()
                phone_input.send_keys(phone_number)
                logger.info(f"Entered phone number: {phone_number}")
                time.sleep(1)
            except:
                logger.error("Could not find phone input field")
                return False
            
            # Step 4: Click Continue
            try:
                continue_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
                continue_btn.click()
                logger.info("Clicked Continue")
                time.sleep(3)
            except:
                logger.warning("Continue button not found")
            
            # Step 5: Enter random name
            random_name = self.generate_random_name()
            try:
                name_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='name' or contains(@placeholder, 'Name')]"))
                )
                name_input.clear()
                name_input.send_keys(random_name)
                logger.info(f"Entered name: {random_name}")
                time.sleep(1)
            except:
                logger.warning("Name input not found, might be on different page")
            
            # Step 6: Final Continue/Signup
            try:
                final_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Sign up')]")
                final_btn.click()
                logger.info("Completed signup attempt")
            except:
                logger.warning("Final button not found")
            
            # Step 7: Wait 2 seconds
            logger.info("Waiting 2 seconds...")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing number {phone_number}: {e}")
            return False
    
    def run_automation(self, numbers_file='numbers.txt'):
        """Main automation loop"""
        if not self.setup_driver():
            return
        
        try:
            # Read phone numbers
            numbers = self.read_phone_numbers(numbers_file)
            
            if not numbers:
                logger.error("No phone numbers to process!")
                return
            
            logger.info(f"Starting automation for {len(numbers)} numbers")
            
            # Process each number
            for i, number in enumerate(numbers, 1):
                logger.info(f"Progress: {i}/{len(numbers)}")
                
                success = self.process_number(number)
                
                if success:
                    logger.info(f"Successfully processed number {i}")
                else:
                    logger.error(f"Failed to process number {i}")
                
                # Random delay between attempts (2-5 seconds)
                if i < len(numbers):
                    delay = random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.1f} seconds before next attempt...")
                    time.sleep(delay)
            
            logger.info("Automation completed!")
            
        except KeyboardInterrupt:
            logger.info("Automation stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")

def main():
    """Main function"""
    print("""
    ╔════════════════════════════════════╗
    ║   Canva Phone Automation Tool      ║
    ║       For Termux + GitHub          ║
    ╚════════════════════════════════════╝
    """)
    
    # Check if numbers file exists
    numbers_file = 'numbers.txt'
    if not os.path.exists(numbers_file):
        print(f"⚠️  {numbers_file} not found!")
        print("Creating sample file with test numbers...")
        automation = CanvaAutomation()
        automation.create_sample_file()
    
    print(f"📱 Using numbers from: {numbers_file}")
    print("1️⃣  Starting automation in normal mode")
    print("2️⃣  Starting automation in headless mode (background)")
    print("3️⃣  Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        automation = CanvaAutomation(headless=False)
        automation.run_automation(numbers_file)
    elif choice == '2':
        automation = CanvaAutomation(headless=True)
        automation.run_automation(numbers_file)
    else:
        print("Exiting...")
        return

if __name__ == "__main__":
    main()
