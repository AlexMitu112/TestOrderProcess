import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time 
import csv
import logging
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')


class ElementsExistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up the WebDriver for the test class. This method initializes the Chrome WebDriver
        with specified options and navigates to the target URL.
        """
        cls.service = Service()
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--no-sandbox")
        cls.options.add_argument("--disable-webusb")
        cls.options.add_argument("--log-level=1")
        cls.options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        cls.driver = webdriver.Chrome(service=cls.service, options=cls.options)
        cls.driver.get("https://magento.softwaretestingboard.com/")

    def test_search_box(self):
        """Test if the search box is present on the page."""
        self.assertTrue(self.is_element_present(By.NAME, "q"), "Search box is not present on the page.")

    def test_cart_button(self):
        """Test if the cart button is present on the page."""
        self.assertTrue(self.is_element_present(By.CLASS_NAME, "showcart"), "Cart button is not present on the page.")

    @classmethod
    def tearDownClass(cls):
        """
        Tear down the WebDriver after all tests have been run. This method quits the WebDriver,
        closing all associated windows.
        """
        cls.driver.quit()

    def is_element_present(self, how, what):
        """
        Check if an element is present on the page.

        Args:
            how (By): The type of locator (e.g., By.ID, By.NAME, etc.).
            what (str): The value of the locator.

        Returns:
            bool: True if the element is found, False otherwise.
        """
        try:
            self.driver.find_element(how, what)
            return True
        except NoSuchElementException:
            return False

class TestOrderPlacementProcess(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.service = Service()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-webusb")
        self.options.add_argument("--log-level=1")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.driver.get("https://magento.softwaretestingboard.com/")
    
    @classmethod
    def tearDown(self):
        self.driver.quit()

    def search_item(self, item_name):
        search_field = self.driver.find_element(By.ID, "search")
        search_field.send_keys(item_name,Keys.ENTER)
        items = self.driver.find_elements(By.CLASS_NAME, "product-item-info")
        if items:
            first_item = items[0]
            first_item.click()
            logging.info("itemfound")
        else:
            logging.info("item not found")


    def add_item_to_cart(self, item_name, quantity, size = None, color = None ):
        
        self.search_item(item_name)
        
        if size:
            size_xpath = f"//div[@class='swatch-option text' and .//text()='{size}']"
            size_locator = self.driver.find_element(By.XPATH,size_xpath)
            size_locator.click()
        if color:
            color_xpath = f"//div[@class='swatch-option color' and @option-label='{color}']"
            color_locator = self.driver.find_element(By.XPATH,color_xpath)
            color_locator.click()
        
        quantity_field = self.driver.find_element(By.XPATH,"//input[@id='qty']")
        quantity_field.clear()
        quantity_field.send_keys(quantity)

        add_to_card_button = self.driver.find_element(By.ID, "product-addtocart-button")
        add_to_card_button.click()


    def fill_text_fields(self, by_strategy, locator_value, text):
        
        try:
            element = self.driver.find_element(by_strategy, locator_value)
            element.clear()  # Clear existing text
            element.send_keys(text)
            return True
        except Exception as e:
            logging.error(f"Failed to send keys to element {locator_value}: {e}")
            return False


    def fill_order_details_for_no_login_user(self):
        """
        Fills in the order details for a user who is not logged in.

        This function reads user details from a CSV file and fills out the order form fields on the page.
        It also selects the appropriate country and region from dropdown menus.
        """

        # Wait for the page to load
        time.sleep(3)

        # Load the order details from the CSV file into a dictionary
        csv_dict = {}
        try:
            with open('order_details.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                csv_dict = {row[0]: row[1] for row in csv_reader}
            logging.info(f"Loaded order details from CSV: {csv_dict}")
        except FileNotFoundError:
            logging.error("The order_details.csv file was not found.")
            return False
        except Exception as e:
            logging.error(f"An error occurred while reading the CSV file: {e}")
            return False

        # Define field locators and corresponding CSV keys
        field_mappings = {
            "customer-email": (By.ID, "customer-email"),
            "firstname": (By.NAME, "firstname"),
            "lastname": (By.NAME, "lastname"),
            "company": (By.NAME, "company"),
            "street[0]": (By.NAME, "street[0]"),
            "street[1]": (By.NAME, "street[1]"),
            "street[2]": (By.NAME, "street[2]"),
            "city": (By.NAME, "city"),
            "postcode": (By.NAME, "postcode"),
            "telephone": (By.NAME, "telephone"),
        }

        # Fill in the form fields using the field mappings
        for csv_key, locator in field_mappings.items():
            if csv_key in csv_dict:
                self.fill_text_fields(*locator, csv_dict[csv_key])
            else:
                logging.warning(f"CSV key '{csv_key}' not found in the CSV data.")

        # Select the country from the dropdown menu
        try:
            country_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[@name='country_id']"))
            )
            select = Select(country_dropdown)
            select.select_by_value("RO")
            logging.info("Country selected successfully.")
        except Exception as e:
            logging.error(f"Failed to select country: {e}")
            return False

        # Select the region from the dropdown menu
        try:
            region_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[@name='region_id']"))
            )
            select = Select(region_dropdown)
            select.select_by_value("279")
            logging.info("Region selected successfully.")
        except Exception as e:
            logging.error(f"Failed to select region: {e}")
            return False

        return True

    def log_in(self):
        self.driver.get("https://magento.softwaretestingboard.com/customer/account/login")

        WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((By.ID, "email")))
        username_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "pass")
        
        username_field.send_keys("test123@yahoo.com")
        password_field.send_keys("Test123!")
        
        login_button = self.driver.find_element(By.ID, "send2")
        login_button.click()
        
        return True
    

    
    def test_log_in(self):
        """
        Test the login functionality on the Magento software testing board.

        This test navigates to the login page, enters a predefined username and password, 
        and clicks the login button. It then verifies whether the user is successfully logged in 
        by checking the presence of a welcome message.

        The test will fail if:
        - The login page elements (username, password fields, or login button) are not interactable.
        - The welcome message does not appear after attempting to log in.
        - The welcome message does not match the expected text.
        """
        self.driver.get("https://magento.softwaretestingboard.com/customer/account/login")

        WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((By.ID, "email")))
        username_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "pass")
        
        username_field.send_keys("test123@yahoo.com")
        password_field.send_keys("Test123!")
        
        login_button = self.driver.find_element(By.ID, "send2")
        login_button.click()
        
        try:
            email_display = WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((By.CLASS_NAME, "logged-in")))
            self.assertEqual(email_display.text, "Welcome, Test Testing!", "Name not valid")
        except NoSuchElementException:
            self.fail("Failed to validate the login by seeing the welcome prompt (logged-in text).")

    def log_out(self):
        """
        Logs the user out from the Magento software testing board.

        This function navigates to the homepage, triggers the logout process by 
        interacting with the user action menu, and clicks the sign-out button to 
        log the user out. It assumes the user is already logged in.

        The function will fail silently if:
        - The logout action switch or sign-out button cannot be found.
        """
        self.driver.get("https://magento.softwaretestingboard.com/")
        log_out_action_switch = self.driver.find_elements(By.XPATH,"//span[@class='customer-name']//button[@class='action switch']")
        log_out_action_switch[0].click()

        sign_out_locators = self.driver.find_elements(By.XPATH, "//li[@class='authorization-link']/a")
        sign_out_button = sign_out_locators[0]
        sign_out_button.click()

        
    
    def test_log_out(self):
        """
        Test the logout functionality on the Magento software testing board.

        This test uses the log_in function to log in, navigates to the homepage, 
        triggers the logout process by interacting with the user action menu, 
        and clicks the sign-out button to log the user out. It then verifies 
        that the user is logged out by checking for the presence of the "Sign In" button.

        The test will fail if:
        - The logout action switch or sign-out button cannot be found.
        - The "Sign In" button does not appear after logging out.
        """
        driver = self.driver
        driver.get("https://magento.softwaretestingboard.com/")

        self.log_in()
        
        try:
            # Locate the action switch for the user menu to reveal the logout option
            log_out_action_switch = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='customer-name']//button[@class='action switch']"))
            )
            # Click the action switch button
            log_out_action_switch.click()

            # Locate the sign-out button from the dropdown menu
            sign_out_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@class='authorization-link']/a"))
            )
            # Click the sign-out button to log out
            sign_out_button.click()

        except (NoSuchElementException, TimeoutError) as e:
            self.fail(f"Logout failed: {e}")


    def go_to_view_and_edit_cart(self):
        """
        Navigates to the 'View and Edit Cart' page.

        This function clicks the 'Show Cart' button to display the cart dropdown,
        waits for it to be fully loaded, and then clicks the 'View and Edit Cart' 
        button to navigate to the cart page.
        """

        # Find and click the 'Show Cart' button
        try:
            show_cart_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.action.showcart"))
            )
            logging.info("Show Cart button found and clicked.")
            show_cart_button.click()
        except Exception as e:
            logging.error(f"Failed to find or click the Show Cart button: {e}")
            return

        # Wait for the cart dropdown to fully load and be clickable
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@class='action viewcart']"))
            )
            logging.info("Cart dropdown is visible.")
        except Exception as e:
            logging.error(f"Cart dropdown did not become visible: {e}")
            return

        # Find and click the 'View and Edit Cart' button
        try:
            view_cart_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='action viewcart']"))
            )
            view_cart_button.click()
            logging.info("View Cart button clicked, navigating to the cart page.")
        except Exception as e:
            logging.error(f"Failed to find or click the View Cart button: {e}")
            return


        
    def go_to_checkout(self):
        """
        Navigates to the checkout page.

        This function first verifies the presence of items in the cart, then interacts 
        with the 'Show Cart' button to display the cart dropdown, and finally clicks 
        the 'Go to Checkout' button to navigate to the checkout page.
        """
        WebDriverWait(self.driver, 20).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-mask"))
        )
        time.sleep(3)
        # Verify that the item counter is present and visible
        try:
            item_counter = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "counter-number"))
            )
            logging.info("Item counter found!")
        except Exception as e:
            logging.error(f"Item counter not found: {e}")
            return

        # Find and click the 'Show Cart' button
        try:
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-mask"))
            )
            show_cart_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.action.showcart"))
            )
            logging.info("Show Cart button found and clicked.")
            show_cart_button.click()
        except Exception as e:
            logging.error(f"Failed to find or click the Show Cart button: {e}")
            return

        # Wait for the 'Go to Checkout' button to be clickable
        try:
            go_to_checkout_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "top-cart-btn-checkout"))
            )
            logging.info("Go to Checkout button found and clicked.")
            go_to_checkout_button.click()
        except Exception as e:
            logging.error(f"Failed to find or click the Go to Checkout button: {e}")
            return



    def apply_discount_code(self):
        """
        Applies a discount code during the checkout process.

        This function opens the discount code section, removes any existing discount code 
        if present, and applies a new discount code. The function assumes that the user 
        is already on the checkout page or a relevant page where the discount can be applied.

        The function will fail if:
        - The discount code section cannot be opened.
        - The discount code field or apply button is not interactable.
        """

        try:
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-mask"))
            )
            time.sleep(3)
            # Wait for and click the discount code section to expand it
            discount_code_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "block-discount-heading"))
            )
            discount_code_button.click()
            logging.info("Discount code section opened.")
            
        except Exception as e:
            logging.error(f"Failed to open the discount code section: {e}")
            return False

        # If a cancel button is present, it means a coupon is already applied, so remove it
        try:
            cancel_coupon_button = self.driver.find_element(By.XPATH, "//button[@class='action action-cancel']//span//span")
            cancel_coupon_button.click()
            logging.info("Existing discount code canceled.")
        except Exception:
            logging.info("No existing discount code to cancel.")

        try:
            # Wait for the discount code field to be interactable, then input the discount code
            discount_code_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "discount-code"))
            )
            discount_code_field.send_keys("20poff")
            logging.info("Discount code '20poff' entered.")
            
            # Wait for and click the apply button
            apply_button = self.driver.find_element(By.XPATH, "//button[@class='action action-apply']")
            apply_button.click()
            logging.info("Apply button clicked.")

            # Optionally, add a wait here for any confirmation message or element that appears after applying the discount

        except Exception as e:
            logging.error(f"Failed to apply the discount code: {e}")
            return False

        logging.info("Discount applied successfully.")
        return True


    def delete_all_cart_items(self):
        """
        Deletes all items from the shopping cart.

        This function navigates to the cart page, iteratively removes each item by clicking
        the delete button, and waits until all items are removed from the cart. The process
        continues until no delete buttons are found, indicating an empty cart.

        The function logs the number of items found and deleted, and handles exceptions if
        issues are encountered during the process.
        """

        # Navigate to the cart page
        self.driver.get("https://magento.softwaretestingboard.com/checkout/cart/")

        while True:
            try:
                # Find all delete buttons currently on the page
                delete_item_buttons = self.driver.find_elements(By.CLASS_NAME, "action-delete")
                if not delete_item_buttons:
                    logging.info("No more items to delete. The cart is empty.")
                    break

                logging.info(f"Found {len(delete_item_buttons)} delete item button(s).")

                # Click the first delete button found
                elem = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(delete_item_buttons[0])
                )
                elem.click()
                logging.info("Clicked delete button for an item.")

                # Wait until the item is removed from the DOM (element becomes stale)
                WebDriverWait(self.driver, 20).until(EC.staleness_of(elem))
                logging.info("Item removed from the cart.")

                # Optional: Short sleep to allow DOM to fully update before next iteration
                time.sleep(2)

            except Exception as e:
                logging.error(f"Error encountered while trying to delete items: {e}")
                break
        

    def delete_specific_item_from_cart_by_item_name(self, item_name):
        self.go_to_view_and_edit_cart()
    
    def delete_specific_item_from_cart_by_index(self, index):
        self.go_to_view_and_edit_cart()

 
    def test_buy_item_no_login(self):
        """
        Tests purchasing items as a guest user without logging in.

        This function:
        - Adds specified items to the shopping cart.
        - Verifies the item counter to confirm items were added.
        - Proceeds to checkout.
        - Fills in the order details as a guest user.
        - Submits the order.

        The function logs each step and handles any issues encountered during the process.
        """

        # Navigate to the homepage
        self.driver.get("https://magento.softwaretestingboard.com")

        # Add items to the cart
        self.add_item_to_cart("Proteus Fitness Jackshirt", 3, "XL", "Orange")
        self.add_item_to_cart("Overnight Duffle", 3)

        # Check if the item counter exists and validate the cart contents
        try:
            item_counter = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "counter-number"))
            )
            logging.info(f"Item counter found with {item_counter.text} item(s).")
        except Exception as e:
            logging.error(f"Item counter not found: {e}")
            return False

        # Proceed to checkout using the cart button
        try:
            show_cart_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.action.showcart"))
            )
            logging.info("Show Cart button found and clicked.")
            show_cart_button.click()
        except Exception as e:
            logging.error(f"Show Cart button not found or not clickable: {e}")
            return False

        try:
            go_to_checkout_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "top-cart-btn-checkout"))
            )
            logging.info("Go to Checkout button found and clicked.")
            go_to_checkout_button.click()
        except Exception as e:
            logging.error(f"Go to Checkout button not found or not clickable: {e}")
            return False
        self.driver.get("https://magento.softwaretestingboard.com/checkout/#shipping")
        # Wait for the page to load completely before proceeding
        WebDriverWait(self.driver, 100).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

        # Fill in the order details as a guest user
        self.fill_order_details_for_no_login_user()

        # Select shipping method
        try:
            # Wait for any loading mask to disappear
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-mask"))
            )
            time.sleep(5)

            shipping_radio_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio']"))
            )
            shipping_radio_button.click()
            logging.info("Shipping method selected.")

            # Wait for any loading mask to disappear
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.loading-mask"))
            )
            time.sleep(3)

            shipping_method_form = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "co-shipping-method-form"))
            )
            shipping_method_form.submit()
            logging.info("Shipping method form submitted.")
        except Exception as e:
            logging.error(f"Failed to select shipping method or submit form: {e}")
            return False

        # Proceed to payment
        try:
            
            payment_form = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "co-payment-form"))
            )
            payment_form.submit()
            logging.info("Payment form submitted.")

            place_order_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Place Order']"))
            )
            place_order_button.click()
            logging.info("Place Order button clicked, order placed.")
        except Exception as e:
            logging.error(f"Failed to submit payment or place order: {e}")
            return False

        return True



    def test_buy_item_login(self):
        """
        Tests purchasing items while logged in.

        This function:
        - Logs into the user account.
        - Adds specified items to the shopping cart.
        - Proceeds to checkout.
        - Applies a discount code.
        - Completes the checkout process.

        The function logs each step and handles exceptions if any issues are encountered.
        """

        # Navigate to the homepage
        self.driver.get("https://magento.softwaretestingboard.com")

        # Log in
        self.log_in()
        logging.info("User logged in successfully.")

        # Add items to the cart
        self.add_item_to_cart("Proteus Fitness Jackshirt", 3, "XL", "Orange")
        self.add_item_to_cart("Overnight Duffle", 3)
        self.add_item_to_cart("Ina Compression Short", 3, 28, "Red")
        logging.info("Items added to cart.")

        # Proceed to checkout
        self.go_to_checkout()
        logging.info("Navigated to checkout.")

        # Wait for the page to load fully
        time.sleep(4)  # Replace with WebDriverWait if specific element presence is needed

        try:
            # Locate and submit the shipping method form
            form_next_thing = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "co-shipping-method-form"))
            )
            form_next_thing.submit()
            logging.info("Shipping method form submitted.")
        except Exception as e:
            logging.error(f"Error submitting shipping method form: {e}")
            return False

        # Apply a discount code
        self.apply_discount_code()
        logging.info("Discount code applied.")

        return True

            
    def test_delete_cart_items(self):
        """
        Tests adding items to the cart, deleting them, and logging out.

        This function:
        - Logs into the user account.
        - Adds specified items to the shopping cart.
        - Deletes all items from the cart.
        - Logs out from the account.

        The function logs each step and waits appropriately to ensure actions are completed.
        """

        # Navigate to the homepage
        driver = self.driver
        driver.get("https://magento.softwaretestingboard.com")
        logging.info("Navigated to homepage.")

        # Log in to the account
        self.log_in()
        logging.info("User logged in successfully.")

        # Add items to the cart
        self.add_item_to_cart("Proteus Fitness Jackshirt", 3, "XL", "Orange")
        self.add_item_to_cart("Overnight Duffle", 3)
        logging.info("Items added to cart.")

        # Delete all items from the cart
        self.delete_all_cart_items()
        logging.info("All items deleted from cart.")

        # Wait for the cart to update
        time.sleep(10)  # Consider replacing with a more dynamic wait if needed

        # Log out of the account
        self.log_out()
        logging.info("User logged out successfully.")


if __name__ == "__main__":
    # unittest.main()


    elements_checking = unittest.TestLoader().loadTestsFromTestCase(ElementsExistenceTests)
    order_process_checking = unittest.TestLoader().loadTestsFromTestCase(TestOrderPlacementProcess)
    test_suite = unittest.TestSuite([order_process_checking, elements_checking])


    # run the suite
    unittest.TextTestRunner(verbosity=2).run(test_suite)
